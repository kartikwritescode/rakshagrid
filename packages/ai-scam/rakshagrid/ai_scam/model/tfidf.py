# packages/ai-scam/rakshagrid/ai_scam/model/tfidf.py
"""TF-IDF + Logistic Regression model wrapper."""

import os
import joblib
from rakshagrid.common.exceptions.base import MissingModelArtifactError, MLInferenceException
from rakshagrid.ai_scam.config import scam_config
from rakshagrid.ai_scam.utils.helpers import get_risk_band

_vectorizer = None
_clf = None

def _load_model():
    global _vectorizer, _clf
    if _vectorizer is None or _clf is None:
        if os.path.exists(scam_config.TFIDF_VECTORIZER_PATH) and os.path.exists(scam_config.TFIDF_MODEL_PATH):
            try:
                _vectorizer = joblib.load(scam_config.TFIDF_VECTORIZER_PATH)
                _clf = joblib.load(scam_config.TFIDF_MODEL_PATH)
            except Exception as e:
                raise MLInferenceException(f"Error loading TF-IDF model artifacts: {e}", module_name="ai-scam")
        else:
            raise MissingModelArtifactError(
                f"TF-IDF model artifacts missing: vectorizer={scam_config.TFIDF_VECTORIZER_PATH}, model={scam_config.TFIDF_MODEL_PATH}",
                module_name="ai-scam"
            )

def get_scam_probability(transcript: str) -> float:
    """Helper to return scam probability for the ensemble/meta-classifier."""
    _load_model()
    if _vectorizer is None or _clf is None:
        raise MissingModelArtifactError("TF-IDF vectorizer and classifier not initialized", module_name="ai-scam")
    try:
        vec = _vectorizer.transform([transcript])
        prob = _clf.predict_proba(vec)[0][1]
        return float(prob)
    except Exception as e:
        raise MLInferenceException(f"Error during TF-IDF prediction: {e}", module_name="ai-scam")

def score_tfidf(transcript: str) -> dict:
    """Returns scored transcript with TF-IDF and risk band."""
    prob = get_scam_probability(transcript)
    band = get_risk_band(prob)
    return {"score": prob, "band": band}
