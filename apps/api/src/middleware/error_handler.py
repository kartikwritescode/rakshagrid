# backend/fastapi/app/middleware/error_handler.py
"""Centralized exception handling middleware."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from rakshagrid.common.exceptions.base import RakshaGridException
from rakshagrid.common.logging.logger import setup_logger

logger = setup_logger("apps.api.error_handler")

def setup_exception_handlers(app: FastAPI):
    """Registers exception handlers for custom domain exceptions and unhandled errors."""
    
    @app.exception_handler(RakshaGridException)
    async def rakshagrid_exception_handler(request: Request, exc: RakshaGridException):
        logger.error(f"RakshaGrid Exception on {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Exception on {request.url.path}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": f"Internal Server Error: {str(exc)}",
                "details": {}
            }
        )
