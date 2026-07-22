# ml/module2/model/transformer.py
"""Fine-tuned DistilBERT transformer model wrapper."""

import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from ml.module2.config import scam_config
from ml.module2.utils.helpers import get_risk_band

_tokenizer = None
_model = None
_device = None

def _load_model():
    global _tokenizer, _model, _device
    if _tokenizer is None or _model is None:
        model_path = scam_config.TRANSFORMER_MODEL_PATH
        if os.path.exists(model_path):
            try:
                _device = scam_config.get_transformer_device()
                _tokenizer = AutoTokenizer.from_pretrained(model_path)
                
                quantized_path = os.path.join(model_path, "quantized_model.pt")
                if _device == "cpu" and os.path.exists(quantized_path):
                    try:
                        _model = torch.jit.load(quantized_path, map_location="cpu")
                        _model.eval()
                        return
                    except Exception as e:
                        print(f"Failed to load PyTorch quantized model: {e}")

                _model = AutoModelForSequenceClassification.from_pretrained(model_path)
                _model.to(_device)
                _model.eval()
            except Exception as e:
                print(f"Error loading Fine-Tuned Transformer model artifacts: {e}")

def get_scam_probability(transcript: str) -> float:
    """Helper to return scam probability for the ensemble/meta-classifier."""
    _load_model()
    if _tokenizer is None or _model is None:
        return 0.5

    try:
        inputs = _tokenizer(
            transcript,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )

        if not isinstance(_model, torch.jit.ScriptModule):
            inputs = {k: v.to(_device) for k, v in inputs.items()}

        with torch.no_grad():
            if isinstance(_model, torch.jit.ScriptModule):
                logits = _model(inputs["input_ids"], inputs["attention_mask"])
            else:
                outputs = _model(**inputs)
                logits = outputs.logits

            probs = torch.softmax(logits, dim=-1)
            scam_prob = float(probs[0][1].item())
            return scam_prob
    except Exception as e:
        print(f"Error during Transformer prediction: {e}")
        return 0.5

def score_transformer(transcript: str) -> dict:
    """Returns scored transcript with Fine-Tuned Transformer and risk band."""
    prob = get_scam_probability(transcript)
    band = get_risk_band(prob)
    return {"score": prob, "band": band}

_load_model()
