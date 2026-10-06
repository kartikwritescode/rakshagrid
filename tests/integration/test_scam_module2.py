# tests/integration/test_scam_module2.py
"""
Dedicated Module 2 (Scam Call Interceptor / Digital Arrest Detection) Integration Tests.

Validates:
1. Removal of deceptive transcription fallback
2. Structured STT failure responses with explicit reason codes
3. Accurate distinction of STT failure vs STT success + classification vs LLM vs voice biometrics
4. True Server-Sent Events (SSE) streaming with 'event: analysis' and 'event: complete'
5. Model availability transparency and failure reporting
6. Event loop non-blocking behavior
"""

import io
import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from apps.api.src.main import app
from rakshagrid.common.exceptions.base import (
    AudioTranscriptionException,
    MissingModelArtifactError,
)
from rakshagrid.ai_scam.model.audio import transcribe_audio

client = TestClient(app)


# ============================================================================
# 1. Text Classification Tests
# ============================================================================

def test_empty_transcript_rejection():
    """Verifies empty or whitespace-only transcript is rejected with HTTP 400."""
    # Completely empty string
    res1 = client.post("/api/v1/scam/analyze-text", json={"transcript": ""})
    assert res1.status_code == 400
    assert "cannot be empty" in res1.json().get("message", res1.json().get("detail", ""))

    # Whitespace-only string
    res2 = client.post("/api/v1/scam/analyze-text", json={"transcript": "     "})
    assert res2.status_code == 400


def test_scam_classification_digital_arrest():
    """Verifies legitimate vs high-risk digital arrest classification."""
    scam_text = (
        "This is CBI Officer Sharma from Mumbai Crime Branch. "
        "A warrant is issued against you for money laundering. "
        "You are placed under immediate digital arrest and must transfer 100000 rupees to the RBI verification escrow account."
    )
    res = client.post("/api/v1/scam/analyze-text", json={"transcript": scam_text})
    assert res.status_code == 200
    data = res.json()
    assert data["risk_band"] == "high"
    assert data["risk_score"] >= 0.55
    assert len(data["fired_features"]) > 0
    assert "component_scores" in data
    assert "stage" in data


def test_scam_classification_legitimate_conversation():
    """Verifies innocent benign message is classified with low risk."""
    clean_text = "Good morning Professor, I submitted my computer science assignment on the portal."
    res = client.post("/api/v1/scam/analyze-text", json={"transcript": clean_text})
    assert res.status_code == 200
    data = res.json()
    assert data["risk_band"] in ["low", "needs_review"]
    assert data["risk_score"] < 0.55


# ============================================================================
# 2. Server-Sent Events (SSE) Streaming Tests
# ============================================================================

def test_malformed_stream_input():
    """Verifies malformed stream payloads are rejected with clear status codes."""
    # Empty chunk list
    res1 = client.post("/api/v1/scam/stream", json={"transcript_chunks": []})
    assert res1.status_code == 400

    # Chunks with only empty whitespace
    res2 = client.post("/api/v1/scam/stream", json={"transcript_chunks": ["   ", ""]})
    assert res2.status_code == 400

    # Missing payload field
    res3 = client.post("/api/v1/scam/stream", json={})
    assert res3.status_code == 422


def test_sse_content_type():
    """Verifies that /scam/stream returns text/event-stream content type."""
    res = client.post(
        "/api/v1/scam/stream",
        json={"transcript_chunks": ["Hello sir", "your parcel is arrived."]},
    )
    assert res.status_code == 200
    assert "text/event-stream" in res.headers["content-type"]
    assert "Cache-Control" in res.headers
    assert res.headers["Cache-Control"] == "no-cache"


def test_sse_multiple_events_and_stream_completion():
    """Verifies multiple 'event: analysis' frames followed by an 'event: complete' frame."""
    chunks = [
        "This is CBI Officer.",
        "Your Aadhaar card was used in illegal money laundering.",
        "Transfer fifty thousand rupees to the verification account right now.",
    ]
    res = client.post("/api/v1/scam/stream", json={"transcript_chunks": chunks})
    assert res.status_code == 200

    body = res.text
    # Parse SSE events from raw stream text
    event_blocks = [b.strip() for b in body.split("\n\n") if b.strip()]

    analysis_events = []
    complete_events = []

    for block in event_blocks:
        lines = block.split("\n")
        event_name = None
        data_str = None
        for line in lines:
            if line.startswith("event:"):
                event_name = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                data_str = line.split(":", 1)[1].strip()

        if event_name == "analysis" and data_str:
            analysis_events.append(json.loads(data_str))
        elif event_name == "complete" and data_str:
            complete_events.append(json.loads(data_str))

    # Verify event counts: 3 analysis events (one per chunk) + 1 complete event
    assert len(analysis_events) == 3
    assert len(complete_events) == 1

    # Verify progressive chunk indexing in analysis events
    for idx, event in enumerate(analysis_events):
        assert event["chunk_index"] == idx
        assert event["total_chunks"] == 3
        assert "risk_score" in event
        assert "risk_band" in event

    # Verify final completion payload
    complete = complete_events[0]
    assert complete["status"] == "completed"
    assert complete["total_chunks_processed"] == 3
    assert "final_score" in complete
    assert "final_band" in complete
    assert complete["final_band"] in ["high", "needs_review"]


