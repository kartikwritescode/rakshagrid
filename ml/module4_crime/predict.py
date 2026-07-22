# ml/module4_crime/predict.py
"""Public interface for Module 4: VigilGrid Crime Hotspot & Patrol Allocation Intelligence."""

from typing import Optional
from shared.exceptions.base import MLInferenceException
from shared.logging.logger import setup_logger
from ml.module4_crime.model.hotspot_engine import HotspotEngine
from ml.module4_crime.config import crime_config

logger = setup_logger("ml.module4_crime.predict")

_engine: Optional[HotspotEngine] = None

def init_engine() -> HotspotEngine:
    """Initializes and fits the hotspot engine once at startup."""
    global _engine
    if _engine is None:
        try:
            logger.info("Initializing and fitting HotspotEngine...")
            _engine = HotspotEngine().load().fit()
        except Exception as e:
            logger.error(f"Error initializing HotspotEngine: {e}")
            _engine = None
    return _engine

def predict_hotspots() -> list[dict]:
    """Returns detected crime hotspots."""
    eng = init_engine()
    if eng is None:
        raise MLInferenceException("Crime Hotspot Engine not ready", module_name="module4_crime")
    return eng.get_hotspots()

def predict_points(limit: int = 5000) -> list[dict]:
    """Returns geocoded incident points up to specified limit."""
    eng = init_engine()
    if eng is None:
        raise MLInferenceException("Crime Hotspot Engine not ready", module_name="module4_crime")
    return eng.get_points(limit=limit)

def allocate_patrols(n_units: int = crime_config.DEFAULT_PATROL_UNITS) -> list[dict]:
    """Allocates patrol units across top ranked hotspot clusters."""
    eng = init_engine()
    if eng is None:
        raise MLInferenceException("Crime Hotspot Engine not ready", module_name="module4_crime")
    return eng.allocate_patrols(n_units=n_units)

def get_engine_status() -> dict:
    """Returns runtime state of crime engine."""
    eng = init_engine()
    if eng is None or eng.points is None:
        return {"status": "unavailable", "points_loaded": 0, "hotspots_found": 0}
    return {
        "status": "ready",
        "points_loaded": len(eng.points),
        "hotspots_found": len(eng.hotspots) if eng.hotspots is not None else 0
    }
