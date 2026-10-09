"""
Tests for Accenture GridOS™ Evaluation Framework and AuditEvaluationAgent.
"""

import pytest
from AccentureAssessment.core.portfolio import UtilityPortfolioState
from AccentureAssessment.agents.orchestrator_agent import ChiefExecutiveOrchestrator
from AccentureAssessment.evaluation.evaluation_agent import AuditEvaluationAgent
from AccentureAssessment.evaluation.metrics import MetricsCalculator
from AccentureAssessment.evaluation.benchmark_runner import BenchmarkRunner
from AccentureAssessment.core.llm_client import get_gemini_client, load_env_file


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


def test_benchmark_runner_all_scenarios():
    runner = BenchmarkRunner()
    scorecards = runner.run_all_benchmarks(use_llm_for_eval=False)

    assert len(scorecards) == 8
    df = runner.scorecards_to_dataframe(scorecards)
    assert len(df) == 8
    assert all(df["Energy Error (MW)"] < 0.5)
    assert all(df["Safety Passed"] == "✅ PASS")

