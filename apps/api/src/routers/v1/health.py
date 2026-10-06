# apps/api/src/routers/v1/health.py
"""Lightweight system health check router."""

from datetime import datetime, timezone
from fastapi import APIRouter, status
from apps.api.src.config import settings
from apps.api.src.core.lifespan import get_uptime_seconds
from apps.api.src.schemas.health_schema import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check():
    """
    Lightweight health check endpoint.
    Performs fast status verification without triggering heavy ML model loading.
    """
    return HealthResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        uptime_seconds=get_uptime_seconds(),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
