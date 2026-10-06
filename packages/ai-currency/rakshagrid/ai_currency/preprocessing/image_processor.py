# packages/ai-currency/rakshagrid/ai_currency/preprocessing/image_processor.py
"""Image preprocessing and normalization for EfficientNetB0 banknote classification."""

import io
from typing import Tuple
import numpy as np
from PIL import Image

from rakshagrid.common.exceptions.base import ValidationException
from rakshagrid.ai_currency.config import currency_settings
from rakshagrid.ai_currency.preprocessing.validator import validate_image_bytes


def preprocess_image(
    image_bytes: bytes,
    target_size: Tuple[int, int] = currency_settings.IMG_SIZE,
    validate: bool = True,
    claimed_content_type: str | None = None,
) -> np.ndarray:
    """Validates raw image bytes and prepares a 4D batch tensor for model inference.

    Args:
        image_bytes: Raw bytes from the uploaded file.
        target_size: Tuple of (height, width), defaults to (224, 224).
        validate: Whether to run magic byte and decode validation first.
        claimed_content_type: Optional MIME type from HTTP header.

    Returns:
        np.ndarray: Preprocessed batch tensor of shape (1, 224, 224, 3) with float32 values.

    Raises:
        ValidationException: If image is empty, exceeds max size, or cannot be decoded.
    """
    if validate:
        validate_image_bytes(image_bytes, claimed_content_type=claimed_content_type)

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize(target_size, Image.Resampling.BILINEAR)
        img_array = np.array(img, dtype=np.float32)
        # Expand dims to batch dimension (1, height, width, 3)
        img_batch = np.expand_dims(img_array, axis=0)
        return img_batch
    except Exception as exc:
        raise ValidationException(f"Failed to preprocess banknote image: {exc}") from exc
