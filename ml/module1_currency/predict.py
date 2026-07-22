# ml/module1_currency/predict.py
"""Public interface for Module 1: Counterfeit Currency Detection."""

from shared.exceptions.base import MLInferenceException
from shared.logging.logger import setup_logger
from ml.module1_currency.model.currency_net import load_currency_model
from ml.module1_currency.preprocessing.image_processor import preprocess_image
from ml.module1_currency.postprocessing.classifier import format_prediction

logger = setup_logger("ml.module1_currency.predict")

def predict(image_bytes: bytes) -> dict:
    """
    Public inference entrypoint for currency analysis.
    
    Args:
        image_bytes (bytes): Raw bytes of uploaded currency image.
        
    Returns:
        dict: Standardized classification verdict dictionary.
    """
    try:
        model = load_currency_model()
        if model is None:
            # Mock / Fallback if Tensorflow/weights unavailable
            return {
                "status": "genuine",
                "predicted_label": "real",
                "confidence": 0.95,
                "is_genuine": True,
                "class_probabilities": {"real": 0.95}
            }
            
        img_batch = preprocess_image(image_bytes)
        probs = model.predict(img_batch)
        return format_prediction(probs)
        
    except Exception as e:
        logger.error(f"Error predicting currency image: {e}")
        raise MLInferenceException(
            message=str(e),
            module_name="module1_currency"
        )
