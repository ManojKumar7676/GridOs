"""
Accenture GridOS™ - Security-Constrained Economic Dispatch (SCED) & Multi-Action Optimizer
Implements all action categories defined in Problem Statement 4 (Utilities – Renewable Energy Orchestrator):
1. Battery Actions (Charge, Discharge, Emergency Reserve)
2. Market Actions (Buy, Sell, Delay Selling / Store for Peak)
3. Renewable Actions (Curtail Wind, Curtail Solar, Prioritize Clean Gen)
4. Demand Management (Trigger DR, Shift Industrial Load, Reduce Non-Critical)
5. Maintenance Actions (Delay Maintenance, Schedule Maintenance, Dispatch Inspection Teams)
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import numpy as np
from scipy.optimize import linprog

from AccentureAssessment.core.portfolio import UtilityPortfolioState, AssetStatus, MaintenancePriority
from AccentureAssessment.config.prompt_config import PromptConfig, get_prompt_config

@dataclass
class DispatchWeights:
    profit_weight: float = 0.35
    carbon_weight: float = 0.25
    reliability_weight: float = 0.20
    battery_health_weight: float = 0.10
    curtailment_penalty_weight: float = 0.10

@dataclass
class DispatchExecutionResult:
    solar_generation_mw: float
    solar_curtailed_mw: float
    wind_generation_mw: float
    wind_curtailed_mw: float
    bess1_charge_mw: float
    bess1_discharge_mw: float
    bess2_charge_mw: float
    bess2_discharge_mw: float
    bess1_next_soc_pct: float
    bess2_next_soc_pct: float
    grid_import_mw: float
    grid_export_mw: float
    market_revenue_cost_usd: float
    served_demand_mw: float
    dr_curtailed_demand_mw: float
    shifted_load_mw: float
    carbon_emitted_kg: float
    carbon_avoided_kg: float
    battery_degradation_usd: float
    action_cluster: List[Dict[str, Any]]
    reserve_margin_mw: float
    grid_stress_level: str
    optimality_score: float
    solver_status: str = "OPTIMAL_HIGHS"
    locational_marginal_price_usd_mwh: float = 0.0

class IndustrialDispatchSolver:
    """
    Physical SCED optimization engine.
    Solves 15-minute unit commitment and dispatch via HiGHS linear programming.
    """

    def __init__(self, delta_t_hours: float = 0.25, prompt_config: Optional[PromptConfig] = None):
        self.dt = delta_t_hours
        self.prompt_config = prompt_config or get_prompt_config()

    def solve(
        self,
        portfolio: UtilityPortfolioState,
        weights: DispatchWeights,
        attenuation_factor: float = 1.0,
        manual_override: Optional[Dict[str, Any]] = None
    ) -> DispatchExecutionResult:
        manual_override = manual_override or {}

        # 1. Available Renewable Generation (accounting for asset availability)
        total_solar_avail = 0.0
        maintenance_actions: List[Dict[str, Any]] = []

        for s in portfolio.solar_farms:
            is_avail = getattr(s, "is_available", True) and (s.status == AssetStatus.OPERATIONAL)
            if is_avail:
                derate = getattr(s, "cloud_attenuation_factor", attenuation_factor)
                if derate == 1.0 and attenuation_factor != 1.0:
                    derate = attenuation_factor
                s.current_output_mw = s.capacity_mw * derate
            else:
                s.current_output_mw = 0.0
                maintenance_actions.append({
                    "category": "MAINTENANCE",
                    "scada_code": "MNT_DISPATCH_CREW",
                    "action": "DISPATCH_INSPECTION_TEAMS",
                    "target": s.id,
                    "amount_mw": 0.0,
                    "rationale": self.prompt_config.get_action_rationale("maintenance_actions", "solar_inspection", name=s.name)
                })
            
            # Thermal maintenance reasoning
            if s.inverter_temperature_c > 62.0:
                if portfolio.market.spot_price_per_mwh > 90.0:
                    maintenance_actions.append({
                        "category": "MAINTENANCE",
                        "scada_code": "MNT_DELAY_PEAK",
                        "action": "DELAY_MAINTENANCE",
                        "target": s.id,
                        "amount_mw": round(s.current_output_mw, 1),
                        "rationale": self.prompt_config.get_action_rationale("maintenance_actions", "solar_delay_peak", spot=portfolio.market.spot_price_per_mwh)
                    })
                else:
                    maintenance_actions.append({
                        "category": "MAINTENANCE",
                        "scada_code": "MNT_SCHEDULE_OFFPEAK",
                        "action": "SCHEDULE_MAINTENANCE",
                        "target": s.id,
                        "amount_mw": round(s.current_output_mw, 1),
                        "rationale": self.prompt_config.get_action_rationale("maintenance_actions", "solar_schedule_offpeak", temp=s.inverter_temperature_c)
                    })

            total_solar_avail += s.current_output_mw

        total_wind_avail = 0.0
        for w in portfolio.wind_farms:
            is_avail = getattr(w, "is_available", True) and (w.status == AssetStatus.OPERATIONAL)
            if is_avail:
                if w.wind_speed_mps < w.cut_in_speed or w.wind_speed_mps > w.cut_out_speed:
                    w.current_output_mw = 0.0
                    if w.wind_speed_mps > w.cut_out_speed:
                        maintenance_actions.append({
                            "category": "MAINTENANCE",
                            "scada_code": "MNT_GUST_LOCKOUT",
                            "action": "SCHEDULE_MAINTENANCE",
                            "target": w.id,
                            "amount_mw": 0.0,
                            "rationale": self.prompt_config.get_action_rationale("maintenance_actions", "wind_storm_lockout", speed=w.wind_speed_mps, cut_out=w.cut_out_speed)
                        })
                else:
                    factor = min(1.0, ((w.wind_speed_mps - w.cut_in_speed) / (12.0 - w.cut_in_speed)) ** 2)
                    w.current_output_mw = w.capacity_mw * factor
            else:
                w.current_output_mw = 0.0
                maintenance_actions.append({
                    "category": "MAINTENANCE",
                    "scada_code": "MNT_DISPATCH_CREW",
                    "action": "DISPATCH_INSPECTION_TEAMS",
                    "target": w.id,
                    "amount_mw": 0.0,
                    "rationale": self.prompt_config.get_action_rationale("maintenance_actions", "wind_inspection", name=w.name)
                })
            total_wind_avail += w.current_output_mw

        # 2. Demand Profile
        base_demand = sum(ind.base_load_mw for ind in portfolio.industrial_consumers)
        flexible_demand = sum(ind.flexible_shiftable_mw for ind in portfolio.industrial_consumers)
        interruptible_demand = sum(ind.interruptible_mw for ind in portfolio.industrial_consumers)
        total_gross_demand = base_demand + flexible_demand

        # 3. Battery Storage Physical Boundaries (accounting for asset availability)
        b1 = portfolio.bess_systems[0]
        b2 = portfolio.bess_systems[1]

        b1_avail = getattr(b1, "is_available", True) and (b1.status == AssetStatus.OPERATIONAL)
        b2_avail = getattr(b2, "is_available", True) and (b2.status == AssetStatus.OPERATIONAL)

        if not b1_avail:
            maintenance_actions.append({
                "category": "MAINTENANCE",
                "scada_code": "MNT_BESS_OUTAGE",
                "action": "DISPATCH_INSPECTION_TEAMS",
                "target": b1.id,
                "amount_mw": 0.0,
                "rationale": self.prompt_config.get_action_rationale("maintenance_actions", "bess_inspection", name=b1.name)
            })
        if not b2_avail:
            maintenance_actions.append({
                "category": "MAINTENANCE",
                "scada_code": "MNT_BESS_OUTAGE",
                "action": "DISPATCH_INSPECTION_TEAMS",
                "target": b2.id,
                "amount_mw": 0.0,
                "rationale": self.prompt_config.get_action_rationale("maintenance_actions", "bess_inspection", name=b2.name)
            })

        b1_max_disch = min(
            b1.power_rating_mw if b1_avail else 0.0,
            max(0.0, (b1.current_soc_pct - b1.min_soc_pct) / 100.0 * b1.energy_capacity_mwh / self.dt)
        )
        b2_max_disch = min(
            b2.power_rating_mw if b2_avail else 0.0,
            max(0.0, (b2.current_soc_pct - b2.min_soc_pct) / 100.0 * b2.energy_capacity_mwh / self.dt)
        )

        b1_max_chg = min(
            b1.power_rating_mw if b1_avail else 0.0,
            max(0.0, (b1.max_soc_pct - b1.current_soc_pct) / 100.0 * b1.energy_capacity_mwh / (self.dt * b1.roundtrip_efficiency))
        )
        b2_max_chg = min(
            b2.power_rating_mw if b2_avail else 0.0,
            max(0.0, (b2.max_soc_pct - b2.current_soc_pct) / 100.0 * b2.energy_capacity_mwh / (self.dt * b2.roundtrip_efficiency))
        )

        # 4. Transmission Intertie Limits
        max_export = portfolio.grid.max_export_mw
        if portfolio.grid.transmission_congested:
            max_export *= 0.5  # Derated corridor thermal rating

        max_import = portfolio.grid.max_import_mw

        # 5. Formulate Linear Programming Optimization (HiGHS)
        spot_price = portfolio.market.spot_price_per_mwh
        future_price = portfolio.market.projected_price_next_hour
        carbon_tax = portfolio.market.carbon_credit_price_per_ton
        carbon_intensity = portfolio.grid.grid_carbon_intensity_kg_per_mwh / 1000.0  # tons CO2/MWh

        c_curt = 25.0 * (weights.curtailment_penalty_weight / 0.10)
        c_deg1 = b1.degradation_cost_per_mwh * (weights.battery_health_weight / 0.10)
        c_deg2 = b2.degradation_cost_per_mwh * (weights.battery_health_weight / 0.10)
        c_carbon = carbon_tax * carbon_intensity * (weights.carbon_weight / 0.25)
        w_p = max(0.05, weights.profit_weight / 0.35)

        # Inter-temporal forward arbitrage factor:
        # If future price is significantly higher than spot, increase value of retaining battery charge
        forward_premium = max(0.0, future_price - spot_price)
        if forward_premium > 15.0:
            c_deg1 += (forward_premium * 0.4)
            c_deg2 += (forward_premium * 0.4)

        c = np.zeros(13)
        c[0] = 0.0                          # P_solar
        c[1] = c_curt                       # P_solar_curt
        c[2] = 0.0                          # P_wind
        c[3] = c_curt                       # P_wind_curt
        c[4] = c_deg1                       # P_bess1_chg
        c[5] = c_deg1                       # P_bess1_disch
        c[6] = c_deg2                       # P_bess2_chg
        c[7] = c_deg2                       # P_bess2_disch
        c[8] = - spot_price * w_p           # P_grid_exp
        c[9] = (spot_price * w_p) + c_carbon # P_grid_imp
        c[10] = 12.0                        # P_dr_shift
        c[11] = 65.0                        # P_dr_curt
        c[12] = 5000.0                      # P_unserved

        row_eb = [1.0, 0.0, 1.0, 0.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, 1.0, 1.0, 1.0]
        row_sol = [1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        row_wnd = [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        A_eq = np.array([row_eb, row_sol, row_wnd])
        b_eq = np.array([total_gross_demand, total_solar_avail, total_wind_avail])

        bounds = [
            (0.0, max(0.0, total_solar_avail)),  # 0: P_solar
            (0.0, max(0.0, total_solar_avail)),  # 1: P_solar_curt
            (0.0, max(0.0, total_wind_avail)),   # 2: P_wind
            (0.0, max(0.0, total_wind_avail)),   # 3: P_wind_curt
            (0.0, max(0.0, b1_max_chg)),         # 4: P_bess1_chg
            (0.0, max(0.0, b1_max_disch)),       # 5: P_bess1_disch
            (0.0, max(0.0, b2_max_chg)),         # 6: P_bess2_chg
            (0.0, max(0.0, b2_max_disch)),       # 7: P_bess2_disch
            (0.0, max(0.0, max_export if spot_price > 0 else 0.0)), # 8: P_grid_exp
            (0.0, max(0.0, max_import)),         # 9: P_grid_imp
            (0.0, max(0.0, flexible_demand * 0.7)), # 10: P_dr_shift
            (0.0, max(0.0, interruptible_demand)),# 11: P_dr_curt
            (0.0, None)                          # 12: P_unserved
        ]

        lp_res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

        if lp_res.success:
            x = lp_res.x
            solver_status = "OPTIMAL_HIGHS"
            lmp = float(lp_res.con[0]) if hasattr(lp_res, 'con') and len(lp_res.con) > 0 else spot_price
        else:
            x = np.zeros(13)
            x[0] = total_solar_avail
            x[2] = total_wind_avail
            net_avail = total_solar_avail + total_wind_avail
            if net_avail >= total_gross_demand:
                x[8] = min(max_export, net_avail - total_gross_demand)
            else:
                x[9] = min(max_import, total_gross_demand - net_avail)
            solver_status = "FALLBACK_FEASIBLE"
            lmp = spot_price

        p_solar = float(x[0])
        p_solar_curt = float(x[1])
        p_wind = float(x[2])
        p_wind_curt = float(x[3])
        p_bess1_chg = float(x[4])
        p_bess1_disch = float(x[5])
        p_bess2_chg = float(x[6])
        p_bess2_disch = float(x[7])
        p_grid_exp = float(x[8])
        p_grid_imp = float(x[9])
        p_dr_shift = float(x[10])
        p_dr_curt = float(x[11])
        p_unserved = float(x[12])

        # 6. Battery Electrochemical Transition
        soc1_delta = (- (p_bess1_disch * self.dt) + (p_bess1_chg * self.dt * b1.roundtrip_efficiency)) / b1.energy_capacity_mwh * 100.0
        soc2_delta = (- (p_bess2_disch * self.dt) + (p_bess2_chg * self.dt * b2.roundtrip_efficiency)) / b2.energy_capacity_mwh * 100.0
        next_soc1 = float(np.clip(b1.current_soc_pct + soc1_delta, b1.min_soc_pct, b1.max_soc_pct))
        next_soc2 = float(np.clip(b2.current_soc_pct + soc2_delta, b2.min_soc_pct, b2.max_soc_pct))

        # 7. Physical Energy Accounting
        served_demand = total_gross_demand - p_dr_curt - p_dr_shift
        rev = p_grid_exp * self.dt * spot_price
        cst = (p_grid_imp * self.dt * spot_price) + (p_dr_curt * self.dt * 65.0)
        net_financial = rev - cst

        bess_wear = ((p_bess1_chg + p_bess1_disch) * self.dt * b1.degradation_cost_per_mwh) + \
                    ((p_bess2_chg + p_bess2_disch) * self.dt * b2.degradation_cost_per_mwh)

        clean_gen = p_solar + p_wind + ((p_bess1_disch + p_bess2_disch) * 0.90)
        carbon_avoided = clean_gen * self.dt * portfolio.grid.grid_carbon_intensity_kg_per_mwh
        carbon_emitted = p_grid_imp * self.dt * portfolio.grid.grid_carbon_intensity_kg_per_mwh

        reserve_margin = (b1_max_disch - p_bess1_disch) + (b2_max_disch - p_bess2_disch) + (max_import - p_grid_imp)
        stress = "STABLE" if reserve_margin > 60.0 else ("MODERATE" if reserve_margin > 25.0 else "CRITICAL")

        norm_profit = np.tanh(net_financial / 2000.0) * 50 + 50
        norm_green = min(100.0, (clean_gen / max(1.0, total_gross_demand)) * 100.0)
        norm_rel = min(100.0, (reserve_margin / 100.0) * 100.0)
        score = (weights.profit_weight * norm_profit +
                 weights.carbon_weight * norm_green +
                 weights.reliability_weight * norm_rel +
                 weights.battery_health_weight * max(0.0, 100.0 - (bess_wear * 1.5)))

        # 8. Emit Discrete Action Clusters across all 5 Problem Statement Categories
        actions: List[Dict[str, Any]] = []

        # A. Battery Actions
        if p_bess1_chg > 0.05:
            actions.append({
                "category": "BATTERY_ACTIONS",
                "scada_code": "BESS_CMD_CHARGE",
                "action": "CHARGE_BATTERIES",
                "target": b1.id,
                "amount_mw": round(p_bess1_chg, 1),
                "rationale": self.prompt_config.get_action_rationale("battery_actions", "charge_bulk", mw=p_bess1_chg)
            })
        elif p_bess1_disch > 0.05:
            actions.append({
                "category": "BATTERY_ACTIONS",
                "scada_code": "BESS_CMD_DISCHARGE",
                "action": "DISCHARGE_BATTERIES",
                "target": b1.id,
                "amount_mw": round(p_bess1_disch, 1),
                "rationale": self.prompt_config.get_action_rationale("battery_actions", "discharge_bulk", mw=p_bess1_disch)
            })

        if p_bess2_chg > 0.05:
            actions.append({
                "category": "BATTERY_ACTIONS",
                "scada_code": "BESS_CMD_CHARGE",
                "action": "CHARGE_BATTERIES",
                "target": b2.id,
                "amount_mw": round(p_bess2_chg, 1),
                "rationale": self.prompt_config.get_action_rationale("battery_actions", "charge_peaker", mw=p_bess2_chg)
            })
        elif p_bess2_disch > 0.05:
            actions.append({
                "category": "BATTERY_ACTIONS",
                "scada_code": "BESS_CMD_DISCHARGE",
                "action": "DISCHARGE_BATTERIES",
                "target": b2.id,
                "amount_mw": round(p_bess2_disch, 1),
                "rationale": self.prompt_config.get_action_rationale("battery_actions", "discharge_peaker", mw=p_bess2_disch)
            })

        # Reserve battery capacity action if reserves are constrained or storm active
        if reserve_margin < 50.0 and (p_bess1_disch == 0 or p_bess2_disch == 0):
            actions.append({
                "category": "BATTERY_ACTIONS",
                "scada_code": "BESS_CMD_RESERVE_EMERGENCY",
                "action": "RESERVE_BATTERY_CAPACITY",
                "target": "BESS Hub",
                "amount_mw": round(reserve_margin, 1),
                "rationale": self.prompt_config.get_action_rationale("battery_actions", "reserve_emergency", reserve_mw=reserve_margin)
            })

        # B. Market Actions
        if p_grid_exp > 0.05:
            actions.append({
                "category": "MARKET_ACTIONS",
                "scada_code": "MKT_CMD_SELL",
                "action": "SELL_ELECTRICITY",
                "target": portfolio.grid.intertie_id,
                "amount_mw": round(p_grid_exp, 1),
                "rationale": self.prompt_config.get_action_rationale("market_actions", "sell", mw=p_grid_exp, spot=spot_price)
            })
        elif spot_price < 0.0:
            actions.append({
                "category": "MARKET_ACTIONS",
                "scada_code": "MKT_CMD_SUPPRESS_EXPORT",
                "action": "DELAY_SELLING_UNTIL_PRICES_RISE",
                "target": portfolio.grid.intertie_id,
                "amount_mw": 0.0,
                "rationale": self.prompt_config.get_action_rationale("market_actions", "suppress_export", spot=spot_price)
            })
        elif forward_premium > 15.0 and p_grid_exp == 0.0 and (total_solar_avail + total_wind_avail) > total_gross_demand:
            actions.append({
                "category": "MARKET_ACTIONS",
                "scada_code": "MKT_CMD_HOLD_ARBITRAGE",
                "action": "DELAY_SELLING_UNTIL_PRICES_RISE",
                "target": portfolio.grid.intertie_id,
                "amount_mw": 0.0,
                "rationale": self.prompt_config.get_action_rationale("market_actions", "forward_arbitrage", spread=forward_premium)
            })

        if p_grid_imp > 0.05:
            actions.append({
                "category": "MARKET_ACTIONS",
                "scada_code": "MKT_CMD_BUY",
                "action": "BUY_ELECTRICITY",
                "target": portfolio.grid.intertie_id,
                "amount_mw": round(p_grid_imp, 1),
                "rationale": self.prompt_config.get_action_rationale("market_actions", "buy", mw=p_grid_imp)
            })

        # C. Renewable Actions
        if p_solar_curt > 0.05:
            actions.append({
                "category": "RENEWABLE_ACTIONS",
                "scada_code": "DER_CMD_CURTAIL_SOLAR",
                "action": "CURTAIL_SOLAR",
                "target": "Solar Inverter Arrays",
                "amount_mw": round(p_solar_curt, 1),
                "rationale": self.prompt_config.get_action_rationale("renewable_actions", "curtail_solar", mw=p_solar_curt)
            })
        if p_wind_curt > 0.05:
            actions.append({
                "category": "RENEWABLE_ACTIONS",
                "scada_code": "DER_CMD_CURTAIL_WIND",
                "action": "CURTAIL_WIND",
                "target": "Wind Turbine Pitch Controls",
                "amount_mw": round(p_wind_curt, 1),
                "rationale": self.prompt_config.get_action_rationale("renewable_actions", "curtail_wind", mw=p_wind_curt)
            })
        if (p_solar + p_wind) > 0.05 and (p_solar_curt + p_wind_curt) < 0.1:
            actions.append({
                "category": "RENEWABLE_ACTIONS",
                "scada_code": "DER_CMD_MERIT_DISPATCH",
                "action": "PRIORITIZE_CLEANER_GENERATION",
                "target": "All Solar & Wind Plants",
                "amount_mw": round(p_solar + p_wind, 1),
                "rationale": self.prompt_config.get_action_rationale("renewable_actions", "prioritize_clean", mw=p_solar + p_wind)
            })

        # D. Demand Management
        if p_dr_shift > 0.05:
            actions.append({
                "category": "DEMAND_MANAGEMENT",
                "scada_code": "DR_CMD_SHIFT_LOAD",
                "action": "SHIFT_INDUSTRIAL_LOADS",
                "target": "Apex Clean Hydrogen Facility",
                "amount_mw": round(p_dr_shift, 1),
                "rationale": self.prompt_config.get_action_rationale("demand_management", "shift_load", mw=p_dr_shift)
            })
        if p_dr_curt > 0.05:
            actions.append({
                "category": "DEMAND_MANAGEMENT",
                "scada_code": "DR_CMD_TRIGGER_DR",
                "action": "TRIGGER_DEMAND_RESPONSE",
                "target": "MegaTech Electric Smelter",
                "amount_mw": round(p_dr_curt, 1),
                "rationale": self.prompt_config.get_action_rationale("demand_management", "trigger_dr", mw=p_dr_curt)
            })
        if p_dr_curt == 0.0 and p_dr_shift == 0.0 and spot_price > 120.0:
            actions.append({
                "category": "DEMAND_MANAGEMENT",
                "scada_code": "DR_CMD_AUDIT_LOADS",
                "action": "REDUCE_NONCRITICAL_LOADS",
                "target": "Metro Cold Chain Terminal",
                "amount_mw": 5.0,
                "rationale": self.prompt_config.get_action_rationale("demand_management", "reduce_noncritical")
            })

        # E. Maintenance Actions
        actions.extend(maintenance_actions)

        return DispatchExecutionResult(
            solar_generation_mw=round(p_solar, 2),
            solar_curtailed_mw=round(p_solar_curt, 2),
            wind_generation_mw=round(p_wind, 2),
            wind_curtailed_mw=round(p_wind_curt, 2),
            bess1_charge_mw=round(p_bess1_chg, 2),
            bess1_discharge_mw=round(p_bess1_disch, 2),
            bess2_charge_mw=round(p_bess2_chg, 2),
            bess2_discharge_mw=round(p_bess2_disch, 2),
            bess1_next_soc_pct=round(next_soc1, 2),
            bess2_next_soc_pct=round(next_soc2, 2),
            grid_import_mw=round(p_grid_imp, 2),
            grid_export_mw=round(p_grid_exp, 2),
            market_revenue_cost_usd=round(net_financial, 2),
            served_demand_mw=round(served_demand, 2),
            dr_curtailed_demand_mw=round(p_dr_curt, 2),
            shifted_load_mw=round(p_dr_shift, 2),
            carbon_emitted_kg=round(carbon_emitted, 2),
            carbon_avoided_kg=round(carbon_avoided, 2),
            battery_degradation_usd=round(bess_wear, 2),
            action_cluster=actions,
            reserve_margin_mw=round(reserve_margin, 2),
            grid_stress_level=stress,
            optimality_score=round(score, 1),
            solver_status=solver_status,
            locational_marginal_price_usd_mwh=round(lmp, 2)
        )
