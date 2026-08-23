"""
Standardized API request/response schemas for the Privacy-First Chatbot.

All endpoints should use these models for consistency.
The generic APIResponse[T] envelope wraps every response with
success/error status for uniform client-side handling.
"""

from pydantic import BaseModel, Field


class APIResponse[DataT](BaseModel):
    """
    Standard response wrapper for all API endpoints.

    Usage:
        return APIResponse(success=True, data=MyData(...))
        return APIResponse(success=False, error="Something went wrong")
    """

    success: bool
    data: DataT | None = None
    error: str | None = None


# ── Source Attribution ────────────────────────────────────────────────


class SourceInfo(BaseModel):
    """Represents one source chunk used to generate the answer."""

    filename: str
    page: int


# ── Chat Schemas ─────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    """Incoming chat request from the frontend."""

    query: str = Field(..., min_length=1, description="The user's question")
    session_id: str | None = Field(
        default=None,
        description="Optional session ID for conversation continuity. "
        "If not provided, a new session is created automatically.",
    )


class ChatResponseData(BaseModel):
    """Data payload returned from a chat query."""

    query: str
    answer: str
    session_id: str
    sources: list[SourceInfo] = []
    response_time_ms: float = Field(
        ..., description="LLM response time in milliseconds"
    )


class ClearHistoryResponseData(BaseModel):
    """Data returned after clearing conversation history."""

    session_id: str
    messages_deleted: int
    message: str


# ── Document Schemas ─────────────────────────────────────────────────


class DocumentInfo(BaseModel):
    """Metadata about an ingested document."""

    filename: str
    chunk_count: int


class UploadResponseData(BaseModel):
    """Data returned after successful document upload and ingestion."""

    filename: str
    chunk_count: int
    message: str
