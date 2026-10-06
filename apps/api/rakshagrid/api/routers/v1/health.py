# backend/fastapi/app/routers/health_router.py
"""Centralized System Health Router."""

from fastapi import APIRouter
from rakshagrid.api.services.crime_service import crime_service

router = APIRouter(tags=["Health"])

@router.get("/health")
@router.get("/api/health")
@router.get("/api/v1/health")
def system_health():
    """Returns system status across all ML modules and storage."""
    crime_status = crime_service.get_status()
    return {
        "status": "healthy",
        "service": "Raksha Grid Central Intelligence API",
        "version": "2.0.0",
        "modules": {
            "module1_currency": "ready",
            "module2_scam": "ready",
            "module4_crime": crime_status["status"]
        }
    }