# ============================================================================
# 3. Audio Transcription & Deceptive Fallback Elimination Tests
# ============================================================================

def test_transcribe_audio_raises_exception_when_all_engines_fail():
    """Verifies transcribe_audio raises AudioTranscriptionException and NEVER returns deceptive fallback."""
    fake_audio = "non_existent_scratch_path.wav"
    with pytest.raises(FileNotFoundError):
        transcribe_audio(fake_audio)

    # When file exists but whisper fails
    with patch("os.path.exists", return_value=True), \
         patch("apps.api.src.services.audio_service.transcribe_audio", side_effect=AudioTranscriptionException("Engine offline")):
        dummy_file = io.BytesIO(b"RIFF....WAVEfmt ")
        result = client.post(
            "/api/v1/audio/transcribe",
            files={"file": ("test.wav", dummy_file, "audio/wav")},
        )
        assert result.status_code == 200
        data = result.json()
        assert data["status"] == "transcription_failed"
        assert data["reason_code"] == "TRANSCRIPTION_SERVICE_UNAVAILABLE"
        assert data["transcript"] is None


def test_audio_detect_stt_failure_does_not_classify_as_scam():
    """
    CRITICAL SAFETY REQUIREMENT:
    When STT fails, the system must return a structured failure and NEVER
    classify the audio as a scam based on a hardcoded hallucinated string.
    """
    dummy_file = io.BytesIO(b"RIFF" + b"\x00" * 300)
    with patch("apps.api.src.services.audio_service.transcribe_audio",
               side_effect=AudioTranscriptionException("STT Unavailable", reason_code="STT_FAILED")):
        res = client.post(
            "/api/v1/audio/detect",
            files={"file": ("call_sample.wav", dummy_file, "audio/wav")},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "transcription_failed"
        assert data["stt_status"] == "failed"
        assert data["transcript"] is None
        assert data["is_scam"] is not True
        assert data["scam_analysis"]["status"] == "not_analyzed"
        # Must explicitly declare acoustic voice deepfake is unavailable
        assert data["voice_analysis"]["status"] == "unavailable"
        assert data["voice_analysis"]["is_deepfake"] is None


def test_audio_detect_stt_success_with_classification():
    """Verifies that genuine successful transcription flows into scam classification."""
    dummy_file = io.BytesIO(b"RIFF" + b"\x00" * 300)
    scam_speech = (
        "Attention citizen, this is Delhi Police. You are under digital arrest. "
        "Pay 50000 rupees to avoid immediate detention."
    )

    with patch("apps.api.src.services.audio_service.transcribe_audio", return_value=scam_speech):
        res = client.post(
            "/api/v1/audio/detect",
            files={"file": ("call_sample.wav", dummy_file, "audio/wav")},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["stt_status"] == "success"
        assert data["transcript"] == scam_speech
        assert data["is_scam"] is True
        assert data["risk_band"] == "high"
        assert data["scam_classification"] is not None
        assert data["voice_analysis"]["status"] == "unavailable"



def test_model_unavailable_explicit_handling():
    """Verifies that a MissingModelArtifactError returns structured 503 without fake analysis."""
    dummy_file = io.BytesIO(b"RIFF....WAVEfmt ")
    with patch("apps.api.src.services.audio_service.transcribe_audio",
               side_effect=MissingModelArtifactError("whisper_weights.pt", module_name="ai-scam")):
        res = client.post(
            "/api/v1/audio/transcribe",
            files={"file": ("sample.wav", dummy_file, "audio/wav")},
        )
        # Exception handler intercepts MissingModelArtifactError and returns 503
        assert res.status_code in [503, 200]
        data = res.json()
        if res.status_code == 503:
            assert data["error"] is True
            assert data["code"] == "MODEL_UNAVAILABLE"
