# apps/api/src/main.py
"""
Raksha Grid Central Intelligence FastAPI Application.

Authoritative entry point for Raksha Grid backend services.
Provides modular v1 routers, structured error handling, request ID tracing,
CORS security, and application lifecycle management.
"""

from fastapi import FastAPI, APIRouter
from rakshagrid.common.logging.logger import setup_logger

from apps.api.src.config import settings
from apps.api.src.core.lifespan import lifespan
from apps.api.src.middleware.request_id import RequestIDMiddleware
from apps.api.src.middleware.cors import setup_cors
from apps.api.src.middleware.error_handler import setup_exception_handlers

from apps.api.src.routers.v1 import (
    health_router,
    scam_router,
    audio_router,
    currency_router,
    crime_router,
    graph_router,
    reports_router,
    chat_router,
)

logger = setup_logger("rakshagrid.api.main")


def create_app() -> FastAPI:
    """
    Application factory for Raksha Grid FastAPI.
    Initializes lifespan, middleware, exception handlers, and registers versioned routers.
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=(
            "Central Intelligence API for Raksha Grid: Multi-modal Scam Defense, "
            "Counterfeit Currency Detection, Crime Hotspot Forecasting, and Citizen Fraud Registry."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. Register Core Middleware (Request ID tracing & CORS)
    application.add_middleware(RequestIDMiddleware)
    setup_cors(application)

    # 2. Register Structured Safe Exception Handlers
    setup_exception_handlers(application)

    # 3. Explicitly Register API v1 Routers (/api/v1/...)
    v1_router = APIRouter(prefix=settings.API_V1_PREFIX)
    v1_router.include_router(health_router)
    v1_router.include_router(scam_router)
    v1_router.include_router(audio_router)
    v1_router.include_router(currency_router)
    v1_router.include_router(crime_router)
    v1_router.include_router(graph_router)
    v1_router.include_router(reports_router)
    v1_router.include_router(chat_router)
    application.include_router(v1_router)

    # 4. Backward Compatibility: Mount Routers under legacy prefix (/api/...)
    legacy_router = APIRouter(prefix=settings.API_LEGACY_PREFIX)
    legacy_router.include_router(health_router)
    legacy_router.include_router(scam_router)
    legacy_router.include_router(audio_router)
    legacy_router.include_router(currency_router)
    legacy_router.include_router(crime_router)
    legacy_router.include_router(graph_router)
    legacy_router.include_router(reports_router)
    legacy_router.include_router(chat_router)
    application.include_router(legacy_router)

    # 5. Root lightweight health probe and system information
    application.include_router(health_router)

    @application.get("/", tags=["System"])
    def root():
        """Root application information."""
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "docs": "/docs",
            "api_v1": settings.API_V1_PREFIX,
        }

    logger.info(f"Initialized {settings.PROJECT_NAME} with 8 explicit routers mounted.")
    return application


# Authoritative single application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "apps.api.src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
