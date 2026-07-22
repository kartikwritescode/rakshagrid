# shared/configs/base_config.py
"""Centralized environment configuration management."""

import os
from dotenv import load_dotenv

# Load env vars from .env
load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

STORAGE_DIR = os.path.join(BASE_DIR, "storage")
MODELS_DIR = os.path.join(STORAGE_DIR, "models")
UPLOADS_DIR = os.path.join(STORAGE_DIR, "uploads")
OUTPUTS_DIR = os.path.join(STORAGE_DIR, "outputs")

# Ensure storage directories exist
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
