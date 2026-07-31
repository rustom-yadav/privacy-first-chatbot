"""
Document management routes — upload, list, and delete PDF documents.

Security:
    - Filename sanitization (prevents path traversal)
    - File size validation (MAX_UPLOAD_SIZE_MB)
    - PDF-only format check
    - Rate limited uploads
    - No internal paths exposed in responses

Ingestion runs in asyncio.to_thread() to avoid blocking the event loop.
"""

import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, File, Request, UploadFile

from app.config import settings
from app.exceptions import (
    DocumentIngestionError,
    FileTooLargeError,
    InvalidFileFormatError,
)
from app.middleware.rate_limiter import limiter
from app.models.schemas import APIResponse, DocumentInfo, UploadResponseData

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=APIResponse[UploadResponseData])
@limiter.limit(settings.RATE_LIMIT_UPLOAD)
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    """
    Upload a PDF document for RAG ingestion.

    Security checks:
        1. File format must be .pdf
        2. File size must be under MAX_UPLOAD_SIZE_MB
        3. Filename is sanitized to prevent path traversal
    """
    from app.services.rag_service import rag_service

    # 1. Validate file format
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise InvalidFileFormatError()

    # 2. Sanitize filename — prevents path traversal attacks
    # Path("../../evil.pdf").name → "evil.pdf"
    secure_name = Path(file.filename).name
    if not secure_name or ".." in secure_name:
        raise InvalidFileFormatError("Invalid filename.")

    # 3. Read file content and check size
    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if len(content) > max_bytes:
        raise FileTooLargeError(
            f"File size ({len(content) / (1024 * 1024):.1f} MB) exceeds "
            f"the maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    # 4. Save to disk securely
    file_path = settings.UPLOAD_DIR / secure_name

    try:
        file_path.write_bytes(content)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise DocumentIngestionError(f"Failed to save file to disk: {e}")
    finally:
        await file.close()

    # 5. Run RAG ingestion in a thread to avoid blocking the event loop
    chunk_count = await asyncio.to_thread(rag_service.ingest_document, file_path)

    return APIResponse(
        success=True,
        data=UploadResponseData(
            filename=secure_name,
            chunk_count=chunk_count,
            message="File uploaded and ingested successfully. You can now ask questions!",
        ),
    )


@router.get("/list", response_model=APIResponse[list[DocumentInfo]])
async def list_documents(request: Request):
    """Returns a list of all ingested documents with their chunk counts."""
    from app.services.rag_service import rag_service

    docs = await asyncio.to_thread(rag_service.list_documents)

    return APIResponse(
        success=True,
        data=[DocumentInfo(**doc) for doc in docs],
    )


@router.delete("/{filename}", response_model=APIResponse)
async def delete_document(request: Request, filename: str):
    """
    Deletes a document and all its vectors from ChromaDB.
    Also removes the file from disk if it exists.
    """
    from app.services.rag_service import rag_service

    # Sanitize filename
    secure_name = Path(filename).name
    if not secure_name or ".." in secure_name:
        raise InvalidFileFormatError("Invalid filename.")

    await asyncio.to_thread(rag_service.delete_document, secure_name)

    return APIResponse(
        success=True,
        data={"message": f"Document '{secure_name}' deleted successfully."},
    )
