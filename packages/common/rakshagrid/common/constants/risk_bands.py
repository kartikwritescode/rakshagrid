# packages/common/rakshagrid/common/constants/risk_bands.py
"""Centralized, canonical risk threshold and calibration configurations across all Raksha Grid modules."""

from pydantic import BaseModel, Field

# Canonical Risk Band Labels
RISK_BAND_HIGH = "high"
RISK_BAND_LOW = "low"
RISK_BAND_NEEDS_REVIEW = "needs_review"

VALID_RISK_BANDS = [RISK_BAND_LOW, RISK_BAND_NEEDS_REVIEW, RISK_BAND_HIGH]


class RiskThresholds(BaseModel):
    """Canonical model risk score thresholds defining risk boundaries."""
    low: float = Field(0.15, description="Upper bound for low risk classification")
    high: float = Field(0.55, description="Lower bound for high risk classification")
    needs_review_low: float = Field(0.15, description="Borderline lower bound for needs_review")
    needs_review_high: float = Field(0.55, description="Borderline upper bound for needs_review")


class CalibrationConfig(BaseModel):
    """
    Explicit named calibration configurations across the platform.
    Consolidates distinct sub-tier thresholds into a single audited location.
    """
    # Canonical ensemble score thresholds
    scam_ensemble: RiskThresholds = Field(
        default_factory=lambda: RiskThresholds(low=0.15, high=0.55, needs_review_low=0.15, needs_review_high=0.55)
    )
    
    # Explicit domain calibrations:
    # 1. Rules safety override: if rule score is >= 0.30, force low ensemble score to needs_review
    rules_safety_override: float = Field(0.30, description="Rule score threshold forcing needs_review override")
    
    # 2. LLM fallback decision confidence: minimum LLM confidence to accept verdict (else fallback to review)
    llm_confidence_threshold: float = Field(0.70, description="Minimum LLM confidence required to accept decision")
    
    # 3. Currency CNN classification confidence threshold
    currency_confidence_threshold: float = Field(0.80, description="Confidence threshold for currency classifier")
    
    # 4. Geospatial DBSCAN hotspot severity density
    crime_hotspot_confidence: float = Field(0.60, description="Density threshold for crime hotspot assignment")


# Global canonical calibration instance
CALIBRATION = CalibrationConfig()

# Canonical baseline thresholds
DEFAULT_HIGH_THRESHOLD: float = CALIBRATION.scam_ensemble.high
DEFAULT_LOW_THRESHOLD: float = CALIBRATION.scam_ensemble.low
DEFAULT_NEEDS_REVIEW_LOW: float = CALIBRATION.scam_ensemble.needs_review_low
DEFAULT_NEEDS_REVIEW_HIGH: float = CALIBRATION.scam_ensemble.needs_review_high


def get_risk_band(score: float, thresholds: RiskThresholds | dict | None = None) -> str:
    """
    Canonical function to determine the risk band for a given score.
    Returns: 'low', 'needs_review', or 'high'.
    """
    if thresholds is None:
        high_val = DEFAULT_HIGH_THRESHOLD
        low_val = DEFAULT_LOW_THRESHOLD
    elif isinstance(thresholds, dict):
        high_val = thresholds.get("high", DEFAULT_HIGH_THRESHOLD)
        low_val = thresholds.get("low", DEFAULT_LOW_THRESHOLD)
    elif isinstance(thresholds, RiskThresholds):
        high_val = thresholds.high
        low_val = thresholds.low
    else:
        high_val = DEFAULT_HIGH_THRESHOLD
        low_val = DEFAULT_LOW_THRESHOLD

    if score >= high_val:
        return RISK_BAND_HIGH
    elif score <= low_val:
        return RISK_BAND_LOW
    else:
        return RISK_BAND_NEEDS_REVIEW


SCAM_CATEGORIES = [
    "authority_impersonation",
    "isolation_secrecy",
    "urgency",
    "payment_channel_switch",
    "credential_harvesting",
    "tech_support_scam",
    "utility_disconnect_scam",
    "kyc_sms_phishing",
    "subscription_phishing",
]
