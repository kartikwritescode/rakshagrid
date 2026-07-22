# backend/fastapi/app/routers/__init__.py
from backend.fastapi.app.routers.scam_router import router as scam_router
from backend.fastapi.app.routers.currency_router import router as currency_router
from backend.fastapi.app.routers.crime_router import router as crime_router
from backend.fastapi.app.routers.health_router import router as health_router
from backend.fastapi.app.routers.audio_router import router as audio_router

__all__ = [
    "scam_router",
    "currency_router",
    "crime_router",
    "health_router",
    "audio_router",
]
