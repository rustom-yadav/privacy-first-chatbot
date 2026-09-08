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

# Install gosu for safe privilege dropping (root -> appuser at runtime)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gosu && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home appuser

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Ensure the persistent-data directories exist and set correct ownership
# at build-time (matters for compose named volumes on first creation)
RUN mkdir -p uploaded_docs chroma_db local_db && \
    chown -R appuser:appuser uploaded_docs chroma_db local_db

# Entrypoint script: fixes ownership at container start (covers bind
# mounts too, whose ownership comes from the host), then drops from
# root to appuser before running the actual app.
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# NOTE: No `USER appuser` here — container starts as root so the
# entrypoint can fix volume ownership; it then drops to appuser itself
# via gosu before running the app. The app process never runs as root.
ENTRYPOINT ["entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]