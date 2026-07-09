# models/ensemble.py
import os
import joblib
import config
from utils.helpers import get_risk_band

_clf = None

def _load_model():
    global _clf
    if _clf is None:
        if os.path.exists(config.ENSEMBLE_MODEL_PATH):
            try:
                _clf = joblib.load(config.ENSEMBLE_MODEL_PATH)
            except Exception as e:
                print(f"Error loading ensemble meta-model: {e}")

def score_ensemble(tfidf_prob: float, transformer_prob: float, rules_score: float, eng_feats: dict) -> dict:
    """
    Combines outputs of TF-IDF, Transformer, and Rules along with 9 engineered features
    using a trained meta-classifier (HistGradientBoostingClassifier or LogisticRegression).
    Falls back to a weighted average if model is not loaded.
    """
    _load_model()
    
    # Feature list ordered EXACTLY as during training
    feats = [
        tfidf_prob,
        transformer_prob,
        rules_score,
        eng_feats["turn_count"],
        eng_feats["char_len"],
        eng_feats["word_count"],
        eng_feats["placeholder_count"],
        eng_feats["urgency_word_count"],
        eng_feats["money_word_count"],
        eng_feats["authority_word_count"],
        eng_feats["has_phone_number"],
        eng_feats["exclaim_count"]
    ]
    
    if _clf is not None:
        try:
            # Predict probability of class 1 (scam)
            prob = float(_clf.predict_proba([feats])[0][1])
            band = get_risk_band(prob)
            return {"score": prob, "band": band, "method": "ensemble_stacking"}
        except Exception as e:
            print(f"Ensemble meta-model prediction error: {e}")
            
    # Fallback: Weighted average
    weighted_score = (rules_score * 0.20) + (tfidf_prob * 0.30) + (transformer_prob * 0.50)
    band = get_risk_band(weighted_score)
    return {"score": weighted_score, "band": band, "method": "weighted_average_fallback"}

# Load the model eagerly at import time to prevent OpenMP collision with PyTorch
_load_model()
