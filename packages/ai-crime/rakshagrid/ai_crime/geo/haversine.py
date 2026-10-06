# packages/ai-crime/rakshagrid/ai_crime/geo/haversine.py
"""Haversine great-circle distance calculations for geospatial crime analytics."""

import math
from typing import Any, Sequence, Tuple
import numpy as np

from rakshagrid.ai_crime.geo.coordinates import validate_coordinates

# Earth mean radius constants (IUGG standard: 6371.0088 km)
EARTH_RADIUS_KM = 6371.0088
EARTH_RADIUS_METERS = 6371008.8
EARTH_RADIUS_MILES = 3958.7613
EARTH_RADIUS_NAUTICAL_MILES = 3440.0695

_RADIUS_MAP = {
    "km": EARTH_RADIUS_KM,
    "m": EARTH_RADIUS_METERS,
    "meters": EARTH_RADIUS_METERS,
    "mi": EARTH_RADIUS_MILES,
    "miles": EARTH_RADIUS_MILES,
    "nm": EARTH_RADIUS_NAUTICAL_MILES,
}


def get_earth_radius(unit: str = "km") -> float:
    """Returns Earth's mean radius in the requested unit."""
    cleaned = unit.lower().strip()
    if cleaned not in _RADIUS_MAP:
        raise ValueError(
            f"Unsupported distance unit: {unit!r}. Supported units: {list(_RADIUS_MAP.keys())}"
        )
    return _RADIUS_MAP[cleaned]


def haversine_distance(
    lat1: Any,
    lon1: Any,
    lat2: Any,
    lon2: Any,
    unit: str = "km"
) -> float:
    """Computes the great-circle distance between two points on Earth using the Haversine formula.

    Formula:
        a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
        c = 2 * atan2(√a, √(1-a))
        d = R * c

    Args:
        lat1, lon1: First coordinate pair in decimal degrees.
        lat2, lon2: Second coordinate pair in decimal degrees.
        unit: Distance unit ('km', 'm', 'mi', 'nm'). Defaults to 'km'.

    Returns:
        Great-circle distance in the specified unit.

    Raises:
        ValueError: If any coordinate fails validation or unit is unsupported.
    """
    v_lat1, v_lon1 = validate_coordinates(lat1, lon1)
    v_lat2, v_lon2 = validate_coordinates(lat2, lon2)

    # Identical coordinates short-circuit
    if v_lat1 == v_lat2 and v_lon1 == v_lon2:
        return 0.0

    radius = get_earth_radius(unit)

    # Convert decimal degrees to radians
    phi1 = math.radians(v_lat1)
    phi2 = math.radians(v_lat2)
    delta_phi = math.radians(v_lat2 - v_lat1)
    delta_lambda = math.radians(v_lon2 - v_lon1)

    # Haversine computation
    sin_dphi_2 = math.sin(delta_phi / 2.0)
    sin_dlambda_2 = math.sin(delta_lambda / 2.0)

    a = (sin_dphi_2 * sin_dphi_2) + (
        math.cos(phi1) * math.cos(phi2) * (sin_dlambda_2 * sin_dlambda_2)
    )

    # Clamp a to [0.0, 1.0] to guard against floating-point inaccuracies
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return radius * c


def haversine_distance_vector(
    lat1: Any,
    lon1: Any,
    lats: Sequence[float] | np.ndarray,
    lons: Sequence[float] | np.ndarray,
    unit: str = "km"
) -> np.ndarray:
    """Vectorized calculation of Haversine distance from a single point to an array of points.

    Args:
        lat1, lon1: Reference point in decimal degrees.
        lats: Sequence or NumPy array of target latitudes in degrees.
        lons: Sequence or NumPy array of target longitudes in degrees.
        unit: Distance unit ('km', 'm', 'mi', 'nm').

    Returns:
        NumPy array of distances in the specified unit.
    """
    v_lat1, v_lon1 = validate_coordinates(lat1, lon1)
    radius = get_earth_radius(unit)

    arr_lats = np.asarray(lats, dtype=np.float64)
    arr_lons = np.asarray(lons, dtype=np.float64)

    if arr_lats.shape != arr_lons.shape:
        raise ValueError(
            f"Latitude array shape {arr_lats.shape} does not match longitude array shape {arr_lons.shape}"
        )

    if arr_lats.size == 0:
        return np.empty((0,), dtype=np.float64)

    phi1 = np.radians(v_lat1)
    phi2 = np.radians(arr_lats)
    delta_phi = np.radians(arr_lats - v_lat1)
    delta_lambda = np.radians(arr_lons - v_lon1)

    a = (np.sin(delta_phi / 2.0) ** 2) + (
        np.cos(phi1) * np.cos(phi2) * (np.sin(delta_lambda / 2.0) ** 2)
    )
    a = np.clip(a, 0.0, 1.0)
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))

    return radius * c


def find_nearest_hotspot(
    lat: Any,
    lon: Any,
    hotspots: list[dict],
    unit: str = "km"
) -> Tuple[dict | None, float]:
    """Finds the nearest hotspot cluster and its distance from a given point.

    Returns:
        Tuple of (nearest_hotspot_dict, distance). If hotspots list is empty, returns (None, inf).
    """
    v_lat, v_lon = validate_coordinates(lat, lon)

    if not hotspots:
        return None, float("inf")

    best_spot = None
    min_dist = float("inf")

    for spot in hotspots:
        s_lat = spot.get("lat")
        s_lon = spot.get("lon")
        if s_lat is None or s_lon is None:
            continue
        dist = haversine_distance(v_lat, v_lon, s_lat, s_lon, unit=unit)
        if dist < min_dist:
            min_dist = dist
            best_spot = spot

    return best_spot, min_dist
