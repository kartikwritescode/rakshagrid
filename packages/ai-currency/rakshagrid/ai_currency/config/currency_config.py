# packages/ai-currency/rakshagrid/ai_currency/config/currency_config.py
"""Configuration for Module 1: Counterfeit Currency Detection."""

from pathlib import Path
from rakshagrid.common.configs.base_config import artifact_config
from rakshagrid.common.constants.risk_bands import CALIBRATION

MODEL_PATH: str = str(artifact_config.resolve_model_path("currency_model.h5", required=False, module_name="ai-currency"))
IMG_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = CALIBRATION.currency_confidence_threshold

CLASS_NAMES = [
    "real",
    "fake_print_defect",
    "fake_color_shift",
    "fake_missing_thread",
    "fake_missing_microprint"
]
