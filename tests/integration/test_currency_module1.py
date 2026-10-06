# tests/integration/test_currency_module1.py
"""Unit and integration tests for Module 1: Counterfeit Currency Identification."""

import io
import math
from pathlib import Path
import numpy as np
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from apps.api.src.main import app
from rakshagrid.common.exceptions.base import (
    MissingModelArtifactError,
    ValidationException,
)
from rakshagrid.ai_currency.config import currency_settings, get_model_path
from rakshagrid.ai_currency.preprocessing.validator import (
    validate_image_bytes,
    detect_mime_from_magic_bytes,
    safe_temporary_image,
)
from rakshagrid.ai_currency.preprocessing.image_processor import preprocess_image
from rakshagrid.ai_currency.model.currency_net import (
    load_currency_model,
    reset_model,
    get_model,
    build_efficientnet_architecture,
)
from rakshagrid.ai_currency.postprocessing.calibration import calibrate_verdict
from rakshagrid.ai_currency.postprocessing.classifier import format_prediction
from rakshagrid.ai_currency.service import currency_service, predict



@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


def create_test_image_bytes(format: str = "JPEG", size: tuple[int, int] = (100, 100), color: str = "green") -> bytes:
    """Helper to generate valid image bytes in memory."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


# ----------------------------------------------------------------------
# 1. Preprocessing & Input Validation Tests
# ----------------------------------------------------------------------

def test_detect_mime_from_magic_bytes():
    """Detects correct MIME type from genuine file headers."""
    jpeg_bytes = create_test_image_bytes(format="JPEG")
    assert detect_mime_from_magic_bytes(jpeg_bytes) == "image/jpeg"

    png_bytes = create_test_image_bytes(format="PNG")
    assert detect_mime_from_magic_bytes(png_bytes) == "image/png"

    webp_bytes = create_test_image_bytes(format="WEBP")
    assert detect_mime_from_magic_bytes(webp_bytes) == "image/webp"

    # Garbage / non-image headers
    assert detect_mime_from_magic_bytes(b"HELLO WORLD TEST STRING") is None
    assert detect_mime_from_magic_bytes(b"") is None


def test_validate_image_bytes_valid_formats():
    """Valid JPEG, PNG, and WebP images pass validation and return dimensions."""
    for fmt in ["JPEG", "PNG", "WEBP"]:
        data = create_test_image_bytes(format=fmt, size=(160, 120))
        mime, w, h = validate_image_bytes(data)
        assert mime == f"image/{fmt.lower()}"
        assert w == 160 and h == 120


def test_validate_image_bytes_empty():
    """Empty payload raises ValidationException."""
    with pytest.raises(ValidationException, match="empty"):
        validate_image_bytes(b"")


def test_validate_image_bytes_oversized():
    """Payload exceeding max size raises ValidationException."""
    fake_large = b"\xFF\xD8\xFF" + b"\x00" * 200
    with pytest.raises(ValidationException, match="maximum allowed size"):
        validate_image_bytes(fake_large, max_size_bytes=100)


def test_validate_image_bytes_invalid_magic_bytes():
    """Text, HTML, or corrupted headers raise ValidationException."""
    text_data = b"This is not a banknote image, just raw plain text."
    with pytest.raises(ValidationException, match="magic bytes header does not match"):
        validate_image_bytes(text_data)


def test_validate_image_bytes_corrupt_payload():
    """Valid magic bytes followed by truncated/garbage body fails image decoding."""
    corrupted = b"\xFF\xD8\xFF\xE0\x00\x10JFIF" + b"\x00\x00\x00\x00GARBAGE"
    with pytest.raises(ValidationException, match="cannot be decoded"):
        validate_image_bytes(corrupted)


def test_safe_temporary_image_lifecycle():
    """Temporary image files are deterministically cleaned up on normal exit and exceptions."""
    data = create_test_image_bytes(format="JPEG")
    saved_path = None

    with safe_temporary_image(data, suffix=".jpg") as tmp_path:
        saved_path = tmp_path
        assert tmp_path.exists()
        assert tmp_path.stat().st_size == len(data)

    # After with-block, file MUST be deleted
    assert not saved_path.exists()

    # Exception safety check
    caught = False
    try:
        with safe_temporary_image(data, suffix=".jpg") as tmp_path:
            saved_path = tmp_path
            assert tmp_path.exists()
            raise RuntimeError("Intentional test failure")
    except RuntimeError:
        caught = True

    assert caught
    assert not saved_path.exists()


def test_preprocess_image_output_shape_and_dtype():
    """preprocess_image produces a 4D batch tensor of shape (1, 224, 224, 3) and float32 dtype."""
    raw = create_test_image_bytes(format="JPEG", size=(350, 200))
    tensor = preprocess_image(raw)

    assert isinstance(tensor, np.ndarray)
    assert tensor.shape == (1, 224, 224, 3)
    assert tensor.dtype == np.float32
    assert tensor.min() >= 0.0


# ----------------------------------------------------------------------
# 2. Calibration & Postprocessing Tests
# ----------------------------------------------------------------------

def test_calibration_verdict_logic():
    """Calibrated probability thresholds determine authenticity verdicts."""
    threshold = 0.80

    # 1. Genuine banknote with high confidence (>= 0.80) -> Authentic
    verdict, is_genuine = calibrate_verdict("real", 0.94, threshold=threshold)
    assert verdict == "authentic"
    assert is_genuine is True

    # 2. Real class but low confidence (< 0.80) -> Flagged as suspicious for manual review
    verdict_low, is_genuine_low = calibrate_verdict("real", 0.65, threshold=threshold)
    assert verdict_low == "suspicious_low_confidence"
    assert is_genuine_low is False

    # 3. Counterfeit classes -> Always counterfeit regardless of confidence
    for defect in ["fake_print_defect", "fake_color_shift", "fake_missing_thread", "fake_missing_microprint"]:
        v, g = calibrate_verdict(defect, 0.92, threshold=threshold)
        assert v == f"counterfeit_{defect}"
        assert g is False


def test_format_prediction_postprocessing():
    """format_prediction structures 5-class softmax probabilities into complete verdict dictionary."""
    # Probabilities: [real, fake_print_defect, fake_color_shift, fake_missing_thread, fake_missing_microprint]
    mock_probs = np.array([[0.88, 0.05, 0.03, 0.02, 0.02]], dtype=np.float32)

    result = format_prediction(mock_probs, threshold=0.80, processing_time_ms=12.5)

    assert result["status"] == "genuine"
    assert result["predicted_label"] == "real"
    assert result["confidence"] == 0.88
    assert result["is_genuine"] is True
    assert result["calibrated_verdict"] == "authentic"
    assert result["confidence_threshold"] == 0.80
    assert result["processing_time_ms"] == 12.5
    assert len(result["class_probabilities"]) == 5
    assert math.isclose(sum(result["class_probabilities"].values()), 1.0, abs_tol=0.01)


def test_format_prediction_invalid_shape_raises():
    """Invalid probability array shapes raise ValueError."""
    with pytest.raises(ValueError, match="Expected probability vector of length 5"):
        format_prediction(np.array([0.5, 0.5]))


# ----------------------------------------------------------------------
# 3. Configuration & Missing Model Artifact Tests
# ----------------------------------------------------------------------

def test_missing_model_raises_explicit_failure():
    """Missing model weights raise explicit MissingModelArtifactError and NEVER initialize random weights."""
    reset_model()
    fake_path = Path("/nonexistent/weights/currency_model.h5")

    with pytest.raises(MissingModelArtifactError) as exc_info:
        load_currency_model(model_path=fake_path, force_reload=True)

    assert exc_info.value.module_name == "ai-currency"
    assert "not found" in exc_info.value.message
    # Verify singleton was NOT initialized with random weights
    assert get_model() is None


def test_api_missing_model_returns_503(client, monkeypatch):
    """When model artifact is missing, API endpoint returns HTTP 503 with MODEL_UNAVAILABLE code."""
    reset_model()
    fake_path = Path("/nonexistent/storage/models/currency_model.h5")
    monkeypatch.setattr(
        "rakshagrid.ai_currency.model.currency_net.get_model_path",
        lambda: fake_path
    )
    monkeypatch.setattr(
        "rakshagrid.ai_currency.config.get_model_path",
        lambda: fake_path
    )


    valid_image = create_test_image_bytes(format="JPEG")
    resp = client.post(
        "/api/v1/currency/predict",
        files={"file": ("banknote.jpg", valid_image, "image/jpeg")}
    )

    assert resp.status_code == 503
    data = resp.json()
    assert data["error"] is True
    assert data["code"] == "MODEL_UNAVAILABLE"

    # Reset model singleton to clean state
    reset_model()


def test_model_singleton_cached_once():
    """Model is loaded once and cached in process lifecycle, avoiding redundant reloads."""
    canonical_path = get_model_path()
    if not canonical_path.exists():
        pytest.skip(f"Canonical model not found at {canonical_path}")

    reset_model()
    m1 = load_currency_model()
    m2 = load_currency_model()
    assert m1 is m2, "Model singleton was re-created on second call!"


# ----------------------------------------------------------------------
# 4. Inference Smoke Test & API Functional Endpoints
# ----------------------------------------------------------------------

def test_inference_smoke_test_with_canonical_model(client):
    """Inference smoke test using canonical storage/models/currency_model.h5 weights."""
    canonical_path = get_model_path()
    if not canonical_path.exists():
        pytest.skip(f"Canonical model weights not present at {canonical_path}")

    test_image = create_test_image_bytes(format="JPEG", size=(224, 224), color="green")

    # Direct service call
    result = currency_service.analyze_image(test_image, filename="smoke_test.jpg")
    assert result["status"] in ["genuine", "counterfeit"]
    assert result["predicted_label"] in currency_settings.CLASS_NAMES
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["is_genuine"], bool)
    assert len(result["class_probabilities"]) == 5
    assert math.isclose(sum(result["class_probabilities"].values()), 1.0, abs_tol=0.01)

    # FastAPI endpoint call POST /api/v1/currency/predict
    resp = client.post(
        "/api/v1/currency/predict",
        files={"file": ("banknote.jpg", test_image, "image/jpeg")}
    )
    assert resp.status_code == 200
    api_data = resp.json()
    assert "status" in api_data
    assert "predicted_label" in api_data
    assert "confidence" in api_data
    assert "is_genuine" in api_data
    assert "class_probabilities" in api_data

    # Legacy endpoint POST /api/v1/currency/analyze-image
    resp_alias = client.post(
        "/api/v1/currency/analyze-image",
        files={"file": ("banknote.jpg", test_image, "image/jpeg")}
    )
    assert resp_alias.status_code == 200


def test_api_upload_validation_non_image_rejected(client):
    """Uploading non-image content is rejected with HTTP 400 Validation Error."""
    text_content = b"This is a text document, not an image."
    resp = client.post(
        "/api/v1/currency/predict",
        files={"file": ("document.txt", text_content, "text/plain")}
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"] is True
    assert data["code"] == "VALIDATION_ERROR"


def test_api_upload_validation_empty_file_rejected(client):
    """Uploading an empty file is rejected with HTTP 400 Validation Error."""
    resp = client.post(
        "/api/v1/currency/predict",
        files={"file": ("empty.jpg", b"", "image/jpeg")}
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"] is True
    assert data["code"] == "VALIDATION_ERROR"
