# packages/ai-currency/rakshagrid/ai_currency/config.py
"""Centralized configuration for Module 1: Counterfeit Currency Identification."""

import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from rakshagrid.common.configs.base_config import artifact_config
from rakshagrid.common.constants.risk_bands import CALIBRATION


class CurrencyConfig(BaseSettings):
    """Configuration settings for EfficientNet-B0 Banknote Authenticity Engine."""
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    MODEL_PATH: Path = Field(
        default_factory=lambda: Path(
            os.getenv(
                "CURRENCY_MODEL_PATH",
                str(artifact_config.STORAGE_DIR / "models" / "currency_model.h5")
            )
        ),
        description="Canonical filesystem path to trained EfficientNetB0 currency weights"
    )

    IMG_SIZE: tuple[int, int] = (224, 224)
    CONFIDENCE_THRESHOLD: float = Field(
        default_factory=lambda: float(
            os.getenv("CURRENCY_CONFIDENCE_THRESHOLD", str(CALIBRATION.currency_confidence_threshold))
        ),
        description="Calibrated probability threshold for banknote authenticity"
    )

    MAX_UPLOAD_SIZE_BYTES: int = Field(
        default=15 * 1024 * 1024,  # 15 MB
        description="Maximum allowed image upload size in bytes"
    )

    ALLOWED_MIME_TYPES: tuple[str, ...] = (
        "image/jpeg",
        "image/png",
        "image/webp",
    )

    CLASS_NAMES: tuple[str, ...] = (
        "real",
        "fake_print_defect",
        "fake_color_shift",
        "fake_missing_thread",
        "fake_missing_microprint",
    )


currency_settings = CurrencyConfig()


def get_model_path() -> Path:
    """Returns canonical model path, prioritizing runtime environment override."""
    env_override = os.getenv("CURRENCY_MODEL_PATH")
    if env_override:
        return Path(env_override).resolve()
    return currency_settings.MODEL_PATH.resolve()


# Backwards compatibility bindings
MODEL_PATH: str = str(currency_settings.MODEL_PATH)
IMG_SIZE = currency_settings.IMG_SIZE
CONFIDENCE_THRESHOLD = currency_settings.CONFIDENCE_THRESHOLD
MAX_UPLOAD_SIZE_BYTES = currency_settings.MAX_UPLOAD_SIZE_BYTES
ALLOWED_MIME_TYPES = currency_settings.ALLOWED_MIME_TYPES
CLASS_NAMES = list(currency_settings.CLASS_NAMES)
