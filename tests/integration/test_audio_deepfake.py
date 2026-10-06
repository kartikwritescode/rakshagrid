# tests/integration/test_audio_deepfake.py
"""
Test suite validating the decoupled Audio Deepfake & Scam Analysis architecture.

Verifies:
1. scam == high does NOT imply deepfake (voice analysis remains independent and unavailable if no model).
2. scam == low does NOT imply genuine voice (voice analysis remains independent).
3. Missing acoustic deepfake model returns status = 'unavailable' with a clear explanation.
4. STT failure does NOT create a fake transcript, and preserves clean error reporting.
5. Voice and text analysis are independent and separately reported in the API.
"""

import io
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "apps" / "api"))
sys.path.insert(0, str(ROOT_DIR / "apps" / "api" / "src"))
sys.path.insert(0, str(ROOT_DIR / "packages" / "common"))
sys.path.insert(0, str(ROOT_DIR / "packages" / "ai-scam"))

import pytest
from unittest.mock import patch, MagicMock
from rakshagrid.common.exceptions.base import AudioTranscriptionException
from rakshagrid.ai_scam.model.voice_deepfake import (
    VoiceDeepfakeDetector,
    VoiceDeepfakeStatus,
    VoiceDeepfakeResult,
)
from apps.api.src.services.audio_service import AudioService



@pytest.fixture
def dummy_audio_bytes():
    """Generates dummy audio bytes with sufficient length (>128 bytes)."""
    return b"RIFF" + b"\x00" * 300


def test_missing_deepfake_model_returns_unavailable(dummy_audio_bytes):
    """Missing acoustic deepfake model must return status='unavailable' with reason."""
    detector = VoiceDeepfakeDetector(model_path=None)
    
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(dummy_audio_bytes)
        temp_name = f.name

    try:
        res = detector.detect(temp_name)
        assert res.status == VoiceDeepfakeStatus.UNAVAILABLE
        assert res.is_deepfake is None
        assert res.confidence is None
        assert "Acoustic voice deepfake detection model is not installed" in res.reason
        assert "RawNet2" in str(res.details)
    finally:
        if os.path.exists(temp_name):
            os.remove(temp_name)


def test_scam_high_does_not_imply_deepfake(dummy_audio_bytes):
    """
    A call with high scam risk (e.g. digital arrest threats) must NOT be marked as deepfake.
    is_deepfake must NEVER be derived from risk_band == 'high'.
    """
    service = AudioService()
    file_obj = io.BytesIO(dummy_audio_bytes)

    with patch("apps.api.src.services.audio_service.transcribe_audio") as mock_stt, \
         patch("apps.api.src.services.audio_service.predict") as mock_predict:
        
        mock_stt.return_value = "This is CBI officer. You are under digital arrest. Transfer all funds."
        mock_predict.return_value = {
            "risk_score": 0.98,
            "risk_band": "high",
            "stage": "ensemble_stacking",
            "fired_features": ["threat_words", "digital_arrest"],
            "component_scores": {"rules": 0.95, "ensemble": 0.98},
        }

        result = service.detect_deepfake(file_obj, "scam_call.wav")

        assert result["status"] == "success"
        # Scam analysis is high
        assert result["scam_analysis"]["risk_band"] == "high"
        assert result["scam_analysis"]["is_scam"] is True
        
        # Voice deepfake analysis is INDEPENDENT: status is 'unavailable', NOT 'detected'
        assert result["voice_analysis"]["status"] == "unavailable"
        assert result["voice_analysis"]["is_deepfake"] is None
        
        # Backward compatibility field must NOT claim is_deepfake == True
        assert result.get("is_deepfake") is not True


def test_scam_low_does_not_imply_genuine_voice(dummy_audio_bytes):
    """
    A call with benign content (weather talk) must NOT be declared genuine voice
    if acoustic analysis is unavailable or detecting a synthetic voice clone.
    """
    service = AudioService()
    file_obj = io.BytesIO(dummy_audio_bytes)

    with patch("apps.api.src.services.audio_service.transcribe_audio") as mock_stt, \
         patch("apps.api.src.services.audio_service.predict") as mock_predict:
        
        mock_stt.return_value = "Hello mom, the weather in Delhi is very sunny today."
        mock_predict.return_value = {
            "risk_score": 0.04,
            "risk_band": "low",
            "stage": "ensemble_stacking",
            "fired_features": [],
            "component_scores": {"rules": 0.0, "ensemble": 0.04},
        }

        result = service.detect_deepfake(file_obj, "benign_call.wav")

        assert result["status"] == "success"
        # Scam analysis is low
        assert result["scam_analysis"]["risk_band"] == "low"
        assert result["scam_analysis"]["is_scam"] is False
        
        # Voice deepfake analysis is NOT 'not_detected' just because the text is benign!
        assert result["voice_analysis"]["status"] == "unavailable"
        assert result["voice_analysis"]["is_deepfake"] is None


