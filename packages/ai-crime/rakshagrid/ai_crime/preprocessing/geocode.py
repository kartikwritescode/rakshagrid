# packages/ai-crime/rakshagrid/ai_crime/preprocessing/geocode.py
"""VigilGrid — Geocoding and Indian city coordinate normalization module."""

import logging
from typing import Optional, Tuple
import pandas as pd

from rakshagrid.ai_crime.geo.coordinates import validate_coordinates, normalize_coordinates

logger = logging.getLogger("rakshagrid.ai_crime.geocode")

# Canonical coordinate table for prominent Indian urban crime analytics hubs
INDIAN_METRO_COORDINATES: dict[str, Tuple[float, float]] = {
    "Delhi": (28.6139, 77.2090),
    "New Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Chandigarh": (30.7333, 76.7794),
    "Bhopal": (23.2599, 77.4126),
    "Patna": (25.5941, 85.1376),
    "Surat": (21.1702, 72.8311),
    "Indore": (22.7196, 75.8577),
    "Nagpur": (21.1458, 79.0882),
    "Coimbatore": (11.0168, 76.9558),
    "Visakhapatnam": (17.6868, 83.2185),
    "Kochi": (9.9312, 76.2673),
    "Cochin": (9.9312, 76.2673),
}

INDIAN_CITY_ALIASES: dict[str, str] = {
    "Bombay": "Mumbai",
    "Calcutta": "Kolkata",
    "Madras": "Chennai",
    "Bangalore": "Bengaluru",
    "Cochin": "Kochi",
    "Poona": "Pune",
    "Trivandrum": "Thiruvananthapuram",
    "Baroda": "Vadodara",
    "Banaras": "Varanasi",
    "Benares": "Varanasi",
}


def normalize_city_name(city: str) -> str:
    """Cleans whitespace, standardizes casing, and resolves historic city aliases."""
    if not city:
        return ""
    cleaned = city.strip().title()
    return INDIAN_CITY_ALIASES.get(cleaned, cleaned)


def geocode_city(city: str) -> Optional[Tuple[float, float]]:
    """Resolves coordinates for a known Indian city name.

    Returns:
        (latitude, longitude) tuple or None if city is unrecognized.
    """
    normalized = normalize_city_name(city)
    if normalized in INDIAN_METRO_COORDINATES:
        return INDIAN_METRO_COORDINATES[normalized]
    # Check case-insensitive
    for k, coords in INDIAN_METRO_COORDINATES.items():
        if k.lower() == normalized.lower():
            return coords
    return None


def load_india_city_lookup(world_cities_path: str) -> pd.DataFrame:
    """Loads and filters world cities CSV for Indian municipalities."""
    world_cities = pd.read_csv(world_cities_path)[["city_ascii", "lat", "lng", "country"]]
    india = world_cities[world_cities["country"] == "India"][["city_ascii", "lat", "lng"]].copy()
    india = india.rename(columns={"city_ascii": "city"})
    india["city"] = india["city"].str.strip().str.title()

    dupes = india["city"].duplicated().sum()
    if dupes:
        logger.warning("Dropping %d duplicate city rows from lookup table", dupes)
    india = india.drop_duplicates(subset="city", keep="first")
    logger.info("Loaded %d unique India city coordinates", len(india))
    return india


def geocode_crimes(df: pd.DataFrame, city_lookup: pd.DataFrame, aliases: dict | None = None) -> pd.DataFrame:
    """Merges incident records with city coordinates table, resolving known aliases."""
    alias_dict = aliases or INDIAN_CITY_ALIASES
    df = df.copy()
    original_len = len(df)
    df["City"] = df["City"].str.strip().str.title()
    df["City"] = df["City"].replace(alias_dict)

    df = df.merge(city_lookup, left_on="City", right_on="city", how="left", suffixes=("", "_dup"))
    if len(df) != original_len:
        raise ValueError(f"Merge changed row count: {original_len} -> {len(df)}")
    if "lat" not in df.columns:
        raise ValueError(f"Merge produced unexpected columns: {df.columns.tolist()}")
    return df


def coverage_report(df: pd.DataFrame) -> Tuple[float, pd.Series]:
    """Computes geocoding coverage percentage and reports unmatched cities."""
    total = len(df)
    if total == 0:
        return 1.0, pd.Series(dtype=int)
    missing = df["lat"].isna().sum()
    coverage = 1.0 - (missing / total)
    by_city = df.loc[df["lat"].isna(), "City"].value_counts()
    return coverage, by_city


def enforce_coverage_gate(df: pd.DataFrame, threshold: float = 0.95) -> float:
    """Verifies that geocoding coverage meets or exceeds the required quality gate."""
    coverage, by_city = coverage_report(df)
    logger.info("Geocode coverage: %.2f%%", coverage * 100.0)
    if coverage < threshold:
        logger.error("Unmatched cities:\n%s", by_city)
        raise ValueError(f"Geocode coverage {coverage:.1%} below threshold {threshold:.0%}")
    return coverage
