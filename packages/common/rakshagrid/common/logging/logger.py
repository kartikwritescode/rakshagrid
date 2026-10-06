# packages/common/rakshagrid/common/logging/logger.py
"""
Centralized logging utility for Raksha Grid with automated PII masking and structured output.

Protects citizen privacy by redacting:
- Phone numbers (+91 98765 43210 -> +91 ******43210)
- UPI IDs (user@oksbi -> u***r@oksbi)
- Bank Account Numbers (123456789012 -> ********9012)
- Bearer tokens & API Keys (Bearer ey... -> Bearer [REDACTED])
"""

import logging
import re
import sys
from typing import Any

# Regex patterns for PII scrubbing
PHONE_PATTERN = re.compile(r"(\+?91[\s-]?)?([6-9]\d{2})\d{4}(\d{3})\b")
UPI_PATTERN = re.compile(r"\b([a-zA-Z0-9._-]{1,3})[a-zA-Z0-9._-]+(@[a-zA-Z0-9.-]+)\b")
ACCOUNT_PATTERN = re.compile(r"\b\d{5,}(\d{4})\b")
BEARER_PATTERN = re.compile(r"(Bearer\s+)[A-Za-z0-9\-_.]+", re.IGNORECASE)
API_KEY_PATTERN = re.compile(r"(X-API-Key\s*[:=]\s*)[A-Za-z0-9\-_.]+", re.IGNORECASE)


def mask_phone(phone: str) -> str:
    """Masks a phone number, preserving region prefix and trailing digits."""
    if not phone:
        return ""
    return PHONE_PATTERN.sub(r"\1\2****\3", str(phone))


def mask_upi(upi: str) -> str:
    """Masks a UPI ID, preserving first character and handle domain."""
    if not upi:
        return ""
    return UPI_PATTERN.sub(r"\1***\2", str(upi))


def mask_bank_account(account: str) -> str:
    """Masks a bank account number, preserving only the last 4 digits."""
    if not account:
        return ""
    cleaned = str(account).strip()
    if len(cleaned) <= 4:
        return "****"
    return "*" * (len(cleaned) - 4) + cleaned[-4:]


def mask_pii_text(text: str) -> str:
    """Sanitizes an arbitrary string by masking phone numbers, UPI IDs, accounts, and tokens."""
    if not isinstance(text, str):
        return text

    # Mask auth tokens
    text = BEARER_PATTERN.sub(r"\1[REDACTED]", text)
    text = API_KEY_PATTERN.sub(r"\1[REDACTED]", text)

    # Mask UPI IDs
    text = UPI_PATTERN.sub(r"\1***\2", text)

    # Mask Indian phone numbers
    text = PHONE_PATTERN.sub(r"\1\2****\3", text)

    # Mask Bank account numbers (>=9 digits)
    text = re.sub(r"\b\d{5,}(\d{4})\b", r"********\1", text)

    return text


class PIIMaskingFilter(logging.Filter):
    """Logging filter that scrubs sensitive PII from log message text and arguments."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = mask_pii_text(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: (mask_pii_text(v) if isinstance(v, str) else v) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple((mask_pii_text(a) if isinstance(a, str) else a) for a in record.args)
        return True


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Configures and returns a standardized, privacy-preserving logger instance."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(PIIMaskingFilter())

        logger.addHandler(console_handler)
        logger.addFilter(PIIMaskingFilter())
        logger.propagate = False

    return logger
