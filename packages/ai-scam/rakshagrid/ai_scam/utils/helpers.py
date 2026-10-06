# packages/ai-scam/rakshagrid/ai_scam/utils/helpers.py
"""Helpers for risk threshold calibration and JSON loading."""

import os
from rakshagrid.common.utils.json_utils import load_json, save_json
from rakshagrid.common.constants.risk_bands import (
    get_risk_band as canonical_get_risk_band,
    DEFAULT_HIGH_THRESHOLD,
    DEFAULT_LOW_THRESHOLD,
    DEFAULT_NEEDS_REVIEW_LOW,
    DEFAULT_NEEDS_REVIEW_HIGH,
)
from rakshagrid.ai_scam.config import scam_config

def get_calibrated_thresholds() -> dict:
    """Load calibrated thresholds or return canonical default settings."""
    calibrated = load_json(scam_config.THRESHOLDS_PATH)
    return {
        "high": calibrated.get("high", DEFAULT_HIGH_THRESHOLD),
        "low": calibrated.get("low", DEFAULT_LOW_THRESHOLD),
        "needs_review_low": calibrated.get("needs_review_low", DEFAULT_NEEDS_REVIEW_LOW),
        "needs_review_high": calibrated.get("needs_review_high", DEFAULT_NEEDS_REVIEW_HIGH)
    }

def get_risk_band(score: float) -> str:
    """
    Determine the risk band for a given score using calibrated or canonical thresholds.
    """
    thresholds = get_calibrated_thresholds()
    return canonical_get_risk_band(score, thresholds=thresholds)
