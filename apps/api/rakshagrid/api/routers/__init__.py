# apps/api/src/routers/__init__.py
from .v1 import (
    scam_router,
    currency_router,
    crime_router,
    health_router,
    audio_router,
)

__all__ = [
    "scam_router",
    "currency_router",
    "crime_router",
    "health_router",
    "audio_router",
]
