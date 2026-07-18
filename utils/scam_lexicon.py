# utils/scam_lexicon.py
import re

# URGENCY_WORDS regex pattern
URGENCY_WORDS = r"\b(immediately|urgent|now|verify|suspend|arrest|warrant|legal action|fine|penalty|act now|limited time|final notice)\b"

# MONEY_WORDS regex pattern
MONEY_WORDS = r"\b(gift card|wire transfer|bitcoin|crypto|bank account|social security|ssn|routing number|card number|cvv|otp|one[- ]time password)\b"

# AUTHORITY_WORDS regex pattern - unified with CBI/ED/police
AUTHORITY_WORDS = r"\b(irs|police|fbi|government|officer|department|agent|court|federal|cbi|ed|customs|income tax dept|cyber cell)\b"

# Centralized rules lexicon containing weights and pattern matchers
LEXICON = {
    "authority_impersonation": {
        "patterns": [
            r"\b(cbi|ed|customs|income tax dept|cyber cell|police|irs|fbi|government|officer|department|agent|court|federal)\b",
            r"\bwarrant\b",
            r"\bfir\b"
        ],
        "weight": 0.30,
    },
    "isolation_secrecy": {
        "patterns": [
            r"don'?t (disconnect|hang up|tell anyone)",
            r"stay on (the )?call",
            r"video verification"
        ],
        "weight": 0.25,
    },
    "urgency": {
        "patterns": [
            r"immediately",
            r"within (the next )?\d+ (minutes|hours)",
            r"right now",
            r"\b(urgent|suspend|arrest|legal action|fine|penalty|act now|limited time|final notice)\b"
        ],
        "weight": 0.15,
    },
    "payment_channel_switch": {
        "patterns": [
            r"\bupi\b",
            r"gift card",
            r"crypto|bitcoin",
            r"transfer.*account",
            r"\b(wire transfer|bank account|social security|ssn|routing number)\b"
        ],
        "weight": 0.30,
    },
    "credential_harvesting": {
        "patterns": [
            r"\bpassword\b",
            r"\botp\b",
            r"\bone[- ]time (password|code)\b",
            r"\bpin\b",
            r"\bcvv\b",
            r"\bcard number\b",
            r"\bverification code\b",
            r"maiden name",
            r"security question",
            r"first pet|favorite pet|childhood pet",
            r"\bnickname\b",
            r"favorite place",
            r"\b(kyc|aadhaar|pan card|pan number)\b",
            r"link.*update",
            r"suspend.*account",
            r"account.*suspend",
            r"payment method failed",
            r"subscription.*paused",
            r"update.*card details"
        ],
        "weight": 0.30,
    }
}
