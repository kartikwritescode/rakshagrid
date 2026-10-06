# apps/api/src/core/security.py
"""Security utilities, headers, and authentication guards for sensitive intelligence endpoints."""

import hmac
from typing import Optional
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from apps.api.src.config import settings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
HTTP_BEARER = HTTPBearer(auto_error=False)


def verify_api_key(
    api_key: Optional[str] = Security(API_KEY_HEADER),
    bearer_creds: Optional[HTTPAuthorizationCredentials] = Security(HTTP_BEARER),
) -> bool:
    """
    Validates authentication credentials against settings.API_KEY.
    
    Accepts:
    1. Header: 'X-API-Key: <key>'
    2. Header: 'Authorization: Bearer <token>'
    
    Behavior:
    - If settings.AUTH_ENABLED is False: permits access.
    - If neither credential is provided: raises HTTP 401 UNAUTHORIZED.
    - If a credential is provided but does not match: raises HTTP 403 FORBIDDEN.
    - Timing-safe comparison is used to thwart timing side-channel attacks.
    """
    if not settings.AUTH_ENABLED:
        return True

    configured_key = settings.API_KEY.get_secret_value() if settings.API_KEY else ""
    if not configured_key:
        # If no key is configured in settings, require explicit configuration
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server authentication configuration error: API_KEY is unset."
        )

    # Extract provided token
    candidate_key: Optional[str] = None
    if api_key:
        candidate_key = api_key.strip()
    elif bearer_creds and bearer_creds.credentials:
        candidate_key = bearer_creds.credentials.strip()

    if not candidate_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid 'X-API-Key' or 'Authorization: Bearer <token>' header.",
            headers={"WWW-Authenticate": "Bearer, ApiKey"},
        )

    # Constant-time comparison to prevent timing attacks
    is_valid = hmac.compare_digest(
        candidate_key.encode("utf-8"),
        configured_key.encode("utf-8"),
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or unauthorized authentication credentials.",
        )

    return True


# Convenience alias for dependency injection
require_auth = verify_api_key

