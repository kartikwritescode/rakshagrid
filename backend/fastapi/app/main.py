# backend/fastapi/app/main.py
"""Centralized FastAPI Application for Raksha Grid Platform."""

import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI
from backend.fastapi.app.config.settings import settings
from backend.fastapi.app.core.events import lifespan
from backend.fastapi.app.middleware.cors import setup_cors
from backend.fastapi.app.middleware.error_handler import setup_exception_handlers

from backend.fastapi.app.routers.scam_router import router as scam_router
from backend.fastapi.app.routers.currency_router import router as currency_router
from backend.fastapi.app.routers.crime_router import router as crime_router
from backend.fastapi.app.routers.health_router import router as health_router
from backend.fastapi.app.routers.audio_router import router as audio_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Unified REST API serving Digital Arrest Scam Interception, Audio Deepfake Detection, Counterfeit Currency Scanning, and Geospatial Crime Intelligence.",
        lifespan=lifespan
    )
    
    setup_cors(app)
    setup_exception_handlers(app)
    
    app.include_router(health_router)
    app.include_router(scam_router)
    app.include_router(currency_router)
    app.include_router(audio_router)
    app.include_router(crime_router)
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.fastapi.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
