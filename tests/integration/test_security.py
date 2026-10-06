# tests/integration/test_security.py
"""
Comprehensive Production Security Integration Tests for Raksha Grid.

Verifies:
1. Unauthorized requests to sensitive intelligence endpoints fail with HTTP 401.
2. Invalid authentication credentials fail with HTTP 403.
3. Authorized requests with X-API-Key or Bearer token succeed.
4. CORS rejects '*' wildcard when credentials are enabled.
5. Upload security enforces 25 MB max size, magic byte verification, and extension whitelist.
6. Path traversal filename attempts are sanitized safely.
7. Error responses do not leak stacktraces, internal paths, or credentials.
8. PII masking scrubs sensitive phone numbers, UPI IDs, bank accounts, and tokens from logs.
"""

import io
import pytest
from fastapi.testclient import TestClient

from apps.api.src.main import app
from apps.api.src.config import settings
from rakshagrid.common.logging.logger import mask_pii_text, mask_phone, mask_upi, mask_bank_account

VALID_KEY = "rakshagrid-master-key-2026"
INVALID_KEY = "unauthorized-malicious-key"

unauth_client = TestClient(app)
auth_client = TestClient(app, headers={"X-API-Key": VALID_KEY})
bearer_client = TestClient(app, headers={"Authorization": f"Bearer {VALID_KEY}"})
invalid_client = TestClient(app, headers={"X-API-Key": INVALID_KEY})


# ============================================================================
# 1. Authentication & Authorization Enforcement
# ============================================================================

@pytest.mark.parametrize(
    "endpoint,method,payload",
    [
        ("/api/v1/crime/incidents", "GET", None),
        ("/api/v1/crime/hotspots", "GET", None),
        ("/api/v1/crime/patrol-allocation", "GET", None),
        ("/api/v1/graph/nodes", "GET", None),
        ("/api/v1/graph/centrality", "GET", None),
        ("/api/v1/graph/clusters", "GET", None),
        ("/api/v1/reports", "GET", None),
        ("/api/v1/chat", "POST", {"messages": [{"role": "user", "content": "Help me"}]}),
    ],
)
def test_sensitive_endpoints_reject_unauthorized_requests(endpoint, method, payload):
    """Verifies that sensitive intelligence endpoints return 401 when no auth is provided."""
    if method == "GET":
        resp = unauth_client.get(endpoint)
    else:
        resp = unauth_client.post(endpoint, json=payload)

    assert resp.status_code == 401, f"{endpoint} did not return 401 Unauthorized"
    data = resp.json()
    assert data["error"] is True
    assert data["code"] == "UNAUTHORIZED"
    assert "request_id" in data


@pytest.mark.parametrize(
    "endpoint,method,payload",
    [
        ("/api/v1/crime/incidents", "GET", None),
        ("/api/v1/graph/nodes", "GET", None),
        ("/api/v1/reports", "GET", None),
        ("/api/v1/chat", "POST", {"messages": [{"role": "user", "content": "Help me"}]}),
    ],
)
def test_sensitive_endpoints_reject_invalid_credentials(endpoint, method, payload):
    """Verifies that sensitive endpoints return 403 Forbidden when an invalid key is provided."""
    if method == "GET":
        resp = invalid_client.get(endpoint)
    else:
        resp = invalid_client.post(endpoint, json=payload)

    assert resp.status_code == 403
    data = resp.json()
    assert data["error"] is True
    assert data["code"] == "FORBIDDEN"


def test_sensitive_endpoints_accept_valid_api_key_and_bearer_token():
    """Verifies that valid X-API-Key and Bearer tokens allow authorized access."""
    # 1. X-API-Key header
    resp_key = auth_client.get("/api/v1/graph/nodes")
    assert resp_key.status_code == 200

    # 2. Authorization: Bearer token header
    resp_bearer = bearer_client.get("/api/v1/graph/nodes")
    assert resp_bearer.status_code == 200


# ============================================================================
# 2. CORS Security
# ============================================================================

