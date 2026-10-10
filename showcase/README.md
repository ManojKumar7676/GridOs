# Showcase materials

This directory keeps presentation and demo assets outside the application code.

- `pitch-decks/` contains the single selected pitch deck in PDF and PowerPoint formats.
- `demo/` contains a static launch page linking to the running app, deck, docs, and screenshots.
- `media/` contains the official 4-minute demonstration video, narration script, and prompts:
  - **Online Video Stream:** [Watch on Google Drive](https://drive.google.com/file/d/1R5Kq_YbG9N30QcWxWlONRRq7RDFZDpzJ/view?usp=sharing)
  - **Local Video:** [`GridOS_Demo_Video.mp4`](media/GridOS_Demo_Video.mp4) (41.29 MB, 1080p Full HD)
  - **Narration Script:** [`DEMO_VIDEO_NARRATION.md`](media/DEMO_VIDEO_NARRATION.md)
  - **Storyboard & Prompts:** [`VIDEO_PROMPTS.html`](media/VIDEO_PROMPTS.html)
- `assets/` contains app screenshots and exported slide images.

The app is started from the repository root with `python -m streamlit run frontend/app.py --server.port 8501`.
