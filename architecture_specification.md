# Technical Architecture & Solution Specification
## ET AI Hackathon: Agentic Edition (Accenture × The Economic Times)
**Problem Statement 4: Utilities – Renewable Energy Orchestrator**
**Codebase Directory**: `AccentureAssessment`
**Target Evaluation Grid Position**: **Level F3 - D3**

---

## 1. Executive Summary & Problem Formulation

The transition of utility power grids toward deep renewable penetration is constrained by **high-frequency weather intermittency, market price volatility, and physical network limits**. As defined in Problem Statement 4, the utility manages an extensive cyber-physical portfolio:
* **☀️ 5 Solar Farms (230 MW nameplate)** across microclimates with cloud attenuation.
* **💨 3 Wind Farms (250 MW nameplate)** with cut-in (3 m/s) and storm safety cut-out (25 m/s) limits.
* **🔋 2 Battery Energy Storage Systems (BESS: 150 MW / 500 MWh total)** (Iron-Phosphate bulk + Titanate peaker).
* **🏭 Heavy Industrial Consumers** (Baseload, flexible PEM green hydrogen electrolyzers, interruptible smelters).
* **🌐 500 kV Regional Interties** subject to thermal line ratings and transmission congestion limits.
* **💲 Wholesale Electricity Market** with real-time spot LMP trading, carbon offset pricing, and forward spreads.

### Why Agentic AI Is Required:
Unlike classical static linear dispatch tools or conversational chatbots, this cyber-physical system:
1. **Perceives Heterogeneous Multimodal Data (D3)**: Ingests satellite Doppler radar imagery (NEXRAD WSR-88D Level II) to predict cloud optical depth, localized attenuation per solar plant, and wind gust fronts.
2. **Deliberates Across Multiple Competing Goals (F2)**: Continuously negotiates non-linear trade-offs between minimizing costs, carbon emissions, curtailment, and battery degradation while maximizing profit, clean penetration, and grid frequency stability.
3. **Executes Discrete Physical Actions (F1)**: Directly dispatches all 5 action categories specified on Page 12:
   - **Battery actions**: Charge, Discharge, Reserve capacity for emergencies
   - **Market actions**: Buy electricity, Sell electricity, Delay selling until prices rise
   - **Renewable actions**: Curtail wind, Curtail solar, Prioritize cleaner generation
   - **Demand management**: Trigger demand response, Reduce noncritical loads, Shift industrial loads
   - **Maintenance**: Delay maintenance, Schedule maintenance, Dispatch inspection teams
4. **Sustains Multi-Period Temporal Coherence (F3)**: Governs operations across a 24-hour diurnal cycle (96 intervals of 15 minutes each) with proven resilience against all 7 real-world disruptions from the specification:
   - Clouds reduce solar output
   - Wind suddenly increases & storm cut-outs
   - Electricity prices spike ($285/MWh)
   - Negative electricity pricing (-$18.50/MWh)
   - One battery becomes unavailable (outage)
   - Transmission line reaches capacity (thermal congestion)
   - Industrial demand increases unexpectedly (+35 MW surge)

---

## 2. 9-Blocker Verification Matrix (Level F3 - D3)

```
        SOLUTION DEPTH
        ▲
     D3 │ [D3-F1]        [D3-F2]       ★ [D3-F3] (TARGET CLAIM)
        │
     D2 │ [D2-F1]        [D2-F2]         [D2-F3]
        │
     D1 │ [D1-F1]        [D1-F2]         [D1-F3]
        └────────────────────────────────────────►
          F1              F2              F3
                    SOLUTION FEATURES
```

| Dimension | Declared Level | Concrete Implementation Proof |
| :--- | :---: | :--- |
| **Features** | **F3** | **F1**: Emits discrete action clusters across all 5 categories: Battery, Market, Renewable, Demand Response, and Maintenance.<br>**F2**: Situational dynamic Pareto weighting dynamically shifts priorities under grid stress, storm warnings, price spikes, and negative tariffs.<br>**F3**: Simulates 96 discrete 15-minute intervals across diurnal duck curves, with verified resilience against all 7 real-world disruptions. |
| **Depth** | **D3** | **D1**: Structured SCADA telemetry, spot LMP time-series, and IEC 61850 data models.<br>**D2**: Formal Linear Programming optimizer (`scipy.optimize.linprog` with HiGHS solver) guaranteeing exact energy balance and electrochemical SoC envelopes (10% to 95%).<br>**D3**: **Computer Vision Perception Engine** ingesting Doppler satellite radar maps (and external image uploads) for cloud optical thickness and gust front tracking. |

---

## 3. System Architecture Diagram

