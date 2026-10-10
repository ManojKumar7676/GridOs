# GridOS — Renewable Energy Orchestrator

GridOS is a local prototype for renewable energy dispatch. It combines a Streamlit operations UI, a FastAPI service, a modeled 24-hour scenario, rule-based agent components, and a linear dispatch optimizer.

The project is intended for a hackathon demonstration and development. It does **not** connect to live SCADA, market, weather, or plant systems. Telemetry shown by default is simulated. Imported CSV/JSON records are kept separate from the demo data, and optimizer output is a recommendation rather than a field command.

## Run locally

Use Python 3.10 or newer. From the repository root:

```powershell
python -m venv .venv
\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run frontend/app.py --server.port 8501
```

Open [http://localhost:8501](http://localhost:8501). The **Telemetry & Replay** tab opens with a simulated 96-interval hardware-shaped data set. You can import a CSV or JSON export to view and replay measured records separately.

### Optional API

In another terminal, from the repository root:

```powershell
python -m uvicorn backend.api:app --reload --port 8000
```

The API docs are at [http://localhost:8000/docs](http://localhost:8000/docs).

## Project layout

```text
AccentureAssessment/
├── frontend/                 # Streamlit application
├── backend/                  # FastAPI, agents, optimizer, simulation, config
│   ├── agents/
│   ├── config/
│   ├── core/
│   ├── evaluation/
│   ├── perception/
│   └── simulation/
├── tests/                    # Automated tests
├── docs/                     # Architecture and developer documentation
├── scripts/                  # Application support utilities
├── showcase/                 # Pitch decks, demo portal, and video materials
├── storage/                  # Local database and generated runtime data
├── requirements.txt
└── README.md
```

## Documentation and showcase

- [Demo video (Google Drive)](https://drive.google.com/file/d/1R5Kq_YbG9N30QcWxWlONRRq7RDFZDpzJ/view?usp=sharing) · [Local MP4 (41MB)](showcase/media/GridOS_Demo_Video.mp4)
- [Pitch deck (PDF)](showcase/pitch-decks/GridOS_Pitch_Deck.pdf) · [PowerPoint](showcase/pitch-decks/GridOS_Pitch_Deck.pptx)
- [Demo portal](showcase/demo/index.html) · [Video storyboard](showcase/media/VIDEO_PROMPTS.html)
- [Showcase materials](showcase/README.md)
- [Local development and validation](docs/EXECUTION_GUIDE.md)
- [Architecture specification](docs/architecture_specification.md)
- [Architecture and flow diagrams](docs/architecture_and_flows.html)

## Configuration and local data

Copy `.env.example` to `.env` only if you need optional integrations. Keep secrets out of source control. Agent prompts are in `backend/config/prompts.json`.

The app stores its local SQLite database, agent/skill/tool definitions, user-profile metadata, and generated radar images in `storage/`. These files are local development data; user profiles do not provide authentication or role-based access control.

## Current prototype boundaries

- Hardware telemetry is disconnected. The demo readings are simulated; imported readings are not live-connected.
- API and MCP tool entries in Agent Studio are definitions only; the prototype does not execute them.
- User management stores local profile metadata and does not authenticate users.
- Weather-image analysis uses prototype heuristics and has not been validated against a labeled operational data set.
- Optimizer recommendations are software outputs and are never sent to physical equipment.

## Tests

Run the project tests from the repository root:

```powershell
python -m pytest tests/ -v
```
