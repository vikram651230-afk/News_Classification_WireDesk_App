# Lifecycle stage 7 — Model Testing
 
import joblib
try:
    from ..data.preprocess import clean_text
except ImportError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.data.preprocess import clean_text
 
model = joblib.load("models/news_model.pkl")
 
vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
 
while True:
 
    text = input("\nEnter News: ")
    if text.lower().strip() in {"quit", "exit"}:
        break
 
    X = vectorizer.transform([clean_text(text)])
 
    prediction = model.predict(X)
 
    print("\nPrediction:", prediction[0])
