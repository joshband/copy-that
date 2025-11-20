"""
Copy That API - Minimal MVP for Cloud Run Deployment
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os

from copy_that.infrastructure.database import get_db
from copy_that.domain.models import Project

# Create FastAPI app
app = FastAPI(
    title="Copy That API",
    description="Multi-Modal Token Platform - Transform images, video, and audio into universal design tokens",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS (allow frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (required for Cloud Run)
@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run and monitoring"""
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Welcome message"""
    return {
        "message": "Welcome to Copy That API! 🎨",
        "tagline": "Multi-Modal Token Platform",
        "docs": "/docs",
        "health": "/health"
    }

# Example API endpoint
@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api": "Copy That v1.0.0",
        "status": "operational",
        "features": {
            "image_tokens": "coming soon",
            "video_tokens": "coming soon",
            "audio_tokens": "coming soon"
        },
        "gcp_project": os.getenv("GCP_PROJECT_ID", "copy-that-platform"),
        "environment": os.getenv("ENVIRONMENT", "production")
    }

# Token extraction endpoint (placeholder)
@app.post("/api/v1/extract")
async def extract_tokens():
    """Token extraction endpoint (MVP placeholder)"""
    return {
        "message": "Token extraction coming soon!",
        "status": "not_implemented",
        "roadmap": "Phase 1 - Q1 2025"
    }

# Database test endpoint
@app.get("/api/v1/db-test")
async def test_database(db: AsyncSession = Depends(get_db)):
    """Test database connection and query projects"""
    from sqlalchemy import select

    result = await db.execute(select(Project))
    projects = result.scalars().all()

    return {
        "database": "connected",
        "provider": "Neon",
        "projects_count": len(projects),
        "message": "Database connection successful! 🎉"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
