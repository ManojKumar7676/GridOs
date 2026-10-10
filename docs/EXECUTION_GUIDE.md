# Development and execution guide

All commands below run from the repository root.

## Requirements

- Python 3.10 or newer
- Dependencies listed in `requirements.txt`
- Optional Gemini API key for the online language-model path; the app can use its deterministic fallback without one

## Start the Streamlit UI

```powershell
python -m venv .venv
\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run frontend/app.py --server.port 8501
```

Browse to [http://localhost:8501](http://localhost:8501). The default theme is light. Open **Telemetry & Replay** to inspect the clearly labeled simulated telemetry demo or import a CSV/JSON export.

## Start the API

```powershell
python -m uvicorn backend.api:app --reload --port 8000
```

Interactive API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs). The API shares the same local prototype models; it is not a production service or hardware gateway.

## Run checks

```powershell
python -m pytest tests/ -v
```

The Streamlit UI and API can be started in separate terminals. Local data is written under `storage/`; do not commit a database containing non-public operational data.

## Optional model configuration

Copy `.env.example` to `.env`, then set `GEMINI_API_KEY` if you want the optional Gemini path. Keep `.env` private. Without a key, the application uses its deterministic fallback where supported.

## Showcase utilities

The selected PDF and PowerPoint deck are in `showcase/pitch-decks/`. Captured UI images go to `showcase/assets/screenshots/` using `scripts/capture_screenshots.py` while the app is running.

The video materials currently include a prompt/storyboard document in `showcase/media/`; there is no recorded demo video checked into this repository yet.