def test_stt_failure_does_not_create_fake_transcript(dummy_audio_bytes):
    """
    When STT fails (e.g. garbled audio or silence), system must NOT invent
    a fallback transcript and must report failure cleanly.
    """
    service = AudioService()
    file_obj = io.BytesIO(dummy_audio_bytes)

    with patch("apps.api.src.services.audio_service.transcribe_audio") as mock_stt:
        mock_stt.side_effect = AudioTranscriptionException(
            message="No intelligible speech detected in recording.",
            reason_code="EMPTY_TRANSCRIPT",
        )

        result = service.detect_deepfake(file_obj, "unclear_audio.wav")

        assert result["status"] == "transcription_failed"
        assert result["transcription"]["status"] == "failed"
        assert result["transcription"]["transcript"] is None
        assert result["transcription"]["reason_code"] == "EMPTY_TRANSCRIPT"
        
        # Scam analysis was skipped due to STT failure
        assert result["scam_analysis"]["status"] == "not_analyzed"
        assert result["scam_analysis"]["risk_band"] is None
        assert result["scam_analysis"]["is_scam"] is None
        
        # Voice deepfake detector still ran on the raw audio
        assert result["voice_analysis"]["status"] == "unavailable"


def test_voice_and_text_analysis_remain_independent(dummy_audio_bytes):
    """
    Tests that a mock synthetic acoustic detector can report 'detected'
    even when text scam analysis is 'low', and vice-versa.
    """
    # 1. Custom detector that detects a synthetic voice clone
    mock_detector = MagicMock(spec=VoiceDeepfakeDetector)
    mock_detector.detect.return_value = VoiceDeepfakeResult(
        status=VoiceDeepfakeStatus.DETECTED,
        is_deepfake=True,
        confidence=0.96,
        model_name="AASIST-ASVspoof",
        reason="Acoustic phase inconsistencies and vocoder spectral artifacts detected.",
    )

    service = AudioService(deepfake_detector=mock_detector)
    file_obj = io.BytesIO(dummy_audio_bytes)

    with patch("apps.api.src.services.audio_service.transcribe_audio") as mock_stt, \
         patch("apps.api.src.services.audio_service.predict") as mock_predict:
        
        # Benign conversation transcribed
        mock_stt.return_value = "Good morning, please transfer 100 rupees for the groceries."
        mock_predict.return_value = {
            "risk_score": 0.08,
            "risk_band": "low",
            "stage": "ensemble_stacking",
            "fired_features": [],
            "component_scores": {"rules": 0.0, "ensemble": 0.08},
        }

        result = service.detect_deepfake(file_obj, "cloned_family_member.wav")

        # Linguistic scam score is low
        assert result["scam_analysis"]["risk_band"] == "low"
        assert result["scam_analysis"]["is_scam"] is False
        
        # BUT voice deepfake is DETECTED!
        assert result["voice_analysis"]["status"] == "detected"
        assert result["voice_analysis"]["is_deepfake"] is True
        assert result["voice_analysis"]["confidence"] == 0.96
        assert result["voice_analysis"]["model_name"] == "AASIST-ASVspoof"


if __name__ == "__main__":
    audio = b"RIFF" + b"\x00" * 300
    print("Running test_missing_deepfake_model_returns_unavailable...")
    test_missing_deepfake_model_returns_unavailable(audio)
    print("PASS: test_missing_deepfake_model_returns_unavailable")

    print("Running test_scam_high_does_not_imply_deepfake...")
    test_scam_high_does_not_imply_deepfake(audio)
    print("PASS: test_scam_high_does_not_imply_deepfake")

    print("Running test_scam_low_does_not_imply_genuine_voice...")
    test_scam_low_does_not_imply_genuine_voice(audio)
    print("PASS: test_scam_low_does_not_imply_genuine_voice")

    print("Running test_stt_failure_does_not_create_fake_transcript...")
    test_stt_failure_does_not_create_fake_transcript(audio)
    print("PASS: test_stt_failure_does_not_create_fake_transcript")

    print("Running test_voice_and_text_analysis_remain_independent...")
    test_voice_and_text_analysis_remain_independent(audio)
    print("PASS: test_voice_and_text_analysis_remain_independent")
    print("\nALL 5 AUDIO DEEPFAKE ARCHITECTURE TESTS PASSED SUCCESSFULLY!")

