# apps/api/rakshagrid/api/middleware/cors.py
"""CORS Middleware configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rakshagrid.api.config import settings

def setup_cors(app: FastAPI):
    """Applies CORS middleware settings to the FastAPI application."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
