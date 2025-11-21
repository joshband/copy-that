"""
Copy That API - Minimal MVP for Cloud Run Deployment
"""

import os
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.models import Project
from copy_that.infrastructure.database import Base, engine, get_db
from copy_that.interfaces.api.colors import router as colors_router

# Import routers
from copy_that.interfaces.api.projects import router as projects_router
from copy_that.interfaces.api.sessions import router as sessions_router

# Create FastAPI app
app = FastAPI(
    title="Copy That API",
    description="Multi-Modal Token Platform - Transform images, video, and audio into universal design tokens",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS (allow frontend to call API)
# Get allowed origins from environment or use defaults for development
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects_router)
app.include_router(colors_router)
app.include_router(sessions_router)


# Initialize database on startup
@app.on_event("startup")
async def startup():
    """Create database tables on startup (development only)"""
    # Only auto-create tables in local development
    # Production should use Alembic migrations
    if os.getenv("ENVIRONMENT") in ("local", "development", None):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


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
        "version": "1.0.0"
    }


# Root endpoint - serve demo page
@app.get("/", response_class=FileResponse)
async def root():
    """Serve the educational demo page"""
    demo_file = Path(__file__).parent.parent.parent.parent.parent / "static" / "index.html"
    if demo_file.exists():
        return demo_file
    # Fallback to API welcome message
    return JSONResponse({
        "message": "Welcome to Copy That API!",
        "tagline": "Multi-Modal Token Platform",
        "demo": "/static/index.html",
        "docs": "/docs",
        "health": "/health"
    })


# API status endpoint
@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api": "Copy That v1.0.0",
        "status": "operational",
        "features": {
            "color_tokens": "available",
            "typography_tokens": "coming soon",
            "spacing_tokens": "coming soon"
        },
        "gcp_project": os.getenv("GCP_PROJECT_ID", "copy-that-platform"),
        "environment": os.getenv("ENVIRONMENT", "production")
    }


# API Documentation endpoint
@app.get("/api/v1/docs", response_class=JSONResponse)
async def api_documentation():
    """Get API documentation in JSON format"""
    return {
        "title": "Copy That API v1.0.0",
        "description": "AI-powered color extraction platform using Claude Sonnet 4.5",
        "endpoints": {
            "projects": {
                "list": "GET /api/v1/projects",
                "create": "POST /api/v1/projects",
                "get": "GET /api/v1/projects/{id}",
                "update": "PUT /api/v1/projects/{id}",
                "delete": "DELETE /api/v1/projects/{id}"
            },
            "colors": {
                "extract": "POST /api/v1/colors/extract",
                "extract_streaming": "POST /api/v1/colors/extract-streaming",
                "list_by_project": "GET /api/v1/projects/{id}/colors",
                "create": "POST /api/v1/colors",
                "get": "GET /api/v1/colors/{id}"
            },
            "sessions": {
                "create": "POST /api/v1/sessions",
                "get": "GET /api/v1/sessions/{id}",
                "get_library": "GET /api/v1/sessions/{id}/library",
                "batch_extract": "POST /api/v1/sessions/{id}/extract",
                "curate": "POST /api/v1/sessions/{id}/library/curate",
                "export": "GET /api/v1/sessions/{id}/library/export"
            }
        },
        "documentation": {
            "interactive_swagger": "/docs",
            "interactive_redoc": "/redoc",
            "openapi_json": "/openapi.json"
        }
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
        "message": "Database connection successful!"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
