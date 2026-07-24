from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.llm_service import llm_service

router = APIRouter()

# Define Request and Response schemas
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    query: str
    answer: str

@router.post("/", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    """
    Endpoint for the frontend to send chat queries.
    Uses RAG (Retrieval-Augmented Generation) with a local LLM to answer.
    """
    # 1. Basic validation
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty."
        )
    
    try:
        # 2. Pass query to LLM service to get the RAG response
        answer = llm_service.generate_response(request.query)
        
        # 3. Return the structured response
        return ChatResponse(
            query=request.query,
            answer=answer
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
