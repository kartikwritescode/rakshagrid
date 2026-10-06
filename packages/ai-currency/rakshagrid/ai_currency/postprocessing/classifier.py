# packages/ai-currency/rakshagrid/ai_currency/postprocessing/classifier.py
"""Postprocessing logic for currency detection probabilities and structured defect verdicts."""

from typing import Any, Dict, Optional
import numpy as np

from rakshagrid.ai_currency.config import currency_settings
from rakshagrid.ai_currency.postprocessing.calibration import calibrate_verdict


def format_prediction(
    probabilities: np.ndarray,
    threshold: Optional[float] = None,
    processing_time_ms: Optional[float] = None,
) -> Dict[str, Any]:
    """Transforms raw softmax probabilities into a structured banknote classification verdict.

    Args:
        probabilities: Softmax probability array of shape (1, 5) or (5,).
        threshold: Optional override for calibrated authenticity threshold.
        processing_time_ms: Optional latency measurement.

    Returns:
        Dict conforming to CurrencyResponse schema.
    """
    probs = np.squeeze(probabilities)
    if probs.ndim != 1 or len(probs) != len(currency_settings.CLASS_NAMES):
        raise ValueError(
            f"Expected probability vector of length {len(currency_settings.CLASS_NAMES)}, received shape {probs.shape}"
        )

    top_idx = int(np.argmax(probs))
    predicted_class = currency_settings.CLASS_NAMES[top_idx]
    confidence = float(probs[top_idx])

    applied_threshold = (
        float(threshold) if threshold is not None else currency_settings.CONFIDENCE_THRESHOLD
    )
    calibrated_verdict_str, is_real = calibrate_verdict(
        predicted_class,
        confidence,
        threshold=applied_threshold,
    )

    defect_breakdown = {
        cls_name: round(float(prob), 4)
        for cls_name, prob in zip(currency_settings.CLASS_NAMES, probs)
    }

    result = {
        "status": "genuine" if is_real else "counterfeit",
        "predicted_label": predicted_class,
        "confidence": round(confidence, 4),
        "is_genuine": is_real,
        "class_probabilities": defect_breakdown,
        "calibrated_verdict": calibrated_verdict_str,
        "confidence_threshold": round(applied_threshold, 4),
        "processing_time_ms": round(processing_time_ms, 2) if processing_time_ms is not None else None,
    }

    return result
