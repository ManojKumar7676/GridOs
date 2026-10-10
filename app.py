"""
Accenture GridOS™ - Industrial SCADA Command Center & Operational Dispatcher
Enterprise Multi-Agent Platform for Problem Statement 4 (Utilities - Renewable Energy Orchestrator)
Target 9-Blocker Evaluation Grid Position: F3 - D3 (Multi-Period Stochastic Simulation + Multimodal Vision)
"""

import sys
import os

# Ensure package root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io
import time
from PIL import Image
from datetime import datetime
import streamlit.components.v1 as components

from AccentureAssessment.core.portfolio import UtilityPortfolioState, AssetStatus, MaintenancePriority
from AccentureAssessment.core.database import OrchestratorDatabase
from AccentureAssessment.perception.radar_vision import RadarVisionEngine, MultimodalPerceptionReport
from AccentureAssessment.agents.orchestrator_agent import ChiefExecutiveOrchestrator
from AccentureAssessment.simulation.engine import IndustrialSimulationEngine
from AccentureAssessment.config.prompt_config import get_prompt_config
from AccentureAssessment.core.llm_client import get_gemini_client
from AccentureAssessment.evaluation.evaluation_agent import AuditEvaluationAgent
from AccentureAssessment.evaluation.benchmark_runner import BenchmarkRunner
from AccentureAssessment.evaluation.metrics import MetricsCalculator

