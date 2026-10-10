# Showcase materials

This directory keeps presentation and demo assets outside the application code.

- `pitch-decks/` contains the official 11-slide pitch deck in PDF and PowerPoint formats:
  - **PDF Presentation:** [`GridOS_Pitch_Deck.pdf`](pitch-decks/GridOS_Pitch_Deck.pdf) (11 Slides)
  - **PowerPoint Presentation:** [`GridOS_Pitch_Deck.pptx`](pitch-decks/GridOS_Pitch_Deck.pptx) (11 Slides)
- `demo/` contains a static launch page linking to the running app, deck, docs, and screenshots.
- `media/` contains the official 3-minute 50-second demonstration video, narration script, and prompts:
  - **Online Video Stream:** [Watch on Google Drive](https://drive.google.com/file/d/1R5Kq_YbG9N30QcWxWlONRRq7RDFZDpzJ/view?usp=sharing)
  - **Local Video:** [`GridOS_Demo_Video.mp4`](media/GridOS_Demo_Video.mp4) (40.78 MB, 3m 50s, 1080p Full HD)
  - **Narration Script:** [`DEMO_VIDEO_NARRATION.md`](media/DEMO_VIDEO_NARRATION.md)
  - **Storyboard & Prompts:** [`VIDEO_PROMPTS.html`](media/VIDEO_PROMPTS.html)
- `assets/` contains app screenshots and exported slide images.

The app is started from the repository root with `python -m streamlit run frontend/app.py --server.port 8501`.
