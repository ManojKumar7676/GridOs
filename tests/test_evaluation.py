"""
Tests for Accenture GridOS™ Evaluation Framework and AuditEvaluationAgent.
"""

from dataclasses import replace
import pytest
from AccentureAssessment.backend.core.portfolio import UtilityPortfolioState
from AccentureAssessment.backend.agents.orchestrator_agent import ChiefExecutiveOrchestrator
from AccentureAssessment.backend.evaluation.evaluation_agent import AuditEvaluationAgent
from AccentureAssessment.backend.evaluation.metrics import MetricsCalculator
from AccentureAssessment.backend.evaluation.benchmark_runner import BenchmarkRunner
from AccentureAssessment.backend.core.llm_client import get_gemini_client, load_env_file


def test_env_loader_finds_api_key():
    env = load_env_file()
    assert "GEMINI_API_KEY" in env
    assert len(env["GEMINI_API_KEY"]) > 10


def test_gemini_client_configured():
    client = get_gemini_client()
    assert client.is_configured is True
    assert client.api_key.startswith("AQ.")


def test_metrics_calculator_exact_balance():
    portfolio = UtilityPortfolioState()
    orchestrator = ChiefExecutiveOrchestrator()
    out = orchestrator.orchestrate(portfolio, interval_idx=24)

    eval_agent = AuditEvaluationAgent()
    scorecard = eval_agent.evaluate_interval(
        portfolio=portfolio,
        dispatch_result=out["dispatch_result"],
        agent_deliberations=out["agent_deliberations"],
        scenario_name="Nominal Test",
        use_llm_narrative=False
    )

    assert scorecard.system_composite_score > 85.0
    assert scorecard.compliance_passed is True
    assert scorecard.orchestrator_metrics.energy_balance_error_mw < 0.5
    assert scorecard.reliability_metrics.thermal_line_violations_count == 0
    assert scorecard.reliability_metrics.bess_soc_violations_count == 0
    assert scorecard.forecast_metrics.ground_truth_available is False
    assert scorecard.forecast_metrics.storm_alert_f1_score is None
    assert scorecard.forecast_metrics.to_dict()["composite_score"] is None
    assert scorecard.market_metrics.arbitrage_capture_efficiency is None
    assert any("ground truth was not supplied" in finding for finding in scorecard.audit_findings)


def test_negative_pricing_evaluation():
    portfolio = UtilityPortfolioState()
    portfolio.market.spot_price_per_mwh = -18.50
    orchestrator = ChiefExecutiveOrchestrator()
    out = orchestrator.orchestrate(portfolio, interval_idx=52)

    eval_agent = AuditEvaluationAgent()
    scorecard = eval_agent.evaluate_interval(
        portfolio=portfolio,
        dispatch_result=out["dispatch_result"],
        agent_deliberations=out["agent_deliberations"],
        scenario_name="Negative Pricing Test",
        use_llm_narrative=False
    )

    # Export must be suppressed
    assert scorecard.market_metrics.negative_pricing_suppression_rate == 100.0
    assert out["dispatch_result"].grid_export_mw == 0.0


def test_unserved_load_fails_dispatch_compliance():
    portfolio = UtilityPortfolioState()
    orchestrator = ChiefExecutiveOrchestrator()
    out = orchestrator.orchestrate(portfolio, interval_idx=25)
    dispatch = out["dispatch_result"]
    dispatch_with_shed_load = replace(
        dispatch,
        served_demand_mw=max(0.0, dispatch.served_demand_mw - 1.0),
        unserved_demand_mw=1.0,
    )

    scorecard = AuditEvaluationAgent().evaluate_interval(
        portfolio=portfolio,
        dispatch_result=dispatch_with_shed_load,
        agent_deliberations=out["agent_deliberations"],
        scenario_name="Unserved Load Test",
        use_llm_narrative=False,
    )

    assert scorecard.reliability_metrics.unserved_energy_mwh == 0.25
    assert scorecard.orchestrator_metrics.energy_balance_error_mw >= 0.99
    assert scorecard.compliance_passed is False


def test_benchmark_runner_all_scenarios():
    runner = BenchmarkRunner()
    scorecards = runner.run_all_benchmarks(use_llm_for_eval=False)

    assert len(scorecards) == 8
    df = runner.scorecards_to_dataframe(scorecards)
    assert len(df) == 8
    assert all(df["Energy Error (MW)"] < 0.5)
    assert all(df["Safety Passed"] == "✅ PASS")

