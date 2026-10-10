"""
Accenture GridOS™ - Industrial SCADA Command Center & Operational Dispatcher
Enterprise Multi-Agent Platform for Problem Statement 4 (Utilities - Renewable Energy Orchestrator)
Self-Estimated 9-Blocker Position: F3 - D2 (image perception remains an unvalidated prototype)
"""

import sys
import os
import json
import ast
from urllib.parse import urlparse

# Make the repository package importable when Streamlit is launched from the
# repository root or directly against this frontend entry point.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io
import hashlib
import time
from PIL import Image
from datetime import datetime
import streamlit.components.v1 as components

from AccentureAssessment.backend.core.portfolio import UtilityPortfolioState, AssetStatus, MaintenancePriority
from AccentureAssessment.backend.core.database import OrchestratorDatabase
from AccentureAssessment.backend.perception.radar_vision import RadarVisionEngine, MultimodalPerceptionReport
from AccentureAssessment.backend.agents.orchestrator_agent import ChiefExecutiveOrchestrator
from AccentureAssessment.backend.simulation.engine import IndustrialSimulationEngine
from AccentureAssessment.backend.config.prompt_config import get_prompt_config
from AccentureAssessment.backend.core.llm_client import get_gemini_client
from AccentureAssessment.backend.evaluation.evaluation_agent import AuditEvaluationAgent
from AccentureAssessment.backend.evaluation.benchmark_runner import BenchmarkRunner
from AccentureAssessment.backend.evaluation.metrics import MetricsCalculator
from AccentureAssessment.backend.simulation.telemetry_replay import HardwareTelemetryStore, normalize_hardware_telemetry, replay_hardware_telemetry

