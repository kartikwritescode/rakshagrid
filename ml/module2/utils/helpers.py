# ml/module2/utils/helpers.py
"""Helpers for risk threshold calibration and JSON loading."""

import os
from shared.utils.json_utils import load_json, save_json
from ml.module2.config import scam_config

def get_calibrated_thresholds() -> dict:
    """Load calibrated thresholds or return default settings."""
    calibrated = load_json(scam_config.THRESHOLDS_PATH)
    return {
        "high": calibrated.get("high", scam_config.DEFAULT_HIGH_THRESHOLD),
        "low": calibrated.get("low", scam_config.DEFAULT_MEDIUM_THRESHOLD),
        "needs_review_low": calibrated.get("needs_review_low", scam_config.DEFAULT_NEEDS_REVIEW_LOW),
        "needs_review_high": calibrated.get("needs_review_high", scam_config.DEFAULT_NEEDS_REVIEW_HIGH)
    }

def get_risk_band(score: float) -> str:
    """
    Determine the risk band for a given score.
    If the score is between low and high thresholds, it falls to needs_review.
    """
    thresholds = get_calibrated_thresholds()
    
    if score >= thresholds["high"]:
        return "high"
    elif score <= thresholds["low"]:
        return "low"
    else:
        return "needs_review"
