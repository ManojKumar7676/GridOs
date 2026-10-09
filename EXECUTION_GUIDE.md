# 🚀 Accenture GridOS™ — Complete Execution & Verification Guide
## Problem Statement 4: Utilities – Autonomous Renewable Energy Orchestrator
**Hackathon:** The Economic Times × Accenture AI Hackathon (Agentic Edition)  
**Self-Declared Evaluation Grid Position:** **Level F3 – Level D3** (Highest Possible Coverage)  
**Codebase Directory:** `C:\Users\paddu\Downloads\AccentureAssessment`

---

## 🤖 1. AI & LLM Architecture Overview: Which Models Are Used?

### Multi-Tier Hybrid AI Architecture
Power utility grids operate under strict **NERC / IEEE reliability mandates** where mathematical hallucinations or network violations can cause physical blackout events. To achieve both **strategic intelligence** and **100% mathematical reliability**, Accenture GridOS™ utilizes a **hybrid multi-tier AI architecture**:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           1. MULTIMODAL PERCEPTION TIER                         │
│  - Engine: Doppler CV Tensor Segmentation (OpenCV / NumPy / WSR-88D Ingestion)   │
│  - Vision LLM Support: Google Gemini 1.5 Pro / GPT-4o Vision API                │
│  - Output: Cloud optical opacity (0-100%), localized solar derating, gust front │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           2. AGENTIC DELIBERATION TIER                          │
│  - Master Framework: 4 Collaborative Autonomous Agents (JSON Prompt Config)      │
│  - Primary LLM Compatibility:                                                   │
│    • OpenAI GPT-4o / GPT-4o-mini (Function Calling / Structured Outputs)        │
│    • Anthropic Claude 3.5 Sonnet (Multi-Step Contingency Reasoning)             │
│    • Google Gemini 1.5 Pro / 2.0 Flash (Fast Multi-Agent Coordination)          │
│    • Open-Source Llama 3 / Mistral (Air-Gapped SCADA On-Premise via Ollama/vLLM)│
│  - Built-in High-Reliability Engine: Deterministic Python Domain Expert Engine   │
│    (Runs 100% offline with ZERO API key dependencies, zero token cost, and 0ms  │
│     latency, fully reproducible in any evaluation environment)                  │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    3. DETERMINISTIC MATHEMATICAL SOLVER TIER                    │
│  - Engine: scipy.optimize.linprog with HiGHS Dual-Simplex Solver                │
│  - Output: 13-Variable Decision Matrix guaranteeing EXACT Kirchhoff balance     │
│    (Sum of Generation = Sum of Load to Δ = 0.00 MW) & BESS SoC bounds (10%-95%) │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Prompt & Configuration Externalization
All agent system prompts, roles, specialized domains, skills, step-by-step instructions, and actuator tool definitions are fully externalized in:
* **JSON Prompt Configuration:** [`config/prompts.json`](config/prompts.json)
* **Python Manager:** [`config/prompt_config.py`](config/prompt_config.py)

---

## 🛠️ 2. System Requirements & Prerequisites

* **Operating System:** Windows 10/11, Linux (Ubuntu 20.04+), or macOS
* **Python Version:** Python 3.10, 3.11, 3.12, 3.13, or 3.14
* **Required Libraries:**
  ```text
  streamlit
  scipy
  numpy
  pandas
  pydantic
  pytest
  fastapi (optional for REST endpoints)
  uvicorn (optional for REST endpoints)
  ```

---

## ⚡ 3. Quickstart: Step-by-Step Execution

### Step 1: Open PowerShell / Terminal in Project Directory
```powershell
cd C:\Users\paddu\Downloads\AccentureAssessment
```

### Step 2: Set Python Path (Windows PowerShell)
Ensure Python can resolve the root package module:
```powershell
$env:PYTHONPATH = "c:\Users\paddu\Downloads"
```
*(On Linux/macOS, use: `export PYTHONPATH="/path/to/downloads"`)*

---

### Step 3: Launch the Full Interactive Working Demo (Streamlit Console)
Execute the following command to start the SCADA Dispatch Operations Console:
```powershell
python -m streamlit run app.py --server.port 8501
```
The application will launch in your browser at:
👉 **`http://localhost:8501`**

#### 🧭 What to Inspect in the Demo (Tab by Tab):
1. **Tab 1 — 🎛️ Problem Statement 4 Core Resolution Station:**
   * Pick any of the **7 Real-World Operational Shocks** (Cloud Deck, Gale Storm Cut-out, Price Spike, Negative Pricing, Battery Outage, Transmission Congestion, Industrial Demand Surge) or Routine Baseline.
   * View the **Pre-Disruption vs. Autonomous Resolution Diagnosis**.
   * Inspect the **13-Variable HiGHS Linear Programming Dispatch Vector**.
   * Verify the **Exact Energy Balance Conservation** ($\Delta = 0.00\,\text{MW}$).
   * Audit the **Executed Action Cluster** across all 5 categories with physical SCADA command codes and engineering rationales.
