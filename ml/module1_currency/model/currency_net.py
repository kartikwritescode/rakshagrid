# ml/module1_currency/model/currency_net.py
"""Model architecture definition and weight loader for EfficientNetB0 Currency Classifier."""

import os
from shared.logging.logger import setup_logger
from ml.module1_currency.config import currency_config

logger = setup_logger("ml.module1_currency.model")

_model = None

def load_currency_model():
    """Lazy loads the currency model architecture and weights."""
    global _model
    if _model is not None:
        return _model

    try:
        import tensorflow as tf
        from tensorflow.keras.applications import EfficientNetB0
        from tensorflow.keras import layers, models

        base = EfficientNetB0(
            input_shape=currency_config.IMG_SIZE + (3,),
            include_top=False,
            weights=None
        )
        base.trainable = False

        model = models.Sequential([
            base,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.3),
            layers.Dense(len(currency_config.CLASS_NAMES), activation="softmax")
        ])

        # Check model path
        model_path = currency_config.MODEL_PATH
        if not os.path.exists(model_path):
            # Fallback check in legacy locations
            legacy_path = os.path.join("module1_currency", "best_model_finetuned.h5")
            if os.path.exists(legacy_path):
                model_path = legacy_path

        if os.path.exists(model_path):
            model.load_weights(model_path)
            logger.info(f"Loaded currency model weights from {model_path}")
        else:
            logger.warning(f"Currency model weights not found at {model_path}, initialized with random weights")

        _model = model
        return _model
    except Exception as e:
        logger.error(f"Error loading Tensorflow currency model: {e}")
        return None
