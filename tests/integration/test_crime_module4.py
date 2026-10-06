# tests/integration/test_crime_module4.py
"""Integration and unit tests for Module 4: VigilGrid Geospatial Crime Pattern Intelligence."""

import math
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from apps.api.src.main import app
from rakshagrid.common.exceptions.base import CrimeDataUnavailableException
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
)
from rakshagrid.ai_crime.model.hotspot_engine import HotspotEngine
from rakshagrid.ai_crime.predict import (
    init_engine,
    reset_engine,
    predict_hotspots,
    predict_points,
    allocate_patrols,
    get_engine_status,
)


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app, headers={"X-API-Key": "rakshagrid-master-key-2026"})


# ----------------------------------------------------------------------
# 1. Haversine Great-Circle Calculation Tests
# ----------------------------------------------------------------------

def test_haversine_identical_points():
    """Distance between identical coordinates must be exactly 0.0."""
    dist = haversine_distance(19.0760, 72.8777, 19.0760, 72.8777)
    assert dist == 0.0


def test_haversine_symmetry():
    """Distance from A to B must equal distance from B to A."""
    mumbai = (19.0760, 72.8777)
    delhi = (28.6139, 77.2090)
    d_ab = haversine_distance(*mumbai, *delhi)
    d_ba = haversine_distance(*delhi, *mumbai)
    assert math.isclose(d_ab, d_ba, rel_tol=1e-9)


def test_haversine_accuracy_known_benchmarks():
    """Haversine distance matches standard geodesic benchmarks within 0.5% tolerance."""
    # London (51.5074, -0.1278) to Paris (48.8566, 2.3522) ~ 343.5 km
    london = (51.5074, -0.1278)
    paris = (48.8566, 2.3522)
    dist_lp = haversine_distance(*london, *paris, unit="km")
    assert 340.0 < dist_lp < 346.0

    # Mumbai (19.0760, 72.8777) to Delhi (28.6139, 77.2090) ~ 1148 km
    dist_md = haversine_distance(19.0760, 72.8777, 28.6139, 77.2090, unit="km")
    assert 1140.0 < dist_md < 1160.0


def test_haversine_distance_units():
    """Unit conversion (km, meters, miles, nautical miles) operates consistently."""
    p1 = (19.0760, 72.8777)
    p2 = (19.1000, 72.9000)

    d_km = haversine_distance(*p1, *p2, unit="km")
    d_m = haversine_distance(*p1, *p2, unit="m")
    d_mi = haversine_distance(*p1, *p2, unit="mi")
    d_nm = haversine_distance(*p1, *p2, unit="nm")

    assert math.isclose(d_km * 1000.0, d_m, rel_tol=1e-4)
    assert math.isclose(d_km * 0.621371, d_mi, rel_tol=1e-3)
    assert d_km > 0.0
    assert d_mi < d_km


def test_haversine_vector():
    """Vectorized Haversine distance matches scalar computations for every target."""
    ref_lat, ref_lon = 19.0760, 72.8777
    lats = [28.6139, 12.9716, 22.5726]
    lons = [77.2090, 77.5946, 88.3639]

    vec_dists = haversine_distance_vector(ref_lat, ref_lon, lats, lons, unit="km")
    assert len(vec_dists) == 3

    for i in range(3):
        scalar_dist = haversine_distance(ref_lat, ref_lon, lats[i], lons[i], unit="km")
        assert math.isclose(vec_dists[i], scalar_dist, rel_tol=1e-9)


def test_find_nearest_hotspot():
    """find_nearest_hotspot returns the closest cluster and distance."""
    hotspots = [
        {"cluster": 0, "lat": 28.6139, "lon": 77.2090},  # Delhi
        {"cluster": 1, "lat": 19.0760, "lon": 72.8777},  # Mumbai
    ]
    # Point near Mumbai
    spot, dist = find_nearest_hotspot(19.0800, 72.8800, hotspots)
    assert spot is not None
    assert spot["cluster"] == 1
    assert dist < 5.0

    # Empty hotspots list returns (None, inf)
    empty_spot, empty_dist = find_nearest_hotspot(19.0800, 72.8800, [])
    assert empty_spot is None
    assert empty_dist == float("inf")


