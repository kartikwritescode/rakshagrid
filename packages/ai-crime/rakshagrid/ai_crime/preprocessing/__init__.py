# packages/ai-crime/rakshagrid/ai_crime/preprocessing/__init__.py
"""Preprocessing, geocoding, and spatial augmentation utilities for VigilGrid."""

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

__all__ = [
    "INDIAN_METRO_COORDINATES",
    "INDIAN_CITY_ALIASES",
    "normalize_city_name",
    "geocode_city",
    "load_india_city_lookup",
    "geocode_crimes",
    "coverage_report",
    "enforce_coverage_gate",
    "jitter_points",
]
