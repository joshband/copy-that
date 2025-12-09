# Multi-stage build for optimal image size
# Using Python 3.12 (latest stable) with BuildKit features

# ============================================
# Stage 1: Base Image with uv (modern pip replacement)
# ============================================
FROM python:3.12-slim as base

# Install system dependencies for OpenCV and other libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv (10-100x faster than pip)
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files and README (required by hatchling)
COPY pyproject.toml README.md ./

# ============================================
# Stage 2: Development Image
# ============================================
FROM base as development

# Copy source code first (needed for editable install)
COPY . .

# Install dev dependencies
RUN uv pip install --system -e ".[dev]"

# Expose port
EXPOSE 8000

# Development command (with hot reload)
CMD ["uvicorn", "copy_that.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================
# Stage 3: Builder (compile dependencies)
# ============================================
FROM base as builder

# Copy only dependency files first (better caching)
COPY pyproject.toml README.md ./

# Install production dependencies only (cached layer)
# Increase timeout for large ML packages (PyTorch = 858MB)
ENV UV_HTTP_TIMEOUT=300
RUN uv pip install --system --no-cache .

# Copy source code (changes frequently, separate layer)
COPY . .

# ============================================
# Stage 4: Production Image (minimal size)
# ============================================
FROM python:3.12-slim as production

# Security: Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/storage && \
    chown -R appuser:appuser /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Copy source code and entire project structure
COPY --chown=appuser:appuser . .

# Install the package in the production environment using the copied site-packages
# This ensures the copy_that module is properly registered
RUN python -m pip install --no-cache-dir --no-deps .

# Add src to PYTHONPATH for additional modules (core, cv_pipeline, etc.)
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# Switch to non-root user
USER appuser

# Health check (use PORT env var, default 8080)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:${PORT:-8080}/health')"

# Expose port (Cloud Run uses PORT env var, default 8080)
EXPOSE 8080

# Production command (gunicorn with uvicorn workers)
# Use shell form to support PORT environment variable from Cloud Run
CMD gunicorn copy_that.interfaces.api.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8080} \
    --access-logfile - \
    --error-logfile -
