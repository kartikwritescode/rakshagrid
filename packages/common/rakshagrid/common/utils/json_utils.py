# shared/utils/json_utils.py
"""Centralized JSON reading and writing utilities."""

import json
import os
from rakshagrid.common.logging.logger import setup_logger

logger = setup_logger("rakshagrid.common.utils.json")

def load_json(path: str) -> dict:
    """Helper to safely load a JSON file."""
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON from {path}: {e}")
    return {}

def save_json(path: str, data: dict):
    """Helper to safely save data as formatted JSON."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Saved JSON data to {path}")
    except Exception as e:
        logger.error(f"Error saving JSON to {path}: {e}")
