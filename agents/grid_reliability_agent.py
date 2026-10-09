"""
Accenture GridOS™ - Grid Reliability & SCADA Physical Asset Health Agent (Agent 3)
Enforces NERC BAL-001 Real-Time Balancing, IEEE 1547 Interconnection Standards,
battery electrochemical C-rate bounds, and 500 kV transmission corridor thermal ratings.
"""

from typing import Optional
from AccentureAssessment.agents.base import AgentDeliberationMessage
from AccentureAssessment.core.portfolio import UtilityPortfolioState
from AccentureAssessment.config.prompt_config import PromptConfig, get_prompt_config

class GridReliabilityAgent:
    """
    Domain Agent 3: Physical SCADA Telemetry, Frequency Stability & Asset Protection.
    """

    def __init__(self, prompt_config: Optional[PromptConfig] = None):
        self.prompt_config = prompt_config or get_prompt_config()
        self.agent_cfg = self.prompt_config.get_agent_config("grid_reliability_agent")

    def deliberate(self, portfolio: UtilityPortfolioState) -> AgentDeliberationMessage:
        b1 = portfolio.bess_systems[0]
        b2 = portfolio.bess_systems[1]
        freq = portfolio.grid.current_frequency_hz
        congested = portfolio.grid.transmission_congested
        volt = portfolio.grid.voltage_kv

        alerts = []
        priority = "NORMAL"

        if freq < 49.85:
            alerts.append(self.prompt_config.get_grid_alert("under_frequency", freq=freq))
            priority = "CRITICAL"
        elif freq > 50.15:
            alerts.append(self.prompt_config.get_grid_alert("over_frequency", freq=freq))
            priority = "ELEVATED"

        if b1.current_soc_pct <= 15.0:
            alerts.append(self.prompt_config.get_grid_alert("bess1_low_soc", soc=b1.current_soc_pct))
        if b2.current_soc_pct >= 93.0:
            alerts.append(self.prompt_config.get_grid_alert("bess2_high_soc", soc=b2.current_soc_pct))

        if congested:
            alerts.append(self.prompt_config.get_grid_alert("transmission_congested"))
            priority = "ELEVATED"

        obs = " | ".join(alerts) if alerts else self.prompt_config.get_grid_alert("nominal", volt=volt, freq=freq)
        reasoning = self.prompt_config.format_grid_reasoning(
            b1_soc=b1.current_soc_pct,
            b2_soc=b2.current_soc_pct,
            freq=freq,
            alerts_count=len(alerts)
        )

        return AgentDeliberationMessage(
            agent_id=self.agent_cfg.get("agent_id", "AGT-03-GRID"),
            agent_name=self.agent_cfg.get("agent_name", "Grid Reliability & SCADA Protection Agent"),
            domain=self.agent_cfg.get("domain", "Physical SCADA Constraints, Electrochemical Health & Frequency"),
            observation=obs,
            analytical_reasoning=reasoning,
            recommended_parameters={
                "reserve_headroom_critical": freq < 49.85,
                "derate_intertie_export": congested,
                "protect_bess1_degradation": b1.current_soc_pct <= 15.0,
                "grid_frequency_hz": freq
            },
            priority_level=priority
        )