```mermaid
graph TD
    subgraph Data Layer [Multimodal Telemetry & Market Feed]
        RADAR["🛰️ Doppler Satellite Radar & Multi-Spectral Imagery"]
        SCADA["⚡ Real-Time SCADA Telemetry (IEC 61850 / DNP3)"]
        SPOT_MKT["💲 Wholesale Spot Market & Forward Spreads"]
        DB[(🗄️ ACID SQLite Persistent Database)]
    end

    subgraph Perception Layer [Vision & Feature Extraction (D3)]
        CV_ENGINE["Perception & Vision Engine<br><i>Cloud Opacity Index, Derating & Storm Tracking</i>"]
    end

    subgraph Multi-Agent Collective [Collaborative Agents]
        AGT_1["👁️ Meteorological & Vision Agent"]
        AGT_2["💹 Wholesale Market & Arbitrage Agent"]
        AGT_3["🛡️ Grid Reliability & Asset Health Agent"]
        CHIEF["⚡ Chief Executive Orchestrator<br><i>Dynamic Pareto Weight Arbitration (F2)</i>"]
    end

    subgraph Optimization Layer [Physical Safety & Dispatch]
        SOLVER["HiGHS Linear Programming Solver<br><i>Energy Balance & Electrochemical Bounds</i>"]
    end

    subgraph Physical Execution [All 5 Action Categories (F1)]
        ACT_BESS["🔋 Battery Actions (Charge / Discharge / Reserve)"]
        ACT_GRID["💹 Market Actions (Buy / Sell / Delay Selling)"]
        ACT_CURT["☀️ Renewable Actions (Curtail Solar/Wind / Prioritize Clean)"]
        ACT_DR["🏭 Demand Management (Trigger DR / Shift Loads / Reduce Noncritical)"]
        ACT_MNT["🔧 Maintenance (Delay / Schedule / Dispatch Inspection)"]
    end

    RADAR --> CV_ENGINE
    CV_ENGINE --> AGT_1
    SCADA --> AGT_3
    SPOT_MKT --> AGT_2

    AGT_1 --> CHIEF
    AGT_2 --> CHIEF
    AGT_3 --> CHIEF

    CHIEF --> SOLVER
    SOLVER --> ACT_BESS
    SOLVER --> ACT_GRID
    SOLVER --> ACT_CURT
    SOLVER --> ACT_DR
    SOLVER --> ACT_MNT

    SOLVER --> DB
    CHIEF --> DB
```

---

## 4. Multi-Agent Hierarchy: The 4 Agents and the Orchestrator Role

A central architectural question for enterprise agentic systems: **Do we have 4 domain agents, and is there an orchestrator?**

### The Answer:
**Yes, exactly.** GridOS deploys a **hierarchical multi-agent collective** comprising **4 distinct autonomous agents**, with **1 Chief Executive Orchestrator** presiding over **3 specialized domain agents**:

```
                          ┌────────────────────────────────────────────────────────┐
                          │     AGT-00-EXEC: Chief Executive Orchestrator          │
                          │   (Master Dispatcher & Dynamic Pareto Arbitrator)      │
                          └──────────────────────────┬─────────────────────────────┘
                                                     │ Coordinates every 15 mins
                 ┌───────────────────────────────────┼───────────────────────────────────┐
                 │                                   │                                   │
                 ▼                                   ▼                                   ▼
  ┌─────────────────────────────┐     ┌─────────────────────────────┐     ┌─────────────────────────────┐
  │ AGT-01-METEO: Forecast Agent│     │  AGT-02-MRKT: Market Agent  │     │   AGT-03-GRID: Grid Agent   │
  │ Atmospheric & Radar Vision  │     │  Wholesale Trading & LMP    │     │  Reliability, SoC & Thermal │
  └─────────────────────────────┘     └─────────────────────────────┘     └─────────────────────────────┘
```

