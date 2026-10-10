"""
Accenture GridOS™ - Automated Multi-Scenario Benchmark Suite
Runs the 4 agents through all 7 Problem Statement 4 real-world shocks + nominal baseline,
audits every execution via AuditEvaluationAgent, and computes an end-to-end benchmark report.
"""

from typing import Dict, Any, List
import pandas as pd
from AccentureAssessment.backend.core.portfolio import UtilityPortfolioState
from AccentureAssessment.backend.agents.orchestrator_agent import ChiefExecutiveOrchestrator
from AccentureAssessment.backend.evaluation.evaluation_agent import AuditEvaluationAgent
from AccentureAssessment.backend.evaluation.metrics import SystemEvaluationScorecard


class BenchmarkRunner:
    """
    Executes automated stress tests across all 7 real-world operational disruptions.
    """

    SCENARIOS = [
        {
            "id": 0,
            "name": "Nominal Baseline (Merit Dispatch)",
            "step": 24, "storm": False, "neg_price": False, "outage": False, "congestion": False, "surge": 0.0
        },
        {
            "id": 1,
            "name": "Scenario 1: Clouds Reduce Solar (78% Attenuation)",
            "step": 48, "storm": False, "neg_price": False, "outage": False, "congestion": False, "surge": 0.0,
            "cloud_derate": 0.22
        },
        {
            "id": 2,
            "name": "Scenario 2: Wind Storm Cut-Out (>25 m/s Gale)",
            "step": 56, "storm": True, "neg_price": False, "outage": False, "congestion": False, "surge": 0.0
        },
        {
            "id": 3,
            "name": "Scenario 3: Wholesale Electricity Price Spike ($285/MWh)",
            "step": 72, "storm": False, "neg_price": False, "outage": False, "congestion": False, "surge": 0.0,
            "price_override": 285.0
        },
        {
            "id": 4,
            "name": "Scenario 4: Negative Electricity Pricing (-$18.50/MWh)",
            "step": 52, "storm": False, "neg_price": True, "outage": False, "congestion": False, "surge": 0.0,
            "price_override": -18.50
        },
        {
            "id": 5,
            "name": "Scenario 5: Battery Unavailable (BESS-01 Thermal Trip)",
            "step": 40, "storm": False, "neg_price": False, "outage": True, "congestion": False, "surge": 0.0
        },
        {
            "id": 6,
            "name": "Scenario 6: Transmission Congestion (500kV Derated 50%)",
            "step": 68, "storm": False, "neg_price": False, "outage": False, "congestion": True, "surge": 0.0
        },
        {
            "id": 7,
            "name": "Scenario 7: Industrial Demand Surge (+35 MW Smelter)",
            "step": 86, "storm": False, "neg_price": False, "outage": False, "congestion": False, "surge": 35.0
        }
    ]

    def __init__(self, orchestrator: ChiefExecutiveOrchestrator = None, eval_agent: AuditEvaluationAgent = None):
        self.orchestrator = orchestrator or ChiefExecutiveOrchestrator()
        self.eval_agent = eval_agent or AuditEvaluationAgent()

    def run_all_benchmarks(self, use_llm_for_eval: bool = False) -> List[SystemEvaluationScorecard]:
        """
        Executes all 8 benchmark scenarios and evaluates every agent's performance.
        """
        scorecards: List[SystemEvaluationScorecard] = []

        for sc in self.SCENARIOS:
            portfolio = UtilityPortfolioState()

            # Apply Scenario Disturbance
            if sc.get("cloud_derate"):
                for s in portfolio.solar_farms:
                    s.cloud_attenuation_factor = sc["cloud_derate"]
            if sc.get("storm"):
                for w in portfolio.wind_farms:
                    w.wind_speed_mps = 28.5
                    w.is_available = False
            if sc.get("price_override") is not None:
                portfolio.market.spot_price_per_mwh = sc["price_override"]
            if sc.get("outage"):
                portfolio.bess_systems[0].is_available = False
            if sc.get("congestion"):
                portfolio.grid.max_export_mw = 80.0
                portfolio.grid.transmission_congested = True
            if sc.get("surge"):
                portfolio.industrial_consumers[0].base_load_mw += sc["surge"]

            # Run Orchestrator
            orch_output = self.orchestrator.orchestrate(
                portfolio=portfolio,
                interval_idx=sc["step"],
                event_tag=sc["name"]
            )

            # Evaluate with Evaluation Agent
            card = self.eval_agent.evaluate_interval(
                portfolio=portfolio,
                dispatch_result=orch_output["dispatch_result"],
                agent_deliberations=orch_output["agent_deliberations"],
                scenario_name=sc["name"],
                use_llm_narrative=use_llm_for_eval
            )
            scorecards.append(card)

        return scorecards

    @staticmethod
    def scorecards_to_dataframe(scorecards: List[SystemEvaluationScorecard]) -> pd.DataFrame:
        """
        Converts scorecards into a structured summary DataFrame.
        """
        rows = []
        for c in scorecards:
            rows.append({
                "Scenario": c.scenario_name,
                "Grade": c.overall_grade,
                "Composite Score": c.system_composite_score,
                "Forecast Score": c.forecast_metrics.composite_forecast_score if c.forecast_metrics.ground_truth_available else None,
                "Market Score": c.market_metrics.composite_market_score,
                "Reliability Score": c.reliability_metrics.composite_reliability_score,
                "Orchestrator Score": c.orchestrator_metrics.composite_orchestration_score,
                "Energy Error (MW)": c.orchestrator_metrics.energy_balance_error_mw,
                "Safety Passed": "✅ PASS" if c.compliance_passed else "❌ FAIL"
            })
        return pd.DataFrame(rows)
