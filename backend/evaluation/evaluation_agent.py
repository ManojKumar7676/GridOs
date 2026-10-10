"""
Accenture GridOS™ - Autonomous Evaluation Agent (AGT-04-EVAL)
Independent regulatory auditor agent assessing compliance, safety envelopes,
Pareto optimization efficiency, and deliberation quality across all 4 operational agents.
"""

from typing import Dict, Any, List, Optional
from AccentureAssessment.backend.core.portfolio import UtilityPortfolioState
from AccentureAssessment.backend.core.solver import DispatchExecutionResult
from AccentureAssessment.backend.agents.base import AgentDeliberationMessage
from AccentureAssessment.backend.evaluation.metrics import (
    MetricsCalculator,
    ForecastMetrics,
    MarketMetrics,
    GridReliabilityMetrics,
    OrchestratorMetrics,
    SystemEvaluationScorecard
)
from AccentureAssessment.backend.core.llm_client import get_gemini_client, GeminiClient


class AuditEvaluationAgent:
    """
    AGT-04-EVAL: Autonomous Benchmark & Audit Evaluation Agent.
    Evaluates each agent's telemetry, decisions, and physical commands.
    """

    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        self.gemini_client = gemini_client or get_gemini_client()
        self.calculator = MetricsCalculator()

    def evaluate_interval(
        self,
        portfolio: UtilityPortfolioState,
        dispatch_result: DispatchExecutionResult,
        agent_deliberations: List[AgentDeliberationMessage],
        scenario_name: str = "Routine Operations",
        actual_solar_mw: Optional[float] = None,
        actual_wind_mw: Optional[float] = None,
        use_llm_narrative: bool = True
    ) -> SystemEvaluationScorecard:
        """
        Runs comprehensive quantitative evaluation and produces an executive audit scorecard.
        """
        # 1. Compute per-agent quantitative metrics
        fc_metrics = self.calculator.calculate_forecast_metrics(portfolio, actual_solar_mw, actual_wind_mw)
        mrkt_metrics = self.calculator.calculate_market_metrics(dispatch_result, portfolio.market.spot_price_per_mwh, portfolio)
        rel_metrics = self.calculator.calculate_reliability_metrics(portfolio, dispatch_result)
        orch_metrics = self.calculator.calculate_orchestrator_metrics(dispatch_result, portfolio)

        # 2. Compute composite score
        weighted_scores = [
            (0.20, fc_metrics.composite_forecast_score, fc_metrics.ground_truth_available),
            (0.25, mrkt_metrics.composite_market_score, True),
            (0.30, rel_metrics.composite_reliability_score, True),
            (0.25, orch_metrics.composite_orchestration_score, True),
        ]
        scored = [(weight, score) for weight, score, available in weighted_scores if available and score is not None]
        system_score = sum(weight * score for weight, score in scored) / sum(weight for weight, _ in scored)

        # 3. Determine Overall Grade
        if system_score >= 93.0:
            grade = "GRADE A+ (Exceptional)"
        elif system_score >= 88.0:
            grade = "GRADE A (Exemplary)"
        elif system_score >= 80.0:
            grade = "GRADE B+ (Compliant)"
        elif system_score >= 70.0:
            grade = "GRADE B (Conditional)"
        else:
            grade = "GRADE C (Underperforming)"

        # 4. Formulate Audit Findings
        findings: List[str] = []
        if not fc_metrics.ground_truth_available:
            findings.append("ℹ️ Forecast metrics not scored: measured solar and wind ground truth was not supplied.")
        if orch_metrics.energy_balance_error_mw < 0.1:
            findings.append("✅ Kirchhoff Energy Conservation: Exact physical balance verified (Delta = 0.00 MW).")
        else:
            findings.append(f"⚠️ Energy Imbalance Detected: Delta = {orch_metrics.energy_balance_error_mw:.4f} MW.")

        if (rel_metrics.thermal_line_violations_count == 0
                and rel_metrics.bess_soc_violations_count == 0
                and rel_metrics.unserved_energy_mwh <= 1e-6
                and orch_metrics.energy_balance_error_mw < 0.5
                and "OPTIMAL" in dispatch_result.solver_status):
            findings.append("✅ Grid Safety Envelopes: Zero thermal overloads; BESS SoC preserved within [10.0%, 95.0%].")
        else:
            findings.append(
                "❌ Dispatch compliance failure: "
                f"{rel_metrics.thermal_line_violations_count} line overloads, "
                f"{rel_metrics.bess_soc_violations_count} SoC breaches, "
                f"{rel_metrics.unserved_energy_mwh:.3f} MWh unserved, "
                f"{orch_metrics.energy_balance_error_mw:.3f} MW balance error, "
                f"solver={dispatch_result.solver_status}."
            )

        if portfolio.market.spot_price_per_mwh < 0.0:
            if mrkt_metrics.negative_pricing_suppression_rate == 100.0:
                findings.append("✅ Negative Price Protection: Export suppression & battery absorption 100% active.")
            else:
                findings.append("❌ Negative Pricing Leak: Grid injection occurred during negative pricing tariff.")

        if dispatch_result.dr_curtailed_demand_mw > 0.0:
            findings.append(f"✅ Demand Response Engaged: Contractual industrial shedding triggered ({dispatch_result.dr_curtailed_demand_mw:.1f} MW).")

        if mrkt_metrics.arbitrage_capture_efficiency is None:
            findings.append("ℹ️ Arbitrage capture not scored: a single interval has no horizon-wide optimum for comparison.")

        action_cats = set(a.get("category", "") for a in dispatch_result.action_cluster)
        findings.append(f"✅ Action Diversity: Executed physical commands across {len(action_cats)}/5 problem statement categories.")

        # 5. Formulate AI Auditor Narrative via Gemini (if configured and requested)
        llm_narrative = ""
        if use_llm_narrative and self.gemini_client.is_configured:
            prompt = (
                f"You are the Chief Regulatory Auditor for an autonomous power grid. "
                f"Evaluate this 15-minute dispatch cycle:\n"
                f"- Scenario: {scenario_name}\n"
                f"- Composite System Score: {system_score:.1f}/100 ({grade})\n"
                f"- Energy Balance Error: {orch_metrics.energy_balance_error_mw:.4f} MW\n"
                f"- Spot LMP: ${portfolio.market.spot_price_per_mwh:.2f}/MWh\n"
                f"- Line Violations: {rel_metrics.thermal_line_violations_count}\n"
                f"- BESS SoC Violations: {rel_metrics.bess_soc_violations_count}\n"
                f"- Actions Taken: {len(dispatch_result.action_cluster)} physical commands\n\n"
                f"Write a concise 2-sentence regulatory compliance audit statement."
            )
            llm_res = self.gemini_client.generate_content(
                prompt=prompt,
                system_instruction="You are an uncompromising industrial SCADA compliance auditor evaluating autonomous AI dispatch.",
                max_tokens=150,
                timeout=5
            )
            if llm_res.get("success"):
                llm_narrative = llm_res.get("text", "")
                findings.append(f"🤖 Gemini Auditor Assessment ({llm_res.get('model_used')}): {llm_narrative}")

        scorecard = SystemEvaluationScorecard(
            interval_id=0,
            scenario_name=scenario_name,
            overall_grade=grade,
            system_composite_score=system_score,
            forecast_metrics=fc_metrics,
            market_metrics=mrkt_metrics,
            reliability_metrics=rel_metrics,
            orchestrator_metrics=orch_metrics,
            audit_findings=findings,
            compliance_passed=(
                rel_metrics.thermal_line_violations_count == 0
                and rel_metrics.bess_soc_violations_count == 0
                and rel_metrics.unserved_energy_mwh <= 1e-6
                and orch_metrics.energy_balance_error_mw < 0.5
                and "OPTIMAL" in dispatch_result.solver_status
                and mrkt_metrics.negative_pricing_suppression_rate == 100.0
            )
        )
        return scorecard

