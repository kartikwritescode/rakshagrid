# apps/api/rakshagrid/api/main.py
"""Centralized FastAPI Application for Raksha Grid Platform."""

import sys
import os

# Dynamic repository root and packages sys.path registration
def _setup_sys_path():
    cur = os.path.abspath(os.path.dirname(__file__))
    repo_root = cur
    while repo_root and os.path.dirname(repo_root) != repo_root:
        if os.path.exists(os.path.join(repo_root, "pyproject.toml")) or os.path.exists(os.path.join(repo_root, ".git")):
            break
        repo_root = os.path.dirname(repo_root)

    paths_to_add = [
        repo_root,
        os.path.join(repo_root, "apps", "api"),
        os.path.join(repo_root, "packages", "common"),
        os.path.join(repo_root, "packages", "ai-scam"),
        os.path.join(repo_root, "packages", "ai-currency"),
        os.path.join(repo_root, "packages", "ai-crime"),
        os.path.join(repo_root, "packages", "ai-graph"),
    ]
    for p in paths_to_add:
        if os.path.exists(p) and p not in sys.path:
            sys.path.insert(0, p)

_setup_sys_path()

from fastapi import FastAPI
from rakshagrid.api.config import settings
from rakshagrid.api.core.events import lifespan
from rakshagrid.api.middleware.cors import setup_cors
from rakshagrid.api.middleware.error_handler import setup_exception_handlers
from rakshagrid.api.routers.v1 import (
    scam_router,
    currency_router,
    crime_router,
    health_router,
    audio_router,
)

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Unified REST API serving Digital Arrest Scam Interception, Audio Deepfake Detection, Counterfeit Currency Scanning, and Geospatial Crime Intelligence.",
        lifespan=lifespan
    )
    
    setup_cors(app)
    setup_exception_handlers(app)
    
    # Mount health router at root, /api, and /api/v1
    app.include_router(health_router)
    
    # Mount /api routes (backward compatibility)
    app.include_router(scam_router, prefix="/api")
    app.include_router(currency_router, prefix="/api")
    app.include_router(audio_router, prefix="/api")
    app.include_router(crime_router, prefix="/api")
    
    # Mount /api/v1 routes (modern versioned API)
    app.include_router(scam_router, prefix="/api/v1")
    app.include_router(currency_router, prefix="/api/v1")
    app.include_router(audio_router, prefix="/api/v1")
    app.include_router(crime_router, prefix="/api/v1")
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "rakshagrid.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
