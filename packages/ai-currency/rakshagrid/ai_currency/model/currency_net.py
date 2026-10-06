# packages/ai-currency/rakshagrid/ai_currency/model/currency_net.py
"""Model architecture definition, lifecycle manager, and weight loader for EfficientNetB0 Currency Classifier."""

import os
from pathlib import Path
from typing import Any, Optional
import numpy as np

from rakshagrid.common.exceptions.base import (
    MissingModelArtifactError,
    MLInferenceException,
)
from rakshagrid.common.logging.logger import setup_logger
from rakshagrid.ai_currency.config import currency_settings, get_model_path

logger = setup_logger("rakshagrid.ai_currency.model")

_model_singleton: Any = None


def build_efficientnet_architecture(
    img_size: tuple[int, int] = currency_settings.IMG_SIZE,
    num_classes: int = len(currency_settings.CLASS_NAMES),
) -> Any:
    """Constructs the canonical Sequential(EfficientNetB0 -> GAP -> Dropout(0.3) -> Dense(5)) architecture.

    Note:
        Constructed without pre-initialized random production weights.
        The returned model MUST have trained weights loaded via .load_weights() before inference.
    """
    from tensorflow.keras.applications import EfficientNetB0
    from tensorflow.keras import layers, models

    base = EfficientNetB0(
        input_shape=img_size + (3,),
        include_top=False,
        weights=None,
    )
    base.trainable = False

    model = models.Sequential([
        base,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation="softmax"),
    ])
    return model


def load_currency_model(
    model_path: Optional[str | Path] = None,
    force_reload: bool = False,
) -> Any:
    """Loads and caches the singleton EfficientNetB0 model with production weights.

    Ensures model weights are loaded strictly once per process lifecycle.
    If the model artifact is missing, raises an explicit MissingModelArtifactError.
    NEVER falls back to uninitialized or random weights for production inference.

    Args:
        model_path: Optional override path to currency_model.h5 weights.
        force_reload: If True, forces reloading weights from disk.

    Returns:
        tf.keras.Model: Ready-to-predict Keras model instance.

    Raises:
        MissingModelArtifactError: If weights file is not found at configured path.
        MLInferenceException: If TensorFlow fails to parse or load weights.
    """
    global _model_singleton
    if _model_singleton is not None and not force_reload:
        return _model_singleton

    resolved_path = Path(model_path or get_model_path()).resolve()

    if not resolved_path.exists():
        logger.error("Currency model artifact missing at canonical location: %s", resolved_path)
        raise MissingModelArtifactError(
            f"Currency model weights not found at {resolved_path}. Trained model weights are required.",
            module_name="ai-currency",
        )

    try:
        import tensorflow as tf

        # Suppress verbose TF logging during model initialization
        os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

        model = build_efficientnet_architecture()
        model.load_weights(str(resolved_path))
        logger.info("Successfully loaded canonical currency model weights from %s", resolved_path)

        _model_singleton = model
        return _model_singleton

    except MissingModelArtifactError:
        _model_singleton = None
        raise
    except Exception as exc:
        _model_singleton = None
        logger.error("TensorFlow failed to load currency model from %s: %s", resolved_path, exc)
        raise MLInferenceException(
            f"Failed to load currency model weights: {exc}",
            module_name="ai-currency",
        ) from exc


def get_model() -> Optional[Any]:
    """Returns the current loaded model instance without attempting disk load."""
    return _model_singleton


def reset_model() -> None:
    """Clears cached model singleton. Intended for test isolation."""
    global _model_singleton
    _model_singleton = None


def predict_batch(img_batch: np.ndarray, model: Optional[Any] = None) -> np.ndarray:
    """Executes forward pass inference across a batch of preprocessed banknote images.

    Args:
        img_batch: Preprocessed 4D array of shape (N, 224, 224, 3).
        model: Optional preloaded model instance. Defaults to singleton.

    Returns:
        np.ndarray: Softmax probability matrix of shape (N, 5).
    """
    active_model = model or load_currency_model()
    probs = active_model.predict(img_batch, verbose=0)
    return np.asarray(probs, dtype=np.float32)
