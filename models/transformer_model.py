# models/transformer_model.py
import os
import torch
from transformers import AutoTokenizer
import config
from utils.helpers import get_risk_band

_tokenizer = None
_model = None
_is_quantized = False

def _load_model():
    global _tokenizer, _model, _is_quantized
    if _model is None or _tokenizer is None:
        if os.path.exists(config.TRANSFORMER_MODEL_PATH):
            try:
                _tokenizer = AutoTokenizer.from_pretrained(config.TRANSFORMER_MODEL_PATH)
                from transformers import AutoModelForSequenceClassification
                _model = AutoModelForSequenceClassification.from_pretrained(config.TRANSFORMER_MODEL_PATH)
                device = config.get_transformer_device()
                device_str = "cuda" if "cuda" in device and torch.cuda.is_available() else "cpu"
                _model = _model.to(device_str)
                _model.eval()
                _is_quantized = False
            except Exception as e:
                print(f"Error loading transformer model: {e}")
        else:
            # Silent warning, training needs to run first
            pass

def get_scam_probability(transcript: str) -> float:
    """Helper to return scam probability for the ensemble/meta-classifier."""
    _load_model()
    if _model is None or _tokenizer is None:
        return 0.5  # Fallback probability
    try:
        inputs = _tokenizer(
            transcript,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # If model is on CUDA, move inputs to CUDA, else CPU
        if not _is_quantized and next(_model.parameters()).is_cuda:
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        else:
            inputs = {k: v.to("cpu") for k, v in inputs.items()}
            
        with torch.no_grad():
            outputs = _model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)
            scam_prob = float(probs[0][1].item())
            return scam_prob
    except Exception as e:
        print(f"Error during transformer prediction: {e}")
        return 0.5

def score_transformer(transcript: str) -> dict:
    """Returns scored transcript with transformer model and risk band."""
    prob = get_scam_probability(transcript)
    band = get_risk_band(prob)
    return {"score": prob, "band": band}