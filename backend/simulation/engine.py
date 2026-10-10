"""
Accenture GridOS™ - 24-Hour Continuous Multi-Period Simulation Engine (F3 Feature)
Simulates 96 discrete 15-minute dispatch intervals across a full diurnal duck curve.
Directly models all real-world scenarios specified in Problem Statement 4:
- Clouds reduce solar output
- Wind suddenly increases & storm cut-outs
- Electricity prices spike and go negative
- One battery storage system becomes unavailable
- Transmission line reaches its thermal capacity
- Industrial demand increases unexpectedly
- Weather radar forecasts updated
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from AccentureAssessment.backend.core.portfolio import UtilityPortfolioState, AssetStatus
from AccentureAssessment.backend.perception.radar_vision import RadarVisionEngine
from AccentureAssessment.backend.agents.orchestrator_agent import ChiefExecutiveOrchestrator

class IndustrialSimulationEngine:
    """
    Continuous 24-Hour Time-Series Simulation Engine for Utility Operations.
    Fulfills Feature F3 (Multi-Period Stochastic Simulation with Uncertainty & Shock Resilience).
    """

    def __init__(self, db_path: Optional[str] = None):
        self.vision = RadarVisionEngine()
        self.orchestrator = ChiefExecutiveOrchestrator(db_path)

    def generate_scenario_profile(self, random_seed: int = 101) -> List[Dict[str, Any]]:
        np.random.seed(random_seed)
        intervals = []

        for step in range(96):
            hour = step / 4.0
            time_str = f"{int(hour):02d}:{int((step % 4) * 15):02d}"

            # 1. Solar Diurnal Insolation Curve (Air Mass AM1.5 atmospheric model)
            if 6.0 <= hour <= 18.5:
                solar_factor = np.sin((hour - 6.0) / 12.5 * np.pi)
            else:
                solar_factor = 0.0

            # 2. Atmospheric Cloud Cover Index (0.05 to 0.95)
            cloud_index = float(np.clip(0.18 + 0.08 * np.cos(hour / 2.5) + np.random.normal(0, 0.03), 0.05, 0.95))

            # 3. Wind Velocity (m/s) with diurnal coastal breeze modulation
            wind_speed = float(np.clip(8.0 + 3.0 * np.sin(hour / 3.8 + 0.8) + np.random.normal(0, 0.6), 2.5, 23.5))

            # 4. Wholesale Electricity Market Price ($/MWh) with evening duck-curve peak
            if 17.5 <= hour <= 21.0:
                base_price = 190.0 + 45.0 * np.sin((hour - 17.5) / 3.5 * np.pi)
            elif 11.0 <= hour <= 14.5:
                base_price = 18.0  # Solar surplus midday trough
            else:
                base_price = 48.0 + 8.0 * np.cos(hour / 3.0)
            spot_price = float(base_price + np.random.normal(0, 3.5))

            # 5. Industrial Demand Profile
            if 8.0 <= hour <= 20.0:
                demand_factor = 1.12 + 0.08 * np.sin((hour - 8.0) / 12.0 * np.pi)
            else:
                demand_factor = 0.92

            # 6. Injected Real-World Operational Disturbances (from Problem Statement 4)
            event_tag = "Routine Operations"
            storm_alert = False
            transmission_congested = False
            bess1_available = True
            demand_surge_mw = 0.0

            # Scenario 1: Clouds reduce solar output
            if 34 <= step <= 38:
                cloud_index = 0.88
                solar_factor *= 0.22
                event_tag = "Clouds Reduce Solar Output (Dense Front Over Basin)"

            # Scenario 2: Negative electricity pricing
            elif step == 48:
                spot_price = -18.50
                event_tag = "Negative Electricity Pricing Event (-$18.50/MWh)"

            # Scenario 3: Wind suddenly increases & storm cut-out reached
            elif step == 60:
                storm_alert = True
                wind_speed = 26.8  # Exceeds 25 m/s cut-out threshold
                event_tag = "Storm Gusts Exceed 25 m/s Safety Cut-Out (Wind Tripped)"

            # Scenario 4: One battery becomes unavailable
            elif step == 66:
                bess1_available = False
                event_tag = "Battery Contingency: BESS-01 Becomes Unavailable (BMS Thermal Outage)"

            # Scenario 5: Electricity prices spike
            elif step == 72:
                spot_price = 285.00
                event_tag = "Electricity Price Spike ($285.00/MWh Peak Surge)"

            # Scenario 6: Transmission line reaches capacity / congestion
            elif step == 80:
                transmission_congested = True
                event_tag = "500kV Intertie Reaches Thermal Capacity (Corridor Congested)"

            # Scenario 7: Industrial demand increases unexpectedly
            elif step == 86:
                demand_surge_mw = 35.0
                event_tag = "Industrial Demand Increases Unexpectedly (+35 MW Smelter Surge)"

            intervals.append({
                "step": step,
                "time": time_str,
                "hour": hour,
                "solar_factor": max(0.0, float(solar_factor)),
                "cloud_index": cloud_index,
                "wind_speed": wind_speed,
                "spot_price": spot_price,
                "demand_factor": demand_factor,
                "storm_alert": storm_alert,
                "transmission_congested": transmission_congested,
                "bess1_available": bess1_available,
                "demand_surge_mw": demand_surge_mw,
                "event_tag": event_tag
            })

        return intervals

    def run_full_simulation(
        self,
        num_intervals: int = 96,
        generate_radar_every: int = 12
    ) -> pd.DataFrame:
        scenario = self.generate_scenario_profile()
        portfolio = UtilityPortfolioState()

        records = []
        cum_financial = 0.0
        cum_carbon_avoided = 0.0
        cum_degradation = 0.0

        for idx in range(min(num_intervals, len(scenario))):
            s = scenario[idx]

            # Sync external environmental conditions
            portfolio.market.spot_price_per_mwh = s["spot_price"]
            portfolio.market.projected_price_next_hour = scenario[min(idx + 4, len(scenario) - 1)]["spot_price"]
            portfolio.grid.transmission_congested = s["transmission_congested"]

            # Battery availability contingency
            portfolio.bess_systems[0].is_available = s["bess1_available"]
            portfolio.bess_systems[0].status = AssetStatus.OPERATIONAL if s["bess1_available"] else AssetStatus.MAINTENANCE

            # Industrial demand surge
            if s["demand_surge_mw"] > 0:
                portfolio.industrial_consumers[0].base_load_mw = 70.0 + s["demand_surge_mw"]
            else:
                portfolio.industrial_consumers[0].base_load_mw = 70.0

            for sol in portfolio.solar_farms:
                sol.cloud_attenuation_factor = s["solar_factor"]
            for wnd in portfolio.wind_farms:
                wnd.wind_speed_mps = s["wind_speed"]

            # Generate radar frame if scheduled or storm active
            radar_file = None
            if idx % generate_radar_every == 0 or s["storm_alert"]:
                radar_file = self.vision.generate_radar_feed(
                    cloud_density=s["cloud_index"],
                    storm_front=s["storm_alert"],
                    interval_idx=idx
                )

            # Execute Orchestration Cycle
            decision = self.orchestrator.orchestrate(
                portfolio=portfolio,
                interval_idx=idx,
                clock_time=s["time"],
                radar_image_path=radar_file,
                event_tag=s["event_tag"]
            )
            res = decision["dispatch_result"]

            cum_financial += res.market_revenue_cost_usd
            cum_carbon_avoided += res.carbon_avoided_kg
            cum_degradation += res.battery_degradation_usd

            # Count action categories
            action_categories = [a.get("category", "") for a in res.action_cluster]
            bess_acts = sum(1 for c in action_categories if "BATTERY" in c or "STORAGE" in c)
            mkt_acts = sum(1 for c in action_categories if "MARKET" in c or "WHOLESALE" in c)
            ren_acts = sum(1 for c in action_categories if "RENEWABLE" in c)
            dr_acts = sum(1 for c in action_categories if "DEMAND" in c)
            mnt_acts = sum(1 for c in action_categories if "MAINTENANCE" in c)

            records.append({
                "interval_idx": idx,
                "time": s["time"],
                "event": s["event_tag"],
                "spot_price": round(s["spot_price"], 2),
                "solar_gen_mw": res.solar_generation_mw,
                "wind_gen_mw": res.wind_generation_mw,
                "total_renewables_mw": round(res.solar_generation_mw + res.wind_generation_mw, 1),
                "served_demand_mw": res.served_demand_mw,
                "bess1_soc_pct": res.bess1_next_soc_pct,
                "bess2_soc_pct": res.bess2_next_soc_pct,
                "bess_net_flow_mw": round((res.bess1_discharge_mw + res.bess2_discharge_mw) - (res.bess1_charge_mw + res.bess2_charge_mw), 1),
                "grid_export_mw": res.grid_export_mw,
                "grid_import_mw": res.grid_import_mw,
                "curtailed_mw": round(res.solar_curtailed_mw + res.wind_curtailed_mw, 1),
                "interval_net_financial_usd": res.market_revenue_cost_usd,
                "cumulative_profit_usd": round(cum_financial, 2),
                "carbon_avoided_kg": res.carbon_avoided_kg,
                "cumulative_carbon_tons": round(cum_carbon_avoided / 1000.0, 2),
                "battery_degradation_usd": res.battery_degradation_usd,
                "reserve_margin_mw": res.reserve_margin_mw,
                "grid_stress": res.grid_stress_level,
                "optimality_score": res.optimality_score,
                "action_count": len(res.action_cluster),
                "bess_actions_count": bess_acts,
                "market_actions_count": mkt_acts,
                "renewable_actions_count": ren_acts,
                "dr_actions_count": dr_acts,
                "maintenance_actions_count": mnt_acts,
                "trade_off_explanation": decision["trade_off_explanation"],
                "radar_file": radar_file
            })

        return pd.DataFrame(records)
