"""
Unit tests for Accenture GridOS™ Prompt & Directive Configuration Engine.
Verifies that all agent prompts, system instructions, and rationale templates
are cleanly decoupled into config/prompts.json and loaded dynamically.
"""

import os
import json
import tempfile
import pytest
from AccentureAssessment.config.prompt_config import PromptConfig, get_prompt_config

def test_prompt_config_loads_all_agents():
    cfg = get_prompt_config()
    assert cfg is not None
    assert "agents" in cfg.raw
    
    expected_agents = ["orchestrator_agent", "forecast_agent", "market_agent", "grid_reliability_agent"]
    for ag in expected_agents:
        ag_data = cfg.get_agent_config(ag)
        assert ag_data is not None, f"Agent {ag} missing from configuration"
        assert "system_prompt" in ag_data
        assert len(ag_data["system_prompt"]) > 20
        assert "agent_id" in ag_data

def test_prompt_config_system_prompts_not_empty():
    cfg = get_prompt_config()
    assert "Renewable Energy Orchestrator" in cfg.get_system_prompt("orchestrator_agent")
    assert "Meteorological & Vision" in cfg.get_system_prompt("forecast_agent")
    assert "Wholesale Electricity Market" in cfg.get_system_prompt("market_agent")
    assert "Grid Reliability" in cfg.get_system_prompt("grid_reliability_agent")

def test_prompt_config_formatters():
    cfg = get_prompt_config()
    
    # Forecast reasoning formatter
    fc_reasoning = cfg.format_forecast_reasoning(
        cloud_index=0.75,
        peak_dbz=45.0,
        attenuation=0.35,
        storm_active=True
    )
    assert "0.75" in fc_reasoning
    assert "45.0" in fc_reasoning
    assert "35.0%" in fc_reasoning
    assert "CRITICAL GUST WARNING" in fc_reasoning

    # Market reasoning formatter
    mkt_neg = cfg.get_market_reasoning("negative_pricing", spot=-15.0)
    assert "-15.00" in mkt_neg
    assert "Negative wholesale spot pricing detected" in mkt_neg

    # Grid alert formatter
    alert_under_freq = cfg.get_grid_alert("under_frequency", freq=49.75)
    assert "49.75" in alert_under_freq
    assert "NERC BAL-001" in alert_under_freq

def test_prompt_config_all_five_action_categories_rationales():
    cfg = get_prompt_config()
    rationales = cfg.raw.get("action_rationales", {})
    
    # Verify all 5 categories have rationale templates
    assert "battery_actions" in rationales
    assert "market_actions" in rationales
    assert "renewable_actions" in rationales
    assert "demand_management" in rationales
    assert "maintenance_actions" in rationales

    # Test formatting on each category
    b_rat = cfg.get_action_rationale("battery_actions", "charge_bulk", mw=50.0)
    assert "50.0 MW" in b_rat

    m_rat = cfg.get_action_rationale("market_actions", "sell", mw=30.0, spot=75.5)
    assert "30.0 MW" in m_rat
    assert "75.50" in m_rat

    r_rat = cfg.get_action_rationale("renewable_actions", "curtail_solar", mw=12.5)
    assert "12.5 MW" in r_rat

    d_rat = cfg.get_action_rationale("demand_management", "shift_load", mw=20.0)
    assert "20.0 MW" in d_rat

    mnt_rat = cfg.get_action_rationale("maintenance_actions", "solar_inspection", name="Solar Alpha")
    assert "Solar Alpha" in mnt_rat

def test_prompt_config_custom_file_override():
    custom_data = {
        "system_info": {"platform_name": "Custom GridOS"},
        "agents": {
            "orchestrator_agent": {
                "system_prompt": "Custom Orchestrator Prompt for testing"
            }
        }
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
        json.dump(custom_data, tf)
        tmp_path = tf.name

    try:
        custom_cfg = PromptConfig(config_path=tmp_path)
        assert custom_cfg.get_system_prompt("orchestrator_agent") == "Custom Orchestrator Prompt for testing"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_prompt_config_skills_instructions_tools():
    cfg = get_prompt_config()
    agents = ["orchestrator_agent", "forecast_agent", "market_agent", "grid_reliability_agent"]
    for ag in agents:
        skills = cfg.get_skills(ag)
        instructions = cfg.get_instructions(ag)
        tools = cfg.get_tools(ag)
        role = cfg.get_role(ag)

        assert len(skills) >= 4, f"Agent {ag} should have at least 4 skills"
        assert len(instructions) >= 4, f"Agent {ag} should have at least 4 instructions"
        assert len(tools) >= 3, f"Agent {ag} should have at least 3 tools"
        assert len(role) > 5, f"Agent {ag} role should be defined"