# ----------------------------------------------------------------------
# 2. Coordinate Validation & Normalization Tests
# ----------------------------------------------------------------------

def test_validate_coordinates_valid():
    """Valid global coordinates convert to floats successfully."""
    lat, lon = validate_coordinates(28.6139, 77.2090)
    assert isinstance(lat, float) and isinstance(lon, float)
    assert lat == 28.6139 and lon == 77.2090

    # Boundary coordinates [-90, 90] and [-180, 180]
    assert validate_coordinates(90.0, 180.0) == (90.0, 180.0)
    assert validate_coordinates(-90.0, -180.0) == (-90.0, -180.0)


def test_validate_coordinates_invalid_bounds():
    """Coordinates out of global bounds raise ValueError."""
    with pytest.raises(ValueError, match="Latitude out of bounds"):
        validate_coordinates(91.0, 72.0)

    with pytest.raises(ValueError, match="Latitude out of bounds"):
        validate_coordinates(-90.5, 72.0)

    with pytest.raises(ValueError, match="Longitude out of bounds"):
        validate_coordinates(19.0, 180.5)

    with pytest.raises(ValueError, match="Longitude out of bounds"):
        validate_coordinates(19.0, -181.0)


def test_validate_coordinates_nan_inf_none():
    """NaN, infinite, None, or string values raise ValueError."""
    with pytest.raises(ValueError):
        validate_coordinates(float("nan"), 72.0)

    with pytest.raises(ValueError):
        validate_coordinates(19.0, float("inf"))

    with pytest.raises(ValueError):
        validate_coordinates(None, 72.0)

    with pytest.raises(ValueError):
        validate_coordinates("not-a-number", 72.0)


def test_normalize_coordinates():
    """normalize_coordinates rounds coordinates to 6 decimal places."""
    n_lat, n_lon = normalize_coordinates(19.0760123456, 72.8777123456)
    assert n_lat == 19.076012
    assert n_lon == 72.877712


def test_is_within_india_bounds():
    """Detects whether coordinates fall within India's geographical boundaries."""
    assert is_within_india_bounds(28.6139, 77.2090) is True   # Delhi
    assert is_within_india_bounds(19.0760, 72.8777) is True   # Mumbai
    assert is_within_india_bounds(51.5074, -0.1278) is False  # London


# ----------------------------------------------------------------------
# 3. DBSCAN Geospatial Clustering & Hotspot Detection Tests
# ----------------------------------------------------------------------

