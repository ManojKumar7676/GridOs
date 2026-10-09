"""
Accenture GridOS™ - Wholesale Electricity & Carbon Market Trading Agent (Agent 2)
Evaluates real-time Locational Marginal Pricing (LMP), forward arbitrage spreads,
negative pricing tariffs, carbon offset credit compliance, and Demand Response economics.
"""

from typing import Optional
from AccentureAssessment.agents.base import AgentDeliberationMessage
from AccentureAssessment.core.portfolio import UtilityPortfolioState
from AccentureAssessment.config.prompt_config import PromptConfig, get_prompt_config

class MarketArbitrageAgent:
    """
    Domain Agent 2: Wholesale Electricity Trading, Spark Spread & Carbon Arbitrage.
    """

    def __init__(self, prompt_config: Optional[PromptConfig] = None):
        self.prompt_config = prompt_config or get_prompt_config()
        self.agent_cfg = self.prompt_config.get_agent_config("market_agent")

    def deliberate(self, portfolio: UtilityPortfolioState) -> AgentDeliberationMessage:
        spot = portfolio.market.spot_price_per_mwh
        proj_next = portfolio.market.projected_price_next_hour
        carbon_tax = portfolio.market.carbon_credit_price_per_ton
        spread = proj_next - spot

        if spot < 0.0:
            strategy = "ABSORB_CHARGE_CURTAIL"
            priority = "CRITICAL"
            reasoning = self.prompt_config.get_market_reasoning("negative_pricing", spot=spot)
        elif spot > 140.0:
            strategy = "PEAK_DISCHARGE_ARBITRAGE"
            priority = "ELEVATED"
            reasoning = self.prompt_config.get_market_reasoning("price_spike", spot=spot)
        elif spread > 18.0:
            strategy = "STORE_FOR_FORWARD_PEAK"
            priority = "NORMAL"
            reasoning = self.prompt_config.get_market_reasoning("forward_arbitrage", spread=spread)
        else:
            strategy = "ECONOMIC_MERIT_DISPATCH"
            priority = "NORMAL"
            reasoning = self.prompt_config.get_market_reasoning("nominal", spot=spot)

        obs = self.prompt_config.format_market_observation(
            spot=spot,
            proj_next=proj_next,
            spread=spread,
            carbon_tax=carbon_tax
        )

        return AgentDeliberationMessage(
            agent_id=self.agent_cfg.get("agent_id", "AGT-02-MRKT"),
            agent_name=self.agent_cfg.get("agent_name", "Wholesale Market & Trading Agent"),
            domain=self.agent_cfg.get("domain", "Electricity Spot Market, Carbon Credits & Arbitrage"),
            observation=obs,
            analytical_reasoning=reasoning,
            recommended_parameters={
                "strategy": strategy,
                "arbitrage_spread": spread,
                "spot_price": spot,
                "carbon_offset_rate": carbon_tax
            },
            priority_level=priority
        )
