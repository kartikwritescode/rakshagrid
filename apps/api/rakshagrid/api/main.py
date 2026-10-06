# apps/api/rakshagrid/api/main.py
"""
Installable package entry point for Raksha Grid API.
Redirects to the authoritative application factory and instance in apps.api.src.main.
"""

from apps.api.src.main import app, create_app
from apps.api.src.config import settings

__all__ = ["app", "create_app", "settings"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "rakshagrid.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
