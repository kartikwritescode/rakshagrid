# ml/module1_currency/postprocessing/classifier.py
"""Postprocessing logic for currency detection probabilities."""

import numpy as np
from ml.module1_currency.config.currency_config import CLASS_NAMES

def format_prediction(probabilities: np.ndarray) -> dict:
    """Formats softmax probabilities into structured classification result."""
    probs = probabilities[0]
    top_idx = int(np.argmax(probs))
    predicted_class = CLASS_NAMES[top_idx]
    confidence = float(probs[top_idx])
    
    is_real = (predicted_class == "real")
    
    defect_breakdown = {
        cls_name: float(prob)
        for cls_name, prob in zip(CLASS_NAMES, probs)
    }
    
    return {
        "status": "genuine" if is_real else "counterfeit",
        "predicted_label": predicted_class,
        "confidence": round(confidence, 4),
        "is_genuine": is_real,
        "class_probabilities": defect_breakdown
    }
