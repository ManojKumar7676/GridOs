"""
Accenture GridOS™ - Production Enterprise REST API
Implements real-time SCADA telemetry, multi-agent dispatch orchestration,
and multimodal computer vision endpoints for Problem Statement 4 (Utilities – Renewable Energy Orchestrator).
"""

import sys
import os

# Ensure package root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from AccentureAssessment.core.portfolio import UtilityPortfolioState, AssetStatus
from AccentureAssessment.core.database import OrchestratorDatabase
from AccentureAssessment.perception.radar_vision import RadarVisionEngine, MultimodalPerceptionReport
from AccentureAssessment.agents.orchestrator_agent import ChiefExecutiveOrchestrator
from AccentureAssessment.simulation.engine import IndustrialSimulationEngine

app = FastAPI(
    title="Accenture GridOS™ | Renewable Energy Orchestrator API",
    description="Production Multi-Agent SCADA Telemetry & Dispatch Optimization Engine (Problem Statement 4 - Utilities)",
    version="1.0.0"
)

# Global shared state
db = OrchestratorDatabase()
vision_engine = RadarVisionEngine()
orchestrator = ChiefExecutiveOrchestrator()
sim_engine = IndustrialSimulationEngine()
portfolio = UtilityPortfolioState()

class DispatchRequest(BaseModel):
    interval_idx: int = Field(0, ge=0, le=95, description="15-minute dispatch interval index (0 to 95)")
    clock_time: str = Field("12:00", description="Time of day (HH:MM)")
    spot_price_override: Optional[float] = Field(None, description="Wholesale electricity spot price ($/MWh)")
    storm_alert: bool = Field(False, description="Convective storm alert flag")
    bess1_available: bool = Field(True, description="BESS-01 availability status (outage toggle)")
    transmission_congested: bool = Field(False, description="500kV intertie thermal congestion flag")
    demand_surge_mw: float = Field(0.0, description="Unforecasted industrial demand surge (MW)")
    radar_image_path: Optional[str] = Field(None, description="Doppler radar image path or URI")
    pareto_weights: Optional[Dict[str, float]] = Field(None, description="Dynamic Pareto multi-objective weights")

@app.get("/health")
def health_check():
    return {
        "status": "ONLINE",
        "system": "Accenture GridOS Renewable Energy Orchestrator",
        "standard": "IEC 61850 / IEEE 1547 / NERC BAL-001",
        "problem_statement": "Problem 4: Utilities – Renewable energy orchestrator",
        "claimed_9_blocker": "F3 - D3"
    }

@app.get("/api/v1/portfolio")
def get_portfolio_state():
    return portfolio.model_dump()

@app.post("/api/v1/dispatch")
def execute_dispatch(req: DispatchRequest):
    if req.spot_price_override is not None:
        portfolio.market.spot_price_per_mwh = req.spot_price_override
    
    portfolio.grid.transmission_congested = req.transmission_congested
    portfolio.bess_systems[0].is_available = req.bess1_available
    portfolio.bess_systems[0].status = AssetStatus.OPERATIONAL if req.bess1_available else AssetStatus.MAINTENANCE
    
    if req.demand_surge_mw > 0:
        portfolio.industrial_consumers[0].base_load_mw = 70.0 + req.demand_surge_mw
    else:
        portfolio.industrial_consumers[0].base_load_mw = 70.0

    result = orchestrator.orchestrate(
        portfolio=portfolio,
        interval_idx=req.interval_idx,
        clock_time=req.clock_time,
        radar_image_path=req.radar_image_path,
        manual_pareto_weights=req.pareto_weights
    )

    return {
        "interval_idx": result["interval_idx"],
        "clock_time": result["clock_time"],
        "dispatch_result": result["dispatch_result"].__dict__,
        "trade_off_explanation": result["trade_off_explanation"],
        "agent_deliberations": [msg.model_dump() for msg in result["agent_deliberations"]]
    }

@app.get("/api/v1/telemetry/history")
def get_telemetry_history(limit: int = Query(96, ge=1, le=500)):
    records = db.get_recent_telemetry(limit=limit)
    return {"count": len(records), "records": records}

@app.get("/api/v1/actions/{interval_idx}")
def get_actions(interval_idx: int):
    actions = db.get_actions_for_interval(interval_idx)
    return {"interval_idx": interval_idx, "actions": actions}

@app.post("/api/v1/simulation/run-24h")
def run_simulation(num_steps: int = Query(96, ge=1, le=96)):
    df = sim_engine.run_full_simulation(num_intervals=num_steps)
    return {
        "status": "COMPLETED",
        "intervals_evaluated": len(df),
        "cumulative_profit_usd": float(df["cumulative_profit_usd"].iloc[-1]),
        "cumulative_carbon_tons": float(df["cumulative_carbon_tons"].iloc[-1]),
        "total_curtailment_mwh": float(df["curtailed_mw"].sum() * 0.25)
    }

@app.post("/api/v1/perception/radar")
def generate_and_analyze_radar(cloud_density: float = 0.4, storm_front: bool = False, interval_idx: int = 0):
    img_path = vision_engine.generate_radar_feed(cloud_density, storm_front, interval_idx)
    report = vision_engine.process_radar_image(img_path)
    return report.model_dump()

@app.post("/api/v1/perception/upload-image")
async def upload_and_analyze_image(file: UploadFile = File(...)):
    contents = await file.read()
    report = vision_engine.process_radar_image(contents)
    return report.model_dump()