# High-grade enterprise layout
st.set_page_config(
    page_title="GridOS | Renewable Operations Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

theme_is_dark = st.session_state.get("ui_dark_mode", False)

# Professional SCADA Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: #0b1120;
        color: #e5e7eb;
    }

    [data-testid="stHeader"] {
        background: rgba(11, 17, 32, 0.96);
    }

    [data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #263247;
        border-radius: 10px;
        padding: 12px 14px;
    }

    [data-testid="stMetricLabel"], [data-testid="stCaptionContainer"] {
        color: #a7b3c5;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc;
    }

    [data-testid="stPopoverBody"] {
        background: #0b1120 !important;
        color: #e5e7eb !important;
        border: 1px solid #263247;
    }
    [data-testid="stPopoverBody"] h1,
    [data-testid="stPopoverBody"] h2,
    [data-testid="stPopoverBody"] h3,
    [data-testid="stPopoverBody"] label,
    [data-testid="stPopoverBody"] p { color: #e5e7eb !important; }
    div.st-key-top_nav_row > div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        align-items: flex-start;
    }
    div.st-key-top_nav_row > div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        min-width: 0 !important;
    }
    div.st-key-top_nav_row > div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child {
        flex: 1 1 auto !important;
    }
    div.st-key-top_nav_row > div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child {
        flex: 0 0 280px !important;
    }
    div.st-key-top_nav_launchers {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: flex-end;
        gap: 8px;
        flex-wrap: wrap;
    }
    div.st-key-top_nav_launchers > [data-testid="stLayoutWrapper"] {
        flex: 0 0 auto;
        width: auto !important;
    }
    div.st-key-top_nav_launchers button[data-testid="stPopoverButton"] {
        min-width: 42px;
        min-height: 42px;
        padding: 6px 9px;
        border: 1px solid #334155;
        border-radius: 10px;
        background: #172033 !important;
        color: #e5e7eb !important;
    }
    div.st-key-top_nav_row h1 { font-size: clamp(1.55rem, 4vw, 2.65rem); }

    .stButton > button {
        border: 1px solid #334155;
        background: #172033;
        color: #e5e7eb;
        border-radius: 8px;
    }

    .stButton > button:hover {
        border-color: #38bdf8;
        color: #f8fafc;
    }

    h1, h2, h3, h4 {
        color: #f8fafc;
    }
    
    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    .status-online {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .status-warning {
        background-color: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .status-critical {
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .badge-f3d3 {
        background: linear-gradient(135deg, #059669 0%, #2563eb 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.88rem;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }

    .agent-card-critical {
        background: #111827;
        border-left: 4px solid #ef4444;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 10px;
        border-top: 1px solid #1f2937;
        border-right: 1px solid #1f2937;
        border-bottom: 1px solid #1f2937;
    }

    .agent-card-elevated {
        background: #111827;
        border-left: 4px solid #f59e0b;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 10px;
        border-top: 1px solid #1f2937;
        border-right: 1px solid #1f2937;
        border-bottom: 1px solid #1f2937;
    }

    .agent-card-normal {
        background: #111827;
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 10px;
        border-top: 1px solid #1f2937;
        border-right: 1px solid #1f2937;
        border-bottom: 1px solid #1f2937;
    }
</style>
""", unsafe_allow_html=True)

if not theme_is_dark:
    st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #f4f7fb; color: #172033; }
        [data-testid="stHeader"] { background: rgba(244, 247, 251, 0.96); }
        [data-testid="stMetric"] { background: #ffffff; border-color: #d8e0eb; }
        [data-testid="stMetricValue"], h1, h2, h3, h4 { color: #172033; }
        [data-testid="stMetricLabel"], [data-testid="stCaptionContainer"] { color: #526175; }
        [data-testid="stPopoverBody"] { background: #ffffff !important; color: #172033 !important; border-color: #d8e0eb; }
        [data-testid="stPopoverBody"] h1, [data-testid="stPopoverBody"] h2,
        [data-testid="stPopoverBody"] h3, [data-testid="stPopoverBody"] label,
        [data-testid="stPopoverBody"] p { color: #172033 !important; }
        .stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"] { color: #243247; }
        .stButton > button { background: #ffffff; color: #172033; border-color: #cbd5e1; }
        .stButton > button:hover { background: #eff6ff; color: #0f172a; border-color: #3b82f6; }
        .agent-card-critical, .agent-card-elevated, .agent-card-normal { background: #ffffff; color: #172033; border-top-color: #d8e0eb; border-right-color: #d8e0eb; border-bottom-color: #d8e0eb; }
        [data-testid="stDataFrame"] { border: 1px solid #d8e0eb; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# Shared State Initialization
if "db" not in st.session_state:
    st.session_state.db = OrchestratorDatabase()

if "sim_engine" not in st.session_state:
    st.session_state.sim_engine = IndustrialSimulationEngine()

if "sim_data" not in st.session_state:
    with st.spinner("Initializing 24-Hour Multi-Period Stochastic Simulation (96 Intervals)..."):
        st.session_state.sim_data = st.session_state.sim_engine.run_full_simulation(num_intervals=96, generate_radar_every=12)

if "portfolio" not in st.session_state:
    st.session_state.portfolio = UtilityPortfolioState()

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = ChiefExecutiveOrchestrator()

if "active_step" not in st.session_state:
    st.session_state.active_step = 36

if "is_streaming" not in st.session_state:
    st.session_state.is_streaming = False

APP_STORAGE_DIR = os.path.join(PROJECT_ROOT, "storage")
AGENT_PROFILE_PATH = os.path.join(APP_STORAGE_DIR, "agent_studio_profiles.json")
SKILL_PROFILE_PATH = os.path.join(APP_STORAGE_DIR, "skill_college_catalog.json")
USER_PROFILE_PATH = os.path.join(APP_STORAGE_DIR, "user_management_profiles.json")
TOOLS_PROFILE_PATH = os.path.join(APP_STORAGE_DIR, "agent_tools_catalog.json")


def load_local_catalog(path):
    """Read a local JSON list, returning an empty list when no catalog exists yet."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as catalog_file:
            data = json.load(catalog_file)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_local_catalog(path, records):
    os.makedirs(APP_STORAGE_DIR, exist_ok=True)
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as catalog_file:
        json.dump(records, catalog_file, indent=2, ensure_ascii=False)
    os.replace(temp_path, path)


def prompt_skills_catalog(raw_config):
    """Expose configured agent skills as searchable, source-attributed catalog entries."""
    catalog = []
    for agent_key, agent_config in raw_config.get("agents", {}).items():
        for position, skill_text in enumerate(agent_config.get("skills", []), start=1):
            skill_name, separator, definition = str(skill_text).partition(":")
            catalog.append({
                "skill_id": f"runtime.{agent_key}.{position}",
                "name": skill_name.strip(),
                "category": agent_config.get("agent_name", agent_key),
                "purpose": ("Prompt declaration: " + definition.strip()) if separator else ("Prompt declaration: " + str(skill_text).strip()),
                "use_when": f"When {agent_config.get('role', agent_key)} is handling its configured domain.",
                "inputs": [agent_config.get("domain", "Configured agent context"), "Structured portfolio or scenario values"],
                "outputs": ["An agent observation, recommendation, or calculation in the simulation"],
                "procedure": [],
                "guardrails": ["This catalog entry describes configured prototype capability; it is not an independent validated service."],
                "success_criteria": "The skill reports a result consistent with the supplied modeled inputs.",
                "tools": [],
                "source": "Agent prompt catalog (declarative)",
            })
    return catalog


def unique_record_id(name, existing_records):
    base = "".join(character.lower() if character.isalnum() else "-" for character in name).strip("-") or "new-record"
    base = "-".join(part for part in base.split("-") if part)
    used_ids = {record.get("id", record.get("skill_id", "")) for record in existing_records}
    candidate, suffix = base, 2
    while candidate in used_ids:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate

# Header Console and compact top-right tool launchers
with st.container(key="top_nav_row"):
    top_c1, launcher_col = st.columns([4.2, 2.4])
    with top_c1:
        st.title("⚡ GridOS | Renewable Operations Center")
        st.markdown("**Renewable dispatch control room** · Scenario simulation")
        st.markdown("""
            <div style="display: flex; gap: 8px; margin-top: 4px; flex-wrap: wrap;">
                <span class="status-pill status-online">● SIMULATION ONLINE</span>
                <span class="status-pill status-online">● DISPATCH OPTIMIZER READY</span>
                <span class="status-pill status-online">● 10 ASSETS IN MODEL</span>
                <span class="status-pill status-online">● 15-MINUTE INTERVALS</span>
            </div>
        """, unsafe_allow_html=True)

    with launcher_col:
        with st.container(key="top_nav_launchers"):
            agent_studio_popover = st.popover("🧩", help="Open Agent Studio")
            user_management_popover = st.popover("👤", help="Open User Management")
            st.toggle("Dark theme", value=False, key="ui_dark_mode")

st.markdown("---")

# Main Navigation Tabs
tab_dashboard, tab_telemetry, tab1, tab2, tab3, tab4, tab_vision, tab_eval, tab_prompts, tab_overview = st.tabs([
    "⚡ Operations Dashboard",
    "📡 Telemetry & Replay",
    "🎛️ Dispatch & Scenarios",
    "📈 Trends & Run History",
    "🗺️ Asset Registry",
    "📋 Audit Log",
    "🌦️ Weather Imagery",
    "✅ Evaluation",
    "⚙️ Configuration",
    "ℹ️ System Notes"
])

# =========================================================================
# OPERATIONS DASHBOARD: primary operator workflow
# =========================================================================
with tab_dashboard:
    df = st.session_state.sim_data
    if "dashboard_step" not in st.session_state:
        st.session_state.dashboard_step = int(st.session_state.active_step)

    st.markdown("## Operations overview")
    st.caption("Modeled telemetry · 96 scenario intervals · 15-minute resolution")

    control_col, step_col, mode_col = st.columns([1.15, 2.2, 1.4])
    with control_col:
        prev_col, next_col = st.columns(2)
        if prev_col.button("◀ Previous", use_container_width=True):
            st.session_state.dashboard_step = max(0, st.session_state.dashboard_step - 1)
            st.rerun()
        if next_col.button("Next ▶", use_container_width=True):
            st.session_state.dashboard_step = min(95, st.session_state.dashboard_step + 1)
            st.rerun()
    with step_col:
        active_step = st.slider(
            "Scenario interval (0–95)",
            min_value=0,
            max_value=95,
            key="dashboard_step"
        )
    st.session_state.active_step = int(active_step)
    current = df.iloc[int(active_step)]
    with mode_col:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"<span class='status-pill status-online'>● {current['time']} · INTERVAL {int(active_step) + 1:02d}/96</span>",
            unsafe_allow_html=True
        )
        st.caption("SIMULATED DATA · No field connection")

    renewable_mw = float(current["solar_gen_mw"] + current["wind_gen_mw"])
    demand_mw = float(current["served_demand_mw"])
    clean_share = min(100.0, renewable_mw / demand_mw * 100) if demand_mw > 0 else 0.0
    bess_flow = float(current["bess_net_flow_mw"])
    grid_flow = float(current["grid_export_mw"] - current["grid_import_mw"])
    kpi_cols = st.columns(6)
    kpi_cols[0].metric("Renewable output", f"{renewable_mw:.1f} MW", f"{clean_share:.0f}% of served load")
    kpi_cols[1].metric("Served load", f"{demand_mw:.1f} MW")
    kpi_cols[2].metric("Battery power", f"{bess_flow:+.1f} MW", "Discharging" if bess_flow > 0 else "Charging" if bess_flow < 0 else "Idle")
    kpi_cols[3].metric("Grid exchange", f"{grid_flow:+.1f} MW", "Export" if grid_flow > 0 else "Import" if grid_flow < 0 else "Balanced")
    kpi_cols[4].metric("Spot price", f"${float(current['spot_price']):.2f}/MWh")
    kpi_cols[5].metric("Reserve margin", f"{float(current['reserve_margin_mw']):.1f} MW", str(current["grid_stress"]))

    status_col, chart_col = st.columns([1.05, 2.3])
    with status_col:
        st.markdown("### System status")
        event_name = str(current["event"])
        if event_name != "Routine Operations":
            st.warning(f"**Active event**\n\n{event_name}")
        else:
            st.success("**No active scenario event**\n\nAll modeled subsystems operating within the selected scenario.")

        st.markdown("#### Asset snapshot")
        asset_snapshot = pd.DataFrame([
            {"Asset group": "Solar fleet", "Output": f"{float(current['solar_gen_mw']):.1f} MW", "State": "Producing" if float(current["solar_gen_mw"]) > 0 else "Night / unavailable"},
            {"Asset group": "Wind fleet", "Output": f"{float(current['wind_gen_mw']):.1f} MW", "State": "Storm cut-out" if "Storm" in event_name else "Producing"},
            {"Asset group": "BESS-01", "Output": f"{float(current['bess1_soc_pct']):.1f}% SoC", "State": "Unavailable" if "BESS-01" in event_name else "Available"},
            {"Asset group": "BESS-02", "Output": f"{float(current['bess2_soc_pct']):.1f}% SoC", "State": "Available"},
            {"Asset group": "Grid intertie", "Output": f"{abs(grid_flow):.1f} MW", "State": "Congested" if "Congested" in event_name else "Connected (modeled)"},
        ])
        st.dataframe(asset_snapshot, hide_index=True, use_container_width=True)

    with chart_col:
        st.markdown("### Dispatch profile")
        lo, hi = max(0, int(active_step) - 16), min(len(df), int(active_step) + 17)
        window = df.iloc[lo:hi]
        fig_live = go.Figure()
        fig_live.add_trace(go.Scatter(x=window["time"], y=window["solar_gen_mw"], name="Solar", stackgroup="generation", line=dict(color="#fbbf24")))
        fig_live.add_trace(go.Scatter(x=window["time"], y=window["wind_gen_mw"], name="Wind", stackgroup="generation", line=dict(color="#34d399")))
        fig_live.add_trace(go.Scatter(x=window["time"], y=window["served_demand_mw"], name="Served load", line=dict(color="#fb7185", width=3)))
        fig_live.add_trace(go.Scatter(x=window["time"], y=window["grid_import_mw"], name="Grid import", line=dict(color="#a78bfa", dash="dot")))
        fig_live.add_trace(go.Scatter(x=window["time"], y=window["grid_export_mw"], name="Grid export", line=dict(color="#60a5fa", dash="dot")))
        fig_live.add_vline(x=str(current["time"]), line_dash="dash", line_color="white", opacity=0.65)
        fig_live.update_layout(
            template="plotly_dark", height=410, margin=dict(l=10, r=10, t=20, b=10),
            xaxis_title="Scenario time", yaxis_title="Power (MW)", hovermode="x unified",
            legend=dict(orientation="h", y=-0.2)
        )
        st.plotly_chart(fig_live, use_container_width=True)

    lower_left, lower_right = st.columns([1.3, 1])
    with lower_left:
        st.markdown("### Upcoming scenario events")
        upcoming = df.iloc[int(active_step) + 1:]
        upcoming = upcoming[upcoming["event"] != "Routine Operations"].head(5)
        if upcoming.empty:
            st.info("No further scripted events in this run.")
        else:
            st.dataframe(upcoming[["time", "event", "spot_price", "grid_stress"]].rename(columns={
                "time": "Time", "event": "Event", "spot_price": "Price ($/MWh)", "grid_stress": "Grid state"
            }), hide_index=True, use_container_width=True)
    with lower_right:
        st.markdown("### Run summary")
        st.metric("Net financial result", f"${float(current['cumulative_profit_usd']):,.0f}", "cumulative modeled value")
        st.metric("Clean energy generated", f"{float(df.iloc[:int(active_step) + 1]['total_renewables_mw'].sum() * 0.25):,.1f} MWh")
        st.caption("Use **Dispatch & Scenarios** to choose a stress case and inspect the optimizer's dispatch recommendation.")

# =========================================================================
# TELEMETRY LAB: imported hardware readings and explicit simulated replay
# =========================================================================
with tab_telemetry:
    st.markdown("## Hardware telemetry & replay")
    st.caption("Import measured plant data, inspect it separately from simulations, then replay those measurements through the local dispatch optimizer.")
    st.warning("No physical hardware or SCADA link is connected. Hardware readings enter this prototype only when you import an exported CSV or JSON file.")

    hardware_store = HardwareTelemetryStore(os.path.join(APP_STORAGE_DIR, "orchestrator.db"))
    hardware_records = hardware_store.get_recent(limit=5000)
    newest_import = hardware_records[-1] if hardware_records else None
    simulated_hardware_frame = st.session_state.sim_data
    simulated_hardware_records = [{
        "timestamp": str(row["time"]),
        "solar_generation_mw": float(row["solar_gen_mw"]),
        "wind_generation_mw": float(row["wind_gen_mw"]),
        "demand_mw": float(row["served_demand_mw"]),
        "spot_price_usd_mwh": float(row["spot_price"]),
        "bess1_soc_pct": float(row["bess1_soc_pct"]),
        "bess2_soc_pct": float(row["bess2_soc_pct"]),
        "transmission_congested": "congest" in str(row["event"]).casefold(),
        "bess1_available": "bess-01" not in str(row["event"]).casefold(),
        "source": "SIMULATED DEMO",
    } for _, row in simulated_hardware_frame.iterrows()]
    status_col, count_col, latest_col = st.columns(3)
    status_col.metric("Field connection", "Disconnected", "Import-only prototype")
    count_col.metric("Imported hardware samples", f"{len(hardware_records):,}")
    latest_col.metric("Latest imported sample", newest_import["device_timestamp"] if newest_import else "None")

    st.markdown("### Import a hardware telemetry export")
    st.caption("Required fields: solar generation (MW), wind generation (MW), site demand (MW), and spot price ($/MWh). Timestamp, battery state of charge, wind speed, cloud index, grid frequency, voltage, and status flags are optional.")
    template = pd.DataFrame([{
        "timestamp": "2026-10-10T09:00:00Z",
        "solar_generation_mw": 82.5,
        "wind_generation_mw": 54.0,
        "demand_mw": 165.0,
        "spot_price_usd_mwh": 42.35,
        "bess1_soc_pct": 64.0,
        "bess2_soc_pct": 78.0,
        "wind_speed_mps": 9.5,
        "cloud_index": 0.22,
        "grid_frequency_hz": 50.0,
        "voltage_kv": 500.0,
        "transmission_congested": False,
        "bess1_available": True,
    }])
    st.download_button(
        "Download telemetry CSV template (illustrative row)",
        data=template.to_csv(index=False),
        file_name="gridos_hardware_telemetry_template.csv",
        mime="text/csv",
        help="The example row is illustrative and must not be treated as a real hardware observation.",
    )
    telemetry_upload = st.file_uploader("Choose CSV or JSON telemetry", type=["csv", "json"], key="hardware_telemetry_upload")
    imported_preview = None
    if telemetry_upload is not None:
        try:
            payload = telemetry_upload.getvalue()
            if telemetry_upload.name.casefold().endswith(".csv"):
                raw_upload = pd.read_csv(io.BytesIO(payload))
            else:
                decoded = json.loads(payload.decode("utf-8-sig"))
                if isinstance(decoded, dict):
                    decoded = decoded.get("records", decoded.get("telemetry"))
                if not isinstance(decoded, list) or not all(isinstance(item, dict) for item in decoded):
                    raise ValueError("JSON must contain an array of telemetry record objects, or a 'records' array.")
                raw_upload = pd.DataFrame(decoded)
            imported_preview = normalize_hardware_telemetry(raw_upload)
            st.success(f"File validated: {len(imported_preview):,} rows with the required replay fields.")
            st.dataframe(imported_preview.head(12), hide_index=True, use_container_width=True)
            upload_digest = hashlib.sha256(telemetry_upload.name.encode("utf-8") + payload).hexdigest()
            if st.button("Import validated readings to local hardware history", type="primary", key="import_hardware_telemetry"):
                if st.session_state.get("last_hardware_upload_digest") == upload_digest:
                    st.info("This exact file has already been imported in this app session.")
                else:
                    count = hardware_store.save(
                        imported_preview.where(pd.notna(imported_preview), None).to_dict(orient="records"),
                        telemetry_upload.name,
                    )
                    st.session_state.last_hardware_upload_digest = upload_digest
                    st.success(f"Imported {count:,} hardware telemetry records into the local database.")
                    st.rerun()
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError, pd.errors.ParserError) as error:
            st.error(f"Could not import this telemetry file: {error}")

    if hardware_records:
        st.markdown("### Collected hardware data")
        hardware_frame = pd.DataFrame(hardware_records).rename(columns={
            "device_timestamp": "Device timestamp",
            "source_file": "Imported file",
            "solar_generation_mw": "Solar (MW)",
            "wind_generation_mw": "Wind (MW)",
            "demand_mw": "Site demand (MW)",
            "spot_price_usd_mwh": "Spot price ($/MWh)",
            "bess1_soc_pct": "BESS-01 SoC (%)",
            "bess2_soc_pct": "BESS-02 SoC (%)",
            "grid_frequency_hz": "Frequency (Hz)",
            "voltage_kv": "Voltage (kV)",
            "imported_at": "Imported at (UTC)",
        })
        display_columns = [column for column in [
            "Device timestamp", "Imported file", "Solar (MW)", "Wind (MW)", "Site demand (MW)",
            "Spot price ($/MWh)", "BESS-01 SoC (%)", "BESS-02 SoC (%)", "Frequency (Hz)",
            "Voltage (kV)", "Imported at (UTC)",
        ] if column in hardware_frame]
        st.dataframe(hardware_frame[display_columns].iloc[::-1].head(200), hide_index=True, use_container_width=True)
    else:
        st.info("No measured hardware readings have been imported. The demo data below is simulated for this showcase and is not a live device feed.")

    st.markdown("### Simulated hardware demo data")
    st.caption(f"{len(simulated_hardware_records)} demo samples from the built-in scenario, formatted like a hardware telemetry export. These values are simulated and are not collected from a device.")
    demo_frame = pd.DataFrame(simulated_hardware_records).rename(columns={
        "timestamp": "Demo timestamp",
        "source": "Source",
        "solar_generation_mw": "Solar (MW)",
        "wind_generation_mw": "Wind (MW)",
        "demand_mw": "Site demand (MW)",
        "spot_price_usd_mwh": "Spot price ($/MWh)",
        "bess1_soc_pct": "BESS-01 SoC (%)",
        "bess2_soc_pct": "BESS-02 SoC (%)",
        "transmission_congested": "Grid congested (demo)",
        "bess1_available": "BESS-01 available (demo)",
    })
    st.dataframe(demo_frame.iloc[::-1].head(24), hide_index=True, use_container_width=True)

    st.markdown("### Replay data through dispatch simulation")
    replay_options = (["Imported hardware telemetry"] if hardware_records else []) + ["Simulated hardware demo"]
    replay_source = st.radio("Replay source", replay_options, horizontal=True, key="telemetry_replay_source_v2")

    if replay_source == "Imported hardware telemetry":
        replay_records = [{
            "timestamp": record["device_timestamp"],
            "solar_generation_mw": record["solar_generation_mw"],
            "wind_generation_mw": record["wind_generation_mw"],
            "demand_mw": record["demand_mw"],
            "spot_price_usd_mwh": record["spot_price_usd_mwh"],
            "bess1_soc_pct": record["bess1_soc_pct"],
            "bess2_soc_pct": record["bess2_soc_pct"],
            "wind_speed_mps": record["wind_speed_mps"],
            "cloud_index": record["cloud_index"],
            "grid_frequency_hz": record["grid_frequency_hz"],
            "voltage_kv": record["voltage_kv"],
            "transmission_congested": bool(record["transmission_congested"]) if record["transmission_congested"] is not None else None,
            "bess1_available": bool(record["bess1_available"]) if record["bess1_available"] is not None else None,
        } for record in hardware_records]
    else:
        replay_records = simulated_hardware_records

    replay_limit = min(96, len(replay_records))
    replay_count = st.slider("Intervals to replay", min_value=1, max_value=max(1, replay_limit), value=replay_limit, key="telemetry_replay_count")
    replay_source_signature = hashlib.sha256(
        (replay_source + json.dumps(replay_records, sort_keys=True, default=str)).encode("utf-8")
    ).hexdigest()
    if st.button("Run telemetry replay through optimizer", type="primary", key="run_telemetry_replay"):
        try:
            replayed = replay_hardware_telemetry(replay_records[-replay_count:])
            st.session_state.telemetry_replay_result = replayed
            st.session_state.telemetry_replay_result_source = replay_source_signature
        except (ValueError, KeyError, TypeError) as error:
            st.error(f"Replay could not be completed: {error}")

    replayed = st.session_state.get("telemetry_replay_result")
    if replayed is not None and st.session_state.get("telemetry_replay_result_source") == replay_source_signature:
        input_label = "Imported hardware readings" if replay_source == "Imported hardware telemetry" else "Simulated hardware demo values"
        chart_prefix = "Hardware input" if replay_source == "Imported hardware telemetry" else "Demo input"
        st.caption(f"Replay uses {input_label.lower()} for renewable availability, site demand, market price, and any supplied battery/grid states. It computes a software dispatch recommendation only; no field command is sent.")
        latest_replay = replayed.iloc[-1]
        replay_kpis = st.columns(5)
        replay_kpis[0].metric("Intervals replayed", len(replayed))
        replay_kpis[1].metric("Latest optimizer unserved load", f"{latest_replay['unserved_demand_mw']:.2f} MW")
        replay_kpis[2].metric("Latest grid import", f"{latest_replay['grid_import_mw']:.1f} MW")
        replay_kpis[3].metric("Latest grid export", f"{latest_replay['grid_export_mw']:.1f} MW")
        replay_kpis[4].metric("Peak balance error", f"{replayed['power_balance_residual_mw'].abs().max():.4f} MW")

        replay_chart = go.Figure()
        replay_chart.add_trace(go.Scatter(x=replayed["timestamp"], y=replayed["measured_solar_mw"], name=f"{chart_prefix} solar", line=dict(color="#fbbf24")))
        replay_chart.add_trace(go.Scatter(x=replayed["timestamp"], y=replayed["measured_wind_mw"], name=f"{chart_prefix} wind", line=dict(color="#34d399")))
        replay_chart.add_trace(go.Scatter(x=replayed["timestamp"], y=replayed["measured_demand_mw"], name=f"{chart_prefix} demand", line=dict(color="#fb7185", dash="dash")))
        replay_chart.add_trace(go.Scatter(x=replayed["timestamp"], y=replayed["served_demand_mw"], name="Optimizer served", line=dict(color="#60a5fa", width=3)))
        replay_chart.update_layout(template="plotly_dark", height=340, margin=dict(l=15, r=15, t=30, b=15), title=f"{input_label} and optimizer replay", xaxis_title="Device time / interval", yaxis_title="Power (MW)", hovermode="x unified")
        st.plotly_chart(replay_chart, use_container_width=True)
        replay_display = replayed.rename(columns={
            "measured_solar_mw": f"{chart_prefix} solar (MW)",
            "measured_wind_mw": f"{chart_prefix} wind (MW)",
            "measured_demand_mw": f"{chart_prefix} demand (MW)",
            "spot_price_usd_mwh": "Input spot price ($/MWh)",
            "measured_bess1_soc_pct": "Input BESS-01 SoC (%)",
            "measured_bess2_soc_pct": "Input BESS-02 SoC (%)",
            "dispatch_solar_mw": "Optimizer solar dispatch (MW)",
            "dispatch_wind_mw": "Optimizer wind dispatch (MW)",
            "served_demand_mw": "Optimizer served load (MW)",
            "bess1_soc_pct": "Simulated BESS-01 SoC (%)",
            "bess2_soc_pct": "Simulated BESS-02 SoC (%)",
            "grid_import_mw": "Optimizer grid import (MW)",
            "grid_export_mw": "Optimizer grid export (MW)",
            "unserved_demand_mw": "Unserved demand (MW)",
            "net_value_usd": "Modeled net value ($)",
            "frequency_hz": "Input frequency (Hz)",
            "frequency_status": "Frequency check",
            "solver_status": "Solver status",
            "power_balance_residual_mw": "Power balance error (MW)",
        })
        st.dataframe(replay_display, hide_index=True, use_container_width=True)

# =========================================================================
# AGENT STUDIO: inspect runtime agents and author local agent profiles
# =========================================================================
with agent_studio_popover:
    raw_agent_config = get_prompt_config().raw
    runtime_agent_cards = [
        {
            "key": "orchestrator_agent",
            "component": "ChiefExecutiveOrchestrator",
            "implementation": "Coordinates domain-agent outputs and passes dispatch inputs to the local optimizer.",
            "runtime_tools": ["IndustrialDispatchSolver", "OrchestratorDatabase", "Forecast / Market / Reliability agents"],
        },
        {
            "key": "forecast_agent",
            "component": "ForecastPerceptionAgent",
            "implementation": "Applies RGB image heuristics to synthetic or uploaded images; not a validated weather forecast.",
            "runtime_tools": ["RadarVisionEngine", "Pillow / NumPy image processing"],
        },
        {
            "key": "market_agent",
            "component": "MarketArbitrageAgent",
            "implementation": "Evaluates modeled spot and forward price inputs; no market API is connected.",
            "runtime_tools": ["Modeled portfolio price fields"],
        },
        {
            "key": "grid_reliability_agent",
            "component": "GridReliabilityAgent",
            "implementation": "Checks modeled asset, reserve, battery, and intertie constraints; no SCADA connection is active.",
            "runtime_tools": ["Modeled portfolio constraints"],
        },
    ]
    builtin_skills = prompt_skills_catalog(raw_agent_config)
    saved_skills = load_local_catalog(SKILL_PROFILE_PATH)
    skill_options = builtin_skills + saved_skills
    skill_labels = {item["skill_id"]: f"{item['name']} · {item['category']}" for item in skill_options}
    saved_agents = load_local_catalog(AGENT_PROFILE_PATH)
    saved_tools = load_local_catalog(TOOLS_PROFILE_PATH)
    tool_labels = {item["id"]: f"{item['name']} · {item['type']}" for item in saved_tools}

    st.markdown("## Agent Studio")
    st.caption("Inspect the four agents wired into the simulation, or create reusable local agent profiles.")
    live_col, draft_col, skill_col = st.columns(3)
    live_col.metric("Runtime agents", str(len(runtime_agent_cards)), "wired into dispatch simulation")
    draft_col.metric("Local profiles", str(len(saved_agents)), "saved separately")
    skill_col.metric("Skills available", str(len(skill_options)), "runtime catalog + local skills")

    agents_tab, skills_tab, tools_tab = st.tabs(["Agents", "Skills", "Tools"])
    with agents_tab:
        studio_runtime, studio_create, studio_saved = st.tabs(["Runtime agents", "Create agent", "Saved profiles"])
        with studio_runtime:
            st.info("These four components run in the current local simulation. Agents you create below are saved as profiles; this UI does not execute arbitrary instructions or activate external tools.")
            for runtime_agent in runtime_agent_cards:
                config = raw_agent_config.get("agents", {}).get(runtime_agent["key"], {})
                with st.expander(f"{config.get('agent_name', runtime_agent['component'])} · {runtime_agent['component']}", expanded=False):
                    role_col, domain_col = st.columns(2)
                    role_col.markdown(f"**Role**\n\n{config.get('role', 'Domain agent')}")
                    domain_col.markdown(f"**Operating domain**\n\n{config.get('domain', 'Dispatch simulation')}")
                    st.markdown(f"**What it does in this app**\n\n{runtime_agent['implementation']}")
                    left, right = st.columns(2)
                    with left:
                        st.markdown("**Configured skills**")
                        for skill in config.get("skills", []):
                            st.markdown(f"- {skill}")
                    with right:
                        st.markdown("**Runtime tools**")
                        for tool_name in runtime_agent["runtime_tools"]:
                            st.markdown(f"- `{tool_name}`")
                    st.caption(f"Prompt configuration key: `{runtime_agent['key']}`")

        with studio_create:
            st.markdown("### Define an agent profile")
            st.caption("Profiles are local design artifacts. MCP/API entries are connection declarations only; this app does not call or authenticate to them.")
            with st.form("create_agent_profile", clear_on_submit=True):
                agent_name = st.text_input("Agent name", placeholder="e.g. Renewable Forecast Reviewer")
                name_col, role_col = st.columns(2)
                with name_col:
                    agent_role = st.text_input("Role", placeholder="e.g. Forecast quality analyst")
                with role_col:
                    agent_domain = st.text_input("Domain", placeholder="e.g. Solar and wind forecast review")
                agent_purpose = st.text_area("Purpose", placeholder="What should this agent accomplish, and for whom?", height=90)
                agent_instructions = st.text_area(
                    "Instructions",
                    placeholder="Write the agent's task instructions, decision process, output format, and escalation behavior.",
                    height=150,
                )
                selected_skill_ids = st.multiselect(
                    "Skills to assign",
                    options=list(skill_labels),
                    format_func=lambda skill_id: skill_labels.get(skill_id, skill_id),
                    help="Choose from runtime prompt skills and skills created in Agent Studio.",
                )
                selected_tool_ids = st.multiselect(
                    "Tools from Tools College",
                    options=list(tool_labels),
                    format_func=lambda tool_id: tool_labels.get(tool_id, tool_id),
                    help="Select local API, MCP, or function definitions. They are assignments only until connected by a trusted runtime.",
                )
                tool_lines = st.text_area(
                    "Tool connections (one per line)",
                    placeholder="mcp | weather-mcp | http://localhost:8000/sse | Read modeled weather data | WEATHER_TOKEN\napi | forecast-service | https://api.example.test/v1 | Retrieve forecast metadata | FORECAST_API_KEY",
                    height=100,
                    help="Format: type | name | endpoint or server ID | purpose | optional auth environment-variable name. Types: mcp, api, internal. Do not enter secrets.",
                )
                save_agent = st.form_submit_button("Create local agent profile", use_container_width=True)

            if save_agent:
                problems = []
                if not agent_name.strip():
                    problems.append("Add an agent name.")
                if not agent_role.strip() or not agent_domain.strip():
                    problems.append("Add both a role and an operating domain.")
                if not agent_purpose.strip() or not agent_instructions.strip():
                    problems.append("Add a purpose and actionable instructions.")

                connectors, connector_errors = [], []
                for line_number, line in enumerate(tool_lines.splitlines(), start=1):
                    if not line.strip():
                        continue
                    fields = [part.strip() for part in line.split("|")]
                    if len(fields) not in (4, 5):
                        connector_errors.append(f"Tool line {line_number} needs 4 or 5 pipe-separated fields.")
                        continue
                    connection_type, connection_name, endpoint, purpose = fields[:4]
                    auth_env = fields[4] if len(fields) == 5 else ""
                    if connection_type.lower() not in {"mcp", "api", "internal"}:
                        connector_errors.append(f"Tool line {line_number} type must be mcp, api, or internal.")
                    elif not connection_name or not endpoint or not purpose:
                        connector_errors.append(f"Tool line {line_number} needs a name, endpoint/server ID, and purpose.")
                    else:
                        connectors.append({
                            "type": connection_type.lower(),
                            "name": connection_name,
                            "endpoint_or_server": endpoint,
                            "purpose": purpose,
                            "auth_env_var": auth_env,
                            "status": "Declared only; not connected",
                        })
                problems.extend(connector_errors)

                if problems:
                    for problem in problems:
                        st.error(problem)
                else:
                    profile = {
                        "id": unique_record_id(agent_name, saved_agents),
                        "name": agent_name.strip(),
                        "role": agent_role.strip(),
                        "domain": agent_domain.strip(),
                        "purpose": agent_purpose.strip(),
                        "instructions": agent_instructions.strip(),
                        "skill_ids": selected_skill_ids,
                        "tool_ids": selected_tool_ids,
                        "tools": connectors,
                        "status": "Draft profile · not connected to runtime",
                        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                    }
                    saved_agents.append(profile)
                    save_local_catalog(AGENT_PROFILE_PATH, saved_agents)
                    st.success(f"Saved **{profile['name']}** to the local Agent Studio catalog.")

        with studio_saved:
            st.markdown("### Saved local profiles")
            if not saved_agents:
                st.info("No custom agent profiles yet. Create one from the Create agent tab.")
            for profile in reversed(saved_agents):
                with st.expander(f"{profile.get('name', 'Unnamed agent')} · {profile.get('status', 'Local profile')}"):
                    st.markdown(f"**Role:** {profile.get('role', '')}  ·  **Domain:** {profile.get('domain', '')}")
                    st.markdown(f"**Purpose**\n\n{profile.get('purpose', '')}")
                    st.markdown(f"**Instructions**\n\n{profile.get('instructions', '')}")
                    assigned = [skill_labels.get(skill_id, skill_id) for skill_id in profile.get("skill_ids", [])]
                    st.markdown("**Skills:** " + (", ".join(assigned) if assigned else "None assigned"))
                    assigned_tools = [tool_labels.get(tool_id, tool_id) for tool_id in profile.get("tool_ids", [])]
                    st.markdown("**Tools College assignments:** " + (", ".join(assigned_tools) if assigned_tools else "None assigned"))
                    if profile.get("tools"):
                        st.markdown("**Declared MCP/API/internal tools**")
                        st.json(profile["tools"])
                    else:
                        st.caption("No tool connections declared.")

    with skills_tab:
        skill_catalog_tab, create_skill_tab = st.tabs(["Skill catalog", "Create skill"])
        with skill_catalog_tab:
            st.markdown("### Skills available to agents")
            st.caption("Browse configured capabilities or inspect locally authored skills and their operating boundaries.")
            skill_query = st.text_input("Find a skill", placeholder="Search skill names, domains, and purpose", key="agent_studio_skill_search")
            matching_skills = [
                skill for skill in skill_options
                if not skill_query.strip() or skill_query.strip().casefold() in json.dumps(skill, ensure_ascii=False).casefold()
            ]
            st.caption(f"{len(matching_skills)} skills available · {sum(1 for item in matching_skills if item.get('source') != 'Agent prompt catalog (declarative)')} locally authored")
            for skill in matching_skills:
                with st.expander(f"{skill.get('name', 'Unnamed skill')} · {skill.get('category', 'General')}"):
                    st.markdown(f"**Purpose**\n\n{skill.get('purpose', '')}")
                    st.markdown(f"**Use when:** {skill.get('use_when', 'Not specified')}")
                    input_col, output_col = st.columns(2)
                    input_col.markdown("**Inputs**\n\n" + ("\n".join(f"- {item}" for item in skill.get('inputs', [])) or "Not specified"))
                    output_col.markdown("**Outputs**\n\n" + ("\n".join(f"- {item}" for item in skill.get('outputs', [])) or "Not specified"))
                    if skill.get("procedure"):
                        st.markdown("**Procedure**\n\n" + "\n".join(f"{number}. {step}" for number, step in enumerate(skill["procedure"], start=1)))
                    if skill.get("guardrails"):
                        st.markdown("**Limits and guardrails**\n\n" + "\n".join(f"- {item}" for item in skill["guardrails"]))
                    if skill.get("success_criteria"):
                        st.markdown(f"**Success check:** {skill['success_criteria']}")
                    if skill.get("tools"):
                        st.caption("Tools/resources: " + ", ".join(skill["tools"]))
                    st.caption(f"Source: {skill.get('source', 'Locally authored')}")

        with create_skill_tab:
            st.markdown("### Define a reusable skill")
            st.caption("Specify its purpose, trigger, inputs, outputs, steps, required resources, guardrails, and success check.")
            tool_choices = [
                "Local dispatch optimizer", "Local portfolio data", "Local SQLite audit store",
                "RGB image heuristic pipeline", "No external tool",
            ] + [f"{item['id']} · {item['name']} ({item['type']})" for item in saved_tools]
            with st.form("create_skill_definition", clear_on_submit=True):
                skill_name = st.text_input("Skill name", placeholder="e.g. Battery reserve review")
                skill_domain = st.text_input("Domain / owning agent", placeholder="e.g. Grid reliability")
                skill_purpose = st.text_area("Purpose", placeholder="The specific capability this skill provides.", height=80)
                skill_when = st.text_area("When to use", placeholder="Trigger conditions and situations where the skill applies.", height=75)
                input_col, output_col = st.columns(2)
                with input_col:
                    skill_inputs = st.text_area("Inputs (one per line)", placeholder="Battery state of charge\nReserve target\nDispatch interval", height=100)
                with output_col:
                    skill_outputs = st.text_area("Outputs (one per line)", placeholder="Reserve status\nRecommended action\nReason codes", height=100)
                skill_procedure = st.text_area("Procedure (one step per line)", placeholder="1. Read the modeled battery state.\n2. Compare against configured limits.\n3. Return a recommendation and explain the checks.", height=125)
                skill_guardrails = st.text_area("Limits and guardrails (one per line)", placeholder="Do not send commands to equipment.\nReport missing inputs instead of guessing.", height=90)
                skill_tools = st.multiselect("Tools or resources required", tool_choices, default=["Local portfolio data"])
                skill_success = st.text_area("Success criteria", placeholder="How can an operator or evaluator tell the skill worked correctly?", height=75)
                save_skill = st.form_submit_button("Save skill", use_container_width=True)

            if save_skill:
                required_fields = {
                    "Skill name": skill_name, "Domain / owning agent": skill_domain,
                    "Purpose": skill_purpose, "When to use": skill_when, "Inputs": skill_inputs,
                    "Outputs": skill_outputs, "Procedure": skill_procedure,
                    "Limits and guardrails": skill_guardrails, "Success criteria": skill_success,
                }
                missing = [label for label, value in required_fields.items() if not value.strip()]
                if missing:
                    st.error("Complete these required fields: " + ", ".join(missing) + ".")
                else:
                    skill_record = {
                        "skill_id": unique_record_id(skill_name, saved_skills),
                        "name": skill_name.strip(), "category": skill_domain.strip(),
                        "purpose": skill_purpose.strip(), "use_when": skill_when.strip(),
                        "inputs": [line.strip() for line in skill_inputs.splitlines() if line.strip()],
                        "outputs": [line.strip() for line in skill_outputs.splitlines() if line.strip()],
                        "procedure": [line.strip() for line in skill_procedure.splitlines() if line.strip()],
                        "guardrails": [line.strip() for line in skill_guardrails.splitlines() if line.strip()],
                        "success_criteria": skill_success.strip(), "tools": skill_tools,
                        "source": "Agent Studio skill catalog",
                        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                    }
                    saved_skills.append(skill_record)
                    save_local_catalog(SKILL_PROFILE_PATH, saved_skills)
                    st.success(f"Saved **{skill_record['name']}**. It is now available for assignment to agent profiles.")

    with tools_tab:
        st.markdown("### Tools College")
        st.caption("Define API, MCP, or Python function tools and review what is available to agent profiles.")
        runtime_tools = []
        for runtime_agent in runtime_agent_cards:
            for runtime_tool in runtime_agent.get('runtime_tools', []):
                if runtime_tool not in runtime_tools:
                    runtime_tools.append(runtime_tool)
        built_in_tool_col, saved_tool_col = st.columns(2)
        built_in_tool_col.metric("Runtime tools", len(runtime_tools), "used by current agents")
        saved_tool_col.metric("Saved definitions", len(saved_tools), "local tool catalog")

        for runtime_tool in runtime_tools:
            st.markdown(f"- **{runtime_tool}** · Existing local capability")
        for tool in saved_tools:
            with st.expander(f"{tool.get('name', 'Unnamed tool')} · {tool.get('type', 'Tool')} · Local definition"):
                st.markdown(f"**Purpose:** {tool.get('purpose', '')}")
                st.markdown(f"**Input contract:** {tool.get('input_schema', 'Not specified')}")
                st.markdown(f"**Output contract:** {tool.get('output_schema', 'Not specified')}")
                if tool.get('endpoint'):
                    st.markdown(f"**Endpoint:** `{tool['endpoint']}`")
                if tool.get('server_id'):
                    st.markdown(f"**MCP server:** `{tool['server_id']}` · {tool.get('transport', '')}")
                if tool.get('function_code'):
                    st.code(tool['function_code'], language="python")
                if tool.get('auth_env_var'):
                    st.caption(f"Credentials expected from environment variable `{tool['auth_env_var']}`; no secret is stored here.")

        st.info("Definitions are saved locally and can be assigned to agent profiles. API and MCP endpoints are not called; code snippets are validated for syntax and never executed by this prototype.")
        tool_type = st.selectbox("Tool type", ["REST API", "MCP server/tool", "Python function"], key="tool_college_type")
        with st.form("create_tool_definition", clear_on_submit=True):
            tool_name = st.text_input("Tool name", placeholder="e.g. Forecast lookup")
            tool_purpose = st.text_area("Purpose", placeholder="What this tool does, and when an agent should use it.", height=75)
            input_schema = st.text_area("Input contract", placeholder='JSON Schema or a clear input description, e.g. {"location": "string"}', height=75)
            output_schema = st.text_area("Output contract", placeholder='JSON Schema or a clear output description, e.g. {"forecast": "object"}', height=75)
            api_endpoint = api_method = auth_env_var = ""
            mcp_server_id = mcp_endpoint = mcp_transport = mcp_tool_name = ""
            function_code = ""
            if tool_type == "REST API":
                api_endpoint = st.text_input("API endpoint URL", placeholder="https://api.example.com/v1/forecast")
                api_method = st.selectbox("HTTP method", ["GET", "POST", "PUT", "PATCH", "DELETE"])
                auth_env_var = st.text_input("Auth environment variable name (optional)", placeholder="FORECAST_API_KEY")
            elif tool_type == "MCP server/tool":
                mcp_server_id = st.text_input("MCP server ID", placeholder="weather-mcp")
                mcp_transport = st.selectbox("Transport", ["Streamable HTTP", "SSE", "STDIO command declaration"])
                mcp_endpoint = st.text_input("Server URL or local command", placeholder="https://mcp.example.com/mcp or python -m weather_mcp")
                mcp_tool_name = st.text_input("MCP tool name", placeholder="get_forecast")
                auth_env_var = st.text_input("Auth environment variable name (optional)", placeholder="WEATHER_MCP_TOKEN")
            else:
                function_code = st.text_area("Python function code", value='def run(input_data):\n    """Implement this tool when a trusted runtime is connected."""\n    return {"status": "not_implemented"}', height=180, help="Stored as code only. This application does not import or execute it.")
            save_tool = st.form_submit_button("Save tool definition", use_container_width=True)

        if save_tool:
            tool_errors = []
            if not tool_name.strip() or not tool_purpose.strip():
                tool_errors.append("Enter a tool name and purpose.")
            if not input_schema.strip() or not output_schema.strip():
                tool_errors.append("Define both the input and output contracts.")
            if tool_type == "REST API":
                parsed_endpoint = urlparse(api_endpoint.strip())
                if parsed_endpoint.scheme not in {"https", "http"} or not parsed_endpoint.netloc:
                    tool_errors.append("Enter a complete HTTP or HTTPS API endpoint.")
            elif tool_type == "MCP server/tool":
                if not mcp_server_id.strip() or not mcp_endpoint.strip() or not mcp_tool_name.strip():
                    tool_errors.append("Enter an MCP server ID, server URL/command, and tool name.")
                if mcp_transport in {"Streamable HTTP", "SSE"} and not mcp_endpoint.strip().startswith(("https://", "http://")):
                    tool_errors.append("HTTP and SSE MCP transports need an HTTP or HTTPS server URL.")
            else:
                try:
                    parsed_code = ast.parse(function_code)
                    if not any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in parsed_code.body):
                        tool_errors.append("Add at least one Python function definition.")
                except SyntaxError as error:
                    tool_errors.append(f"Python syntax error on line {error.lineno}: {error.msg}.")

            if tool_errors:
                for error in tool_errors:
                    st.error(error)
            else:
                tool_record = {
                    "id": unique_record_id(tool_name, saved_tools),
                    "name": tool_name.strip(),
                    "type": tool_type,
                    "purpose": tool_purpose.strip(),
                    "input_schema": input_schema.strip(),
                    "output_schema": output_schema.strip(),
                    "endpoint": api_endpoint.strip() if tool_type == "REST API" else "",
                    "http_method": api_method if tool_type == "REST API" else "",
                    "server_id": mcp_server_id.strip() if tool_type == "MCP server/tool" else "",
                    "transport": mcp_transport if tool_type == "MCP server/tool" else "",
                    "mcp_endpoint": mcp_endpoint.strip() if tool_type == "MCP server/tool" else "",
                    "mcp_tool_name": mcp_tool_name.strip() if tool_type == "MCP server/tool" else "",
                    "auth_env_var": auth_env_var.strip(),
                    "function_code": function_code.strip() if tool_type == "Python function" else "",
                    "status": "Local definition · not connected or executed",
                    "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                }
                saved_tools.append(tool_record)
                save_local_catalog(TOOLS_PROFILE_PATH, saved_tools)
                st.success(f"Saved **{tool_record['name']}** to Tools College. It is available for assignment to new agent profiles.")

# =========================================================================
# USER MANAGEMENT: local workspace profiles and role descriptions
# =========================================================================
with user_management_popover:
    user_profiles = load_local_catalog(USER_PROFILE_PATH)
    st.markdown("## User Management")
    st.caption("Manage named profiles for this local demonstration workspace.")
    st.info("These profiles are local metadata only. The app does not authenticate users or enforce role-based access control.")

    enabled_count = sum(1 for profile in user_profiles if profile.get("enabled", True))
    metric_cols = st.columns(3)
    metric_cols[0].metric("Profiles", len(user_profiles))
    metric_cols[1].metric("Enabled", enabled_count)
    metric_cols[2].metric("Disabled", len(user_profiles) - enabled_count)

    roles = ["Admin", "Operator", "Analyst", "Viewer"]
    with st.expander("Role descriptions", expanded=False):
        st.dataframe(pd.DataFrame([
            {"Role": "Admin", "Intended access": "Manage profiles and workspace configuration"},
            {"Role": "Operator", "Intended access": "Run scenarios and review dispatch recommendations"},
            {"Role": "Analyst", "Intended access": "Review trends, run history, and evaluation results"},
            {"Role": "Viewer", "Intended access": "Read dashboard and reports"},
        ]), hide_index=True, use_container_width=True)

    create_user_tab, manage_users_tab = st.tabs(["Create profile", "Manage profiles"])
    with create_user_tab:
        st.markdown("### Add a workspace profile")
        with st.form("create_user_profile", clear_on_submit=True):
            name_col, username_col = st.columns(2)
            with name_col:
                display_name = st.text_input("Display name", placeholder="e.g. Alex Morgan")
            with username_col:
                username = st.text_input("Username", placeholder="e.g. alex.morgan")
            team = st.text_input("Team", placeholder="e.g. Grid Operations")
            role = st.selectbox("Role", roles, index=1)
            enabled = st.checkbox("Profile enabled", value=True)
            create_profile = st.form_submit_button("Create profile", use_container_width=True)

        if create_profile:
            normalized_username = username.strip().casefold()
            if not display_name.strip() or not normalized_username:
                st.error("Enter both a display name and username.")
            elif any(str(profile.get("username", "")).casefold() == normalized_username for profile in user_profiles):
                st.error("That username already exists in this local profile list.")
            else:
                user_profiles.append({
                    "id": unique_record_id(normalized_username, user_profiles),
                    "display_name": display_name.strip(),
                    "username": normalized_username,
                    "team": team.strip() or "Unassigned",
                    "role": role,
                    "enabled": enabled,
                    "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                })
                save_local_catalog(USER_PROFILE_PATH, user_profiles)
                st.success(f"Created local profile for **{display_name.strip()}**.")

    with manage_users_tab:
        if not user_profiles:
            st.info("No profiles yet. Create one to populate this list.")
        else:
            st.dataframe(pd.DataFrame([
                {
                    "Name": profile.get("display_name", "Unnamed"),
                    "Username": profile.get("username", ""),
                    "Team": profile.get("team", "Unassigned"),
                    "Role": profile.get("role", "Viewer"),
                    "Status": "Enabled" if profile.get("enabled", True) else "Disabled",
                }
                for profile in user_profiles
            ]), hide_index=True, use_container_width=True)
            for index, profile in enumerate(user_profiles):
                with st.expander(f"{profile.get('display_name', 'Unnamed')} · @{profile.get('username', '')}"):
                    with st.form(f"edit_user_profile_{profile.get('id', index)}"):
                        edit_name = st.text_input("Display name", value=profile.get("display_name", ""))
                        edit_team = st.text_input("Team", value=profile.get("team", "Unassigned"))
                        current_role = profile.get("role", "Viewer")
                        edit_role = st.selectbox("Role", roles, index=roles.index(current_role) if current_role in roles else 3)
                        edit_enabled = st.checkbox("Profile enabled", value=profile.get("enabled", True))
                        save_profile = st.form_submit_button("Save changes", use_container_width=True)
                    if save_profile:
                        profile.update({
                            "display_name": edit_name.strip() or profile.get("display_name", "Unnamed"),
                            "team": edit_team.strip() or "Unassigned",
                            "role": edit_role,
                            "enabled": edit_enabled,
                            "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                        })
                        save_local_catalog(USER_PROFILE_PATH, user_profiles)
                        st.success("Profile updated.")

# =========================================================================
# SYSTEM CONFIGURATION: model and data status
with tab_overview:
    st.markdown("## System configuration")
    st.caption("Runtime and data-source status for this local operator console.")

    status_cols = st.columns(4)
    status_cols[0].metric("Operating mode", "Simulation")
    status_cols[1].metric("Dispatch engine", "HiGHS LP")
    status_cols[2].metric("Weather input", "RGB heuristic")
    status_cols[3].metric("Persistence", "Local SQLite")

    st.markdown("### Connected services")
    st.dataframe(pd.DataFrame([
        {"Service": "Scenario telemetry", "State": "Available", "Source": "Seeded 96-step model"},
        {"Service": "Dispatch optimizer", "State": "Available", "Source": "Local linear optimization"},
        {"Service": "Weather image analysis", "State": "Prototype", "Source": "Synthetic or uploaded RGB image"},
        {"Service": "SCADA / field equipment", "State": "Not connected", "Source": "No live commands or telemetry"},
        {"Service": "Wholesale market", "State": "Not connected", "Source": "Modeled spot-price profile"},
    ]), hide_index=True, use_container_width=True)

    st.markdown("### Data and validation")
    st.write("The dashboard reads the local 96-interval scenario run. Dispatch actions are recommendations recorded locally; no control command leaves this application.")
    st.write("Image quality metrics describe the uploaded raster signal. Weather detections have not been validated against labeled observations.")

# TAB 1: Dispatch & scenario control

# =========================================================================
with tab1:
    st.markdown("### Dispatch & scenario control")
    st.caption("Select a modeled operating condition and calculate a dispatch recommendation. Results remain inside this simulation.")

    # Operator scenario selection and dispatch calculation
    st.markdown("#### Scenario")
    
    scenario_catalog = {
        "☀️ Normal operating conditions": {
            "step": 24, "storm": False, "neg_price": False, "outage": False, "congestion": False, "surge": 0.0,
            "title": "Baseline Diurnal Merit Dispatch",
            "challenge": "Manage standard mid-morning solar ramp and baseload industrial demand while preserving battery buffer.",
            "agent_response": "Forecast agent models laminar clear-sky insolation; Market agent identifies nominal LMP ($48/MWh); Grid agent confirms voltage/frequency within IEEE 1547 envelopes.",
            "solver_goal": "Dispatches zero-marginal-cost solar/wind at 100% capacity; exports economic surplus to wholesale grid for profit."
        },
        "☁️ Reduced solar output": {
            "step": 36, "storm": False, "neg_price": False, "outage": False, "congestion": False, "surge": 0.0,
            "title": "Sudden Cloud Front Attenuation Over Solar Basin",
            "challenge": "Rapid cloud deck causes sudden generation drop of ~140 MW across 5 solar plants, threatening supply shortfall and industrial under-frequency trip.",
            "agent_response": "Forecast Agent extracts Doppler radar cloud opacity (0.88, 48 dBZ) and derates solar capacity to 22%; Grid Reliability Agent detects reserve depletion.",
            "solver_goal": "Instantly discharges BESS-01 bulk storage to replace solar shortfall; ramps grid imports to maintain continuous industrial load without load shedding."
        },
        "💨 Wind cut-out": {
            "step": 60, "storm": True, "neg_price": False, "outage": False, "congestion": False, "surge": 0.0,
            "title": "Convective Squall & Wind Turbine Safety Cut-Out",
            "challenge": "Severe aerodynamic storm gusts exceed the 25.0 m/s safety cut-out limit, forcing 250 MW of wind turbines to trip/feather simultaneously.",
            "agent_response": "Forecast Agent flags CRITICAL convective squall front; Grid Agent initiates BAL-001 synthetic inertia and locks turbine blade pitch (MNT_GUST_LOCKOUT).",
            "solver_goal": "Fast-ramps BESS-02 Titanate peaker within milliseconds; imports intertie power; queues post-storm field inspection teams."
        },
        "📈 High spot price": {
            "step": 72, "storm": False, "neg_price": False, "outage": False, "congestion": False, "surge": 0.0,
            "title": "Wholesale Locational Marginal Price (LMP) Surge",
            "challenge": "Wholesale market clearing price surges from $48/MWh to $285/MWh. Consuming grid power is economically catastrophic; exporting power is extremely lucrative.",
            "agent_response": "Market Trading Agent flags price surge (priority ELEVATED); Orchestrator raises commercial profit weight to 55%; Grid Agent protects battery minimum buffer.",
            "solver_goal": "Maximizes battery discharge into the 500 kV intertie to capture revenue; triggers contractual Smelter Demand Response (curtails 25 MW) to avoid purchasing peak power; defers routine maintenance."
        },
        "📉 Negative spot price": {
            "step": 48, "storm": False, "neg_price": True, "outage": False, "congestion": False, "surge": 0.0,
            "title": "Regional Over-Generation & Negative Wholesale Pricing",
            "challenge": "Wholesale spot price drops to -$18.50/MWh due to regional renewable over-generation. Continued grid injection causes cash penalties (paying the grid to take power).",
            "agent_response": "Market Agent issues CRITICAL mandate to suppress wholesale export; Orchestrator elevates profit weight to 45% and curtailment penalty to 25%.",
            "solver_goal": "Suppresses all wholesale intertie export to 0.0 MW; commands maximum BESS charging to absorb free/negative energy; curtails surplus solar inverters and wind pitch to protect commercial balance."
        },
        "🔋 BESS-01 unavailable": {
            "step": 66, "storm": False, "neg_price": False, "outage": True, "congestion": False, "surge": 0.0,
            "title": "Bulk Battery Storage Unplanned Outage (BESS-01 Trip)",
            "challenge": "BESS-01 (400 MWh bulk storage) suffers an unplanned thermal runaway alarm and goes offline, removing 100 MW of flexible capacity.",
            "agent_response": "Grid Reliability Agent detects asset status change (is_available=False); dispatches emergency BMS thermal inspection crew (MNT_DISPATCH_CREW).",
            "solver_goal": "Transfers all balancing responsibility to BESS-02 Titanate peaker; coordinates additional economic grid imports to ensure uninterrupted demand service."
        },
        "🌐 Intertie congestion": {
            "step": 80, "storm": False, "neg_price": False, "outage": False, "congestion": True, "surge": 0.0,
            "title": "500 kV Intertie Reaches Thermal MVA Line Capacity",
            "challenge": "Transmission corridor reaches thermal capacity limit; line export rating is derated by 50% (from 200 MW to 100 MW) to prevent transmission line sag/flashover.",
            "agent_response": "Grid Reliability Agent flags corridor congestion; Market Agent redirects surplus generation away from intertie.",
            "solver_goal": "Caps wholesale intertie export at 100 MW; redirects excess solar and wind generation into charging BESS-01 and BESS-02; curtails excess generation to protect corridor integrity."
        },
        "🏭 Industrial load increase": {
            "step": 86, "storm": False, "neg_price": False, "outage": False, "congestion": False, "surge": 35.0,
            "title": "Unforecasted Heavy Industrial Load Surge (+35 MW)",
            "challenge": "MegaTech Smelter unexpectedly ramps production, surging load by +35 MW above baseline (from 155 MW to 190 MW).",
            "agent_response": "Forecast Agent notes demand spike; Grid Reliability Agent audits spinning reserve margins.",
            "solver_goal": "Defers flexible PEM green hydrogen electrolyzer production (shifts load to off-peak); increases battery discharge and grid imports; triggers contractual Demand Response curtailment."
        }
    }

    selected_scenario_key = st.selectbox(
        "Operating scenario",
        list(scenario_catalog.keys()),
        index=0
    )

    sc_info = scenario_catalog[selected_scenario_key]

    st.info(f"**Selected scenario:** {sc_info['title']} · **Interval:** {sc_info['step']} · Dispatch is calculated from modeled inputs.")

    # Manual Overrides & Fine-Tuning Expander
    with st.expander("⚙️ Scenario inputs and objective weights", expanded=False):
        fo_col1, fo_col2, fo_col3 = st.columns([1.5, 1.5, 1.2])
        scenario_data = st.session_state.sim_engine.generate_scenario_profile()
        default_step = sc_info["step"]

        with fo_col1:
            step_select = st.slider("Dispatch Interval (00:00 to 23:45)", 0, 95, default_step)
            time_str = f"{int(step_select / 4):02d}:{int((step_select % 4) * 15):02d}"
            st.write(f"⏱️ **Interval:** `{time_str}` (#{step_select})")

        with fo_col2:
            step_env = scenario_data[step_select]
            st.write(f"🏷️ **Environmental Baseline:** `{step_env['event_tag']}`")
            st.write(f"💲 **Wholesale Spot LMP:** `${step_env['spot_price']:.2f} / MWh`")

        with fo_col3:
            manual_storm = st.checkbox("Trigger Storm Cut-Out (>25m/s)", value=sc_info["storm"])
            manual_neg_price = st.checkbox("Force Negative Pricing", value=sc_info["neg_price"])
            manual_bess_outage = st.checkbox("Trip BESS-01 (Outage)", value=sc_info["outage"])
            manual_congested = st.checkbox("Congest 500kV Corridor", value=sc_info["congestion"])

        st.markdown("##### ⚖️ Dynamic Pareto Optimality Weights")
        pw_c1, pw_c2, pw_c3, pw_c4, pw_c5 = st.columns(5)
        w_profit = pw_c1.slider("Market Arbitrage", 0.0, 1.0, 0.35, 0.05)
        w_carbon = pw_c2.slider("Carbon Abatement", 0.0, 1.0, 0.25, 0.05)
        w_reliability = pw_c3.slider("Grid Reliability", 0.0, 1.0, 0.20, 0.05)
        w_battery = pw_c4.slider("Battery Health", 0.0, 1.0, 0.10, 0.05)
        w_curtail = pw_c5.slider("Curtailment Penalty", 0.0, 1.0, 0.10, 0.05)

    # Prepare Portfolio State
    scenario_data = st.session_state.sim_engine.generate_scenario_profile()
    active_step_idx = step_select
    time_str = f"{int(active_step_idx / 4):02d}:{int((active_step_idx % 4) * 15):02d}"
    step_env = scenario_data[active_step_idx]

    current_portfolio = UtilityPortfolioState()
    current_portfolio.market.spot_price_per_mwh = -18.5 if (manual_neg_price or sc_info["neg_price"] or step_env["spot_price"] < 0) else (285.0 if sc_info["step"] == 72 else step_env["spot_price"])
    current_portfolio.market.projected_price_next_hour = scenario_data[min(active_step_idx + 4, 95)]["spot_price"]
    current_portfolio.grid.transmission_congested = manual_congested or sc_info["congestion"] or step_env["transmission_congested"]

    # Asset availability
    bess1_is_avail = not (manual_bess_outage or sc_info["outage"] or not step_env["bess1_available"])
    current_portfolio.bess_systems[0].is_available = bess1_is_avail
    current_portfolio.bess_systems[0].status = AssetStatus.OPERATIONAL if bess1_is_avail else AssetStatus.MAINTENANCE

    # Industrial demand surge
    if sc_info["surge"] > 0:
        current_portfolio.industrial_consumers[0].base_load_mw = 70.0 + sc_info["surge"]

    for sol in current_portfolio.solar_farms:
        sol.cloud_attenuation_factor = 0.22 if sc_info["step"] == 36 else step_env["solar_factor"]
    for wnd in current_portfolio.wind_farms:
        wnd.wind_speed_mps = 26.8 if (manual_storm or sc_info["storm"] or step_env["storm_alert"]) else step_env["wind_speed"]

    # Generate or retrieve radar image
    dispatch_inputs = (
        selected_scenario_key, active_step_idx, manual_storm, manual_neg_price,
        manual_bess_outage, manual_congested, w_profit, w_carbon,
        w_reliability, w_battery, w_curtail
    )
    if st.session_state.get("last_dispatch_inputs") != dispatch_inputs:
        radar_img = st.session_state.orchestrator.vision.generate_radar_feed(
            cloud_density=0.88 if sc_info["step"] == 36 else step_env["cloud_index"],
            storm_front=manual_storm or sc_info["storm"] or step_env["storm_alert"],
            interval_idx=active_step_idx
        )
        decision = st.session_state.orchestrator.orchestrate(
            portfolio=current_portfolio,
            interval_idx=active_step_idx,
            clock_time=time_str,
            radar_image_path=radar_img,
            event_tag=sc_info["title"],
            manual_pareto_weights={
                "profit": w_profit,
                "carbon": w_carbon,
                "reliability": w_reliability,
                "battery_health": w_battery,
                "curtailment": w_curtail,
            },
        )
        st.session_state.last_dispatch_inputs = dispatch_inputs
        st.session_state.last_dispatch_decision = decision
        st.session_state.last_dispatch_radar = radar_img
    else:
        decision = st.session_state.last_dispatch_decision
        radar_img = st.session_state.last_dispatch_radar

    dispatch_res = decision["dispatch_result"]

    # Telemetry KPI row
    st.markdown("---")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("☀️ Solar Generation", f"{dispatch_res.solar_generation_mw:.1f} MW")
    k2.metric("💨 Wind Generation", f"{dispatch_res.wind_generation_mw:.1f} MW")
    bess_net = (dispatch_res.bess1_discharge_mw + dispatch_res.bess2_discharge_mw) - (dispatch_res.bess1_charge_mw + dispatch_res.bess2_charge_mw)
    k3.metric("🔋 BESS Net Flow", f"{bess_net:+.1f} MW")
    grid_net = dispatch_res.grid_export_mw - dispatch_res.grid_import_mw
    k4.metric("🌐 Grid Flow", f"{grid_net:+.1f} MW")
    k5.metric("🏭 Served Demand", f"{dispatch_res.served_demand_mw:.1f} MW")
    k6.metric("💲 Interval Yield", f"${dispatch_res.market_revenue_cost_usd:+.2f}")

    # Two column layout: Multimodal Vision + Multi-Agent Deliberation
    disp_col1, disp_col2 = st.columns([1, 1.4])

    with disp_col1:
        st.markdown("#### Weather image input (heuristic)")
        if os.path.exists(radar_img):
            st.image(radar_img, caption=f"Synthetic weather image · {time_str}", use_container_width=True)
        
        rep: MultimodalPerceptionReport = st.session_state.orchestrator.vision.process_radar_image(radar_img)
        st.info(f"""
            **Radar Feature Telemetry:**
            * Regional Cloud Opacity Index: `{rep.cloud_opacity_index:.2f}`
            * Solar Fleet Attenuation Factor: `{rep.solar_derating_factor:.2f}`
            * Convective Storm Alert: `{'ALERT' if rep.storm_alert_active else 'NOMINAL'}`
            * Peak Reflectivity: `{rep.peak_reflectivity_dbz:.1f} dBZ`
            * Image Input Quality (heuristic, not accuracy): `{rep.input_quality_score*100:.0f}%`
        """)

    with disp_col2:
        st.markdown("#### Dispatch reasoning")
        for agent_msg in decision["agent_deliberations"]:
            badge_class = "agent-card-critical" if agent_msg.priority_level == "CRITICAL" else ("agent-card-elevated" if agent_msg.priority_level == "ELEVATED" else "agent-card-normal")
            st.markdown(f"""
                <div class="{badge_class}">
                    <strong>💬 {agent_msg.agent_name} [{agent_msg.priority_level}]</strong><br>
                    <small style="color: #9ca3af;">{agent_msg.domain}</small><br>
                    <p style="margin-top: 6px; margin-bottom: 4px; font-size: 0.9rem;"><strong>Observation:</strong> {agent_msg.observation}</p>
                    <p style="margin-bottom: 2px; font-size: 0.9rem; color: #d1d5db;"><strong>Reasoning:</strong> {agent_msg.analytical_reasoning}</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.success(f"**Optimizer rationale:** {decision['trade_off_explanation']}")

    # Exact Physical Energy Conservation Proof
    st.markdown("---")
    st.markdown("#### Dispatch balance and operating limits")
    total_in = dispatch_res.solar_generation_mw + dispatch_res.wind_generation_mw + dispatch_res.bess1_discharge_mw + dispatch_res.bess2_discharge_mw + dispatch_res.grid_import_mw
    total_out = dispatch_res.served_demand_mw + dispatch_res.bess1_charge_mw + dispatch_res.bess2_charge_mw + dispatch_res.grid_export_mw
    eb_diff = abs(total_in - total_out)

    eb1, eb2, eb3 = st.columns(3)
    with eb1:
        st.markdown(f"""
            **Total Power Inflow (Generation & Injections):**
            * Solar Active Generation: `{dispatch_res.solar_generation_mw:.2f} MW`
            * Wind Active Generation: `{dispatch_res.wind_generation_mw:.2f} MW`
            * BESS Total Discharge: `{(dispatch_res.bess1_discharge_mw + dispatch_res.bess2_discharge_mw):.2f} MW`
            * Grid Import: `{dispatch_res.grid_import_mw:.2f} MW`
            * **Total Inflow:** **`{total_in:.2f} MW`**
        """)
    with eb2:
        st.markdown(f"""
            **Total Power Outflow (Demand & Absorption):**
            * Served Industrial Load: `{dispatch_res.served_demand_mw:.2f} MW`
            * BESS Total Charging: `{(dispatch_res.bess1_charge_mw + dispatch_res.bess2_charge_mw):.2f} MW`
            * Wholesale Grid Export: `{dispatch_res.grid_export_mw:.2f} MW`
            * Demand Response Curtailed: `{dispatch_res.dr_curtailed_demand_mw:.2f} MW`
            * **Total Outflow:** **`{total_out:.2f} MW`**
        """)
    with eb3:
        st.markdown(f"""
            **Mathematical Constraint Check:**
            * Imbalance &Delta;: **`{eb_diff:.4f} MW`**
            * Physical Balance Status: `{'✅ EXACT CONSERVATION' if eb_diff < 0.05 else '⚠️ IMBALANCE'}`
            * BESS-01 Next SoC: `{dispatch_res.bess1_next_soc_pct:.1f}%`
            * BESS-02 Next SoC: `{dispatch_res.bess2_next_soc_pct:.1f}%`
            * Reserve Margin: `{dispatch_res.reserve_margin_mw:.1f} MW` ({dispatch_res.grid_stress_level})
        """)

    # Categorized Executed Action Cluster (All 5 Categories)
    st.markdown("#### Recommended dispatch actions")
    if dispatch_res.action_cluster:
        act_df = pd.DataFrame(dispatch_res.action_cluster)
        st.dataframe(act_df, use_container_width=True)
    else:
        st.info("System balanced in steady state. No discrete dispatch actions required.")

# =========================================================================
# TAB: Multimodal Computer Vision Perception Laboratory
# =========================================================================
with tab_vision:
    st.markdown("### 🛰️ Weather Image Heuristic Laboratory")
    st.caption("Analyze an uploaded RGB weather image or a synthetic WSR-style illustration. The prototype is not validated for forecast accuracy.")

    v_col1, v_col2 = st.columns([1.2, 1.8])

    with v_col1:
        st.markdown("#### 📥 Upload RGB Weather Image")
        uploaded_file = st.file_uploader("Upload Doppler Radar Frame (PNG / JPG / WEBP)", type=["png", "jpg", "jpeg", "webp"])
        
        if uploaded_file is not None:
            uploaded_bytes = uploaded_file.read()
            uploaded_image = Image.open(io.BytesIO(uploaded_bytes)).convert("RGB")
            st.image(uploaded_image, caption="Uploaded Meteorological Imagery", use_container_width=True)
            v_report = st.session_state.orchestrator.vision.process_radar_image(uploaded_image)
        else:
            default_path = os.path.join(st.session_state.orchestrator.vision.storage_dir, f"radar_frame_{st.session_state.active_step:02d}.png")
            if not os.path.exists(default_path):
                default_path = st.session_state.orchestrator.vision.generate_radar_feed(interval_idx=st.session_state.active_step)
            st.image(default_path, caption=f"Active Doppler Feed (Interval #{st.session_state.active_step:02d})", use_container_width=True)
            v_report = st.session_state.orchestrator.vision.process_radar_image(default_path)

    with v_col2:
        st.markdown("#### 🔬 Computer Vision Feature Extraction Telemetry")
        st.write(f"**Perceptual Synopsis:** {v_report.perceptual_synopsis}")
        
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Cloud Optical Depth", f"{v_report.cloud_opacity_index*100:.1f}%")
        rc2.metric("Solar Basin Attenuation", f"{(1 - v_report.solar_derating_factor)*100:.1f}% Derated")
        rc3.metric("Peak Reflectivity", f"{v_report.peak_reflectivity_dbz:.1f} dBZ")

        st.markdown("#### 📍 Localized Attenuation per Renewable Asset")
        if v_report.asset_level_reports:
            asset_rows = []
            for ar in v_report.asset_level_reports:
                asset_rows.append({
                    "Asset ID": ar.asset_id,
                    "Name": ar.asset_name,
                    "Type": ar.asset_type,
                    "Available Capacity Factor": f"{ar.localized_attenuation_factor*100:.1f}%",
                    "Local Reflectivity": f"{ar.localized_reflectivity_dbz:.1f} dBZ",
                    "Hazard Alert": "⚠️ ALERT" if ar.hazard_flag else "✅ NOMINAL"
                })
            st.dataframe(pd.DataFrame(asset_rows), use_container_width=True)
        else:
            st.info("No localized asset coordinates mapped for external frame.")

# =========================================================================
# TAB 2: 24-Hour Diurnal Telemetry Analytics (F3 Multi-Period)
# =========================================================================
with tab2:
    st.markdown("### 24-hour operating trends")
    st.caption("Modeled generation, demand, storage, grid exchange, and market price over 96 intervals.")

    df = st.session_state.sim_data

    # Top Cumulative KPIs
    tot_gen = df["total_renewables_mw"].sum() * 0.25
    tot_curt = df["curtailed_mw"].sum() * 0.25
    tot_rev = df["cumulative_profit_usd"].iloc[-1]
    tot_co2 = df["cumulative_carbon_tons"].iloc[-1]

    ck1, ck2, ck3, ck4, ck5 = st.columns(5)
    ck1.metric("24h Net Financial Yield", f"${tot_rev:,.2f}")
    ck2.metric("Total Clean Generation", f"{tot_gen:,.1f} MWh")
    ck3.metric("Carbon Emissions Avoided", f"{tot_co2:,.1f} t CO2")
    ck4.metric("Renewable Curtailment", f"{tot_curt:,.1f} MWh")
    ck5.metric("Avg Optimality Index", f"{df['optimality_score'].mean():.1f} / 100")

    # Plot 1: Energy Balance Stacked Area Chart
    fig_balance = go.Figure()
    fig_balance.add_trace(go.Scatter(x=df["time"], y=df["solar_gen_mw"], name="Solar Generation (MW)", fill='tozeroy', line=dict(color="#f59e0b")))
    fig_balance.add_trace(go.Scatter(x=df["time"], y=df["wind_gen_mw"], name="Wind Generation (MW)", fill='tonexty', line=dict(color="#10b981")))
    fig_balance.add_trace(go.Scatter(x=df["time"], y=df["served_demand_mw"], name="Industrial Load (MW)", line=dict(color="#ef4444", width=2.5, dash='dash')))
    fig_balance.add_trace(go.Scatter(x=df["time"], y=df["grid_export_mw"], name="Grid Export (MW)", line=dict(color="#3b82f6", width=2)))
    fig_balance.add_trace(go.Scatter(x=df["time"], y=df["grid_import_mw"], name="Grid Import (MW)", line=dict(color="#8b5cf6", width=2)))

    fig_balance.update_layout(
        title="24-Hour Industrial Energy Balance Profile: Generation, Demand & Grid Intertie",
        xaxis_title="Time of Day (15-min intervals)",
        yaxis_title="Power (MW)",
        hovermode="x unified",
        template="plotly_dark",
        height=380,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_balance, use_container_width=True)

    # Plot 2 & 3: BESS SoC Trajectory & Spot Price Arbitrage
    bcol1, bcol2 = st.columns(2)
    with bcol1:
        fig_bess = go.Figure()
        fig_bess.add_trace(go.Scatter(x=df["time"], y=df["bess1_soc_pct"], name="BESS-01 Bulk LFP (400 MWh) SoC %", line=dict(color="#06b6d4", width=2)))
        fig_bess.add_trace(go.Scatter(x=df["time"], y=df["bess2_soc_pct"], name="BESS-02 Peaker LTO (100 MWh) SoC %", line=dict(color="#ec4899", width=2)))
        fig_bess.add_hline(y=10.0, line_dash="dot", line_color="#ef4444", annotation_text="Min Buffer (10%)")
        fig_bess.add_hline(y=95.0, line_dash="dot", line_color="#f59e0b", annotation_text="Max Buffer (95%)")
        fig_bess.update_layout(
            title="BESS State of Charge (SoC %) Electrochemical Envelopes",
            xaxis_title="Time",
            yaxis_title="State of Charge (%)",
            template="plotly_dark",
            height=320,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_bess, use_container_width=True)

    with bcol2:
        fig_mkt = go.Figure()
        fig_mkt.add_trace(go.Scatter(x=df["time"], y=df["spot_price"], name="Spot Price ($/MWh)", line=dict(color="#f97316", width=2)))
        fig_mkt.add_trace(go.Bar(x=df["time"], y=df["bess_net_flow_mw"], name="BESS Net Flow (MW)", marker_color="#10b981", opacity=0.6))
        fig_mkt.add_hline(y=0.0, line_color="gray")
        fig_mkt.update_layout(
            title="Wholesale Spot Price vs Battery Power Flow (+Discharge / -Charge)",
            xaxis_title="Time",
            yaxis_title="Price ($/MWh) / Power Flow (MW)",
            template="plotly_dark",
            height=320,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_mkt, use_container_width=True)

    # Scenario event log
    st.markdown("#### Scenario event log")
    events = df[df["event"] != "Routine Operations"][["time", "event", "spot_price", "bess_net_flow_mw", "grid_stress", "trade_off_explanation"]]
    st.dataframe(events, use_container_width=True)

    # Export Telemetry CSV
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    st.download_button(
        label="📥 Download Complete 24h Operational Run (CSV)",
        data=csv_buf.getvalue(),
        file_name=f"accenture_dispatch_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# =========================================================================
# TAB 3: Physical Asset Registry
# =========================================================================
with tab3:
    st.markdown("### 🗺️ Physical Utility Asset Registry (IEC 61850 & DNP3 Tagged)")
    st.markdown("Modeled portfolio parameters used by the local dispatch simulation:")

    p = st.session_state.portfolio

    r1, r2 = st.columns(2)
    with r1:
        st.markdown("#### ☀️ 5 Solar Farms (230 MW Total Nameplate)")
        sol_data = [{"ID": s.id, "Name": s.name, "Capacity": f"{s.capacity_mw} MW", "Location": s.location, "IEC Tag": s.iec61850_tag, "Inverter Temp": f"{s.inverter_temperature_c}°C", "Status": s.status.value} for s in p.solar_farms]
        st.dataframe(pd.DataFrame(sol_data), use_container_width=True)

        st.markdown("#### 💨 3 Wind Farms (250 MW Total Nameplate)")
        wnd_data = [{"ID": w.id, "Name": w.name, "Capacity": f"{w.capacity_mw} MW", "Cut-in": f"{w.cut_in_speed} m/s", "Cut-out": f"{w.cut_out_speed} m/s", "IEC Tag": w.iec61850_tag, "Status": w.status.value} for w in p.wind_farms]
        st.dataframe(pd.DataFrame(wnd_data), use_container_width=True)

    with r2:
        st.markdown("#### 🔋 2 Battery Storage Facilities (150 MW / 500 MWh)")
        bess_data = [{"ID": b.id, "Name": b.name, "Power": f"{b.power_rating_mw} MW", "Energy": f"{b.energy_capacity_mwh} MWh", "Chemistry": b.chemistry, "C-Rate": b.c_rate, "Efficiency": f"{b.roundtrip_efficiency*100:.0f}%", "Status": b.status.value} for b in p.bess_systems]
        st.dataframe(pd.DataFrame(bess_data), use_container_width=True)

        st.markdown("#### 🏭 Heavy Industrial Consumers (Demand Response & Shiftable Loads)")
        ind_data = [{"ID": ind.id, "Name": ind.name, "Type": ind.facility_type, "Baseload": f"{ind.base_load_mw} MW", "Shiftable": f"{ind.flexible_shiftable_mw} MW", "Interruptible DR": f"{ind.interruptible_mw} MW", "DR Tariff": f"${ind.dr_incentive_rate_mwh}/MWh"} for ind in p.industrial_consumers]
        st.dataframe(pd.DataFrame(ind_data), use_container_width=True)

# =========================================================================
# TAB 4: SCADA Database & Audit Trail
# =========================================================================
with tab4:
    st.markdown("### 📜 Local Simulation Database & Audit Trail")
    st.caption("Local dispatch simulation and audit records stored in `storage/orchestrator.db`; this is not a live SCADA historian.")

    db_records = st.session_state.db.get_recent_telemetry(limit=48)
    if db_records:
        rec_df = pd.DataFrame(db_records)
        display_cols = ["timestamp", "interval_idx", "clock_time", "spot_price_usd_mwh", "total_renewable_mw", "served_demand_mw", "bess1_soc_pct", "bess2_soc_pct", "grid_export_mw", "grid_import_mw", "interval_net_financial_usd", "grid_stress_level", "event_tag"]
        st.dataframe(rec_df[display_cols], use_container_width=True)
    else:
        st.info("No records in database yet. Run an interval or simulation to populate.")

# =========================================================================
# TAB EVALUATION: Autonomous Agent Evaluation & Benchmark Audit Station
# =========================================================================
with tab_eval:
    st.markdown("### 🏆 Autonomous Multi-Agent Evaluation & Regulatory Audit Station")
    st.caption("Independent compliance, physics, and economic auditor evaluating output quality, constraint satisfaction, and Pareto trade-off optimality across all 4 operational agents.")

    # 1. Google Gemini LLM Connection & Environment Status Banner
    gemini_client = get_gemini_client()
    col_llm1, col_llm2, col_llm3 = st.columns([2, 1, 1])

    with col_llm1:
        if gemini_client.is_configured:
            masked_key = gemini_client.api_key[:6] + "..." + gemini_client.api_key[-4:]
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 14px;">
                <strong style="color: #34d399;">🟢 Google Gemini LLM API Connected</strong><br>
                <span style="font-size: 0.88rem; color: #d1d5db;">
                    Active Model: <code>{gemini_client.model}</code> | Ingested via: <code>.env</code><br>
                    Key Signature: <code>{masked_key}</code>
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Google Gemini API key not found in `.env`. Running with deterministic rule evaluation engine.")

    with col_llm2:
        if st.button("🔌 Ping Gemini Connection", use_container_width=True):
            with st.spinner("Connecting to Google Generative Language API..."):
                ping_res = gemini_client.verify_connection()
                if ping_res.get("connected"):
                    st.success(f"✅ Connected! {ping_res.get('available_models_count')} models available.")
                else:
                    st.error(f"❌ Connection error: {ping_res.get('message')}")

    with col_llm3:
        use_gemini_audit = st.checkbox("Generate Gemini AI Audit Narrative", value=gemini_client.is_configured)

    st.markdown("---")

    # 2. Live Audit Evaluation of Current Dispatch State
    st.markdown("#### 🔍 Dispatch Evaluation Scorecard (Selected Simulation Interval)")
    eval_agent = AuditEvaluationAgent(gemini_client=gemini_client)

    if 'last_dispatch_result' in st.session_state and 'portfolio' in st.session_state:
        cur_portfolio = st.session_state.portfolio
        cur_dispatch = st.session_state.last_dispatch_result
        cur_deliberations = st.session_state.get('last_agent_messages', [])
        cur_scenario = st.session_state.get('active_scenario_title', 'Operational Interval')

        with st.spinner("AGT-04-EVAL auditing dispatch telemetry..."):
            scorecard = eval_agent.evaluate_interval(
                portfolio=cur_portfolio,
                dispatch_result=cur_dispatch,
                agent_deliberations=cur_deliberations,
                scenario_name=cur_scenario,
                use_llm_narrative=use_gemini_audit
            )

        # Top Executive Summary KPIs
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric("Overall Auditor Grade", scorecard.overall_grade)
        with kpi2:
            st.metric("System Composite Score", f"{scorecard.system_composite_score:.1f} / 100")
        with kpi3:
            st.metric("Kirchhoff Energy Balance", f"Δ = {scorecard.orchestrator_metrics.energy_balance_error_mw:.4f} MW", delta="Exact Physics" if scorecard.orchestrator_metrics.energy_balance_error_mw < 0.05 else "Imbalance")
        with kpi4:
            st.metric("Grid Safety Violations", f"{scorecard.reliability_metrics.thermal_line_violations_count + scorecard.reliability_metrics.bess_soc_violations_count} breaches", delta="100% Compliant" if scorecard.compliance_passed else "Violations", delta_color="normal" if scorecard.compliance_passed else "inverse")

        # Per-Agent Quantitative Metrics Radar
        st.markdown("##### 📊 Agent-by-Agent Performance Indicators")
        col_ag1, col_ag2, col_ag3, col_ag4 = st.columns(4)

        with col_ag1:
            st.markdown(f"**🌦️ AGT-01-METEO (Forecast)**")
            if scorecard.forecast_metrics.ground_truth_available:
                st.progress(min(1.0, scorecard.forecast_metrics.composite_forecast_score / 100.0))
                st.caption(f"Score: **{scorecard.forecast_metrics.composite_forecast_score:.1f}/100**")
                st.markdown(f"""
                - **Irradiance MAE:** `{scorecard.forecast_metrics.irradiance_mae:.1f} W/m²`
                - **Wind RMSE:** `{scorecard.forecast_metrics.wind_speed_rmse:.2f} m/s`
                - **Cloud CV Accuracy:** `{scorecard.forecast_metrics.cloud_attenuation_accuracy:.1f}%`
                - **Storm Alert F1:** `Not scored (labeled storm outcomes unavailable)`
                """)
            else:
                st.info("Forecast accuracy is not scored until measured solar and wind outcomes are supplied.")

        with col_ag2:
            st.markdown(f"**💹 AGT-02-MRKT (Market)**")
            st.progress(min(1.0, scorecard.market_metrics.composite_market_score / 100.0))
            st.caption(f"Score: **{scorecard.market_metrics.composite_market_score:.1f}/100**")
            st.markdown(f"""
            - **Arbitrage Efficiency:** `Not scored (requires multi-interval benchmark)`
            - **Negative Price Guard:** `{scorecard.market_metrics.negative_pricing_suppression_rate:.1f}%`
            - **$35 Hurdle Adherence:** `{scorecard.market_metrics.degradation_hurdle_compliance:.1f}%`
            - **DR Revenue:** `${scorecard.market_metrics.dr_revenue_captured_usd:.2f}`
            """)

        with col_ag3:
            st.markdown(f"**🛡️ AGT-03-GRID (Reliability)**")
            st.progress(min(1.0, scorecard.reliability_metrics.composite_reliability_score / 100.0))
            st.caption(f"Score: **{scorecard.reliability_metrics.composite_reliability_score:.1f}/100**")
            st.markdown(f"""
            - **NERC BAL-001 Rate:** `{scorecard.reliability_metrics.nerc_bal001_compliance_rate:.1f}%`
            - **Thermal Overloads:** `{scorecard.reliability_metrics.thermal_line_violations_count}`
            - **SoC Envelope Breaches:** `{scorecard.reliability_metrics.bess_soc_violations_count}`
            - **Reserve Margin:** `{scorecard.reliability_metrics.spinning_reserve_margin_mw:.1f} MW`
            """)

        with col_ag4:
            st.markdown(f"**⚡ AGT-00-EXEC (Orchestrator)**")
            st.progress(min(1.0, scorecard.orchestrator_metrics.composite_orchestration_score / 100.0))
            st.caption(f"Score: **{scorecard.orchestrator_metrics.composite_orchestration_score:.1f}/100**")
            st.markdown(f"""
            - **Kirchhoff Error:** `{scorecard.orchestrator_metrics.energy_balance_error_mw:.4f} MW`
            - **HiGHS LP Status:** `{cur_dispatch.solver_status}`
            - **Action Diversity:** `{scorecard.orchestrator_metrics.action_category_coverage_rate:.1f}%`
            - **Clean Generation:** `{scorecard.orchestrator_metrics.carbon_abatement_pct:.1f}%`
            """)

        # Auditor Findings Box
        st.markdown("##### 📜 Official Audit Findings & Compliance Verification")
        for find in scorecard.audit_findings:
            if "❌" in find:
                st.error(find)
            elif "⚠️" in find:
                st.warning(find)
            elif "🤖" in find:
                st.info(find)
            else:
                st.success(find)
    else:
        st.info("Execute a dispatch cycle in the SCADA Dispatch Console (Tab 1) to inspect live interval audit metrics.")

    # 3. Multi-Scenario Stress Test Benchmark Runner
    st.markdown("---")
    st.markdown("#### 🧪 Automated Multi-Scenario Benchmark Stress Suite")
    st.caption("Scores the modeled operating scenarios against dispatch, balance, compliance, and input-data checks.")

    if st.button("🚀 Run Full 8-Scenario Benchmark Suite", type="primary", use_container_width=True):
        with st.spinner("Executing multi-scenario benchmark stress tests..."):
            runner = BenchmarkRunner(eval_agent=eval_agent)
            bench_scorecards = runner.run_all_benchmarks(use_llm_for_eval=use_gemini_audit)
            bench_df = runner.scorecards_to_dataframe(bench_scorecards)
            st.session_state['benchmark_results_df'] = bench_df

    if 'benchmark_results_df' in st.session_state:
        b_df = st.session_state['benchmark_results_df']
        st.dataframe(b_df, use_container_width=True)

        # Performance summary metrics
        b_col1, b_col2, b_col3 = st.columns(3)
        with b_col1:
            avg_score = b_df["Composite Score"].mean()
            st.metric("Mean Benchmark Score", f"{avg_score:.1f} / 100")
        with b_col2:
            pass_rate = (b_df["Safety Passed"] == "✅ PASS").mean() * 100.0
            st.metric("Safety Compliance Pass Rate", f"{pass_rate:.1f}%")
        with b_col3:
            max_err = b_df["Energy Error (MW)"].max()
            st.metric("Max Kirchhoff Error", f"{max_err:.4f} MW")

        # Download Benchmark CSV
        csv_data = b_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Official Benchmark Audit Report (CSV)",
            data=csv_data,
            file_name="grid_os_multi_agent_benchmark_report.csv",
            mime="text/csv",
            use_container_width=True
        )

# =========================================================================
# TAB 5: Centralized Agent Prompts & Configuration
# =========================================================================
with tab_prompts:
    st.markdown("### ⚙️ Centralized Agent Prompts & SCADA Directives Configuration")
    st.caption("Agent personas, system prompts, observation templates, and action rationales are configured in `backend/config/prompts.json`.")

    prompt_cfg = get_prompt_config()
    raw_prompts = prompt_cfg.raw

    st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 10px; padding: 16px; margin-bottom: 20px;">
            <strong style="color: #60a5fa;">💡 Production Architecture Note:</strong>
            <span style="color: #d1d5db; font-size: 0.95rem;">
                No prompts or reasoning strings are hardcoded in agent business logic. Every agent persona,
                observation template, alert trigger, and physical SCADA action rationale is dynamically ingested from
                the centralized configuration engine (<code>AccentureAssessment/backend/config/prompts.json</code>).
            </span>
        </div>
    """, unsafe_allow_html=True)

    # 4 Autonomous Agents Showcase
    st.markdown("#### 🤖 Autonomous Agent System Directives, Skills, Instructions & Tools")
    st.caption("Inspect the full operational charter for the Chief Orchestrator and the 3 specialized domain agents.")

    agent_tab_orch, agent_tab_fc, agent_tab_mkt, agent_tab_grid = st.tabs([
        "⚡ Chief Executive Orchestrator",
        "🌦️ Meteorological & Vision Agent",
        "💹 Wholesale Market Trading Agent",
        "🔌 Grid Reliability & Protection Agent"
    ])

    # 1. Chief Executive Orchestrator
    with agent_tab_orch:
        orch_cfg = prompt_cfg.get_agent_config("orchestrator_agent")
        st.markdown(f"### ⚡ {orch_cfg.get('agent_name')} (`{orch_cfg.get('agent_id')}`)")
        st.markdown(f"**Operational Role:** `{orch_cfg.get('role')}` | **Domain:** `{orch_cfg.get('domain')}`")
        
        st.markdown("##### 📜 Elaborate System Persona & Mission Directive")
        st.info(orch_cfg.get("system_prompt"))

        col_sk, col_ins, col_tl = st.columns(3)
        with col_sk:
            st.markdown("##### 🧠 Core Skills")
            for sk in prompt_cfg.get_skills("orchestrator_agent"):
                st.markdown(f"- {sk}")
        with col_ins:
            st.markdown("##### 📋 Step-by-Step Instructions")
            for ins in prompt_cfg.get_instructions("orchestrator_agent"):
                st.markdown(f"- {ins}")
        with col_tl:
            st.markdown("##### 🛠️ Tools & Actuators")
            for tl in prompt_cfg.get_tools("orchestrator_agent"):
                st.markdown(f"- `{tl}`")

        st.markdown("##### ⚖️ Dynamic Pareto Trade-Off Rationales")
        for sit_k, sit_v in orch_cfg.get("trade_off_rationales", {}).items():
            st.markdown(f"- **{sit_k}**: `{sit_v}`")

    # 2. Meteorological & Vision Perception Forecast Agent
    with agent_tab_fc:
        fc_cfg = prompt_cfg.get_agent_config("forecast_agent")
        st.markdown(f"### 🌦️ {fc_cfg.get('agent_name')} (`{fc_cfg.get('agent_id')}`)")
        st.markdown(f"**Operational Role:** `{fc_cfg.get('role')}` | **Domain:** `{fc_cfg.get('domain')}`")
        
        st.markdown("##### 📜 Elaborate System Persona & Mission Directive")
        st.info(fc_cfg.get("system_prompt"))

        col_sk, col_ins, col_tl = st.columns(3)
        with col_sk:
            st.markdown("##### 🧠 Core Skills")
            for sk in prompt_cfg.get_skills("forecast_agent"):
                st.markdown(f"- {sk}")
        with col_ins:
            st.markdown("##### 📋 Step-by-Step Instructions")
            for ins in prompt_cfg.get_instructions("forecast_agent"):
                st.markdown(f"- {ins}")
        with col_tl:
            st.markdown("##### 🛠️ Tools & Actuators")
            for tl in prompt_cfg.get_tools("forecast_agent"):
                st.markdown(f"- `{tl}`")

        st.markdown("##### 🔬 Computer Vision & Reasoning Template")
        st.code(fc_cfg.get("reasoning_template", ""), language="text")

    # 3. Wholesale Market Trading Agent
    with agent_tab_mkt:
        mkt_cfg = prompt_cfg.get_agent_config("market_agent")
        st.markdown(f"### 💹 {mkt_cfg.get('agent_name')} (`{mkt_cfg.get('agent_id')}`)")
        st.markdown(f"**Operational Role:** `{mkt_cfg.get('role')}` | **Domain:** `{mkt_cfg.get('domain')}`")
        
        st.markdown("##### 📜 Elaborate System Persona & Mission Directive")
        st.info(mkt_cfg.get("system_prompt"))

        col_sk, col_ins, col_tl = st.columns(3)
        with col_sk:
            st.markdown("##### 🧠 Core Skills")
            for sk in prompt_cfg.get_skills("market_agent"):
                st.markdown(f"- {sk}")
        with col_ins:
            st.markdown("##### 📋 Step-by-Step Instructions")
            for ins in prompt_cfg.get_instructions("market_agent"):
                st.markdown(f"- {ins}")
        with col_tl:
            st.markdown("##### 🛠️ Tools & Actuators")
            for tl in prompt_cfg.get_tools("market_agent"):
                st.markdown(f"- `{tl}`")

        st.markdown("##### 📈 Strategy Reasoning Templates")
        for strat_k, strat_v in mkt_cfg.get("reasoning_templates", {}).items():
            st.markdown(f"- **{strat_k}**: `{strat_v}`")

    # 4. Grid Reliability & Protection Agent
    with agent_tab_grid:
        grid_cfg = prompt_cfg.get_agent_config("grid_reliability_agent")
        st.markdown(f"### 🔌 {grid_cfg.get('agent_name')} (`{grid_cfg.get('agent_id')}`)")
        st.markdown(f"**Operational Role:** `{grid_cfg.get('role')}` | **Domain:** `{grid_cfg.get('domain')}`")
        
        st.markdown("##### 📜 Elaborate System Persona & Mission Directive")
        st.info(grid_cfg.get("system_prompt"))

        col_sk, col_ins, col_tl = st.columns(3)
        with col_sk:
            st.markdown("##### 🧠 Core Skills")
            for sk in prompt_cfg.get_skills("grid_reliability_agent"):
                st.markdown(f"- {sk}")
        with col_ins:
            st.markdown("##### 📋 Step-by-Step Instructions")
            for ins in prompt_cfg.get_instructions("grid_reliability_agent"):
                st.markdown(f"- {ins}")
        with col_tl:
            st.markdown("##### 🛠️ Tools & Actuators")
            for tl in prompt_cfg.get_tools("grid_reliability_agent"):
                st.markdown(f"- `{tl}`")

        st.markdown("##### 🚨 Simulated Alarms & Alert Templates")
        for alt_k, alt_v in grid_cfg.get("alert_templates", {}).items():
            st.markdown(f"- **{alt_k}**: `{alt_v}`")

    # Solver Action Rationales
    st.markdown("---")
    st.markdown("#### 📋 Physical SCED Dispatch Action Rationale Templates (All 5 Categories)")
    rat_c1, rat_c2 = st.columns(2)

    with rat_c1:
        st.markdown("**🔋 Battery Actions Templates:**")
        st.json(raw_prompts.get("action_rationales", {}).get("battery_actions", {}))

        st.markdown("**💹 Market Actions Templates:**")
        st.json(raw_prompts.get("action_rationales", {}).get("market_actions", {}))

        st.markdown("**☀️ Renewable Actions Templates:**")
        st.json(raw_prompts.get("action_rationales", {}).get("renewable_actions", {}))

    with rat_c2:
        st.markdown("**🏭 Demand Management Templates:**")
        st.json(raw_prompts.get("action_rationales", {}).get("demand_management", {}))

        st.markdown("**🔧 Maintenance Actions Templates:**")
        st.json(raw_prompts.get("action_rationales", {}).get("maintenance_actions", {}))

    # Raw Configuration Viewer & Download
    st.markdown("---")
    with st.expander("📄 View / Download Raw Configuration File (`backend/config/prompts.json`)", expanded=False):
        st.json(raw_prompts)
        st.download_button(
            label="📥 Download prompts.json",
            data=json.dumps(raw_prompts, indent=2),
            file_name="prompts.json",
            mime="application/json"
        )

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.85rem;">
    GridOS Renewable Operations Console · Local simulation prototype
</div>
""", unsafe_allow_html=True)