2. **Tab 2 — 📖 Problem Statement 4 Blueprint & Architecture:**
   * In-depth problem statement breakdown and 9-Blocker (F3-D3) evidence.
   * Interactive live viewer of `architecture_and_flows.html`.
   * Direct **"Download HTML Blueprint"** button.
3. **Tab 3 — 🛰️ Multimodal Radar Vision Station:**
   * WSR-88D Doppler radar reflectivity array processing.
   * Localized optical cloud attenuation calculation per solar plant.
4. **Tab 4 — 📊 24-Hour Diurnal Analytics:**
   * 96-interval diurnal simulation player with continuous BESS State-of-Charge tracking.
5. **Tab 5 — 🗺️ Physical Asset Registry:**
   * Comprehensive geospatial parameters for all 5 solar farms, 3 wind farms, 2 BESS units, 3 industrial loads, and the 500kV intertie.
6. **Tab 6 — 📜 SCADA Database & Audit Trail:**
   * Live ACID SQLite telemetry table with downloadable CSV export.
7. **Tab 7 — ⚙️ Agent Prompts & Configuration:**
   * Transparent inspection console displaying the system prompts, skills, operating instructions, and actuator tools for all 4 agents.

---

### Step 4: Run the Automated Pytest Verification Suite
Run the 20-test automated test suite validating all scenarios, constraints, and prompt configurations:
```powershell
$env:PYTHONPATH = "c:\Users\paddu\Downloads"; python -m pytest tests/ -v
```

**Expected Test Output (100% Green):**
```text
tests/test_agents.py::test_multi_agent_orchestration PASSED              [  5%]
tests/test_agents.py::test_full_24h_simulation PASSED                    [ 10%]
tests/test_prompt_config.py::test_prompt_config_loads_all_agents PASSED  [ 15%]
tests/test_prompt_config.py::test_prompt_config_system_prompts_not_empty PASSED [ 20%]
tests/test_prompt_config.py::test_prompt_config_formatters PASSED        [ 25%]
tests/test_prompt_config.py::test_prompt_config_all_five_action_categories_rationales PASSED [ 30%]
tests/test_prompt_config.py::test_prompt_config_custom_file_override PASSED [ 35%]
tests/test_prompt_config.py::test_prompt_config_skills_instructions_tools PASSED [ 40%]
tests/test_scenarios.py::test_scenario_1_clouds_reduce_solar PASSED      [ 45%]
tests/test_scenarios.py::test_scenario_2_wind_storm_cutout PASSED        [ 50%]
tests/test_scenarios.py::test_scenario_3_electricity_price_spike PASSED  [ 55%]
tests/test_scenarios.py::test_scenario_4_negative_electricity_pricing PASSED [ 60%]
tests/test_scenarios.py::test_scenario_5_battery_becomes_unavailable PASSED [ 65%]
tests/test_scenarios.py::test_scenario_6_transmission_line_congested PASSED [ 70%]
tests/test_scenarios.py::test_scenario_7_industrial_demand_surge PASSED  [ 75%]
tests/test_scenarios.py::test_all_five_action_categories_present PASSED  [ 80%]
tests/test_scenarios.py::test_multimodal_vision_real_image_ingestion PASSED [ 85%]
tests/test_solver.py::test_energy_conservation_balance PASSED            [ 90%]
tests/test_solver.py::test_bess_soc_limits PASSED                        [ 95%]
tests/test_solver.py::test_negative_pricing_export_suppression PASSED    [100%]

============================= 20 passed in ~4.5s ==============================
```

---

### Step 5: View the Standalone Structural Architecture Blueprint
Open the generated HTML architecture blueprint directly in your browser:
* Double click or open in browser:  
  👉 **`C:\Users\paddu\Downloads\AccentureAssessment\architecture_and_flows.html`**

Features 5 interactive Mermaid.js vector diagrams:
1. **Figure 1**: Full Technical Architecture
2. **Figure 2**: Functional Sequence Flow across the 15-Minute Cycle
3. **Figure 3**: Logical Decision Tree & Contingency Handling State Machine
4. **Figure 4**: Enterprise Kubernetes / Docker / Edge Deployment Topology
5. **Figure 5**: Industrial SCADA Protocol Integration (IEC 61850, DNP3, IEEE C37.118, OpenADR)

---

### Step 6: (Optional) Run the FastAPI REST Headless Daemon
If you wish to interact with GridOS programmatically via JSON REST API:
```powershell
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
```
* **Swagger API Docs:** `http://localhost:8000/docs`
* **Health Check:** `http://localhost:8000/api/v1/health`
* **Single-Interval Dispatch:** `POST http://localhost:8000/api/v1/dispatch/interval`

