"""
Global exception handler for the FastAPI application.

Catches all AppError subclasses and unhandled exceptions,
returning structured JSON responses with appropriate HTTP status codes.
Stack traces are logged server-side but never sent to the client.
"""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import AppError

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    """
    Handles all AppError subclasses.
    Returns a structured JSON response with the correct HTTP status code.
    """
    logger.warning(
        f"[{request.method}] {request.url.path} → {exc.status_code}: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "data": None, "error": exc.detail},
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Catches any unhandled exception that slips through.
    Logs the full stack trace but returns a safe generic message to the client.
    """
    logger.error(
        f"[{request.method}] {request.url.path} → Unhandled exception: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": "An unexpected error occurred. Please try again later.",
        },
    )
