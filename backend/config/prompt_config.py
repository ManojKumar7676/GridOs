"""
Accenture GridOS™ - Prompt & Directive Configuration Manager
Loads, manages, and validates all agent prompts, system instructions, and rationale templates.
Ensures zero hardcoding and allows live prompt configuration updates without code redeployment.
"""

import os
import json
from typing import Dict, Any, Optional

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts.json")

class PromptConfig:
    """
    Centralized configuration engine for agent prompts, personas, and reasoning templates.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.environ.get("GRIDOS_PROMPT_CONFIG", DEFAULT_CONFIG_PATH)
        self._raw_config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Loads configuration from JSON file with defensive fallback."""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._raw_config = json.load(f)
        else:
            raise FileNotFoundError(f"Prompt configuration file not found at: {self.config_path}")

    @property
    def raw(self) -> Dict[str, Any]:
        """Provides access to raw config dictionary."""
        return self._raw_config

    # --- Agent Metadata & System Prompts ---

    def get_agent_config(self, agent_key: str) -> Dict[str, Any]:
        """Retrieves configuration for a specific agent."""
        return self._raw_config.get("agents", {}).get(agent_key, {})

    def get_system_prompt(self, agent_key: str) -> str:
        """Retrieves system persona prompt for an agent."""
        return self.get_agent_config(agent_key).get("system_prompt", "")

    def get_skills(self, agent_key: str) -> list:
        """Retrieves list of core skills for an agent."""
        return self.get_agent_config(agent_key).get("skills", [])

    def get_instructions(self, agent_key: str) -> list:
        """Retrieves operational step-by-step instructions for an agent."""
        return self.get_agent_config(agent_key).get("instructions", [])

    def get_tools(self, agent_key: str) -> list:
        """Retrieves tools, actuators, and APIs used by an agent."""
        return self.get_agent_config(agent_key).get("tools", [])

    def get_role(self, agent_key: str) -> str:
        """Retrieves the operational role title for an agent."""
        return self.get_agent_config(agent_key).get("role", "")

    # --- Forecast Perception Agent ---

    def format_forecast_reasoning(
        self,
        cloud_index: float,
        peak_dbz: float,
        attenuation: float,
        storm_active: bool
    ) -> str:
        agent_cfg = self.get_agent_config("forecast_agent")
        template = agent_cfg.get("reasoning_template", "")
        storm_status = "ACTIVE CRITICAL GUST WARNING" if storm_active else "Nominal laminar boundary layer"
        return template.format(
            cloud_index=cloud_index,
            peak_dbz=peak_dbz,
            attenuation_pct=attenuation * 100.0,
            storm_status=storm_status
        )

    def get_forecast_default_observation(self) -> str:
        agent_cfg = self.get_agent_config("forecast_agent")
        return agent_cfg.get("observation_templates", {}).get("default", "Station Doppler telemetry nominal.")

    # --- Market Arbitrage Agent ---

    def format_market_observation(
        self,
        spot: float,
        proj_next: float,
        spread: float,
        carbon_tax: float
    ) -> str:
        agent_cfg = self.get_agent_config("market_agent")
        template = agent_cfg.get("observation_template", "")
        return template.format(
            spot=spot,
            proj_next=proj_next,
            spread=spread,
            carbon_tax=carbon_tax
        )

    def get_market_reasoning(self, strategy_key: str, **kwargs) -> str:
        agent_cfg = self.get_agent_config("market_agent")
        templates = agent_cfg.get("reasoning_templates", {})
        template = templates.get(strategy_key, "")
        return template.format(**kwargs) if template else ""

    # --- Grid Reliability Agent ---

    def get_grid_alert(self, alert_key: str, **kwargs) -> str:
        agent_cfg = self.get_agent_config("grid_reliability_agent")
        templates = agent_cfg.get("alert_templates", {})
        template = templates.get(alert_key, "")
        return template.format(**kwargs) if template else ""

    def format_grid_reasoning(
        self,
        b1_soc: float,
        b2_soc: float,
        freq: float,
        alerts_count: int
    ) -> str:
        agent_cfg = self.get_agent_config("grid_reliability_agent")
        template = agent_cfg.get("reasoning_template", "")
        return template.format(
            b1_soc=b1_soc,
            b2_soc=b2_soc,
            freq=freq,
            alerts_count=alerts_count
        )

    # --- Orchestrator Agent ---

    def get_orchestrator_tradeoff_rationale(self, situation_key: str, **kwargs) -> str:
        agent_cfg = self.get_agent_config("orchestrator_agent")
        templates = agent_cfg.get("trade_off_rationales", {})
        template = templates.get(situation_key, "")
        return template.format(**kwargs) if template else ""

    # --- Action Rationales (SCED Solver) ---

    def get_action_rationale(self, category: str, action_key: str, **kwargs) -> str:
        category_dict = self._raw_config.get("action_rationales", {}).get(category, {})
        template = category_dict.get(action_key, "")
        return template.format(**kwargs) if template else ""

    # --- Perception Synopsis ---

    def format_perception_synopsis(
        self,
        cloud_ratio: float,
        peak_dbz: float,
        derate: float,
        severity: str
    ) -> str:
        template = self._raw_config.get("perception_templates", {}).get("radar_synopsis", "")
        return template.format(
            cloud_pct=cloud_ratio * 100.0,
            peak_dbz=peak_dbz,
            derate_pct=(1.0 - derate) * 100.0,
            severity=severity
        )

    def get_fallback_synopsis(self) -> str:
        return self._raw_config.get("perception_templates", {}).get("fallback_synopsis", "Station telemetry nominal.")


# Global Singleton
_GLOBAL_CONFIG: Optional[PromptConfig] = None

def get_prompt_config() -> PromptConfig:
    global _GLOBAL_CONFIG
    if _GLOBAL_CONFIG is None:
        _GLOBAL_CONFIG = PromptConfig()
    return _GLOBAL_CONFIG
