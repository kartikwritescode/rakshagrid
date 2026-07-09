# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "models_status" in data

def test_analyze_text_legit():
    response = client.post(
        "/api/scam/analyze-text",
        json={"transcript": "Hi mom, I am heading home now. See you for dinner!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk_band"] in ["low", "needs_review"]
    assert "component_scores" in data
    assert "fired_features" in data

def test_analyze_text_scam():
    # Text that contains authorities, digital arrest, and urgency to ensure high scam probability
    scam_text = (
        "This is Delhi Police Headquarters. A case of money laundering has been registered against you. "
        "You are placed under digital arrest. You must transfer money to the verification account immediately or go to jail."
    )
    response = client.post(
        "/api/scam/analyze-text",
        json={"transcript": scam_text}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk_band"] in ["high", "needs_review"]
    assert data["risk_score"] > 0.5
    assert len(data["fired_features"]) > 0

def test_stream_endpoint():
    response = client.post(
        "/api/scam/stream",
        json={"transcript_chunks": ["This is police.", "You are under arrest.", "Transfer funds now."]}
    )
    assert response.status_code == 200
    # Check that it returns a streaming/SSE content type
    assert "text/event-stream" in response.headers["content-type"]
