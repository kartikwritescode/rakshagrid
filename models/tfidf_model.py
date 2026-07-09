# models/tfidf_model.py
import joblib
import os
import config
from utils.helpers import get_risk_band

_vectorizer = None
_clf = None

def _load_model():
    global _vectorizer, _clf
    if _vectorizer is None or _clf is None:
        if os.path.exists(config.TFIDF_VECTORIZER_PATH) and os.path.exists(config.TFIDF_MODEL_PATH):
            try:
                _vectorizer = joblib.load(config.TFIDF_VECTORIZER_PATH)
                _clf = joblib.load(config.TFIDF_MODEL_PATH)
            except Exception as e:
                print(f"Error loading TF-IDF model artifacts: {e}")
        else:
            # Silent warning, as training script needs to run first
            pass

def get_scam_probability(transcript: str) -> float:
    """Helper to return scam probability for the ensemble/meta-classifier."""
    _load_model()
    if _vectorizer is None or _clf is None:
        return 0.5  # Fallback default probability
    try:
        vec = _vectorizer.transform([transcript])
        prob = _clf.predict_proba(vec)[0][1]
        return float(prob)
    except Exception as e:
        print(f"Error during TF-IDF prediction: {e}")
        return 0.5

def score_tfidf(transcript: str) -> dict:
    """Returns scored transcript with TF-IDF and risk band."""
    prob = get_scam_probability(transcript)
    band = get_risk_band(prob)
    return {"score": prob, "band": band}