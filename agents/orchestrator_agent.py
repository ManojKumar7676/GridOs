"""
Accenture GridOS™ - Chief Executive Renewable Energy Orchestrator (Executive Agent)
Synthesizes multi-agent telemetry, dynamically arbitrates multi-objective Pareto trade-offs,
executes formal Security-Constrained Economic Dispatch (SCED), and commands physical SCADA actuators.
"""

from typing import Dict, Any, List, Optional, Union
from AccentureAssessment.core.portfolio import UtilityPortfolioState
from AccentureAssessment.core.solver import IndustrialDispatchSolver, DispatchWeights, DispatchExecutionResult
from AccentureAssessment.core.database import OrchestratorDatabase
from AccentureAssessment.perception.radar_vision import RadarVisionEngine
from AccentureAssessment.agents.base import AgentDeliberationMessage
from AccentureAssessment.agents.forecast_agent import ForecastPerceptionAgent
from AccentureAssessment.agents.market_agent import MarketArbitrageAgent
from AccentureAssessment.agents.grid_reliability_agent import GridReliabilityAgent
from AccentureAssessment.config.prompt_config import PromptConfig, get_prompt_config

class ChiefExecutiveOrchestrator:
    """
    Executive Multi-Agent Orchestrator presiding over the grid cyber-physical collective.
    Executes real-time arbitration between commercial profit, carbon abatement, asset life, and grid reliability.
    """

    def __init__(self, db_path: Optional[str] = None, prompt_config: Optional[PromptConfig] = None):
        self.vision = RadarVisionEngine()
        self.db = OrchestratorDatabase(db_path) if db_path else OrchestratorDatabase()
        self.prompt_config = prompt_config or get_prompt_config()
        self.forecast_agent = ForecastPerceptionAgent(self.vision, prompt_config=self.prompt_config)
        self.market_agent = MarketArbitrageAgent(prompt_config=self.prompt_config)
        self.reliability_agent = GridReliabilityAgent(prompt_config=self.prompt_config)
        self.solver = IndustrialDispatchSolver(prompt_config=self.prompt_config)

    def orchestrate(
        self,
        portfolio: UtilityPortfolioState,
        interval_idx: int = 0,
        clock_time: str = "12:00",
        radar_image_path: Optional[Union[str, bytes]] = None,
        event_tag: str = "Routine Operations",
        manual_pareto_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Executes an end-to-end multi-agent dispatch cycle.
        """
        # 1. Deliberation Phase: Ingest telemetry and query specialized domain agents
        msg_meteo = self.forecast_agent.deliberate(portfolio, radar_image_path)
        msg_mrkt = self.market_agent.deliberate(portfolio)
        msg_grid = self.reliability_agent.deliberate(portfolio)
        agent_msgs: List[AgentDeliberationMessage] = [msg_meteo, msg_mrkt, msg_grid]

        # 2. Dynamic Pareto Optimality Determination
        # Baseline balanced utility operational weights
        w_profit = 0.35
        w_carbon = 0.25
        w_rel = 0.20
        w_batt = 0.10
        w_curt = 0.10

        rationales = []

        # Situational Adaptation Logic:
        if msg_grid.recommended_parameters.get("reserve_headroom_critical") or msg_meteo.recommended_parameters.get("storm_active"):
            w_rel = 0.50
            w_profit = 0.15
            rationales.append(self.prompt_config.get_orchestrator_tradeoff_rationale("contingency_alert"))

        if portfolio.market.spot_price_per_mwh < 0.0:
            w_profit = 0.45
            w_curt = 0.25
            rationales.append(self.prompt_config.get_orchestrator_tradeoff_rationale("negative_pricing", spot=portfolio.market.spot_price_per_mwh))

        if portfolio.market.spot_price_per_mwh > 130.0:
            w_profit = 0.55
            w_batt = 0.05
            rationales.append(self.prompt_config.get_orchestrator_tradeoff_rationale("price_spike", spot=portfolio.market.spot_price_per_mwh))

        # Allow operator manual overrides from SCADA console
        if manual_pareto_weights:
            w_profit = manual_pareto_weights.get("profit", w_profit)
            w_carbon = manual_pareto_weights.get("carbon", w_carbon)
            w_rel = manual_pareto_weights.get("reliability", w_rel)
            w_batt = manual_pareto_weights.get("battery_health", w_batt)
            w_curt = manual_pareto_weights.get("curtailment", w_curt)

        total_w = max(0.001, w_profit + w_carbon + w_rel + w_batt + w_curt)
        weights = DispatchWeights(
            profit_weight=w_profit / total_w,
            carbon_weight=w_carbon / total_w,
            reliability_weight=w_rel / total_w,
            battery_health_weight=w_batt / total_w,
            curtailment_penalty_weight=w_curt / total_w
        )

        attenuation = msg_meteo.recommended_parameters.get("solar_derating_factor", 1.0)

        # 3. Solver Phase: Compute physical dispatch & action cluster via HiGHS LP Optimizer
        dispatch_res: DispatchExecutionResult = self.solver.solve(
            portfolio=portfolio,
            weights=weights,
            attenuation_factor=attenuation
        )

        # 4. State Update: Apply physical transitions to live portfolio
        portfolio.bess_systems[0].current_soc_pct = dispatch_res.bess1_next_soc_pct
        portfolio.bess_systems[1].current_soc_pct = dispatch_res.bess2_next_soc_pct

        # 5. Persistence Phase: Log to production SQLite SCADA database
        self.db.log_dispatch_interval(
            interval_idx=interval_idx,
            clock_time=clock_time,
            spot_price=portfolio.market.spot_price_per_mwh,
            solar_gen=dispatch_res.solar_generation_mw,
            wind_gen=dispatch_res.wind_generation_mw,
            served_demand=dispatch_res.served_demand_mw,
            bess1_soc=dispatch_res.bess1_next_soc_pct,
            bess2_soc=dispatch_res.bess2_next_soc_pct,
            bess_net_flow=(dispatch_res.bess1_discharge_mw + dispatch_res.bess2_discharge_mw) - (dispatch_res.bess1_charge_mw + dispatch_res.bess2_charge_mw),
            grid_export=dispatch_res.grid_export_mw,
            grid_import=dispatch_res.grid_import_mw,
            curtailed=dispatch_res.solar_curtailed_mw + dispatch_res.wind_curtailed_mw,
            net_financial=dispatch_res.market_revenue_cost_usd,
            carbon_avoided=dispatch_res.carbon_avoided_kg,
            reserve_margin=dispatch_res.reserve_margin_mw,
            grid_stress=dispatch_res.grid_stress_level,
            optimality_score=dispatch_res.optimality_score,
            event_tag=event_tag,
            action_cluster=dispatch_res.action_cluster,
            agent_logs=[msg.model_dump() for msg in agent_msgs]
        )

        trade_off_explanation = " ".join(rationales) if rationales else self.prompt_config.get_orchestrator_tradeoff_rationale("nominal")

        return {
            "interval_idx": interval_idx,
            "clock_time": clock_time,
            "dispatch_result": dispatch_res,
            "pareto_weights": weights,
            "trade_off_explanation": trade_off_explanation,
            "agent_deliberations": agent_msgs
        }
