# ── Stage 1: Build ───────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first (cache layer)
COPY pyproject.toml uv.lock ./

# Compile bytecode for faster startup
ENV UV_COMPILE_BYTECODE=1

# Install dependencies into the virtual environment
RUN uv sync --no-dev --frozen

# ── Stage 2: Runtime ─────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home appuser

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Copy sample.env as .env for default config values
# (docker-compose environment variables will override these at runtime)
COPY --chown=appuser:appuser sample.env .env

# Switch to non-root user before creating directories
USER appuser

# Ensure the directories exist (created with correct ownership automatically)
RUN mkdir -p uploaded_docs chroma_db local_db

# (User is already switched above)

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