# High-grade enterprise layout
st.set_page_config(
    page_title="Accenture GridOS | Renewable Energy Orchestrator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional SCADA Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
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

# Header Console
top_c1, top_c2 = st.columns([3, 1.2])
with top_c1:
    st.title("⚡ Accenture GridOS™ | Renewable Energy Orchestrator")
    st.markdown("**Autonomous Cyber-Physical Dispatch Platform** | *Problem Statement 4: Utilities (Renewable Energy Orchestrator)*")
    st.markdown("""
        <div style="display: flex; gap: 8px; margin-top: 4px; flex-wrap: wrap;">
            <span class="status-pill status-online">● IEC 61850 SCADA BUS ONLINE</span>
            <span class="status-pill status-online">● 4 AUTONOMOUS AGENTS</span>
            <span class="status-pill status-online">● 10 PHYSICAL ASSETS</span>
            <span class="status-pill status-online">● 15-MIN REAL-TIME DISPATCH</span>
        </div>
    """, unsafe_allow_html=True)

with top_c2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: right;">
            <span class="badge-f3d3">🏆 Claimed 9-Blocker: Level F3 - D3</span><br>
            <small style="color: #9ca3af; font-size: 0.75rem;">Multi-Period Stochastic Dispatch (F3) + Multimodal Doppler Radar (D3)</small>
        </div>
    """, unsafe_allow_html=True)

# 9-Blocker Accordion Details
with st.expander("📌 View 9-Blocker Assessment Grid (F3 - D3 Verification Matrix for Problem 4)", expanded=False):
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("#### Feature Dimension: Level F3")
        st.write("✅ **F1 (Action Clusters)**: Physical battery dispatch, wholesale electricity trading, renewable curtailment, industrial demand response, and asset maintenance scheduling.")
        st.write("✅ **F2 (Dynamic Optimality & Uncertainty)**: Real-time Pareto multi-objective weighting dynamically shifts priorities under stress, negative pricing, price spikes, and storm alerts.")
        st.write("✅ **F3 (Multi-Period Simulation)**: Continuous 24-hour (96-interval) stochastic time-series simulator evaluating diurnal duck curves, weather variability, and 7 real-world shocks.")
    with col_g2:
        st.markdown("#### Depth Dimension: Level D3")
        st.write("✅ **D1 (Structured SCADA Telemetry)**: Real-time SCADA feeds, wholesale spot prices, line thermal ratings, and frequency telemetry.")
        st.write("✅ **D2 (High Reliability LP Optimizer)**: Formal Linear Programming optimization (scipy HiGHS solver) guaranteeing exact energy balance and electrochemical SoC bounds.")
        st.write("✅ **D3 (Multimodal Computer Vision)**: Ingestion and CV processing of Doppler satellite radar maps for cloud optical thickness, localized asset attenuation, and gust fronts.")

st.markdown("---")

# Main Navigation Tabs
tab_overview, tab1, tab_vision, tab2, tab3, tab4, tab_eval, tab_prompts = st.tabs([
    "📖 Problem Statement 4 Blueprint",
    "🎛️ Real-Time SCADA Dispatch Console",
    "🛰️ Multimodal Radar Vision Station",
    "📊 24-Hour Diurnal Analytics",
    "🗺️ Physical Asset Registry",
    "📜 SCADA Database & Audit Trail",
    "🏆 Agent Evaluation & Audit Station",
    "⚙️ Agent Prompts & Configuration"
])

# =========================================================================
# TAB OVERVIEW: Problem Statement 4 Blueprint & Architecture
# =========================================================================
with tab_overview:
    st.markdown("## 📖 Problem Statement 4: Utilities – Renewable Energy Orchestrator")

    # The Problem Statement
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(59, 130, 246, 0.08) 100%); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: #60a5fa; margin-top: 0;">⚡ The Problem</h3>
            <p style="font-size: 1.02rem; line-height: 1.7; color: #e5e7eb;">
                Adoption and utilization of renewable energy are increasing and are expected to increase sharply in the future.
                However, renewable generation is <strong>highly variable</strong>. Coordination across solar, wind, batteries, and market prices
                is therefore <strong>critical to optimizing cost and sustainability</strong>.
            </p>
            <p style="font-size: 1.02rem; line-height: 1.7; color: #d1d5db;">
                An AI agent must <strong>autonomously coordinate</strong> solar generation, wind generation, battery storage,
                grid imports/exports, wholesale energy prices, and industrial demand forecasts <strong>every 15 minutes</strong>
                to simultaneously <strong>minimize cost</strong>, <strong>maximize clean energy utilization</strong>, and <strong>maintain grid reliability</strong>.
            </p>
            <p style="font-size: 0.95rem; line-height: 1.6; color: #9ca3af; margin-bottom: 0;">
                <em>Unlike a chatbot or advisory system, the agent must <strong>take physical actions</strong> —
                dispatching battery charge/discharge commands, executing wholesale market trades,
                curtailing renewable generation, triggering demand response events, and scheduling field maintenance crews.</em>
            </p>
        </div>
    """, unsafe_allow_html=True)

    # How We Solve It
    st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.06); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: #93c5fd; margin-top: 0;">🏗️ How We Solve It: Multi-Agent Autonomous Dispatch Architecture</h3>
            <p style="font-size: 0.98rem; line-height: 1.7; color: #d1d5db;">
                We deploy a <strong>4-agent collaborative system</strong> that perceives the physical environment, deliberates under uncertainty, and executes
                binding dispatch commands across the entire portfolio every 15 minutes. The agents operate on <strong>real SCADA telemetry</strong>, not synthetic chat prompts.
            </p>
        </div>
    """, unsafe_allow_html=True)

    ag1, ag2, ag3, ag4 = st.columns(4)
    with ag1:
        st.markdown("""
        <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid #f59e0b; border-radius: 8px; padding: 14px;">
            <strong style="color: #f59e0b;">🌦️ Forecast Agent</strong><br>
            <small style="color: #9ca3af;">Meteorological & Renewable Prediction</small>
            <hr style="border-color: #1f2937; margin: 8px 0;">
            <span style="font-size: 0.85rem; color: #d1d5db;">
                Processes radar vision output and weather telemetry to predict solar irradiance, wind speed, and generation capacity for the next dispatch interval.
                Applies per-asset localized cloud attenuation from computer vision.
            </span>
        </div>
        """, unsafe_allow_html=True)
    with ag2:
        st.markdown("""
        <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid #10b981; border-radius: 8px; padding: 14px;">
            <strong style="color: #10b981;">💹 Market Agent</strong><br>
            <small style="color: #9ca3af;">Wholesale ISO/LMP Trading Analyst</small>
            <hr style="border-color: #1f2937; margin: 8px 0;">
            <span style="font-size: 0.85rem; color: #d1d5db;">
                Evaluates real-time spot LMP pricing, forward price spreads, carbon credit markets, and negative pricing events.
                Recommends buy/sell/hold positions and identifies arbitrage windows.
            </span>
        </div>
        """, unsafe_allow_html=True)
    with ag3:
        st.markdown("""
        <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid #ef4444; border-radius: 8px; padding: 14px;">
            <strong style="color: #ef4444;">🔌 Grid Reliability Agent</strong><br>
            <small style="color: #9ca3af;">NERC BAL-001 / IEEE 1547 Compliance</small>
            <hr style="border-color: #1f2937; margin: 8px 0;">
            <span style="font-size: 0.85rem; color: #d1d5db;">
                Monitors grid frequency, voltage stability, transmission line thermal limits, reserve margins, and N-1 contingency requirements.
                Triggers demand response or curtailment under grid stress.
            </span>
        </div>
        """, unsafe_allow_html=True)
    with ag4:
        st.markdown("""
        <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid #3b82f6; border-radius: 8px; padding: 14px;">
            <strong style="color: #3b82f6;">⚡ Chief Orchestrator</strong><br>
            <small style="color: #9ca3af;">Pareto Multi-Objective Optimizer</small>
            <hr style="border-color: #1f2937; margin: 8px 0;">
            <span style="font-size: 0.85rem; color: #d1d5db;">
                Synthesizes all agent advisories, runs the HiGHS LP optimizer for exact energy balance, resolves competing objectives,
                and emits the final binding action cluster across all 5 categories.
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # Three-column layout: Portfolio, Scenarios, Actions
    c_ov1, c_ov2 = st.columns(2)

    with c_ov1:
        st.markdown("### 🎯 Physical Portfolio Under Management")
        st.markdown("""
        | Asset Class | Count | Total Capacity | Key Detail |
        |------------|-------|---------------|------------|
        | ☀️ Solar Farms | 5 | 230 MW | Geographically dispersed, per-asset cloud attenuation |
        | 💨 Wind Farms | 3 | 250 MW | Cut-in 3 m/s, cut-out 25 m/s, coastal & ridge |
        | 🔋 BESS (Bulk) | 1 | 100 MW / 400 MWh | LiFePO₄ iron-phosphate, 0.25C rate, 92% RTE |
        | 🔋 BESS (Peaker) | 1 | 50 MW / 100 MWh | Li₄Ti₅O₁₂ titanate, 0.50C rate, 88% RTE |
        | 🏭 Industrial Load | 3 | ~155 MW | Smelter (DR), hydrogen (shiftable), cold storage |
        | 🌐 Grid Intertie | 1 | 200 MW export | 500 kV, subject to thermal congestion |
        """)

        st.markdown("### ⚡ 7 Real-World Scenarios Handled")
        st.markdown("""
        | # | Scenario | How We Respond |
        |---|----------|---------------|
        | 1 | **Clouds reduce solar output** (78% attenuation) | Radar CV detects cloud front → discharge BESS to fill gap → import grid if needed |
        | 2 | **Wind storm exceeds 25 m/s cut-out** | Feather blades → trip turbines → activate BESS peaker → schedule post-storm inspection |
        | 3 | **Price spike** ($285/MWh) | Maximize grid export → discharge all BESS → delay maintenance to keep assets online |
        | 4 | **Negative pricing** (-$18.50/MWh) | Suppress grid export → charge BESS with free energy → curtail surplus renewables |
        | 5 | **Battery outage** (BESS-01 trips) | Dispatch BMS inspection team → transfer load to BESS-02 → increase grid import |
        | 6 | **Transmission congestion** (500kV thermal limit) | Derate export corridor 50% → curtail excess renewable generation → trigger DR |
        | 7 | **Demand surge** (+35 MW industrial) | Increase generation + grid import → shift flexible electrolyzer load → trigger smelter DR |
        """)

        st.markdown("### 📡 5 Input Data Streams Processed")
        st.markdown("""
        1. **Renewable Generation Feeds**: Solar irradiance, inverter output, wind anemometer, turbine SCADA
        2. **Grid Telemetry**: Frequency (60 Hz ±0.03), voltage (500 kV), line thermal ratings, congestion flags
        3. **Battery Systems**: SoC %, cell temperature, BMS health, charge/discharge power, C-rate limits
        4. **Market Data**: Real-time spot LMP ($/MWh), forward prices, carbon credits, negative pricing events
        5. **External Feeds**: Doppler radar imagery (WSR-88D), satellite cloud maps, NWS storm warnings
        """)

    with c_ov2:
        st.markdown("### 📋 All 15 Physical Actions (5 Categories)")
        st.markdown("""
        <div style="font-size: 0.92rem;">
        """, unsafe_allow_html=True)

        st.markdown("**🔋 Battery Actions** — `BATTERY_ACTIONS`")
        st.markdown("""
        1. `CHARGE_BATTERIES` — Absorb surplus renewable/negative-price energy into BESS cells
        2. `DISCHARGE_BATTERIES` — Supply industrial loads or capture peak-price arbitrage revenue
        3. `RESERVE_BATTERY_CAPACITY` — Hold headroom as spinning reserve for N-1 grid contingencies
        """)

        st.markdown("**💹 Market Actions** — `MARKET_ACTIONS`")
        st.markdown("""
        4. `BUY_ELECTRICITY` — Import power from grid when renewables + storage cannot meet demand
        5. `SELL_ELECTRICITY` — Export surplus to wholesale market at favorable spot LMP
        6. `DELAY_SELLING_UNTIL_PRICES_RISE` — Store energy in BESS for forward peak-spread arbitrage
        """)

        st.markdown("**☀️ Renewable Actions** — `RENEWABLE_ACTIONS`")
        st.markdown("""
        7. `CURTAIL_WIND` — Feather turbine blade pitch when grid/storage is congested
        8. `CURTAIL_SOLAR` — Throttle PV inverters under negative pricing or line thermal limits
        9. `PRIORITIZE_CLEANER_GENERATION` — Merit-order dispatch of zero-marginal-cost clean energy
        """)

        st.markdown("**🏭 Demand Management** — `DEMAND_MANAGEMENT`")
        st.markdown("""
        10. `TRIGGER_DEMAND_RESPONSE` — Curtail interruptible smelter block (contractual DR)
        11. `REDUCE_NONCRITICAL_LOADS` — Derate cold storage HVAC, pre-cool refrigeration zones
        12. `SHIFT_INDUSTRIAL_LOADS` — Defer hydrogen electrolyzer production to off-peak window
        """)

        st.markdown("**🔧 Maintenance Actions** — `MAINTENANCE`")
        st.markdown("""
        13. `DELAY_MAINTENANCE` — Keep asset running during lucrative peak-price intervals
        14. `SCHEDULE_MAINTENANCE` — Plan off-peak inverter/turbine service for thermal anomalies
        15. `DISPATCH_INSPECTION_TEAMS` — Send field crews for BMS outage, vibration, or thermal events
        """)

        st.markdown("### ⚖️ Multi-Objective Trade-Off Paradox")
        st.markdown("""
        The agent must **simultaneously** optimize competing objectives that often conflict:

        | Minimize ↓ | Maximize ↑ |
        |-----------|-----------|
        | Electricity cost | Reliability & reserve margin |
        | Carbon emissions | Renewable utilization |
        | Renewable curtailment | Commercial profit |
        | Battery degradation wear | Grid frequency stability |

        *Example conflict: A price spike incentivizes maximum battery discharge for profit,
        but this depletes reserves needed for reliability. The Pareto-weighted LP optimizer
        balances these trade-offs dynamically based on real-time conditions.*
        """)

    # 9-Blocker Evidence Section
    st.markdown("---")
    st.markdown("### 🏆 9-Blocker Assessment: F3 – D3 (Evidence)")

    ev1, ev2 = st.columns(2)
    with ev1:
        st.markdown("""
        #### Feature Dimension: F3 (Multi-Period Stochastic Simulation)
        | Level | Requirement | Evidence |
        |-------|------------|---------|
        | **F1** | Multiple action categories | ✅ 15 actions across 5 categories (Battery, Market, Renewable, DR, Maintenance) |
        | **F2** | Dynamic optimality under uncertainty | ✅ Pareto-weighted LP optimizer with real-time weight adjustment |
        | **F3** | Multi-period simulation | ✅ 96-interval 24h simulation with 7 injected real-world shocks |
        """)
    with ev2:
        st.markdown("""
        #### Depth Dimension: D3 (Multimodal Computer Vision)
        | Level | Requirement | Evidence |
        |-------|------------|---------|
        | **D1** | Structured data ingestion | ✅ SCADA telemetry, spot prices, SoC, line ratings, frequency |
        | **D2** | Mathematical optimization | ✅ scipy.optimize.linprog (HiGHS) with 13-variable LP formulation |
        | **D3** | Multimodal (non-text) data | ✅ WSR-88D Doppler radar CV processing with per-asset attenuation |
        """)

    st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 10px; padding: 16px; margin-top: 10px;">
            <strong style="color: #34d399;">Key Differentiator:</strong>
            <span style="color: #d1d5db;">
                This system is <strong>not a chatbot</strong>. It does not generate text advice for a human operator.
                It autonomously executes binding physical dispatch commands — charging/discharging battery banks, placing wholesale electricity trades,
                curtailing turbines and inverters, triggering contractual demand response events, and dispatching field maintenance crews —
                all within a 15-minute SCADA cycle. Every action has a SCADA command code, a target asset, a MW quantity, and an engineering rationale.
            </span>
        </div>
    """, unsafe_allow_html=True)

    # Core Engineering Team Roster
    st.markdown("---")
    st.markdown("### 👥 Core Systems & Architecture Engineering Team")
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        st.markdown("""
        <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid #38bdf8; border-radius: 8px; padding: 14px; text-align: center;">
            <strong style="color: #38bdf8; font-size: 1.02rem;">ManojKumar P</strong><br>
            <span style="color: #9ca3af; font-size: 0.82rem;">Lead Systems Architect</span><br>
            <small style="color: #64748b; font-size: 0.75rem;">Autonomous Multi-Agent Systems & SCED LP</small>
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        st.markdown("""
        <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid #34d399; border-radius: 8px; padding: 14px; text-align: center;">
            <strong style="color: #34d399; font-size: 1.02rem;">B Iniyavan</strong><br>
            <span style="color: #9ca3af; font-size: 0.82rem;">Systems Co-Lead</span><br>
            <small style="color: #64748b; font-size: 0.75rem;">SCADA Protocol Bus & Real-Time Orchestration</small>
        </div>
        """, unsafe_allow_html=True)
    with col_t3:
        st.markdown("""
        <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid #fbbf24; border-radius: 8px; padding: 14px; text-align: center;">
            <strong style="color: #fbbf24; font-size: 1.02rem;">Nishi Verma</strong><br>
            <span style="color: #9ca3af; font-size: 0.82rem;">Power Optimization Lead</span><br>
            <small style="color: #64748b; font-size: 0.75rem;">Wholesale Market & Kirchhoff Balancer</small>
        </div>
        """, unsafe_allow_html=True)
    with col_t4:
        st.markdown("""
        <div style="background: #111827; border: 1px solid #1f2937; border-top: 3px solid #f87171; border-radius: 8px; padding: 14px; text-align: center;">
            <strong style="color: #f87171; font-size: 1.02rem;">Pasupulati Siva Puja</strong><br>
            <span style="color: #9ca3af; font-size: 0.82rem;">Cyber-Physical AI Lead</span><br>
            <small style="color: #64748b; font-size: 0.75rem;">Doppler Radar CV & Regulatory Audit AI</small>
        </div>
        """, unsafe_allow_html=True)

    # Standalone Technical Architecture & Flow Diagrams Blueprint Section
    st.markdown("---")
    st.markdown("### 🗺️ Standalone Technical Architecture & Flow Diagrams Blueprint")
    html_file_path = os.path.join(os.path.dirname(__file__), "architecture_and_flows.html")
    if os.path.exists(html_file_path):
        with open(html_file_path, "r", encoding="utf-8") as hf:
            html_doc = hf.read()
        
        c_b1, c_b2 = st.columns([3, 1])
        with c_b1:
            st.markdown("""
                <div style="background: #111a2e; border: 1px solid #2563eb; border-radius: 10px; padding: 14px;">
                    <strong style="color: #60a5fa; font-size: 1.0rem;">📄 Standalone Document Generated: <code>architecture_and_flows.html</code></strong><br>
                    <span style="color: #d1d5db; font-size: 0.88rem;">
                        Features 5 interactive Mermaid.js vector diagrams: Technical Architecture, Functional Flow (Sequence),
                        Logical Flow (Shock State-Machine), Deployment Flow (K8s/Docker/Edge), and Integration Flow (IEC 61850 / DNP3).
                    </span>
                </div>
            """, unsafe_allow_html=True)
        with c_b2:
            st.download_button(
                label="📥 Download HTML Blueprint",
                data=html_doc,
                file_name="architecture_and_flows.html",
                mime="text/html",
                key="btn_dl_arch_doc",
                use_container_width=True
            )
        
        with st.expander("🌐 Preview Standalone Architecture & Flow Diagrams Inside App", expanded=False):
            components.html(html_doc, height=750, scrolling=True)

