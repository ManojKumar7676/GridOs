"""
Accenture GridOS™ - Meteorological & Vision Perception Forecast Agent (Agent 1)
Ingests multimodal satellite Doppler radar frames, atmospheric pressure profiles, and solar irradiance.
Extracts localized cloud optical depth, spatial attenuation per solar plant, and aerodynamic gust hazards.
"""

from typing import Optional, Union
from AccentureAssessment.agents.base import AgentDeliberationMessage
from AccentureAssessment.core.portfolio import UtilityPortfolioState
from AccentureAssessment.perception.radar_vision import RadarVisionEngine, MultimodalPerceptionReport
from AccentureAssessment.config.prompt_config import PromptConfig, get_prompt_config

class ForecastPerceptionAgent:
    """
    Domain Agent 1: Atmospheric Science, Computer Vision & Renewable Forecasting.
    """

    def __init__(self, vision_engine: RadarVisionEngine, prompt_config: Optional[PromptConfig] = None):
        self.vision = vision_engine
        self.prompt_config = prompt_config or get_prompt_config()
        self.agent_cfg = self.prompt_config.get_agent_config("forecast_agent")

    def deliberate(
        self,
        portfolio: UtilityPortfolioState,
        radar_input: Optional[Union[str, bytes]] = None
    ) -> AgentDeliberationMessage:
        if radar_input:
            report: MultimodalPerceptionReport = self.vision.process_radar_image(radar_input)
            cloud_index = report.cloud_opacity_index
            attenuation = report.solar_derating_factor
            storm_active = report.storm_alert_active
            peak_dbz = report.peak_reflectivity_dbz
            obs = report.perceptual_synopsis

            # Apply localized attenuation to individual solar farms if available
            if report.asset_level_reports:
                asset_map = {rep.asset_id: rep for rep in report.asset_level_reports}
                for sol in portfolio.solar_farms:
                    if sol.id in asset_map:
                        sol.cloud_attenuation_factor = asset_map[sol.id].localized_attenuation_factor
        else:
            cloud_index = 0.20
            attenuation = 0.88
            storm_active = False
            peak_dbz = 18.0
            obs = self.prompt_config.get_forecast_default_observation()

        priority = "CRITICAL" if storm_active else ("ELEVATED" if cloud_index > 0.45 else "NORMAL")
        reasoning = self.prompt_config.format_forecast_reasoning(
            cloud_index=cloud_index,
            peak_dbz=peak_dbz,
            attenuation=attenuation,
            storm_active=storm_active
        )

        return AgentDeliberationMessage(
            agent_id=self.agent_cfg.get("agent_id", "AGT-01-METEO"),
            agent_name=self.agent_cfg.get("agent_name", "Meteorological & Vision Perception Agent"),
            domain=self.agent_cfg.get("domain", "Multimodal Computer Vision & Atmospheric Forecasting"),
            observation=obs,
            analytical_reasoning=reasoning,
            recommended_parameters={
                "solar_derating_factor": attenuation,
                "storm_active": storm_active,
                "cloud_index": cloud_index,
                "peak_reflectivity_dbz": peak_dbz
            },
            priority_level=priority
        )