def test_dbscan_clustering_synthetic():
    """DBSCAN groups dense incident clusters and assigns noise to outliers."""
    # Create two synthetic clusters (Cluster A near Delhi, Cluster B near Mumbai)
    rng = np.random.default_rng(42)

    # 25 points near Delhi (lat ~ 28.61, lon ~ 77.20) with small 100m dispersion (~0.001 deg)
    delhi_lats = 28.6139 + rng.normal(0, 0.001, 25)
    delhi_lons = 77.2090 + rng.normal(0, 0.001, 25)

    # 25 points near Mumbai (lat ~ 19.07, lon ~ 72.87) with small 100m dispersion
    mumbai_lats = 19.0760 + rng.normal(0, 0.001, 25)
    mumbai_lons = 72.8777 + rng.normal(0, 0.001, 25)

    # 5 noise points scattered far away
    noise_lats = [10.0, 15.0, 20.0, 25.0, 30.0]
    noise_lons = [75.0, 75.0, 75.0, 75.0, 75.0]

    all_lats = np.concatenate([delhi_lats, mumbai_lats, noise_lats])
    all_lons = np.concatenate([delhi_lons, mumbai_lons, noise_lons])
    reports = list(range(1, len(all_lats) + 1))
    domains = ["Violent Crime" if i % 2 == 0 else "Cyber Crime" for i in range(len(all_lats))]

    df = pd.DataFrame({
        "Report Number": reports,
        "lat": all_lats,
        "lon": all_lons,
        "Crime Domain": domains,
    })

    # Fit HotspotEngine with eps=0.5km, min_pts=15
    engine = HotspotEngine(eps_km=0.5, min_pts=15)
    engine.load_dataframe(df).fit()

    hotspots = engine.get_hotspots()
    assert len(hotspots) == 2, f"Expected 2 clusters, found {len(hotspots)}"

    # Check that noise points were recognized
    assert engine.noise_count == 5

    # Check hotspot ranking by weight
    assert hotspots[0]["weight"] >= hotspots[1]["weight"]
    for spot in hotspots:
        assert spot["incidents"] == 25
        assert "violent_share" in spot
        assert "lat" in spot and "lon" in spot
        # Weight formula: incidents * (1 + violent_share)
        expected_weight = round(spot["incidents"] * (1.0 + spot["violent_share"]), 2)
        assert math.isclose(spot["weight"], expected_weight, abs_tol=0.05)


def test_hotspot_engine_empty_dataset():
    """HotspotEngine handles empty dataset gracefully without raising exceptions."""
    empty_df = pd.DataFrame(columns=["Report Number", "lat", "lon", "Crime Domain"])
    engine = HotspotEngine(eps_km=0.4, min_pts=5)
    engine.load_dataframe(empty_df).fit()

    hotspots = engine.get_hotspots()
    assert hotspots == []

    points = engine.get_points()
    assert points == []

    patrols = engine.allocate_patrols(n_units=10)
    assert patrols == []


def test_hotspot_engine_missing_file_raises():
    """Non-existent dataset path raises structured CrimeDataUnavailableException."""
    engine = HotspotEngine(points_path="/non/existent/path/dataset.parquet")
    with pytest.raises(CrimeDataUnavailableException) as exc_info:
        engine.load()
    assert exc_info.value.code == "CRIME_DATA_UNAVAILABLE"


# ----------------------------------------------------------------------
# 4. Patrol Allocation Tests
# ----------------------------------------------------------------------

def test_patrol_allocation_fewer_units_than_hotspots():
    """When n_units <= hotspots, assigns 1 unit to the top n_units ranked hotspots."""
    df_hotspots = pd.DataFrame([
        {"cluster": 0, "incidents": 50, "violent_share": 0.5, "lat": 28.6, "lon": 77.2, "weight": 75.0},
        {"cluster": 1, "incidents": 30, "violent_share": 0.2, "lat": 19.0, "lon": 72.8, "weight": 36.0},
        {"cluster": 2, "incidents": 20, "violent_share": 0.1, "lat": 12.9, "lon": 77.5, "weight": 22.0},
    ])
    engine = HotspotEngine()
    engine.hotspots = df_hotspots

    # Allocate 2 units
    allocations = engine.allocate_patrols(n_units=2)
    assert len(allocations) == 3
    assert allocations[0]["units_assigned"] == 1
    assert allocations[1]["units_assigned"] == 1
    assert allocations[2]["units_assigned"] == 0
    total_assigned = sum(a["units_assigned"] for a in allocations)
    assert total_assigned == 2


def test_patrol_allocation_more_units_than_hotspots():
    """When n_units > hotspots, distributes units proportionally ensuring exact sum matches n_units."""
    df_hotspots = pd.DataFrame([
        {"cluster": 0, "incidents": 60, "violent_share": 0.5, "lat": 28.6, "lon": 77.2, "weight": 90.0},
        {"cluster": 1, "incidents": 30, "violent_share": 0.0, "lat": 19.0, "lon": 72.8, "weight": 30.0},
    ])
    engine = HotspotEngine()
    engine.hotspots = df_hotspots

    # Allocate 10 units across 2 clusters with 3:1 weight ratio (expected: ~8 and 2 or 7 and 3)
    allocations = engine.allocate_patrols(n_units=10)
    assert len(allocations) == 2
    total_assigned = sum(a["units_assigned"] for a in allocations)
    assert total_assigned == 10
    # Higher weight cluster must receive more units
    assert allocations[0]["units_assigned"] > allocations[1]["units_assigned"]


