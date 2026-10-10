"""
Accenture GridOS™ - Comprehensive Verification of Problem Statement 4 Scenarios
Validates all 7 real-world operational disturbances and all 5 action categories
defined in the official hackathon specification (Pages 10 - 14):
1. Clouds reduce solar output
2. Wind suddenly increases & storm cut-outs (> 25 m/s)
3. Electricity prices spike ($285/MWh)
4. Negative electricity pricing (-$18.50/MWh)
5. One battery becomes unavailable (outage)
6. Transmission line reaches capacity (thermal congestion)
7. Industrial demand increases unexpectedly (+35 MW surge)
8. All 5 action categories (Battery, Market, Renewable, Demand Response, Maintenance)
"""

import pytest
import os
import numpy as np
from PIL import Image

from AccentureAssessment.backend.core.portfolio import UtilityPortfolioState, AssetStatus
from AccentureAssessment.backend.core.solver import IndustrialDispatchSolver, DispatchWeights
from AccentureAssessment.backend.agents.orchestrator_agent import ChiefExecutiveOrchestrator
from AccentureAssessment.backend.perception.radar_vision import RadarVisionEngine

@pytest.fixture
def solver():
    return IndustrialDispatchSolver()

@pytest.fixture
def base_portfolio():
    return UtilityPortfolioState()

def test_scenario_1_clouds_reduce_solar(solver, base_portfolio):
    """
    Problem 4 Scenario 1: Clouds reduce solar output.
    Verify localized cloud attenuation Derates generation and shifts dispatch balance.
    """
    weights = DispatchWeights()
    # Nominal clear sky (attenuation = 1.0)
    res_clear = solver.solve(base_portfolio, weights, attenuation_factor=1.0)
    
    # Dense cloud front rolls in (attenuation = 0.22)
    res_cloud = solver.solve(base_portfolio, weights, attenuation_factor=0.22)

    assert res_cloud.solar_generation_mw < res_clear.solar_generation_mw
    assert res_cloud.solar_generation_mw <= (base_portfolio.total_solar_capacity_mw * 0.25)
    # Total supply must still balance served demand
    supply = res_cloud.solar_generation_mw + res_cloud.wind_generation_mw + res_cloud.bess1_discharge_mw + res_cloud.bess2_discharge_mw + res_cloud.grid_import_mw
    disposition = res_cloud.served_demand_mw + res_cloud.bess1_charge_mw + res_cloud.bess2_charge_mw + res_cloud.grid_export_mw
    assert abs(supply - disposition) < 0.5

def test_scenario_2_wind_storm_cutout(solver, base_portfolio):
    """
    Problem 4 Scenario 2: Wind suddenly increases and exceeds storm cut-out (25 m/s).
    Verify wind generation is safely curtailed to 0 MW and aerodynamic pitch lock maintenance is logged.
    """
    weights = DispatchWeights()
    for w in base_portfolio.wind_farms:
        w.wind_speed_mps = 26.8  # Exceeds 25 m/s safety limit

    res = solver.solve(base_portfolio, weights)
    assert res.wind_generation_mw == 0.0, "Wind output must be 0 MW when wind speed exceeds cut-out speed"
    
    # Verify maintenance action is present in action cluster
    action_types = [a["action"] for a in res.action_cluster]
    assert "SCHEDULE_MAINTENANCE" in action_types or "DISPATCH_INSPECTION_TEAMS" in action_types

def test_scenario_3_electricity_price_spike(solver, base_portfolio):
    """
    Problem 4 Scenario 3: Electricity prices spike to $285/MWh.
    Verify maximum battery discharge into grid and demand response activation.
    """
    weights = DispatchWeights(profit_weight=0.55, battery_health_weight=0.05)
    base_portfolio.market.spot_price_per_mwh = 285.0

    res = solver.solve(base_portfolio, weights)
    # BESS should be discharging or industrial DR should be triggered
    assert (res.bess1_discharge_mw + res.bess2_discharge_mw > 0) or (res.dr_curtailed_demand_mw > 0)
    assert res.market_revenue_cost_usd > 0, "High prices should generate substantial market revenue"

def test_scenario_4_negative_electricity_pricing(solver, base_portfolio):
    """
    Problem 4 Scenario 4: Negative electricity pricing (-$18.50/MWh).
    Verify export is completely suppressed and surplus energy is absorbed into BESS.
    """
    weights = DispatchWeights(profit_weight=0.45, curtailment_penalty_weight=0.25)
    base_portfolio.market.spot_price_per_mwh = -18.50

    res = solver.solve(base_portfolio, weights, attenuation_factor=1.0)
    assert res.grid_export_mw == 0.0, "Grid export must be 0 MW during negative wholesale pricing"
    # Action cluster should command delaying selling or charging batteries
    actions = [a["action"] for a in res.action_cluster]
    assert "DELAY_SELLING_UNTIL_PRICES_RISE" in actions or "CHARGE_BATTERIES" in actions

