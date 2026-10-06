# packages/ai-scam/rakshagrid/ai_scam/config/scam_config.py
"""Configuration settings for Module 2: Scam Call Interceptor."""

import os
from pathlib import Path
from dotenv import load_dotenv
from rakshagrid.common.configs.base_config import BASE_DIR, artifact_config
from rakshagrid.common.constants.risk_bands import (
    CALIBRATION,
    DEFAULT_HIGH_THRESHOLD,
    DEFAULT_LOW_THRESHOLD,
    DEFAULT_NEEDS_REVIEW_LOW,
    DEFAULT_NEEDS_REVIEW_HIGH,
)

load_dotenv()

# Detect CUDA availability lazily
def has_cuda():
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

# Model paths resolved via centralized artifact configuration
TFIDF_MODEL_PATH = os.getenv(
    "TFIDF_MODEL_PATH",
    str(artifact_config.resolve_model_path("tfidf_logreg.joblib", required=False, module_name="ai-scam"))
)
TFIDF_VECTORIZER_PATH = os.getenv(
    "TFIDF_VECTORIZER_PATH",
    str(artifact_config.resolve_model_path("tfidf_vectorizer.joblib", required=False, module_name="ai-scam"))
)
TRANSFORMER_MODEL_PATH = os.getenv(
    "TRANSFORMER_MODEL_PATH",
    str(artifact_config.resolve_model_path("scam-transformer", required=False, module_name="ai-scam"))
)
ENSEMBLE_MODEL_PATH = os.getenv(
    "ENSEMBLE_MODEL_PATH",
    str(artifact_config.resolve_model_path("ensemble_meta.joblib", required=False, module_name="ai-scam"))
)
THRESHOLDS_PATH = os.getenv(
    "THRESHOLDS_PATH",
    str(artifact_config.resolve_model_path("calibrated_thresholds.json", required=False, module_name="ai-scam"))
)

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

# Named calibration constants from centralized configuration
RULES_SAFETY_OVERRIDE_THRESHOLD = CALIBRATION.rules_safety_override
LLM_CONFIDENCE_THRESHOLD = CALIBRATION.llm_confidence_threshold
DEFAULT_MEDIUM_THRESHOLD = DEFAULT_LOW_THRESHOLD
