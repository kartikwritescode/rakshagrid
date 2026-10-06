# ml/module1_currency/preprocessing/image_processor.py
"""Image preprocessing for currency detection."""

import numpy as np
from PIL import Image
import io
from rakshagrid.ai_currency.config.currency_config import IMG_SIZE

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Loads image bytes, resizes to (224, 224), and returns normalized array batch."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize(IMG_SIZE)
    img_array = np.array(img, dtype=np.float32)
    # Expand dims to batch dimension (1, 224, 224, 3)
    img_batch = np.expand_dims(img_array, axis=0)
    return img_batch
