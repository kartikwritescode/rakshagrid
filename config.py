import os
from dotenv import load_dotenv

# Load env vars from .env file
load_dotenv()

# Detect CUDA availability lazily
def has_cuda():
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

# Model paths
TFIDF_MODEL_PATH = os.getenv("TFIDF_MODEL_PATH", "artifacts/tfidf_logreg.joblib")
TFIDF_VECTORIZER_PATH = os.getenv("TFIDF_VECTORIZER_PATH", "artifacts/tfidf_vectorizer.joblib")
TRANSFORMER_MODEL_PATH = os.getenv("TRANSFORMER_MODEL_PATH", "artifacts/scam-transformer")
ENSEMBLE_MODEL_PATH = os.getenv("ENSEMBLE_MODEL_PATH", "artifacts/ensemble_meta.joblib")
THRESHOLDS_PATH = os.getenv("THRESHOLDS_PATH", "artifacts/calibrated_thresholds.json")

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

# CORS settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Fallback thresholds if calibration file doesn't exist
DEFAULT_HIGH_THRESHOLD = 0.70
DEFAULT_MEDIUM_THRESHOLD = 0.35
DEFAULT_NEEDS_REVIEW_LOW = 0.35
DEFAULT_NEEDS_REVIEW_HIGH = 0.65
