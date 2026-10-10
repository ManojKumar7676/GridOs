"""
Unit Tests - Mathematical Feasibility & Physical Conservation
"""

import pytest
from AccentureAssessment.backend.core.portfolio import UtilityPortfolioState
from AccentureAssessment.backend.core.solver import IndustrialDispatchSolver, DispatchWeights

def test_energy_conservation_balance():
    solver = IndustrialDispatchSolver()
    portfolio = UtilityPortfolioState()
    weights = DispatchWeights()

    res = solver.solve(portfolio, weights, attenuation_factor=1.0)

    # Total supply vs total disposition
    total_supply = res.solar_generation_mw + res.wind_generation_mw + res.bess1_discharge_mw + res.bess2_discharge_mw + res.grid_import_mw
    total_disposition = res.served_demand_mw + res.bess1_charge_mw + res.bess2_charge_mw + res.grid_export_mw

    # Allow tiny floating point tolerance
    assert abs(total_supply - total_disposition) < 0.5, f"Energy balance violated: Supply {total_supply} != Dispos {total_disposition}"

def test_bess_soc_limits():
    solver = IndustrialDispatchSolver()
    portfolio = UtilityPortfolioState()
    # Force BESS to min SoC
    portfolio.bess_systems[0].current_soc_pct = 10.0
    portfolio.bess_systems[1].current_soc_pct = 95.0

    res = solver.solve(portfolio, DispatchWeights())
    assert res.bess1_next_soc_pct >= 10.0, "BESS-01 violated minimum buffer reserve limit"
    assert res.bess2_next_soc_pct <= 95.0, "BESS-02 violated maximum safety ceiling"

def test_negative_pricing_export_suppression():
    solver = IndustrialDispatchSolver()
    portfolio = UtilityPortfolioState()
    portfolio.market.spot_price_per_mwh = -25.0  # Strongly negative

    res = solver.solve(portfolio, DispatchWeights())
    assert res.grid_export_mw == 0.0, "Grid export was not suppressed during negative spot pricing"
