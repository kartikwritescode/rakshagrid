# packages/ai-crime/rakshagrid/ai_crime/__init__.py
"""Module 4: VigilGrid Geospatial Crime Pattern Intelligence."""

from rakshagrid.ai_crime.geo import (
    validate_coordinates,
    normalize_coordinates,
    is_valid_coordinate,
    is_within_india_bounds,
    haversine_distance,
    haversine_distance_vector,
    find_nearest_hotspot,
    get_earth_radius,
    EARTH_RADIUS_KM,
)
from rakshagrid.ai_crime.preprocessing.geocode import (
    INDIAN_METRO_COORDINATES,
    INDIAN_CITY_ALIASES,
    normalize_city_name,
    geocode_city,
    load_india_city_lookup,
    geocode_crimes,
    coverage_report,
    enforce_coverage_gate,
)
from rakshagrid.ai_crime.preprocessing.jitter import jitter_points
from rakshagrid.ai_crime.model.hotspot_engine import HotspotEngine
from rakshagrid.ai_crime.config import crime_config
from rakshagrid.ai_crime.predict import (
    init_engine,
    reset_engine,
    get_engine,
    predict_hotspots,
    predict_points,
    allocate_patrols,
    get_engine_status,
)

__all__ = [
    # Geo & Coordinates
    "validate_coordinates",
    "normalize_coordinates",
    "is_valid_coordinate",
    "is_within_india_bounds",
    "haversine_distance",
    "haversine_distance_vector",
    "find_nearest_hotspot",
    "get_earth_radius",
    "EARTH_RADIUS_KM",
    # Geocoding & City Normalization
    "INDIAN_METRO_COORDINATES",
    "INDIAN_CITY_ALIASES",
    "normalize_city_name",
    "geocode_city",
    "load_india_city_lookup",
    "geocode_crimes",
    "coverage_report",
    "enforce_coverage_gate",
    "jitter_points",
    # Model Engine
    "HotspotEngine",
    # Config
    "crime_config",
    # Predict API
    "init_engine",
    "reset_engine",
    "get_engine",
    "predict_hotspots",
    "predict_points",
    "allocate_patrols",
    "get_engine_status",
]

