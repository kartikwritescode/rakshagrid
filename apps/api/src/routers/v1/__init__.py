# apps/api/src/routers/v1/__init__.py
from .scam import router as scam_router
from .currency import router as currency_router
from .crime import router as crime_router
from .health import router as health_router
from .audio import router as audio_router

__all__ = [
    "scam_router",
    "currency_router",
    "crime_router",
    "health_router",
    "audio_router",
]