# =========================================================================
# TAB 1: Problem Statement 4 Core Resolution Station & SCADA Dispatch Console
# =========================================================================
with tab1:
    st.markdown("### 🎛️ Problem Statement 4 Core Resolution Station & SCADA Dispatch Console")
    st.caption("Autonomously coordinates solar, wind, batteries, wholesale market prices, and industrial demand every 15 minutes to minimize cost, maximize clean energy utilization, and maintain grid reliability.")

    # 1. Operational Scenario Selector (All 7 Problem Statement 4 Real-World Shocks)
    st.markdown("#### 🎯 Select a Real-World Operational Disturbance (Problem Statement 4 Scenarios)")
    
    scenario_catalog = {
        "☀️ Routine Operations (Baseline 15-Min Diurnal Balance)": {
            "step": 24, "storm": False, "neg_price": False, "outage": False, "congestion": False, "surge": 0.0,
            "title": "Baseline Diurnal Merit Dispatch",
            "challenge": "Manage standard mid-morning solar ramp and baseload industrial demand while preserving battery buffer.",
            "agent_response": "Forecast agent models laminar clear-sky insolation; Market agent identifies nominal LMP ($48/MWh); Grid agent confirms voltage/frequency within IEEE 1547 envelopes.",
            "solver_goal": "Dispatches zero-marginal-cost solar/wind at 100% capacity; exports economic surplus to wholesale grid for profit."
        },
        "☁️ Scenario 1: Clouds Reduce Solar Output (78% Cloud Deck Attenuation)": {
            "step": 36, "storm": False, "neg_price": False, "outage": False, "congestion": False, "surge": 0.0,
            "title": "Sudden Cloud Front Attenuation Over Solar Basin",
            "challenge": "Rapid cloud deck causes sudden generation drop of ~140 MW across 5 solar plants, threatening supply shortfall and industrial under-frequency trip.",
            "agent_response": "Forecast Agent extracts Doppler radar cloud opacity (0.88, 48 dBZ) and derates solar capacity to 22%; Grid Reliability Agent detects reserve depletion.",
            "solver_goal": "Instantly discharges BESS-01 bulk storage to replace solar shortfall; ramps grid imports to maintain continuous industrial load without load shedding."
        },
        "💨 Scenario 2: Gale Wind Storm Breaches Cut-Out (26.8 m/s > 25 m/s Safety Trip)": {
            "step": 60, "storm": True, "neg_price": False, "outage": False, "congestion": False, "surge": 0.0,
            "title": "Convective Squall & Wind Turbine Safety Cut-Out",
            "challenge": "Severe aerodynamic storm gusts exceed the 25.0 m/s safety cut-out limit, forcing 250 MW of wind turbines to trip/feather simultaneously.",
            "agent_response": "Forecast Agent flags CRITICAL convective squall front; Grid Agent initiates BAL-001 synthetic inertia and locks turbine blade pitch (MNT_GUST_LOCKOUT).",
            "solver_goal": "Fast-ramps BESS-02 Titanate peaker within milliseconds; imports intertie power; queues post-storm field inspection teams."
        },
        "📈 Scenario 3: Wholesale Electricity Price Spike ($285.00/MWh Peak Surge)": {
            "step": 72, "storm": False, "neg_price": False, "outage": False, "congestion": False, "surge": 0.0,
            "title": "Wholesale Locational Marginal Price (LMP) Surge",
            "challenge": "Wholesale market clearing price surges from $48/MWh to $285/MWh. Consuming grid power is economically catastrophic; exporting power is extremely lucrative.",
            "agent_response": "Market Trading Agent flags price surge (priority ELEVATED); Orchestrator raises commercial profit weight to 55%; Grid Agent protects battery minimum buffer.",
            "solver_goal": "Maximizes battery discharge into the 500 kV intertie to capture revenue; triggers contractual Smelter Demand Response (curtails 25 MW) to avoid purchasing peak power; defers routine maintenance."
        },
        "📉 Scenario 4: Negative Electricity Pricing Event (-$18.50/MWh Intertie Penalty)": {
            "step": 48, "storm": False, "neg_price": True, "outage": False, "congestion": False, "surge": 0.0,
            "title": "Regional Over-Generation & Negative Wholesale Pricing",
            "challenge": "Wholesale spot price drops to -$18.50/MWh due to regional renewable over-generation. Continued grid injection causes cash penalties (paying the grid to take power).",
            "agent_response": "Market Agent issues CRITICAL mandate to suppress wholesale export; Orchestrator elevates profit weight to 45% and curtailment penalty to 25%.",
            "solver_goal": "Suppresses all wholesale intertie export to 0.0 MW; commands maximum BESS charging to absorb free/negative energy; curtails surplus solar inverters and wind pitch to protect commercial balance."
        },
        "🔋 Scenario 5: Battery Outage Occurs (BESS-01 BMS Thermal Trip)": {
            "step": 66, "storm": False, "neg_price": False, "outage": True, "congestion": False, "surge": 0.0,
            "title": "Bulk Battery Storage Unplanned Outage (BESS-01 Trip)",
            "challenge": "BESS-01 (400 MWh bulk storage) suffers an unplanned thermal runaway alarm and goes offline, removing 100 MW of flexible capacity.",
            "agent_response": "Grid Reliability Agent detects asset status change (is_available=False); dispatches emergency BMS thermal inspection crew (MNT_DISPATCH_CREW).",
            "solver_goal": "Transfers all balancing responsibility to BESS-02 Titanate peaker; coordinates additional economic grid imports to ensure uninterrupted demand service."
        },
        "🌐 Scenario 6: Transmission Corridor Congested (500 kV Intertie Thermal Limits)": {
            "step": 80, "storm": False, "neg_price": False, "outage": False, "congestion": True, "surge": 0.0,
            "title": "500 kV Intertie Reaches Thermal MVA Line Capacity",
            "challenge": "Transmission corridor reaches thermal capacity limit; line export rating is derated by 50% (from 200 MW to 100 MW) to prevent transmission line sag/flashover.",
            "agent_response": "Grid Reliability Agent flags corridor congestion; Market Agent redirects surplus generation away from intertie.",
            "solver_goal": "Caps wholesale intertie export at 100 MW; redirects excess solar and wind generation into charging BESS-01 and BESS-02; curtails excess generation to protect corridor integrity."
        },
        "🏭 Scenario 7: Industrial Smelter Demand Surge (+35 MW Unexpected Load)": {
            "step": 86, "storm": False, "neg_price": False, "outage": False, "congestion": False, "surge": 35.0,
            "title": "Unforecasted Heavy Industrial Load Surge (+35 MW)",
            "challenge": "MegaTech Smelter unexpectedly ramps production, surging load by +35 MW above baseline (from 155 MW to 190 MW).",
            "agent_response": "Forecast Agent notes demand spike; Grid Reliability Agent audits spinning reserve margins.",
            "solver_goal": "Defers flexible PEM green hydrogen electrolyzer production (shifts load to off-peak); increases battery discharge and grid imports; triggers contractual Demand Response curtailment."
        }
    }

    selected_scenario_key = st.selectbox(
        "Choose an operational scenario to simulate and solve:",
        list(scenario_catalog.keys()),
        index=0
    )

    sc_info = scenario_catalog[selected_scenario_key]

    # Render Challenge & Resolution Deep Dive Box
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%); border: 1px solid #3b82f6; border-radius: 10px; padding: 18px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="color: #60a5fa; margin: 0;">⚡ {sc_info['title']}</h4>
                <span class="status-pill status-online">AI Autonomous Resolution Active</span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #ef4444; padding: 10px 14px; border-radius: 0 6px 6px 0;">
                    <strong style="color: #f87171; font-size: 0.9rem;">🚨 Operational Disturbance & Risk:</strong>
                    <p style="color: #e5e7eb; font-size: 0.88rem; margin: 4px 0 0 0;">{sc_info['challenge']}</p>
                </div>
                <div style="background: rgba(16, 185, 129, 0.08); border-left: 3px solid #10b981; padding: 10px 14px; border-radius: 0 6px 6px 0;">
                    <strong style="color: #34d399; font-size: 0.9rem;">🤖 4-Agent Collective Response:</strong>
                    <p style="color: #e5e7eb; font-size: 0.88rem; margin: 4px 0 0 0;">{sc_info['agent_response']}</p>
                </div>
            </div>
            <div style="background: rgba(59, 130, 246, 0.08); border-left: 3px solid #3b82f6; padding: 10px 14px; border-radius: 0 6px 6px 0; margin-top: 10px;">
                <strong style="color: #60a5fa; font-size: 0.9rem;">🧮 HiGHS LP Solver Resolution:</strong>
                <p style="color: #e5e7eb; font-size: 0.88rem; margin: 4px 0 0 0;">{sc_info['solver_goal']}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Manual Overrides & Fine-Tuning Expander
    with st.expander("⚙️ Fine-Tune SCADA Telemetry & Operator Overrides", expanded=False):
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
    active_step_idx = sc_info["step"]
    time_str = f"{int(active_step_idx / 4):02d}:{int((active_step_idx % 4) * 15):02d}"
    step_env = scenario_data[active_step_idx]

    current_portfolio = UtilityPortfolioState()
    current_portfolio.market.spot_price_per_mwh = -18.5 if (sc_info["neg_price"] or step_env["spot_price"] < 0) else (285.0 if sc_info["step"] == 72 else step_env["spot_price"])
    current_portfolio.market.projected_price_next_hour = scenario_data[min(active_step_idx + 4, 95)]["spot_price"]
    current_portfolio.grid.transmission_congested = sc_info["congestion"] or step_env["transmission_congested"]

    # Asset availability
    bess1_is_avail = not sc_info["outage"]
    current_portfolio.bess_systems[0].is_available = bess1_is_avail
    current_portfolio.bess_systems[0].status = AssetStatus.OPERATIONAL if bess1_is_avail else AssetStatus.MAINTENANCE

    # Industrial demand surge
    if sc_info["surge"] > 0:
        current_portfolio.industrial_consumers[0].base_load_mw = 70.0 + sc_info["surge"]

    for sol in current_portfolio.solar_farms:
        sol.cloud_attenuation_factor = 0.22 if sc_info["step"] == 36 else step_env["solar_factor"]
    for wnd in current_portfolio.wind_farms:
        wnd.wind_speed_mps = 26.8 if (sc_info["storm"] or sc_info["step"] == 60) else step_env["wind_speed"]

    # Generate or retrieve radar image
    radar_img = st.session_state.orchestrator.vision.generate_radar_feed(
        cloud_density=0.88 if sc_info["step"] == 36 else step_env["cloud_index"],
        storm_front=sc_info["storm"] or sc_info["step"] == 60,
        interval_idx=active_step_idx
    )

    # Solve Dispatch
    decision = st.session_state.orchestrator.orchestrate(
        portfolio=current_portfolio,
        interval_idx=active_step_idx,
        clock_time=time_str,
        radar_image_path=radar_img,
        event_tag=sc_info["title"]
    )

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
        st.markdown("#### 🛰️ Multimodal Computer Vision Perception (D3)")
        if os.path.exists(radar_img):
            st.image(radar_img, caption=f"WSR-88D Doppler Scan (Interval #{active_step_idx} - {time_str})", use_container_width=True)
        
        rep: MultimodalPerceptionReport = st.session_state.orchestrator.vision.process_radar_image(radar_img)
        st.info(f"""
            **Radar Feature Telemetry:**
            * Regional Cloud Opacity Index: `{rep.cloud_opacity_index:.2f}`
            * Solar Fleet Attenuation Factor: `{rep.solar_derating_factor:.2f}`
            * Convective Storm Alert: `{'ALERT' if rep.storm_alert_active else 'NOMINAL'}`
            * Peak Reflectivity: `{rep.peak_reflectivity_dbz:.1f} dBZ`
            * Sensor Fusion Confidence: `{rep.sensor_fusion_confidence*100:.0f}%`
        """)

    with disp_col2:
        st.markdown("#### 🤖 Collaborative Multi-Agent Deliberations (4 Agents)")
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
        
        st.success(f"**⚡ Chief Orchestrator Dynamic Rationale (F2):** {decision['trade_off_explanation']}")

    # Exact Physical Energy Conservation Proof
    st.markdown("---")
    st.markdown("#### 🧮 Physical Energy Conservation Balance Verification (HiGHS LP Solution)")
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
    st.markdown("#### 📋 Executed Physical Action Cluster (All 5 Problem Statement Categories)")
    if dispatch_res.action_cluster:
        act_df = pd.DataFrame(dispatch_res.action_cluster)
        st.dataframe(act_df, use_container_width=True)
    else:
        st.info("System balanced in steady state. No discrete dispatch actions required.")

