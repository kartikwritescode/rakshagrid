# packages/ai-currency/rakshagrid/ai_currency/postprocessing/calibration.py
"""Calibrated probability thresholding for banknote authenticity and defect verification."""

from typing import Tuple
from rakshagrid.ai_currency.config import currency_settings


def calibrate_verdict(
    predicted_label: str,
    confidence: float,
    threshold: float | None = None,
) -> Tuple[str, bool]:
    """Applies audited probability threshold to determine authenticity and confidence flags.

    Args:
        predicted_label: Top class predicted by the classifier ('real', 'fake_print_defect', etc.).
        confidence: Softmax probability of top class.
        threshold: Decision boundary, defaults to configured currency_settings.CONFIDENCE_THRESHOLD (0.80).

    Returns:
        Tuple of (calibrated_verdict_string, is_genuine_boolean).

    Rules:
        - If label == "real" and confidence >= threshold:
            verdict: "authentic", is_genuine: True
        - If label == "real" and confidence < threshold:
            verdict: "suspicious_low_confidence", is_genuine: False (flagged for review)
        - If label != "real":
            verdict: f"counterfeit_{predicted_label}", is_genuine: False
    """
    calibrated_threshold = (
        float(threshold) if threshold is not None else currency_settings.CONFIDENCE_THRESHOLD
    )

    if predicted_label == "real":
        if confidence >= calibrated_threshold:
            return "authentic", True
        else:
            return "suspicious_low_confidence", False
    else:
        return f"counterfeit_{predicted_label}", False