def test_patrol_allocation_zero_or_negative():
    """Allocating zero or negative units assigns 0 to all clusters."""
    df_hotspots = pd.DataFrame([
        {"cluster": 0, "incidents": 10, "violent_share": 0.0, "lat": 28.6, "lon": 77.2, "weight": 10.0},
    ])
    engine = HotspotEngine()
    engine.hotspots = df_hotspots

    alloc_zero = engine.allocate_patrols(n_units=0)
    assert alloc_zero[0]["units_assigned"] == 0

    alloc_neg = engine.allocate_patrols(n_units=-5)
    assert alloc_neg[0]["units_assigned"] == 0


# ----------------------------------------------------------------------
# 5. Crime Media Endpoint 501 Not Implemented Tests
# ----------------------------------------------------------------------

def test_crime_predict_media_returns_501(client):
    """POST /api/v1/crime/predict must return HTTP 501 Not Implemented with structured payload."""
    # Test with form fields
    resp = client.post(
        "/api/v1/crime/predict",
        data={"city": "Mumbai", "crime_description": "Armed Robbery"}
    )
    assert resp.status_code == 501
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "MEDIA_ANALYSIS_NOT_IMPLEMENTED"
    assert "not currently available" in body["message"]


def test_crime_predict_with_file_upload_returns_501(client):
    """POST /api/v1/crime/predict with media file upload must reject with HTTP 501 Not Implemented."""
    fake_image_bytes = b"\xFF\xD8\xFF\xE0\x00\x10JFIF"
    resp = client.post(
        "/api/v1/crime/predict",
        data={"city": "Delhi"},
        files={"file": ("evidence.jpg", fake_image_bytes, "image/jpeg")},
    )
    assert resp.status_code == 501
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "MEDIA_ANALYSIS_NOT_IMPLEMENTED"
    # Verify no fake confidence or severity is returned
    assert "confidence" not in body
    assert "severity" not in body


def test_legacy_crime_predict_returns_501(client):
    """Legacy mount /api/crime/predict must also return HTTP 501 Not Implemented."""
    resp = client.post(
        "/api/crime/predict",
        data={"city": "Kolkata"}
    )
    assert resp.status_code == 501
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "MEDIA_ANALYSIS_NOT_IMPLEMENTED"


# ----------------------------------------------------------------------
# 6. Real API Functional Endpoints Tests
# ----------------------------------------------------------------------

