# packages/ai-crime/rakshagrid/ai_crime/geo/coordinates.py
"""Geographic coordinate validation and normalization utilities."""

import math
from typing import Any, Tuple

# Bounding box for India mainland and islands
INDIA_MIN_LAT = 6.0
INDIA_MAX_LAT = 38.0
INDIA_MIN_LON = 68.0
INDIA_MAX_LON = 98.0


def validate_coordinates(lat: Any, lon: Any) -> Tuple[float, float]:
    """Validates that latitude and longitude are valid finite real numbers within global bounds.

    Bounds:
        Latitude:  [-90.0, 90.0]
        Longitude: [-180.0, 180.0]

    Returns:
        Tuple of (float(lat), float(lon)).

    Raises:
        ValueError: If coordinates are non-numeric, NaN, infinite, or out of range.
    """
    if lat is None or lon is None:
        raise ValueError("Latitude and longitude must not be None.")

    try:
        f_lat = float(lat)
        f_lon = float(lon)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid coordinate format: lat={lat!r}, lon={lon!r} cannot be converted to float.") from exc

    if math.isnan(f_lat) or math.isnan(f_lon):
        raise ValueError(f"Coordinates must not be NaN: lat={f_lat}, lon={f_lon}.")

    if math.isinf(f_lat) or math.isinf(f_lon):
        raise ValueError(f"Coordinates must not be infinite: lat={f_lat}, lon={f_lon}.")

    if f_lat < -90.0 or f_lat > 90.0:
        raise ValueError(f"Latitude out of bounds: {f_lat}. Must be between -90.0 and +90.0 degrees.")

    if f_lon < -180.0 or f_lon > 180.0:
        raise ValueError(f"Longitude out of bounds: {f_lon}. Must be between -180.0 and +180.0 degrees.")

    return f_lat, f_lon


def normalize_coordinates(lat: Any, lon: Any, precision: int = 6) -> Tuple[float, float]:
    """Validates and rounds coordinates to specified decimal precision.

    Precision 6 provides ~0.1 meter accuracy, standard for GPS and GIS points.
    """
    valid_lat, valid_lon = validate_coordinates(lat, lon)
    return round(valid_lat, precision), round(valid_lon, precision)


def is_valid_coordinate(lat: Any, lon: Any) -> bool:
    """Non-raising validation check for coordinates."""
    try:
        validate_coordinates(lat, lon)
        return True
    except (ValueError, TypeError):
        return False


def is_within_india_bounds(lat: Any, lon: Any) -> bool:
    """Checks whether coordinates fall within the general geographic bounds of India."""
    try:
        f_lat, f_lon = validate_coordinates(lat, lon)
        return (INDIA_MIN_LAT <= f_lat <= INDIA_MAX_LAT) and (INDIA_MIN_LON <= f_lon <= INDIA_MAX_LON)
    except ValueError:
        return False
