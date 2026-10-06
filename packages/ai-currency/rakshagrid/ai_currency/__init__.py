# packages/ai-currency/rakshagrid/ai_currency/__init__.py
"""Module 1: Banknote Authenticity Engine (EfficientNetB0)."""

from rakshagrid.ai_currency.config import currency_settings, get_model_path
from rakshagrid.ai_currency.schemas import CurrencyResponse, CurrencyValidationResult
from rakshagrid.ai_currency.service import CurrencyService, currency_service, predict
from rakshagrid.ai_currency.preprocessing.validator import (
    validate_image_bytes,
    detect_mime_from_magic_bytes,
    safe_temporary_image,
)
from rakshagrid.ai_currency.preprocessing.image_processor import preprocess_image
from rakshagrid.ai_currency.model.currency_net import (
    load_currency_model,
    build_efficientnet_architecture,
    predict_batch,
    reset_model,
    get_model,
)
from rakshagrid.ai_currency.postprocessing.calibration import calibrate_verdict
from rakshagrid.ai_currency.postprocessing.classifier import format_prediction

__all__ = [
    # Config & Settings
    "currency_settings",
    "get_model_path",
    # Schemas
    "CurrencyResponse",
    "CurrencyValidationResult",
    # Service & Functional Entrypoints
    "CurrencyService",
    "currency_service",
    "predict",
    # Preprocessing & Validation
    "validate_image_bytes",
    "detect_mime_from_magic_bytes",
    "safe_temporary_image",
    "preprocess_image",
    # Model
    "load_currency_model",
    "build_efficientnet_architecture",
    "predict_batch",
    "reset_model",
    "get_model",
    # Postprocessing & Calibration
    "calibrate_verdict",
    "format_prediction",
]
