# packages/ai-crime/rakshagrid/ai_crime/predict.py
"""Public interface for Module 4: VigilGrid Crime Hotspot & Patrol Allocation Intelligence."""

from pathlib import Path
from typing import Optional
from rakshagrid.common.exceptions.base import CrimeDataUnavailableException

from rakshagrid.common.logging.logger import setup_logger
from rakshagrid.ai_crime.model.hotspot_engine import HotspotEngine
from rakshagrid.ai_crime.config import crime_config

logger = setup_logger("rakshagrid.ai_crime.predict")

_engine: Optional[HotspotEngine] = None


def init_engine(
    points_path: Optional[str | Path] = None,
    force_reload: bool = False
) -> HotspotEngine:
    """Initializes and fits the singleton HotspotEngine instance once at startup or on demand.

    Raises:
        CrimeDataUnavailableException: If the configured crime dataset cannot be loaded.
    """
    global _engine
    if _engine is None or force_reload or points_path is not None:
        target_path = Path(points_path or crime_config.get_dataset_path())
        logger.info("Initializing and fitting VigilGrid HotspotEngine from %s...", target_path)
        try:
            eng = HotspotEngine(points_path=target_path).load().fit()
            _engine = eng
        except CrimeDataUnavailableException:
            _engine = None
            raise
        except Exception as exc:
            logger.error("Failed to initialize HotspotEngine: %s", exc)
            _engine = None
            raise CrimeDataUnavailableException(
                f"Failed to initialize VigilGrid hotspot engine: {exc}",
                code="CRIME_INITIALIZATION_ERROR",
            ) from exc
    return _engine



def reset_engine() -> None:
    """Resets the singleton engine. Useful for test isolation."""
    global _engine
    _engine = None


def get_engine() -> Optional[HotspotEngine]:
    """Returns the current engine instance without throwing if uninitialized."""
    return _engine


def predict_hotspots() -> list[dict]:
    """Returns detected crime hotspots ranked by composite risk weight.

    Raises:
        CrimeDataUnavailableException: If dataset is missing or engine cannot be initialized.
    """
    eng = init_engine()
    return eng.get_hotspots()


def predict_points(limit: int = 5000) -> list[dict]:
    """Returns geocoded incident points up to the specified limit.

    Raises:
        CrimeDataUnavailableException: If dataset is missing or engine cannot be initialized.
    """
    eng = init_engine()
    return eng.get_points(limit=limit)


def allocate_patrols(n_units: int = crime_config.DEFAULT_PATROL_UNITS) -> list[dict]:
    """Allocates patrol resource units across top ranked hotspot clusters.

    Raises:
        CrimeDataUnavailableException: If dataset is missing or engine cannot be initialized.
    """
    eng = init_engine()
    return eng.allocate_patrols(n_units=n_units)


def get_engine_status() -> dict:
    """Returns runtime state of the VigilGrid crime engine."""
    try:
        eng = init_engine()
        points_count = len(eng.points) if eng.points is not None else 0
        hotspots_count = len(eng.hotspots) if eng.hotspots is not None else 0
        return {
            "status": "ready",
            "points_loaded": points_count,
            "hotspots_found": hotspots_count,
        }
    except CrimeDataUnavailableException as exc:
        logger.warning("Crime engine status unavailable: %s", exc.message)
        return {
            "status": "data_unavailable",
            "points_loaded": 0,
            "hotspots_found": 0,
        }
    except Exception as exc:
        logger.error("Unexpected error checking crime engine status: %s", exc)
        return {
            "status": "error",
            "points_loaded": 0,
            "hotspots_found": 0,
        }
