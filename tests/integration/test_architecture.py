# tests/integration/test_architecture.py
"""
Integration tests verifying clean production architecture requirements:
- Request ID tracing and propagation
- Structured safe error responses (no raw stacktraces or internal paths leaked)
- All 8 v1 routers registered explicitly under /api/v1/
- Lightweight health checks without heavy ML loading
- Environment-driven configuration and secret hiding
"""

import pytest
from fastapi.testclient import TestClient
from apps.api.src.main import app, create_app
from apps.api.src.config import settings

client = TestClient(app, headers={"X-API-Key": "rakshagrid-master-key-2026"})


def test_request_id_middleware_generates_id():
    """Verifies that RequestIDMiddleware assigns a unique ID and header."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"].startswith("req_")


def test_request_id_middleware_preserves_valid_incoming_id():
    """Verifies that an incoming valid X-Request-ID header is preserved."""
    custom_id = "req_custom_tracer_12345"
    response = client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_id


def test_structured_error_on_not_found():
    """Verifies 404 returns structured error schema with request_id and safe message."""
    response = client.get("/api/v1/nonexistent-endpoint-test")
    assert response.status_code == 404
    payload = response.json()
    assert payload["error"] is True
    assert payload["code"] == "NOT_FOUND"
    assert "request_id" in payload
    assert "message" in payload
    assert "X-Request-ID" in response.headers


def test_structured_error_on_validation_failure():
    """Verifies 422 returns structured error schema with validation details."""
    response = client.post("/api/v1/scam/analyze-text", json={})
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"] is True
    assert payload["code"] == "VALIDATION_ERROR"
    assert "request_id" in payload
    assert "validation_errors" in payload.get("details", {})


def test_lightweight_health():
    """Verifies /health and /api/v1/health are fast and return uptime metadata."""
    for path in ["/health", "/api/v1/health"]:
        response = client.get(path)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert "version" in data
        assert "service" in data


def test_all_eight_routers_registered_under_v1():
    """Verifies all 8 domain routers are accessible under /api/v1/."""
    paths = {r.path for r in app.routes}
    expected_v1_prefixes = [
        "/api/v1/health",
        "/api/v1/scam/analyze-text",
        "/api/v1/audio/detect",
        "/api/v1/currency/predict",
        "/api/v1/crime/hotspots",
        "/api/v1/graph",
        "/api/v1/reports",
        "/api/v1/chat",
    ]
    for expected in expected_v1_prefixes:
        assert any(p == expected for p in paths), f"Missing expected route: {expected}"


def test_legacy_api_prefix_compatibility():
    """Verifies backwards compatibility under /api/ without code duplication."""
    paths = {r.path for r in app.routes}
    assert "/api/health" in paths
    assert "/api/scam/analyze-text" in paths
    assert "/api/currency/predict" in paths
    assert "/api/crime/hotspots" in paths


def test_graph_and_reports_endpoints():
    """Verifies citizen fraud report intake and graph retrieval."""
    # 1. Post a new report
    report_data = {
        "victimName": "Ramesh Kumar",
        "phoneNumber": "+91 99999 11111",
        "upiId": "fake@upi",
        "typeOfScam": "Digital Arrest",
        "description": "Caller claimed to be CBI officer demanding verification fee",
        "amountLost": 50000.0,
        "city": "Bengaluru",
        "state": "Karnataka"
    }
    create_resp = client.post("/api/v1/reports", json=report_data)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["id"].startswith("REP-")
    assert created["riskScore"] > 0

    # 2. Get fraud graph
    graph_resp = client.get("/api/v1/graph")
    assert graph_resp.status_code == 200
    graph_data = graph_resp.json()
    assert "nodes" in graph_data
    assert "links" in graph_data
    assert "centrality" in graph_data


def test_chat_advisor_endpoint():
    """Verifies FraudShield AI safety chat advisor returns structured guidance."""
    chat_payload = {
        "messages": [
            {"role": "user", "content": "Someone called saying they are police and I am under digital arrest"}
        ]
    }
    chat_resp = client.post("/api/v1/chat", json=chat_payload)
    assert chat_resp.status_code == 200
    data = chat_resp.json()
    assert "reply" in data
    assert data["risk_band"] in ["high", "needs_review"]
    assert "recommended_action" in data


def test_secrets_not_exposed_in_string_representations():
    """Verifies SecretStr masks sensitive keys when converted to string or repr."""
    secret_str = str(settings.GROQ_API_KEY)
    assert "**********" in secret_str or secret_str == "SecretStr('**********')" or secret_str == "**********"
