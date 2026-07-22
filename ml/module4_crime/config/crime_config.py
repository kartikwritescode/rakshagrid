# ml/module4_crime/config/crime_config.py
"""Configuration settings for Module 4: VigilGrid Crime Intelligence."""

import os
from shared.configs.base_config import STORAGE_DIR

PROCESSED_POINTS = os.path.join(STORAGE_DIR, "outputs", "processed_points.parquet")
if not os.path.exists(PROCESSED_POINTS):
    fallback_paths = [
        "module4_crime/data/processed/points.parquet",
        "module4_crime/data/processed_points.parquet",
        "data/processed_points.parquet"
    ]
    for path in fallback_paths:
        if os.path.exists(path):
            PROCESSED_POINTS = path
            break

DBSCAN_EPS_KM = 0.4
DBSCAN_MIN_PTS = 20
DEFAULT_PATROL_UNITS = 10
