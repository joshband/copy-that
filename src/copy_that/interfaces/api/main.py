"""
Copy That API - Minimal MVP for Cloud Run Deployment
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.models import Project
from copy_that.infrastructure.database import Base, engine, get_db
from copy_that.interfaces.api.auth import router as auth_router
from copy_that.interfaces.api.colors import router as colors_router
from copy_that.interfaces.api.design_tokens import router as design_tokens_router
from copy_that.interfaces.api.lighting import router as lighting_router
from copy_that.interfaces.api.metrics import router as metrics_router
from copy_that.interfaces.api.middleware.security_headers import SecurityHeadersMiddleware
from copy_that.interfaces.api.multi_extract import router as multi_extract_router

# Import routers
from copy_that.interfaces.api.projects import router as projects_router
from copy_that.interfaces.api.sessions import router as sessions_router
from copy_that.interfaces.api.shadows import router as shadows_router
from copy_that.interfaces.api.snapshots import router as snapshots_router
from copy_that.interfaces.api.spacing import router as spacing_router
from copy_that.interfaces.api.typography import router as typography_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Create database tables (development only)
    # Production should use Alembic migrations
    if os.getenv("ENVIRONMENT") in ("local", "development", None):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: cleanup would go here if needed


# Create FastAPI app
app = FastAPI(
    title="Copy That API",
    description="Multi-Modal Token Platform - Transform images, video, and audio into universal design tokens",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS (allow frontend to call API)
# Get allowed origins from environment or use defaults for development
CORS_ORIGINS_RAW = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:3000",
)
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_RAW.split(",")]

# Security: Warn if wildcard CORS is used in non-development environments
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
if "*" in CORS_ORIGINS and ENVIRONMENT not in ("local", "development"):
    import logging

    logging.warning(
        f"SECURITY WARNING: CORS_ORIGINS contains wildcard '*' in {ENVIRONMENT} environment. "
        "This allows any origin to make requests. Configure explicit origins for production."
    )

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware with better security
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Request-ID",
        "X-API-Key",
        "X-Requested-With",
    ],
    expose_headers=[
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ],
    max_age=600,
)

# Include routers
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(colors_router)
app.include_router(spacing_router)
app.include_router(typography_router)
app.include_router(sessions_router)
app.include_router(multi_extract_router)
app.include_router(snapshots_router)
app.include_router(shadows_router)
app.include_router(lighting_router)
app.include_router(design_tokens_router)
app.include_router(metrics_router)

# Setup Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


# Mount static files for educational demo
static_dir = Path(__file__).parent.parent.parent.parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Health check endpoint (required for Cloud Run)
@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run and monitoring"""
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "version": "1.0.0",
    }


# Root endpoint - serve demo page
@app.get("/", response_class=FileResponse)
async def root():
    """Serve the educational demo page"""
    demo_file = Path(__file__).parent.parent.parent.parent.parent / "static" / "index.html"
    if demo_file.exists():
        return demo_file
    # Fallback to API welcome message
    return JSONResponse(
        {
            "message": "Welcome to Copy That API!",
            "tagline": "Multi-Modal Token Platform",
            "demo": "/static/index.html",
            "docs": "/docs",
            "health": "/health",
        }
    )


# API status endpoint
@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api": "Copy That v1.0.0",
        "status": "operational",
        "features": {
            "color_tokens": "available",
            "spacing_tokens": "available",
            "typography_tokens": "available",
        },
        "gcp_project": os.getenv("GCP_PROJECT_ID", "copy-that-platform"),
        "environment": os.getenv("ENVIRONMENT", "production"),
    }


# API Documentation endpoint
@app.get("/api/v1/docs", response_class=JSONResponse)
async def api_documentation():
    """Get API documentation in JSON format"""
    return {
        "title": "Copy That API v1.0.0",
        "description": "AI-powered color extraction platform using Claude Sonnet 4.5",
        "endpoints": {
            "auth": {
                "register": "POST /api/v1/auth/register",
                "login": "POST /api/v1/auth/token",
                "refresh": "POST /api/v1/auth/refresh",
                "me": "GET /api/v1/auth/me",
            },
            "projects": {
                "list": "GET /api/v1/projects",
                "create": "POST /api/v1/projects",
                "get": "GET /api/v1/projects/{id}",
                "update": "PUT /api/v1/projects/{id}",
                "delete": "DELETE /api/v1/projects/{id}",
            },
            "colors": {
                "extract": "POST /api/v1/colors/extract",
                "extract_streaming": "POST /api/v1/colors/extract-streaming",
                "list_by_project": "GET /api/v1/projects/{id}/colors",
                "create": "POST /api/v1/colors",
                "get": "GET /api/v1/colors/{id}",
            },
            "typography": {
                "extract": "POST /api/v1/typography/extract",
                "list_by_project": "GET /api/v1/projects/{id}/typography",
                "batch_extract": "POST /api/v1/typography/batch",
                "create": "POST /api/v1/typography",
                "get": "GET /api/v1/typography/{id}",
                "update": "PUT /api/v1/typography/{id}",
                "delete": "DELETE /api/v1/typography/{id}",
                "export": "GET /api/v1/typography/export/w3c",
            },
            "spacing": {
                "extract": "POST /api/v1/spacing/extract",
                "extract_streaming": "POST /api/v1/spacing/extract-streaming",
                "batch_extract": "POST /api/v1/spacing/batch-extract",
                "scales": "GET /api/v1/spacing/scales",
            },
            "sessions": {
                "create": "POST /api/v1/sessions",
                "get": "GET /api/v1/sessions/{id}",
                "get_library": "GET /api/v1/sessions/{id}/library",
                "batch_extract": "POST /api/v1/sessions/{id}/extract",
                "curate": "POST /api/v1/sessions/{id}/library/curate",
                "export": "GET /api/v1/sessions/{id}/library/export",
            },
        },
        "documentation": {
            "interactive_swagger": "/docs",
            "interactive_redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
    }


# Database test endpoint
@app.get("/api/v1/db-test")
async def test_database(db: AsyncSession = Depends(get_db)):
    """Test database connection and query projects"""
    result = await db.execute(select(Project))
    projects = result.scalars().all()

    return {
        "database": "connected",
        "provider": "Neon",
        "projects_count": len(projects),
        "message": "Database connection successful!",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
