# packages/ai-crime/rakshagrid/ai_crime/config/crime_config.py
"""Configuration settings for Module 4: VigilGrid Crime Intelligence."""

import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rakshagrid.common.configs.base_config import artifact_config
from rakshagrid.common.constants.risk_bands import CALIBRATION


class CrimeConfig(BaseSettings):
    """Configuration for VigilGrid Geospatial DBSCAN Hotspot Engine."""
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    DATASET_PATH: Path = Field(
        default_factory=lambda: Path(
            os.getenv(
                "CRIME_DATASET_PATH",
                str(artifact_config.DATA_ROOT / "processed" / "points.parquet")
            )
        ),
        description="Canonical dataset path for VigilGrid crime point cloud"
    )
    DBSCAN_EPS_KM: float = Field(
        default_factory=lambda: float(os.getenv("CRIME_DBSCAN_EPS_KM", "0.4")),
        description="DBSCAN epsilon radius in kilometers"
    )
    DBSCAN_MIN_PTS: int = Field(
        default_factory=lambda: int(os.getenv("CRIME_DBSCAN_MIN_PTS", "10")),
        description="DBSCAN minimum samples per cluster"
    )
    DEFAULT_PATROL_UNITS: int = Field(
        default_factory=lambda: int(os.getenv("CRIME_DEFAULT_PATROL_UNITS", "10")),
        description="Default number of patrol units to allocate"
    )
    HOTSPOT_CONFIDENCE: float = CALIBRATION.crime_hotspot_confidence


crime_settings = CrimeConfig()

def get_dataset_path() -> Path:
    """Returns canonical dataset path, prioritizing runtime environment override."""
    env_override = os.getenv("CRIME_DATASET_PATH")
    if env_override:
        return Path(env_override)
    return crime_settings.DATASET_PATH


# Canonical configuration bindings
PROCESSED_POINTS: str = str(crime_settings.DATASET_PATH)
DBSCAN_EPS_KM: float = crime_settings.DBSCAN_EPS_KM
DBSCAN_MIN_PTS: int = crime_settings.DBSCAN_MIN_PTS
DEFAULT_PATROL_UNITS: int = crime_settings.DEFAULT_PATROL_UNITS
HOTSPOT_CONFIDENCE: float = crime_settings.HOTSPOT_CONFIDENCE

