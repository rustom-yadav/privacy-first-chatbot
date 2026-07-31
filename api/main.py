"""
Privacy-First Chatbot — FastAPI Application Entry Point.

Registers:
    - CORS middleware (origins from config)
    - Rate limiting middleware (slowapi)
    - Request logging middleware
    - Global exception handlers
    - Route modules (chat, document)
    - Health check endpoint (pings Ollama + ChromaDB)
"""

import logging

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.exceptions import AppError
from app.middleware.exception_handler import (
    app_exception_handler,
    unhandled_exception_handler,
)
from app.middleware.rate_limiter import limiter
from app.middleware.request_logger import RequestLoggerMiddleware
from app.routes import chat, document

# ── Logging Setup ────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# ── FastAPI App ──────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description="Secure, local RAG pipeline using FastAPI, LangChain, and Ollama",
    version="1.0.0",
    debug=settings.DEBUG,
)

# ── Middleware Stack (order matters — last added = first executed) ────

# 1. Request Logger (outermost — logs every request including errors)
app.add_middleware(RequestLoggerMiddleware)

# 2. CORS (controlled from config, no wildcard methods/headers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

# ── Rate Limiter ─────────────────────────────────────────────────────

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Exception Handlers ───────────────────────────────────────────────

app.add_exception_handler(AppError, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# ── Routes ───────────────────────────────────────────────────────────

app.include_router(
    document.router, prefix="/api/document", tags=["Document Ingestion (RAG)"]
)
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chatbot"])


# ── Health Check ─────────────────────────────────────────────────────


@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Real health check that verifies all dependencies are reachable.
    Returns 'healthy' only if Ollama AND ChromaDB are both operational.
    """
    # Check Ollama
    ollama_status = "down"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.OLLAMA_HOST}")
            if resp.status_code == 200:
                ollama_status = "up"
    except Exception:
        pass

    # Check ChromaDB
    chroma_status = "down"
    doc_count = 0
    try:
        from app.services.rag_service import rag_service

        data = rag_service.vector_store.get()
        chroma_status = "up"
        doc_count = len(data.get("documents", [])) if data else 0
    except Exception:
        pass

    overall = "healthy" if (ollama_status == "up" and chroma_status == "up") else "degraded"

    return {
        "status": overall,
        "app": settings.APP_NAME,
        "dependencies": {
            "ollama": {
                "status": ollama_status,
                "host": settings.OLLAMA_HOST,
                "model": settings.LLM_MODEL,
            },
            "chromadb": {
                "status": chroma_status,
                "total_chunks": doc_count,
            },
        },
    }


# ── Script Mode Entry Point ─────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG
    )
