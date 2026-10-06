# apps/api/src/schemas/health_schema.py
"""Schemas for system health check endpoints."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Service readiness status")
    service: str = Field(default="Raksha Grid Central Intelligence API")
    version: str = Field(default="2.0.0")
    uptime_seconds: float | None = Field(default=None, description="Service uptime in seconds")
    timestamp: str | None = None
    modules: dict[str, str] = Field(
        default_factory=lambda: {
            "scam_detector": "ready",
            "currency_detector": "ready",
            "crime_intelligence": "ready",
            "graph_syndicates": "ready",
            "audio_biometrics": "ready",
        }
    )
