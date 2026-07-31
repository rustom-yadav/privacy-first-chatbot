"""
Request/response logging middleware.

Logs every HTTP request with:
- Unique request ID (for tracing)
- HTTP method + path
- Response status code
- Duration in milliseconds

The request ID is also sent back to the client via X-Request-ID header
so frontend errors can be correlated with server logs.
"""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("api.requests")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware that logs every incoming request and its response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = uuid.uuid4().hex[:8]
        start_time = time.perf_counter()

        # Attach request_id to request state for use in other handlers
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} → 500 "
                f"({duration_ms:.0f}ms) [unhandled exception]"
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Choose log level based on status code
        log_fn = logger.info if response.status_code < 400 else logger.warning
        log_fn(
            f"[{request_id}] {request.method} {request.url.path} "
            f"→ {response.status_code} ({duration_ms:.0f}ms)"
        )

        # Send request ID back to client for correlation
        response.headers["X-Request-ID"] = request_id
        return response
