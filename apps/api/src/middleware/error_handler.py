# apps/api/src/middleware/error_handler.py
"""Centralized exception handling with structured, safe error responses."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from rakshagrid.common.exceptions.base import (
    RakshaGridException,
    MLInferenceException,
    MissingModelArtifactError,
    ValidationException,
    ResourceNotFoundException,
    AudioTranscriptionException,
    CrimeDataUnavailableException,
)
from rakshagrid.common.logging.logger import setup_logger
from apps.api.src.config import settings

logger = setup_logger("rakshagrid.api.errors")

def _get_request_id(request: Request) -> str:
    """Helper to extract request ID from request state or header."""
    return getattr(request.state, "request_id", request.headers.get("X-Request-ID", "unknown"))

def setup_exception_handlers(app: FastAPI):
    """Registers standard exception handlers converting exceptions to structured ErrorResponse payloads."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = _get_request_id(request)
        formatted_errors = []
        for err in exc.errors():
            loc = " -> ".join(str(l) for l in err.get("loc", []))
            formatted_errors.append({
                "location": loc,
                "message": err.get("msg", "Invalid value"),
                "type": err.get("type", "value_error")
            })

        logger.warning(f"[{request_id}] Validation Error on {request.method} {request.url.path}: {formatted_errors}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": True,
                "code": "VALIDATION_ERROR",
                "message": "The request payload failed input validation.",
                "request_id": request_id,
                "details": {"validation_errors": formatted_errors}
            },
            headers={"X-Request-ID": request_id}
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        request_id = _get_request_id(request)
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            429: "TOO_MANY_REQUESTS",
            500: "INTERNAL_ERROR",
            503: "SERVICE_UNAVAILABLE"
        }
        error_code = code_map.get(exc.status_code, "HTTP_ERROR")
        safe_message = str(exc.detail) if exc.detail else "An HTTP error occurred."

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "code": error_code,
                "message": safe_message,
                "request_id": request_id
            },
            headers={"X-Request-ID": request_id}
        )

    @app.exception_handler(MissingModelArtifactError)
    async def missing_model_exception_handler(request: Request, exc: MissingModelArtifactError):
        request_id = _get_request_id(request)
        logger.error(f"[{request_id}] Missing Model Artifact: {exc.message}")

        # In debug mode provide module hint, in production do not leak filesystem paths
        safe_message = (
            f"Required AI service component ({exc.module_name}) is unavailable."
            if settings.DEBUG
            else "The requested AI detection service is currently unavailable. Please contact the administrator."
        )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": True,
                "code": "MODEL_UNAVAILABLE",
                "message": safe_message,
                "request_id": request_id
            },
            headers={"X-Request-ID": request_id}
        )

    @app.exception_handler(AudioTranscriptionException)
    async def audio_transcription_exception_handler(request: Request, exc: AudioTranscriptionException):
        request_id = _get_request_id(request)
        logger.warning(f"[{request_id}] Audio STT Error: {exc.reason_code} - {exc.message}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "status": "transcription_failed",
                "code": exc.reason_code,
                "reason_code": exc.reason_code,
                "message": exc.message,
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id},
        )

    @app.exception_handler(CrimeDataUnavailableException)
    async def crime_data_unavailable_exception_handler(request: Request, exc: CrimeDataUnavailableException):
        request_id = _get_request_id(request)
        logger.warning(f"[{request_id}] Crime Data Unavailable: {exc.message}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "status": "data_unavailable",
                "code": exc.code,
                "message": exc.message,
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id},
        )

    @app.exception_handler(RakshaGridException)
    async def rakshagrid_exception_handler(request: Request, exc: RakshaGridException):
        request_id = _get_request_id(request)
        logger.error(f"[{request_id}] Application Error: {exc.message}")

        if isinstance(exc, ValidationException):
            code = "VALIDATION_ERROR"
            safe_message = exc.message
        elif isinstance(exc, ResourceNotFoundException):
            code = "NOT_FOUND"
            safe_message = exc.message
        elif isinstance(exc, MLInferenceException):
            code = "INFERENCE_ERROR"
            safe_message = (
                exc.message if settings.DEBUG
                else "An error occurred during machine learning inference."
            )
        else:
            code = "APPLICATION_ERROR"
            safe_message = (
                exc.message if settings.DEBUG
                else "A processing error occurred in the service."
            )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "code": code,
                "message": safe_message,
                "request_id": request_id,
                "details": exc.details if settings.DEBUG else None
            },
            headers={"X-Request-ID": request_id}
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = _get_request_id(request)
        # Full exception and stacktrace are logged securely on the server
        logger.exception(f"[{request_id}] Internal Server Exception on {request.method} {request.url.path}: {exc}")

        # Production and client responses never expose stacktraces, internal filesystem paths, or credentials
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please contact system support.",
                "request_id": request_id
            },
            headers={"X-Request-ID": request_id}
        )

