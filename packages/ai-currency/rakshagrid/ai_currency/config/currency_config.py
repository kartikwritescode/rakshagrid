# packages/ai-currency/rakshagrid/ai_currency/config/currency_config.py
"""Configuration forwarder for currency detection."""

from rakshagrid.ai_currency.config import (
    CurrencyConfig,
    currency_settings,
    get_model_path,
    MODEL_PATH,
    IMG_SIZE,
    CONFIDENCE_THRESHOLD,
    MAX_UPLOAD_SIZE_BYTES,
    ALLOWED_MIME_TYPES,
    CLASS_NAMES,
)

__all__ = [
    "CurrencyConfig",
    "currency_settings",
    "get_model_path",
    "MODEL_PATH",
    "IMG_SIZE",
    "CONFIDENCE_THRESHOLD",
    "MAX_UPLOAD_SIZE_BYTES",
    "ALLOWED_MIME_TYPES",
    "CLASS_NAMES",
]
