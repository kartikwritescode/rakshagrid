# apps/api/src/core/dependencies.py
"""Centralized dependency injection providers for FastAPI endpoints."""

from fastapi import Request
from apps.api.src.config import Settings, settings

def get_settings() -> Settings:
    """Provides validated application settings."""
    return settings

def get_request_id(request: Request) -> str:
    """Retrieves current request ID injected by RequestIDMiddleware."""
    return getattr(request.state, "request_id", "req-unknown")
