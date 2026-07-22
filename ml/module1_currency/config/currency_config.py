# ml/module1_currency/config/currency_config.py
"""Configuration for Module 1: Counterfeit Currency Detection."""

import os
from shared.configs.base_config import MODELS_DIR

MODEL_PATH = os.path.join(MODELS_DIR, "currency_model.h5")
IMG_SIZE = (224, 224)
CLASS_NAMES = [
    "real",
    "fake_print_defect",
    "fake_color_shift",
    "fake_missing_thread",
    "fake_missing_microprint"
]
