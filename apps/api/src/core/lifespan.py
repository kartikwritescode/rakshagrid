# apps/api/src/core/lifespan.py
"""Modern FastAPI lifespan context manager for startup and graceful shutdown."""

import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from rakshagrid.common.logging.logger import setup_logger
from apps.api.src.config import settings

logger = setup_logger("rakshagrid.api.lifespan")

START_TIME: float = time.time()

def get_uptime_seconds() -> float:
    """Returns uptime in seconds since lifespan startup."""
    return round(time.time() - START_TIME, 2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Initializes lightweight resources on startup and cleans up on shutdown.
    Avoids eager ML model loading to keep startup fast and health checks lightweight.
    """
    global START_TIME
    START_TIME = time.time()
    
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: Debug={settings.DEBUG}, Port={settings.PORT}")
    
    # Ensure storage paths exist
    os.makedirs(settings.UPLOADS_PATH, exist_ok=True)
    os.makedirs(settings.OUTPUTS_PATH, exist_ok=True)
    os.makedirs(settings.MODELS_PATH, exist_ok=True)
    
    yield
    
    # Release ML inference thread pool
    try:
        from apps.api.src.core.concurrency import inference_concurrency
        inference_concurrency.shutdown(wait=False)
    except Exception as e:
        logger.warning(f"Error shutting down inference concurrency: {e}")

    logger.info(f"Shutting down {settings.PROJECT_NAME}. Uptime: {get_uptime_seconds()}s")