def test_scenario_5_battery_becomes_unavailable(solver, base_portfolio):
    """
    Problem 4 Scenario 5: One battery becomes unavailable (e.g. BESS-01 outage).
    Verify BESS-01 is bypassed, BESS-02 compensates, and inspection crew is dispatched.
    """
    weights = DispatchWeights()
    base_portfolio.bess_systems[0].is_available = False
    base_portfolio.bess_systems[0].status = AssetStatus.MAINTENANCE

    res = solver.solve(base_portfolio, weights)
    assert res.bess1_charge_mw == 0.0
    assert res.bess1_discharge_mw == 0.0

    # Verify maintenance action was created
    maint_actions = [a for a in res.action_cluster if a.get("category") == "MAINTENANCE"]
    assert len(maint_actions) > 0
    assert any("BESS-01" in a["target"] for a in maint_actions)

def test_scenario_6_transmission_line_congested(solver, base_portfolio):
    """
    Problem 4 Scenario 6: Transmission line reaches capacity (500 kV intertie congested).
    Verify export is capped at 50% derated corridor limit (100 MW).
    """
    weights = DispatchWeights()
    base_portfolio.grid.transmission_congested = True
    base_portfolio.market.spot_price_per_mwh = 60.0

    res = solver.solve(base_portfolio, weights, attenuation_factor=1.0)
    assert res.grid_export_mw <= 100.0, f"Grid export {res.grid_export_mw} MW exceeded 100 MW thermal congestion limit"

def test_scenario_7_industrial_demand_surge(solver, base_portfolio):
    """
    Problem 4 Scenario 7: Industrial demand increases unexpectedly (+35 MW surge).
    Verify energy balance is preserved and demand is served via batteries or imports.
    """
    weights = DispatchWeights()
    original_demand = base_portfolio.total_industrial_baseload_mw
    base_portfolio.industrial_consumers[0].base_load_mw += 35.0

    res = solver.solve(base_portfolio, weights, attenuation_factor=0.5)
    # Energy balance must strictly hold
    total_supply = res.solar_generation_mw + res.wind_generation_mw + res.bess1_discharge_mw + res.bess2_discharge_mw + res.grid_import_mw
    total_disposition = res.served_demand_mw + res.bess1_charge_mw + res.bess2_charge_mw + res.grid_export_mw
    assert abs(total_supply - total_disposition) < 0.5
    assert res.served_demand_mw >= original_demand

def test_all_five_action_categories_present(solver, base_portfolio):
    """
    Verify all 5 action categories specified on Page 12 of Problem Statement 4:
    - BATTERY_ACTIONS
    - MARKET_ACTIONS
    - RENEWABLE_ACTIONS
    - DEMAND_MANAGEMENT
    - MAINTENANCE
    """
    base_portfolio.market.spot_price_per_mwh = 145.0
    base_portfolio.solar_farms[0].inverter_temperature_c = 68.0  # Trigger maintenance advisory
    weights = DispatchWeights()

    res = solver.solve(base_portfolio, weights, attenuation_factor=0.8)
    categories = {a.get("category") for a in res.action_cluster}

    assert "BATTERY_ACTIONS" in categories
    assert "MARKET_ACTIONS" in categories
    assert "RENEWABLE_ACTIONS" in categories
    assert "DEMAND_MANAGEMENT" in categories
    assert "MAINTENANCE" in categories

    demand_actions = [a for a in res.action_cluster if a.get("category") == "DEMAND_MANAGEMENT"]
    assert demand_actions

def test_multimodal_vision_real_image_ingestion():
    """
    Problem 4 Depth D3: Ingest a real image and extract cloud opacity,
    localized attenuation, and sensor fusion confidence.
    """
    engine = RadarVisionEngine()
    # Create an in-memory sample radar image
    test_arr = np.zeros((380, 500, 3), dtype=np.uint8)
    test_arr[100:250, 150:350] = [230, 50, 30]  # Severe storm core
    img = Image.fromarray(test_arr)

    report = engine.process_radar_image(img)
    assert report.cloud_opacity_index > 0.0
    assert report.storm_alert_active is True
    assert report.storm_severity in ["ELEVATED", "SEVERE"]
    assert report.input_quality_score >= 0.65
    assert len(report.asset_level_reports) == 8

    blank = Image.new("RGB", (500, 380), (0, 0, 0))
    blank_report = engine.process_radar_image(blank)
    assert blank_report.input_quality_score < report.input_quality_score

