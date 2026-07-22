# shared/constants/risk_bands.py
"""Centralized risk band constants across all modules."""

RISK_BAND_HIGH = "high"
RISK_BAND_LOW = "low"
RISK_BAND_NEEDS_REVIEW = "needs_review"

DEFAULT_HIGH_THRESHOLD = 0.55
DEFAULT_LOW_THRESHOLD = 0.12

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