| Agent ID | Agent Name & Operational Role | Domain | Core Skills | Operational Instructions | Tools & Actuators |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`AGT-00-EXEC`** | **Chief Executive Renewable Energy Orchestrator**<br>*(Master Dispatcher & Pareto Arbitrator)* | Multi-Period Stochastic Dispatch, Dynamic Pareto Arbitration & SCED Execution | • Multi-agent consensus synthesis<br>• Dynamic Pareto weight arbitration<br>• 13-variable LP SCED formulation<br>• Inter-temporal forward arbitrage valuation<br>• Contingency escalation & triage<br>• SCADA command emission | 1. Query all 3 domain agents every 15 min.<br>2. Situationally arbitrate Pareto weights.<br>3. Formulate and solve 13-variable LP via HiGHS.<br>4. Apply electrochemical transitions (10-95% SoC).<br>5. Emit 5-category SCADA action clusters.<br>6. Commit telemetry to ACID SQLite DB. | • `IndustrialDispatchSolver` (HiGHS LP)<br>• `OrchestratorDatabase` (SQLite)<br>• `ParetoWeightArbitrator`<br>• IEC 61850 SCADA Actuation Bus<br>• Domain Agent Query Bus |
| **`AGT-01-METEO`** | **Meteorological & Vision Perception Agent**<br>*(Atmospheric Physicist & CV Forecaster)* | Multimodal Computer Vision, Doppler Radar Ingestion & Spatial Renewable Yield | • Doppler radar feature extraction (dBZ)<br>• 20x20 pixel localized asset patch sampling<br>• Solar insolation & Air Mass AM1.5 derating<br>• Convective squall & gust detection (>25 m/s)<br>• Sensor fusion confidence scoring | 1. Ingest Doppler radar frame.<br>2. Compute regional cloud opacity and peak dBZ.<br>3. Sample 20x20 patches around each asset.<br>4. Check wind vs 3 m/s cut-in and 25 m/s cut-out.<br>5. Apply plant-specific cloud attenuation factors.<br>6. Return structured deliberation message. | • `RadarVisionEngine` (WSR-88D CV)<br>• NumPy/PIL Tensor Pipeline<br>• Ground Pyranometer SCADA Network<br>• Ultrasonic Anemometer Array |
| **`AGT-02-MRKT`** | **Wholesale Electricity Market & Trading Agent**<br>*(Commercial Trader & LMP Analyst)* | Wholesale Spot Electricity Markets, Carbon Compliance & DR Economics | • Locational Marginal Price (LMP) analysis<br>• Forward inter-temporal spread arbitrage<br>• Negative pricing cash penalty mitigation<br>• Demand Response valuation ($65/MWh)<br>• Carbon offset accounting ($35/t CO2) | 1. Ingest real-time spot LMP, forward curve, carbon tax.<br>2. Calculate spread $\Delta P = P_{t+4} - P_{t}$.<br>3. Classify market regime (Negative, Surge, Spread, Nominal).<br>4. Issue trading mandate (charge, discharge, store, merit).<br>5. Deliver commercial advisory to Chief Orchestrator. | • ISO/RTO Wholesale Market Ticker<br>• Forward Spark Spread Calculator<br>• Demand Response Settlement Engine<br>• Carbon Compliance Ledger |
| **`AGT-03-GRID`** | **Grid Reliability & SCADA Protection Agent**<br>*(Protection Engineer & Compliance Officer)* | Cyber-Physical Grid Stability, NERC BAL-001 Balancing & Asset Protection | • NERC BAL-001 frequency response monitoring<br>• IEEE 1547 interconnection compliance<br>• Electrochemical BESS health safeguards<br>• 500 kV corridor thermal MVA tracking<br>• Predictive thermal/vibration diagnostics | 1. Ingest grid frequency, intertie voltage, line ratings.<br>2. Audit frequency vs 49.85 - 50.15 Hz thresholds.<br>3. Enforce BESS-01 & BESS-02 SoC boundaries.<br>4. Check 500 kV corridor for thermal congestion.<br>5. Audit inverter temp (>62°C) and turbine vibration.<br>6. Return reliability constraints to Orchestrator. | • SCADA RTU/PMU Substation Bus<br>• Battery Management System (BMS)<br>• Dynamic Line Rating (DLR) Tool<br>• Accelerometer Vibration / Thermal Network |

---

## 5. Codebase Directory Map

```
AccentureAssessment/
├── app.py                             # SCADA Industrial Command Center & Web Console (Streamlit)
├── architecture_specification.md      # Full Technical Architecture & 9-Blocker Defense
├── requirements.txt                   # Production Python Dependencies
├── conftest.py                        # Pytest Package Path Configuration
├── config/
│   ├── __init__.py                    # Config Package Initialization
│   ├── prompts.json                   # Centralized Agent Personas, System Prompts & SCADA Directives
│   └── prompt_config.py               # Prompt Configuration Manager & Validator
├── storage/
│   ├── orchestrator.db                # SQLite Persistent Telemetry & Audit Logs
│   └── radar_imagery/                 # Multi-Spectral Doppler Radar Frames (Multimodal D3)
├── core/
│   ├── portfolio.py                   # Domain Models: 5 Solar, 3 Wind, 2 BESS, Industrial, Grid
│   ├── solver.py                      # Security-Constrained Economic Dispatch LP Optimizer (HiGHS)
│   └── database.py                    # ACID SQLite Storage Layer
├── perception/
│   └── radar_vision.py                # Computer Vision Satellite Radar Analysis Engine
├── agents/
│   ├── base.py                        # Agent Deliberation Protocol & State Messages
│   ├── forecast_agent.py              # Meteorological & Vision Agent (Agent 1)
│   ├── market_agent.py                # Wholesale Market & Arbitrage Agent (Agent 2)
│   ├── grid_reliability_agent.py      # Grid Reliability & Asset Health Agent (Agent 3)
│   └── orchestrator_agent.py          # Chief Executive Orchestrator (Executive Agent)
├── simulation/
│   └── engine.py                      # 24-Hour (96-Interval) Stochastic Simulation Engine
├── backend/
│   └── api.py                         # Enterprise REST API Engine (FastAPI)
└── tests/
    ├── test_solver.py                 # Energy Balance & SoC Bounds Verification
    ├── test_agents.py                 # Multi-Agent Deliberation & 24h Simulation Tests
    ├── test_prompt_config.py          # Dynamic Prompt Decoupling & Rationale Template Tests
    └── test_scenarios.py              # Verification of all 7 Real-World Scenarios from Problem 4
```
