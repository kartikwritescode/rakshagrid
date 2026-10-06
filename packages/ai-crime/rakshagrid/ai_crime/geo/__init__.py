# packages/ai-crime/rakshagrid/ai_crime/geo/__init__.py
"""Geospatial utilities for VigilGrid crime pattern intelligence."""

from rakshagrid.ai_crime.geo.coordinates import (
    validate_coordinates,
    normalize_coordinates,
    is_valid_coordinate,
    is_within_india_bounds,
)
from rakshagrid.ai_crime.geo.haversine import (
    haversine_distance,
    haversine_distance_vector,
    find_nearest_hotspot,
    get_earth_radius,
    EARTH_RADIUS_KM,
    EARTH_RADIUS_METERS,
    EARTH_RADIUS_MILES,
)

__all__ = [
    "validate_coordinates",
    "normalize_coordinates",
    "is_valid_coordinate",
    "is_within_india_bounds",
    "haversine_distance",
    "haversine_distance_vector",
    "find_nearest_hotspot",
    "get_earth_radius",
    "EARTH_RADIUS_KM",
    "EARTH_RADIUS_METERS",
    "EARTH_RADIUS_MILES",
]
