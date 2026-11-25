# Wire Desk: News classifier web app (hands-on guide)

## What this project does
You give it a news story. It cleans the text (spaCy), turns it into numbers (TF-IDF, 20,000 features, 1-2 word phrases),
and a LinearSVC model picks one of 7 sections:
automobile, entertainment, politics, science, sports, technology, world.
Held-out test accuracy: about 94% (weakest section: technology, about 86% F1).

## What was added
| File | What it is |
|---|---|
| `src/api/app.py` | Upgraded FastAPI app: serves the UI, `/predict` now also returns scores for all 7 sections, plus feed endpoints |
| `src/api/static/index.html` | The whole web interface (one file, no build step) |
| `src/routing/store.py` | Same routing as before, now location-proof, plus functions to read feeds |
| `GUIDE.md` | This file |

Nothing else changed. Your model files, data and training code are untouched.

## Run it (Windows PowerShell, from the project folder)
1. Open the project folder in a terminal: the folder that contains `src`, `models`, `data`.
2. Activate your environment:
   `.venv\Scripts\Activate.ps1`
   (If PowerShell blocks it: `Set-ExecutionPolicy -Scope Process Bypass` and try again.)
3. Make sure packages are installed:
   `pip install -r requirements.txt`
   `python -m spacy download en_core_web_sm`
4. Start the server:
   `uvicorn src.api.app:app --reload`
5. Open http://127.0.0.1:8000 in your browser.
   Wait about 10-20 seconds on first start (spaCy and the model load once).
6. Stop the server with Ctrl+C.

Always start it from the project root. The `src.api.app:app` path depends on it.

## Use the interface
1. Click a sample chip, or paste your own story into the box.
2. Click **Classify story** (or press Ctrl+Enter).
3. The stamp shows the winning section, and the bars show how strongly each section matched.
4. Leave **Save to the section feed** ticked to keep the story. It is appended to `data/feeds/<section>.csv`.
5. Open the **Feeds** tab to browse saved stories per section.

## Use the API directly
Interactive docs: http://127.0.0.1:8000/docs

```powershell
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{\"text\": \"India won the T20 final\", \"route\": false}"
```
Response: `{"category": "sports", "confidence": 0.97, "scores": {...}}`

| Endpoint | Purpose |
|---|---|
| `GET /` | The web interface |
| `POST /predict` | Body: `{"text": "...", "route": true}` |
| `GET /api/categories` | The 7 section names |
| `GET /api/feeds` | Saved-story count per section |
| `GET /api/feeds/{section}?limit=20` | Newest saved stories in a section |
| `GET /health` | Quick check that the server is up |

## Re-running the pipeline (only if you change data or the model)
Run from the project root, in this order:
1. `python main.py` (clean raw data into `data/processed/cleaned_news.csv`)
2. `python src/features/vectorizer.py` (fit TF-IDF, save to `models/`)
3. `python src/models/train.py` (train and save the model)
4. `python src/models/evaluate.py` (accuracy report and confusion matrix)
5. `python src/models/predict.py` (type stories in the terminal; type `quit` to exit)
Restart the server afterwards so it loads the new model files.

## Good to know
- **The bars are not true probabilities.** LinearSVC does not produce them, so the app converts its decision scores into relative shares. Treat 90%+ as "clearly this section" and anything near 50% as "unsure".
- **Short or mixed stories** (for example, a politics story about a film) get lower scores. Headline plus first paragraph works best.
- **Fonts** load from Google Fonts. Offline, the page falls back to system fonts and still works.
- **Privacy:** saved stories are plain CSV on your machine. Untick "Save to the section feed" to classify without saving.

## Troubleshooting
| Problem | Fix |
|---|---|
| `ModuleNotFoundError: src` | You started uvicorn from the wrong folder. `cd` into the project root. |
| `OSError: [E050] Can't find model 'en_core_web_sm'` | `python -m spacy download en_core_web_sm` |
| `FileNotFoundError: models/news_model.pkl` | Run steps 2 and 3 of the pipeline section. |
| Port 8000 already in use | `uvicorn src.api.app:app --port 8001` |
| Page says "Can't reach the server" | The terminal running uvicorn was closed. Start it again. |
