from pathlib import Path

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from src.data.preprocess import clean_text
from src.routing.store import route_article, read_feed, feed_counts

BASE_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="News Classifier", version="2.0")

model = joblib.load(BASE_DIR / "models" / "news_model.pkl")
vectorizer = joblib.load(BASE_DIR / "models" / "tfidf_vectorizer.pkl")

CATEGORIES = [str(c) for c in model.classes_]


class Article(BaseModel):
    text: str = Field(..., min_length=1)
    route: bool = True  # save the article into data/feeds/<category>.csv


def score_article(text):
    """Return (best_category, {category: match share}).

    LinearSVC has no predict_proba, so the shares come from a softmax over
    its decision scores. Read them as "how strongly each category matches",
    not as calibrated probabilities.
    """

    X = vectorizer.transform([clean_text(text)])
    d = model.decision_function(X)[0]

    e = np.exp((d - d.max()) * 3.0)
    shares = e / e.sum()

    scores = {c: round(float(s), 4) for c, s in zip(CATEGORIES, shares)}
    best = CATEGORIES[int(np.argmax(d))]

    return best, scores


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/predict")
def predict(article: Article):

    if not article.text.strip():
        raise HTTPException(status_code=422, detail="Article text is empty.")

    category, scores = score_article(article.text)

    if article.route:
        route_article(article.text, category)

    return {
        "category": category,
        "confidence": scores[category],
        "scores": scores,
    }


@app.get("/api/categories")
def categories():
    return {"categories": CATEGORIES}


@app.get("/api/feeds")
def feeds():
    counts = feed_counts()
    return {"counts": {c: counts.get(c, 0) for c in CATEGORIES}}


@app.get("/api/feeds/{category}")
def feed(category: str, limit: int = 20):

    if category not in CATEGORIES:
        raise HTTPException(status_code=404, detail="Unknown category.")

    return {"category": category, "items": read_feed(category, min(limit, 100))}


@app.get("/health")
def health():
    return {"status": "ok", "categories": len(CATEGORIES)}