# =========================================================================
# TAB: Multimodal Computer Vision Perception Laboratory
# =========================================================================
with tab_vision:
    st.markdown("### 🛰️ Multimodal Computer Vision Perception Laboratory (D3)")
    st.caption("Upload any real Doppler radar or satellite weather imagery, or analyze synthesized WSR-88D feeds with localized asset coordinates.")

    v_col1, v_col2 = st.columns([1.2, 1.8])

    with v_col1:
        st.markdown("#### 📥 Ingest Real Weather Radar / Satellite Image")
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
    st.markdown("### 📊 24-Hour Continuous Multi-Period Simulation (F3 Requirement)")
    st.caption("96 discrete 15-minute intervals tracking solar insolation curves, wind volatility, battery cycling, and all 7 real-world disruptions.")

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

    # Handled Real-World Operational Disruptions Table
    st.markdown("#### ⚡ Problem Statement 4: Real-World Disruptions Handled")
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
    st.markdown("Technical specifications and SCADA telemetry endpoints for all portfolio components:")

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
    st.markdown("### 📜 ACID SQLite SCADA Database & Audit Trail")
    st.caption("Live persistent records stored in `storage/orchestrator.db`.")

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
    st.markdown("#### 🔍 Live Evaluation Scorecard (Active SCADA Interval)")
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
            st.progress(min(1.0, scorecard.forecast_metrics.composite_forecast_score / 100.0))
            st.caption(f"Score: **{scorecard.forecast_metrics.composite_forecast_score:.1f}/100**")
            st.markdown(f"""
            - **Irradiance MAE:** `{scorecard.forecast_metrics.irradiance_mae:.1f} W/m²`
            - **Wind RMSE:** `{scorecard.forecast_metrics.wind_speed_rmse:.2f} m/s`
            - **Cloud CV Accuracy:** `{scorecard.forecast_metrics.cloud_attenuation_accuracy:.1f}%`
            - **Storm Alert F1:** `{scorecard.forecast_metrics.storm_alert_f1_score:.2f}`
            """)

        with col_ag2:
            st.markdown(f"**💹 AGT-02-MRKT (Market)**")
            st.progress(min(1.0, scorecard.market_metrics.composite_market_score / 100.0))
            st.caption(f"Score: **{scorecard.market_metrics.composite_market_score:.1f}/100**")
            st.markdown(f"""
            - **Arbitrage Efficiency:** `{scorecard.market_metrics.arbitrage_capture_efficiency:.1f}%`
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
    st.caption("Executes all 7 Problem Statement 4 real-world operational disruptions + nominal baseline through the 4-agent collective, evaluating each with AGT-04-EVAL.")

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
    st.caption("All agent personas, system prompts, observation templates, and physical action rationales are decoupled into `config/prompts.json`.")

    prompt_cfg = get_prompt_config()
    raw_prompts = prompt_cfg.raw

    st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 10px; padding: 16px; margin-bottom: 20px;">
            <strong style="color: #60a5fa;">💡 Production Architecture Note:</strong>
            <span style="color: #d1d5db; font-size: 0.95rem;">
                No prompts or reasoning strings are hardcoded in agent business logic. Every agent persona,
                observation template, alert trigger, and physical SCADA action rationale is dynamically ingested from
                the centralized configuration engine (<code>AccentureAssessment/config/prompts.json</code>).
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

        st.markdown("##### 🚨 SCADA Alarms & Alert Templates")
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
    with st.expander("📄 View / Download Raw Configuration File (`config/prompts.json`)", expanded=False):
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
    Accenture × The Economic Times AI Hackathon (Agentic Edition) | Problem Statement 4: Utilities (Renewable Energy Orchestrator)<br>
    Self-Declared 9-Blocker Position: <strong>F3 - D3</strong> | Production Codebase: <code>AccentureAssessment</code>
</div>
""", unsafe_allow_html=True)
