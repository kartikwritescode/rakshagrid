# apps/api/src/routers/v1/__init__.py
"""V1 API Routers for Raksha Grid."""

from .health import router as health_router
from .scam import router as scam_router
from .audio import router as audio_router
from .currency import router as currency_router
from .crime import router as crime_router
from .graph import router as graph_router
from .reports import router as reports_router
from .chat import router as chat_router

__all__ = [
    "health_router",
    "scam_router",
    "audio_router",
    "currency_router",
    "crime_router",
    "graph_router",
    "reports_router",
    "chat_router",
]
