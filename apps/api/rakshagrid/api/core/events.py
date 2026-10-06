# backend/fastapi/app/core/events.py
"""FastAPI Application Lifespan Events."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from rakshagrid.common.logging.logger import setup_logger
from rakshagrid.ai_crime.predict import init_engine

logger = setup_logger("apps.api.events")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler executing startup and shutdown logic."""
    logger.info("==================================================")
    logger.info("Starting Raksha Grid Central Intelligence API...")
    logger.info("Pre-loading ML Modules & Fitting Engines...")
    logger.info("==================================================")
    
    # Eagerly initialize Module 4 Crime Engine
    try:
        init_engine()
        logger.info("✓ Module 4 Crime Hotspot Engine loaded")
    except Exception as e:
        logger.warning(f"Could not initialize Crime Engine: {e}")
        
    yield
    
    logger.info("Shutting down Raksha Grid Central Intelligence API...")
