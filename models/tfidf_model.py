# models/tfidf_model.py
import joblib

_vectorizer = joblib.load("artifacts/tfidf_vectorizer.joblib")
_clf = joblib.load("artifacts/tfidf_logreg.joblib")

def score_tfidf(transcript: str) -> dict:
    vec = _vectorizer.transform([transcript])
    prob = _clf.predict_proba(vec)[0][1]   # probability of class "1" (scam)
    band = "high" if prob > 0.6 else "medium" if prob > 0.3 else "low"
    return {"score": float(prob), "band": band}