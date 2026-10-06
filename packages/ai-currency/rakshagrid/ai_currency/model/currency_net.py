# ml/module1_currency/model/currency_net.py
"""Model architecture definition and weight loader for EfficientNetB0 Currency Classifier."""

import os
from rakshagrid.common.logging.logger import setup_logger
from rakshagrid.ai_currency.config import currency_config

logger = setup_logger("rakshagrid.ai_currency.model")

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

        # Validate model weights path from centralized artifact configuration
        model_path = currency_config.MODEL_PATH
        if not os.path.exists(model_path):
            raise MissingModelArtifactError(
                f"Currency model weights not found at {model_path}. Trained model weights are required.",
                module_name="ai-currency"
            )

        model.load_weights(model_path)
        logger.info(f"Loaded currency model weights from {model_path}")

        _model = model
        return _model
    except MissingModelArtifactError:
        raise
    except Exception as e:
        logger.error(f"Error loading Tensorflow currency model: {e}")
        raise MLInferenceException(f"Failed to load currency model: {e}", module_name="ai-currency")
