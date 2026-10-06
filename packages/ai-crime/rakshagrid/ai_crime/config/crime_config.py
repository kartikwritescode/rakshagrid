# packages/ai-crime/rakshagrid/ai_crime/config/crime_config.py
"""Configuration settings for Module 4: VigilGrid Crime Intelligence."""

import os
from rakshagrid.common.configs.base_config import artifact_config
from rakshagrid.common.constants.risk_bands import CALIBRATION

PROCESSED_POINTS = str(
    artifact_config.resolve_data_path("processed_points.parquet", required=False)
)
if not os.path.exists(PROCESSED_POINTS):
    fallback_points = artifact_config.DATA_ROOT / "processed" / "points.parquet"
    if fallback_points.exists():
        PROCESSED_POINTS = str(fallback_points)

DBSCAN_EPS_KM = 0.4
DBSCAN_MIN_PTS = 20
DEFAULT_PATROL_UNITS = 10
HOTSPOT_CONFIDENCE = CALIBRATION.crime_hotspot_confidence
