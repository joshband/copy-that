# Multi-stage build for optimal image size
# Using Python 3.12 (latest stable) with BuildKit features

# ============================================
# Stage 1: Base Image with uv (modern pip replacement)
# ============================================
FROM python:3.12-slim as base

# Install uv (10-100x faster than pip)
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# ============================================
# Stage 2: Development Image
# ============================================
FROM base as development

# Install dev dependencies
RUN uv pip install --system -e ".[dev]"

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Development command (with hot reload)
CMD ["uvicorn", "copy_that.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================
# Stage 3: Builder (compile dependencies)
# ============================================
FROM base as builder

# Install production dependencies only
RUN uv pip install --system . --no-dev

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

# Copy source code
COPY --chown=appuser:appuser src ./src

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Production command (gunicorn with uvicorn workers)
CMD ["gunicorn", "copy_that.interfaces.api.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