def test_crime_health_endpoint(client):
    """GET /api/v1/crime/health returns runtime engine status."""
    resp = client.get("/api/v1/crime/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "points_loaded" in data
    assert "hotspots_found" in data
    assert data["status"] in ["ready", "data_unavailable"]


def test_crime_hotspots_endpoint(client):
    """GET /api/v1/crime/hotspots returns detected DBSCAN clusters."""
    resp = client.get("/api/v1/crime/hotspots")
    assert resp.status_code in [200, 503]
    if resp.status_code == 200:
        data = resp.json()
        assert "hotspots" in data
        assert isinstance(data["hotspots"], list)
        if len(data["hotspots"]) > 0:
            spot = data["hotspots"][0]
            assert "cluster" in spot
            assert "incidents" in spot
            assert "weight" in spot
            assert "lat" in spot and "lon" in spot


def test_crime_points_endpoint(client):
    """GET /api/v1/crime/points returns incident point cloud."""
    resp = client.get("/api/v1/crime/points?limit=5")
    assert resp.status_code in [200, 503]
    if resp.status_code == 200:
        data = resp.json()
        assert "points" in data
        assert "total" in data
        assert len(data["points"]) <= 5
        if len(data["points"]) > 0:
            pt = data["points"][0]
            assert "lat" in pt and "lon" in pt


def test_crime_patrol_allocation_endpoint(client):
    """GET /api/v1/crime/patrol-allocation allocates units across clusters."""
    resp = client.get("/api/v1/crime/patrol-allocation?units=10")
    assert resp.status_code in [200, 503]
    if resp.status_code == 200:
        data = resp.json()
        assert "n_units" in data
        assert "allocation" in data
        assert data["n_units"] == 10
        assert isinstance(data["allocation"], list)

    # Test n_units alias
    resp_alias = client.get("/api/v1/crime/patrol-allocation?n_units=15")
    if resp_alias.status_code == 200:
        assert resp_alias.json()["n_units"] == 15


# ----------------------------------------------------------------------
# 7. Additional Geocoding, Invalid Coordinates & Missing Data Tests
# ----------------------------------------------------------------------

def test_geocoding_metro_cities_and_aliases():
    """Geocoding resolves major Indian cities and handles legacy aliases seamlessly."""
    from rakshagrid.ai_crime.preprocessing.geocode import (
        geocode_city,
        normalize_city_name,
        INDIAN_METRO_COORDINATES,
    )

    # Direct city lookup
    delhi_coords = geocode_city("Delhi")
    assert delhi_coords is not None
    assert math.isclose(delhi_coords[0], 28.6139, abs_tol=0.01)
    assert math.isclose(delhi_coords[1], 77.2090, abs_tol=0.01)

    # City alias resolution (Bombay -> Mumbai, Bangalore -> Bengaluru)
    mumbai_coords = geocode_city("Mumbai")
    bombay_coords = geocode_city("Bombay")
    assert mumbai_coords == bombay_coords

    blr1 = geocode_city("Bangalore")
    blr2 = geocode_city("Bengaluru")
    assert blr1 == blr2

    # Normalization
    assert normalize_city_name("  bombay  ") == "Mumbai"
    assert normalize_city_name("CALCUTTA") == "Kolkata"

    # Unrecognized city returns None
    assert geocode_city("NonExistentCityXYZ") is None


def test_dataset_invalid_coordinates_filtering():
    """HotspotEngine drops rows with out-of-bounds, infinite, or NaN coordinates."""
    dirty_df = pd.DataFrame({
        "Report Number": [1, 2, 3, 4, 5, 6],
        "lat": [28.6139, 95.0, np.nan, -91.0, 19.0760, np.inf],  # 2 valid (28.6139, 19.0760), 4 invalid
        "lon": [77.2090, 72.8777, 72.8777, 72.8777, 72.8777, 72.8777],
        "Crime Domain": ["Cyber Crime", "Violent Crime", "Theft", "Fraud", "Cyber Crime", "Theft"],
    })

    engine = HotspotEngine()
    engine.load_dataframe(dirty_df)

    assert len(engine.points) == 2
    assert set(engine.points["Report Number"].tolist()) == {1, 5}


def test_dataset_missing_coordinate_columns_raises():
    """DataFrame missing required 'lat' or 'lon' raises CrimeDataUnavailableException with CRIME_DATA_INVALID_SCHEMA."""
    invalid_schema_df = pd.DataFrame({
        "Report Number": [1, 2],
        "city": ["Delhi", "Mumbai"],
    })
    engine = HotspotEngine()
    with pytest.raises(CrimeDataUnavailableException) as exc_info:
        engine.load_dataframe(invalid_schema_df)
    assert exc_info.value.code == "CRIME_DATA_INVALID_SCHEMA"


def test_dbscan_all_points_classified_as_noise():
    """When min_pts exceeds cluster sizes, all points are marked as noise (-1) and hotspots is empty."""
    df = pd.DataFrame({
        "Report Number": [1, 2, 3],
        "lat": [10.0, 20.0, 30.0],
        "lon": [70.0, 80.0, 90.0],
        "Crime Domain": ["Theft", "Fraud", "Cyber Crime"],
    })
    engine = HotspotEngine(eps_km=1.0, min_pts=10)
    engine.load_dataframe(df).fit()

    assert engine.noise_count == 3
    assert engine.get_hotspots() == []
    assert engine.allocate_patrols(n_units=5) == []


def test_haversine_unsupported_unit_raises():
    """Requesting an unsupported distance unit raises ValueError with supported units list."""
    with pytest.raises(ValueError, match="Unsupported distance unit"):
        haversine_distance(19.0, 72.0, 28.0, 77.0, unit="lightyear")


def test_patrol_allocation_exact_unit_sums():
    """Patrol allocation across varied cluster sizes always preserves exact sum(units_assigned) == n_units."""
    df_hotspots = pd.DataFrame([
        {"cluster": 0, "incidents": 100, "violent_share": 0.8, "lat": 28.6, "lon": 77.2, "weight": 180.0},
        {"cluster": 1, "incidents": 50, "violent_share": 0.2, "lat": 19.0, "lon": 72.8, "weight": 60.0},
        {"cluster": 2, "incidents": 25, "violent_share": 0.1, "lat": 12.9, "lon": 77.5, "weight": 27.5},
        {"cluster": 3, "incidents": 10, "violent_share": 0.0, "lat": 22.5, "lon": 88.3, "weight": 10.0},
    ])
    engine = HotspotEngine()
    engine.hotspots = df_hotspots

    for n in [1, 2, 4, 7, 10, 23, 50, 100]:
        alloc = engine.allocate_patrols(n_units=n)
        total = sum(item["units_assigned"] for item in alloc)
        assert total == n, f"Allocation sum {total} != requested {n}"


def test_api_missing_dataset_returns_503_structured(client, monkeypatch):
    """When dataset is not found at configured path, API returns HTTP 503 structured data-unavailable error."""
    from rakshagrid.ai_crime import predict as crime_predict_mod

    # Force reset and mock dataset path to non-existent location
    crime_predict_mod.reset_engine()
    fake_path = Path("/nonexistent/storage/data/processed/missing_points.parquet")
    monkeypatch.setattr(
        "rakshagrid.ai_crime.config.crime_config.get_dataset_path",
        lambda: fake_path
    )

    resp = client.get("/api/v1/crime/hotspots")
    assert resp.status_code == 503
    body = resp.json()
    assert body["error"] is True
    assert body["status"] == "data_unavailable"
    assert body["code"] == "CRIME_DATA_UNAVAILABLE"
    assert "not available" in body["message"]

    # Verify incidents endpoint also returns structured 503
    resp_incidents = client.get("/api/v1/crime/incidents")
    assert resp_incidents.status_code == 503
    assert resp_incidents.json()["code"] == "CRIME_DATA_UNAVAILABLE"

    # Reset engine to clean state for subsequent tests
    crime_predict_mod.reset_engine()


def test_package_alias_rakshagrid_crime_imports():
    """The rakshagrid.crime compatibility alias exposes the complete public API of rakshagrid.ai_crime."""
    import rakshagrid.crime as crime_pkg
    import rakshagrid.ai_crime as ai_crime_pkg

    assert hasattr(crime_pkg, "haversine_distance")
    assert hasattr(crime_pkg, "HotspotEngine")
    assert hasattr(crime_pkg, "predict_hotspots")
    assert hasattr(crime_pkg, "allocate_patrols")
    assert hasattr(crime_pkg, "geocode_city")
    assert hasattr(crime_pkg, "validate_coordinates")

    # Verify identical function pointers
    assert crime_pkg.haversine_distance is ai_crime_pkg.haversine_distance
    assert crime_pkg.HotspotEngine is ai_crime_pkg.HotspotEngine

