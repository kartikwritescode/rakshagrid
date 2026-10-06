# apps/api/src/main.py
"""Compatibility entrypoint redirecting to rakshagrid.api.main:app."""

from rakshagrid.api.main import app, create_app

__all__ = ["app", "create_app"]

if __name__ == "__main__":
    import uvicorn
    from rakshagrid.api.config import settings
    uvicorn.run("rakshagrid.api.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
