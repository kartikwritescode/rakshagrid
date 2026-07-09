import os
import torch
from dotenv import load_dotenv

# Load env vars from .env file
load_dotenv()

# Detect CUDA availability
HAS_CUDA = torch.cuda.is_available()

# Model paths
TFIDF_MODEL_PATH = os.getenv("TFIDF_MODEL_PATH", "artifacts/tfidf_logreg.joblib")
TFIDF_VECTORIZER_PATH = os.getenv("TFIDF_VECTORIZER_PATH", "artifacts/tfidf_vectorizer.joblib")
TRANSFORMER_MODEL_PATH = os.getenv("TRANSFORMER_MODEL_PATH", "artifacts/scam-transformer")
ENSEMBLE_MODEL_PATH = os.getenv("ENSEMBLE_MODEL_PATH", "artifacts/ensemble_meta.joblib")
THRESHOLDS_PATH = os.getenv("THRESHOLDS_PATH", "artifacts/calibrated_thresholds.json")

# Whisper config
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
# Default to cuda if available, otherwise cpu
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cuda" if HAS_CUDA else "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "float16" if WHISPER_DEVICE == "cuda" else "int8")

# Transformer config
TRANSFORMER_DEVICE = os.getenv("TRANSFORMER_DEVICE", "cuda" if HAS_CUDA else "cpu")

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
