"""
Custom exception hierarchy for the Privacy-First Chatbot API.

All application-specific exceptions inherit from AppError,
which carries an HTTP status code and a user-safe detail message.
The global exception handler middleware catches these and returns
structured JSON responses.
"""


class AppError(Exception):
    """Base exception for all application errors."""

    status_code: int = 500
    detail: str = "An internal server error occurred."

    def __init__(self, detail: str | None = None, status_code: int | None = None):
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.detail)


# ── Document / Ingestion Errors ──────────────────────────────────────


class InvalidFileFormatError(AppError):
    """Raised when the uploaded file is not a supported format."""

    status_code = 400
    detail = "Invalid file format. Only PDF documents are allowed."


class FileTooLargeError(AppError):
    """Raised when the uploaded file exceeds the size limit."""

    status_code = 413
    detail = "File size exceeds the maximum allowed limit."


class DocumentIngestionError(AppError):
    """Raised when document ingestion (parsing, splitting, embedding) fails."""

    status_code = 500
    detail = "Failed to ingest the document."


class DocumentNotFoundError(AppError):
    """Raised when a requested document does not exist."""

    status_code = 404
    detail = "Document not found."


# ── LLM / Retrieval Errors ───────────────────────────────────────────


class LLMConnectionError(AppError):
    """Raised when the LLM backend (Ollama) is unreachable."""

    status_code = 503
    detail = "LLM service is unavailable. Please ensure Ollama is running."


class RetrievalError(AppError):
    """Raised when the retrieval pipeline fails to fetch context."""

    status_code = 500
    detail = "Failed to retrieve context from the knowledge base."


# ── Session / Input Errors ───────────────────────────────────────────


class SessionNotFoundError(AppError):
    """Raised when a session ID does not exist in storage."""

    status_code = 404
    detail = "Session not found."


class QueryTooLongError(AppError):
    """Raised when the user query exceeds the maximum allowed length."""

    status_code = 400
    detail = "Query exceeds the maximum allowed length."
