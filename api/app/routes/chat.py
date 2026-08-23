"""
Chat routes — AI conversation endpoints with session support.

Features:
    - Anonymous session management (auto-generated UUID if not provided)
    - Per-session persistent history (SQLite)
    - Source attribution in responses
    - Response time tracking
    - Rate limiting
    - Query length validation
    - Non-blocking LLM calls via asyncio.to_thread()
"""

import asyncio
import logging
import time
import uuid

from fastapi import APIRouter, Depends, Request

from app.config import settings
from app.exceptions import QueryEmptyError, QueryTooLongError
from app.middleware.rate_limiter import limiter
from app.models.schemas import (
    APIResponse,
    ChatRequest,
    ChatResponseData,
    ClearHistoryResponseData,
    SourceInfo,
)

logger = logging.getLogger(__name__)


def get_llm_service():
    from app.services.llm_service import llm_service

    return llm_service


router = APIRouter()


@router.post("/", response_model=APIResponse[ChatResponseData])
@limiter.limit(settings.RATE_LIMIT_CHAT)
async def chat_with_bot(
    request: Request, body: ChatRequest, llm_service=Depends(get_llm_service)
):
    """
    Send a chat query and get an AI-generated response.

    If no session_id is provided, a new one is generated automatically.
    History is maintained per-session in SQLite (survives restarts).
    """

    # 1. Validate query length
    query = body.query.strip()
    if not query:
        raise QueryEmptyError("Query cannot be empty.")

    if len(query) > settings.MAX_QUERY_LENGTH:
        raise QueryTooLongError(
            f"Query length ({len(query)} chars) exceeds the maximum "
            f"of {settings.MAX_QUERY_LENGTH} characters."
        )

    # 2. Resolve session ID (auto-generate if not provided)
    session_id = body.session_id or uuid.uuid4().hex

    # 3. Run LLM pipeline in thread (non-blocking)
    start_time = time.perf_counter()

    answer, sources = await asyncio.to_thread(
        llm_service.generate_response, query, session_id
    )

    response_time_ms = (time.perf_counter() - start_time) * 1000

    # 4. Return structured response
    return APIResponse(
        success=True,
        data=ChatResponseData(
            query=query,
            answer=answer,
            session_id=session_id,
            sources=[SourceInfo(**s) for s in sources],
            response_time_ms=round(response_time_ms, 2),
        ),
    )


@router.delete("/history", response_model=APIResponse[ClearHistoryResponseData])
async def clear_chat_history(request: Request, session_id: str):
    """
    Clears conversation history for a specific session.
    The session_id must be provided as a query parameter.
    """
    from app.services.session_service import session_service

    deleted = session_service.clear_session(session_id)

    return APIResponse(
        success=True,
        data=ClearHistoryResponseData(
            session_id=session_id,
            messages_deleted=deleted,
            message="Conversation history cleared.",
        ),
    )
