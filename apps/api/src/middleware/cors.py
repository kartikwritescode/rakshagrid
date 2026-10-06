# apps/api/src/middleware/cors.py
"""CORS Middleware configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.src.config import settings

def setup_cors(app: FastAPI):
    """Applies hardened CORS middleware settings to the FastAPI application.
    
    Guarantees:
    - Never uses '*' wildcard when allow_credentials=True.
    - Explicit origins loaded from environment configuration.
    - Restricts allowed HTTP methods and exposes X-Request-ID for client tracing.
    """
    safe_origins = [o for o in settings.CORS_ORIGINS if o and o != "*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=safe_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-Request-ID", "Accept"],
        expose_headers=["X-Request-ID"]
    )
