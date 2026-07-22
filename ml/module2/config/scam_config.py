# ml/module2/config/scam_config.py
"""Configuration settings for Module 2: Scam Call Interceptor."""

import os
from dotenv import load_dotenv
from shared.configs.base_config import BASE_DIR, MODELS_DIR

load_dotenv()

# Detect CUDA availability lazily
def has_cuda():
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

# Model paths (supports environment variable overrides or default storage paths)
TFIDF_MODEL_PATH = os.getenv("TFIDF_MODEL_PATH", os.path.join(MODELS_DIR, "tfidf_logreg.joblib"))
TFIDF_VECTORIZER_PATH = os.getenv("TFIDF_VECTORIZER_PATH", os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib"))
TRANSFORMER_MODEL_PATH = os.getenv("TRANSFORMER_MODEL_PATH", os.path.join(MODELS_DIR, "scam-transformer"))
ENSEMBLE_MODEL_PATH = os.getenv("ENSEMBLE_MODEL_PATH", os.path.join(MODELS_DIR, "ensemble_meta.joblib"))
THRESHOLDS_PATH = os.getenv("THRESHOLDS_PATH", os.path.join(MODELS_DIR, "calibrated_thresholds.json"))

# Fallback paths if not in storage/models
if not os.path.exists(TFIDF_MODEL_PATH) and os.path.exists("artifacts/tfidf_logreg.joblib"):
    TFIDF_MODEL_PATH = "artifacts/tfidf_logreg.joblib"
if not os.path.exists(TFIDF_VECTORIZER_PATH) and os.path.exists("artifacts/tfidf_vectorizer.joblib"):
    TFIDF_VECTORIZER_PATH = "artifacts/tfidf_vectorizer.joblib"
if not os.path.exists(TRANSFORMER_MODEL_PATH) and os.path.exists("artifacts/scam-transformer"):
    TRANSFORMER_MODEL_PATH = "artifacts/scam-transformer"
if not os.path.exists(ENSEMBLE_MODEL_PATH) and os.path.exists("artifacts/ensemble_meta.joblib"):
    ENSEMBLE_MODEL_PATH = "artifacts/ensemble_meta.joblib"
if not os.path.exists(THRESHOLDS_PATH) and os.path.exists("artifacts/calibrated_thresholds.json"):
    THRESHOLDS_PATH = "artifacts/calibrated_thresholds.json"

# Whisper config
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")

def get_whisper_device():
    device = os.getenv("WHISPER_DEVICE")
    if device:
        return device
    return "cuda" if has_cuda() else "cpu"

def get_whisper_compute_type():
    compute_type = os.getenv("WHISPER_COMPUTE_TYPE")
    if compute_type:
        return compute_type
    return "float16" if get_whisper_device() == "cuda" else "int8"

def get_transformer_device():
    device = os.getenv("TRANSFORMER_DEVICE")
    if device:
        return device
    return "cuda" if has_cuda() else "cpu"

# LLM Fallback config
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Default thresholds
DEFAULT_HIGH_THRESHOLD = 0.55
DEFAULT_MEDIUM_THRESHOLD = 0.12
DEFAULT_NEEDS_REVIEW_LOW = 0.12
DEFAULT_NEEDS_REVIEW_HIGH = 0.55