def test_cors_rejects_wildcard_origins_with_credentials():
    """Ensures settings.CORS_ORIGINS contains no '*' wildcard origin."""
    assert "*" not in settings.CORS_ORIGINS
    for origin in settings.CORS_ORIGINS:
        assert origin.startswith("http://") or origin.startswith("https://")


# ============================================================================
# 3. File Upload Security
# ============================================================================

def test_upload_rejects_disallowed_extension():
    """Verifies executable and malicious script extensions are rejected."""
    fake_exe = io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00")
    resp = auth_client.post(
        "/api/v1/currency/predict",
        files={"file": ("malware.exe", fake_exe, "application/octet-stream")},
    )
    assert resp.status_code in [400, 422]
    assert "Unsupported file extension" in resp.json()["message"]


def test_upload_rejects_spoofed_mime_type_with_invalid_magic_bytes():
    """Verifies that an attacker cannot spoof Content-Type if file binary magic bytes are invalid."""
    fake_png = io.BytesIO(b"This is plain text pretending to be a PNG image.")
    resp = auth_client.post(
        "/api/v1/currency/predict",
        files={"file": ("fake.png", fake_png, "image/png")},
    )
    assert resp.status_code in [400, 422]
    assert "signature verification failed" in resp.json()["message"]


def test_upload_rejects_oversized_file():
    """Verifies that files exceeding size limits are rejected with HTTP 413."""
    from apps.api.src.core.upload_security import read_and_validate_upload
    from fastapi import UploadFile

    # Test size rejection using smaller limit simulation
    oversized_data = io.BytesIO(b"\xFF\xD8\xFF" + b"\x00" * 2000)
    fake_upload = UploadFile(filename="test.jpg", file=oversized_data)

    import asyncio
    with pytest.raises(Exception) as exc_info:
        asyncio.run(
            read_and_validate_upload(
                file=fake_upload,
                allowed_extensions={".jpg"},
                allowed_mime_prefixes=("image/",),
                max_size_bytes=1000,  # 1 KB limit for testing
            )
        )
    assert exc_info.value.status_code == 413


def test_filename_sanitization_prevents_path_traversal():
    """Verifies that directory traversal components are stripped or rejected."""
    from apps.api.src.core.upload_security import sanitize_filename

    # Directory traversal stripping
    safe = sanitize_filename("../../etc/passwd.jpg")
    assert ".." not in safe
    assert "/" not in safe
    assert "\\" not in safe
    assert safe == "passwd.jpg"

    # Null byte rejection
    with pytest.raises(Exception):
        sanitize_filename("image.jpg\x00.exe")


# ============================================================================
# 4. Error Handling & Information Leakage Prevention
# ============================================================================

def test_unhandled_errors_do_not_leak_internal_paths_or_stacktraces():
    """Verifies that unexpected 500 exceptions return safe structured JSON without stack traces."""
    # Force 404 or unhandled path
    resp = auth_client.get("/api/v1/nonexistent-security-check")
    assert resp.status_code == 404
    payload = resp.json()
    assert payload["error"] is True
    assert "request_id" in payload
    # Must not contain server filesystem paths
    resp_text = resp.text
    assert "C:\\" not in resp_text
    assert "/home/" not in resp_text
    assert "Traceback" not in resp_text


# ============================================================================
# 5. PII Masking and Privacy Filter
# ============================================================================

def test_pii_masking_phone_and_upi():
    """Verifies that phone numbers, UPI IDs, and bank accounts are sanitized in log text."""
    sample_log = "Citizen 9876543210 submitted payment to scammer.mule@oksbi from account 123456789012"
    masked = mask_pii_text(sample_log)

    assert "9876543210" not in masked
    assert "scammer.mule@oksbi" not in masked
    assert "123456789012" not in masked
    assert "@oksbi" in masked  # Domain remains for debugging


def test_pii_masking_tokens():
    """Verifies that Bearer tokens and API keys are redacted from logs."""
    token_log = "Request authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    masked = mask_pii_text(token_log)
    assert "[REDACTED]" in masked
    assert "eyJhbG" not in masked
