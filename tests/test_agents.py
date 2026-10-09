"""
Unit Tests - Multi-Agent Deliberation & 24-Hour Simulation Engine
"""

import pytest
import os
from AccentureAssessment.core.portfolio import UtilityPortfolioState
from AccentureAssessment.agents.orchestrator_agent import ChiefExecutiveOrchestrator
from AccentureAssessment.simulation.engine import IndustrialSimulationEngine

def test_multi_agent_orchestration():
    db_test = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "test_orchestrator.db")
    orchestrator = ChiefExecutiveOrchestrator(db_path=db_test)
    portfolio = UtilityPortfolioState()

    decision = orchestrator.orchestrate(portfolio, interval_idx=10, clock_time="10:30")
    
    assert "dispatch_result" in decision
    assert "pareto_weights" in decision
    assert len(decision["agent_deliberations"]) == 3
    assert len(decision["dispatch_result"].action_cluster) > 0

    if os.path.exists(db_test):
        try:
            os.remove(db_test)
        except Exception:
            pass

def test_full_24h_simulation():
    db_test = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "test_sim.db")
    sim = IndustrialSimulationEngine(db_path=db_test)
    
    df = sim.run_full_simulation(num_intervals=96, generate_radar_every=24)
    assert len(df) == 96
    assert "cumulative_profit_usd" in df.columns
    assert "cumulative_carbon_tons" in df.columns
    assert df["cumulative_carbon_tons"].iloc[-1] > 500.0

    if os.path.exists(db_test):
        try:
            os.remove(db_test)
        except Exception:
            pass
