import json
import os
import config

def load_json(path: str) -> dict:
    """Helper to load a JSON file safely."""
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON from {path}: {e}")
    return {}

def save_json(path: str, data: dict):
    """Helper to save a JSON file safely."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving JSON to {path}: {e}")

def get_calibrated_thresholds() -> dict:
    """Load calibrated thresholds or return default settings."""
    calibrated = load_json(config.THRESHOLDS_PATH)
    return {
        "high": calibrated.get("high", config.DEFAULT_HIGH_THRESHOLD),
        "low": calibrated.get("low", config.DEFAULT_MEDIUM_THRESHOLD),
        "needs_review_low": calibrated.get("needs_review_low", config.DEFAULT_NEEDS_REVIEW_LOW),
        "needs_review_high": calibrated.get("needs_review_high", config.DEFAULT_NEEDS_REVIEW_HIGH)
    }

def get_risk_band(score: float) -> str:
    """
    Determine the risk band for a given score.
    If the score is between low and high thresholds, it falls to needs_review.
    """
    thresholds = get_calibrated_thresholds()
    
    if score >= thresholds["high"]:
        return "high"
    elif score <= thresholds["low"]:
        return "low"
    else:
        return "needs_review"
