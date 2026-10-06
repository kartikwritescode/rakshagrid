# apps/api/src/middleware/request_id.py
"""Request ID and structured access logging middleware."""

import re
import time
import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from rakshagrid.common.logging.logger import setup_logger

logger = setup_logger("rakshagrid.api.access")

# Context variable accessible across asynchronous tasks
current_request_id: ContextVar[str] = ContextVar("current_request_id", default="")

SAFE_REQUEST_ID_REGEX = re.compile(r"^[a-zA-Z0-9_\-]{8,64}$")

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that assigns a unique Request ID to every HTTP request,
    attaches it to request.state and response headers, and logs structured telemetry.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        incoming_id = request.headers.get("X-Request-ID")
        if incoming_id and SAFE_REQUEST_ID_REGEX.match(incoming_id):
            request_id = incoming_id
        else:
            request_id = f"req_{uuid.uuid4().hex[:12]}"

        # Store in context variable and request state
        token = current_request_id.set(request_id)
        request.state.request_id = request_id

        start_time = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            raise
        finally:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            current_request_id.reset(token)

            # Skip excessive logging for quiet health check probes
            if request.url.path not in ["/health", "/api/health", "/api/v1/health"]:
                logger.info(
                    f"[{request_id}] {request.method} {request.url.path} - {status_code} ({latency_ms}ms)"
                )

        response.headers["X-Request-ID"] = request_id
        return response
