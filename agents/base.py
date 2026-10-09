"""
AccentureAssessment - Multi-Agent System Core Interfaces & Message Protocols
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class AgentDeliberationMessage(BaseModel):
    agent_id: str
    agent_name: str
    domain: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    observation: str
    analytical_reasoning: str
    recommended_parameters: Dict[str, Any]
    priority_level: str = "NORMAL"  # NORMAL, ELEVATED, CRITICAL
