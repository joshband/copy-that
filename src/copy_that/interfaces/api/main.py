"""
Copy That API - Minimal MVP for Cloud Run Deployment
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import json
import logging
from pathlib import Path

from copy_that.infrastructure.database import get_db, engine, Base
from copy_that.domain.models import Project, ColorToken, ExtractionJob
from copy_that.application.color_extractor import AIColorExtractor, extract_colors
from copy_that.interfaces.api.schemas import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ExtractColorRequest,
    ColorExtractionResponse,
    ColorTokenCreateRequest,
    ColorTokenDetailResponse,
    ColorTokenResponse,
)

logger = logging.getLogger(__name__)

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


# Initialize database on startup
@app.on_event("startup")
async def startup():
    """Create database tables on startup (development only)"""
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
        "message": "Welcome to Copy That API! 🎨",
        "tagline": "Multi-Modal Token Platform",
        "demo": "/static/index.html",
        "docs": "/docs",
        "health": "/health"
    })

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


# Project Management Endpoints

@app.post("/api/v1/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    request: ProjectCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new project

    Args:
        request: ProjectCreateRequest with name and optional description
        db: Database session

    Returns:
        Created project with ID
    """
    project = Project(
        name=request.name,
        description=request.description
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat()
    )


@app.get("/api/v1/projects", response_model=list[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0
):
    """List all projects

    Args:
        db: Database session
        limit: Maximum number of projects to return
        offset: Number of projects to skip

    Returns:
        List of projects
    """
    result = await db.execute(
        select(Project).order_by(Project.created_at.desc()).limit(limit).offset(offset)
    )
    projects = result.scalars().all()

    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat()
        )
        for p in projects
    ]


@app.get("/api/v1/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific project

    Args:
        project_id: Project ID
        db: Database session

    Returns:
        Project details

    Raises:
        HTTPException: If project not found
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat()
    )


@app.put("/api/v1/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    request: ProjectUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update a project

    Args:
        project_id: Project ID
        request: ProjectUpdateRequest with fields to update
        db: Database session

    Returns:
        Updated project

    Raises:
        HTTPException: If project not found
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    # Update fields if provided
    if request.name is not None:
        project.name = request.name
    if request.description is not None:
        project.description = request.description

    from datetime import datetime
    project.updated_at = datetime.utcnow()

    db.add(project)
    await db.commit()
    await db.refresh(project)

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat()
    )


@app.delete("/api/v1/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a project

    Args:
        project_id: Project ID
        db: Database session

    Raises:
        HTTPException: If project not found
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    await db.delete(project)
    await db.commit()


# API Documentation endpoint
@app.get("/api/v1/docs", response_class=JSONResponse)
async def api_documentation():
    """Get API documentation in JSON format"""
    return {
        "title": "Copy That API v1.0.0",
        "description": "AI-powered color extraction platform using Claude Sonnet 4.5",
        "endpoints": {
            "color_extraction": {
                "method": "POST",
                "path": "/api/v1/colors/extract",
                "description": "Extract colors from an image URL",
                "request": {
                    "image_url": "URL of the image to analyze",
                    "project_id": "ID of the project to associate colors with",
                    "max_colors": "Maximum number of colors to extract (1-50, default 10)"
                },
                "response": {
                    "colors": "List of extracted ColorToken objects",
                    "dominant_colors": "Top 3 dominant hex colors",
                    "color_palette": "Description of the overall palette",
                    "extraction_confidence": "Overall extraction confidence (0-1)"
                }
            },
            "get_project_colors": {
                "method": "GET",
                "path": "/api/v1/projects/{project_id}/colors",
                "description": "Get all color tokens for a project",
                "response": "List of ColorTokenDetailResponse objects"
            },
            "create_color_token": {
                "method": "POST",
                "path": "/api/v1/colors",
                "description": "Create a new color token",
                "request": {
                    "project_id": "Project ID (required)",
                    "hex": "Hex color code (required)",
                    "rgb": "RGB format (required)",
                    "name": "Human-readable color name (required)",
                    "semantic_name": "Semantic token name (optional)",
                    "confidence": "Confidence score 0-1 (required)"
                }
            },
            "get_color_token": {
                "method": "GET",
                "path": "/api/v1/colors/{color_id}",
                "description": "Get a specific color token"
            }
        },
        "documentation": {
            "interactive_swagger": "/docs",
            "interactive_redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "educational_demo": {
            "url": "/",
            "description": "Interactive web interface for testing color extraction"
        }
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
    result = await db.execute(select(Project))
    projects = result.scalars().all()

    return {
        "database": "connected",
        "provider": "Neon",
        "projects_count": len(projects),
        "message": "Database connection successful! 🎉"
    }


# Color Extraction Endpoints

@app.post("/api/v1/colors/extract", response_model=ColorExtractionResponse)
async def extract_colors_from_image(
    request: ExtractColorRequest,
    db: AsyncSession = Depends(get_db)
):
    """Extract colors from an image URL or base64 data using AI

    This endpoint:
    1. Accepts either an image URL or base64 encoded image data
    2. Uses Claude Sonnet 4.5 to analyze and extract colors
    3. Stores extracted colors in the database
    4. Returns the extracted color palette

    Args:
        request: ExtractColorRequest with image_url or image_base64 and project_id
        db: Database session

    Returns:
        ColorExtractionResponse with extracted colors

    Raises:
        HTTPException: If project not found or extraction fails
    """
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == request.project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {request.project_id} not found"
        )

    # Verify at least one image source is provided
    if not request.image_url and not request.image_base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either image_url or image_base64 must be provided"
        )

    try:
        # Extract colors using AI
        extractor = AIColorExtractor()

        if request.image_base64:
            # Extract from base64 data
            extraction_result = extractor.extract_colors_from_base64(
                request.image_base64, media_type="image/png", max_colors=request.max_colors
            )
        else:
            # Extract from URL
            extraction_result = extractor.extract_colors_from_image_url(
                request.image_url, max_colors=request.max_colors
            )

        # Create extraction job record
        source_identifier = request.image_url or "base64_upload"
        extraction_job = ExtractionJob(
            project_id=request.project_id,
            source_url=source_identifier,
            extraction_type="color",
            status="completed",
            result_data=json.dumps({
                "color_count": len(extraction_result.colors),
                "palette": extraction_result.color_palette
            })
        )
        db.add(extraction_job)
        await db.flush()

        # Store color tokens in database
        for color in extraction_result.colors:
            color_token = ColorToken(
                project_id=request.project_id,
                extraction_job_id=extraction_job.id,
                hex=color.hex,
                rgb=color.rgb,
                name=color.name,
                semantic_name=color.semantic_name,
                confidence=color.confidence,
                harmony=color.harmony,
                usage=json.dumps(color.usage) if color.usage else None
            )
            db.add(color_token)

        await db.commit()
        logger.info(f"Extracted {len(extraction_result.colors)} colors for project {request.project_id}")

        return extraction_result

    except Exception as e:
        logger.error(f"Color extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Color extraction failed: {str(e)}"
        )


@app.post("/api/v1/colors/extract-streaming")
async def extract_colors_streaming(
    request: ExtractColorRequest,
    db: AsyncSession = Depends(get_db)
):
    """Stream color extraction results as they become available

    Returns Server-Sent Events (SSE) stream with:
    1. Phase 1 (instant): Basic color extraction from image
    2. Phase 2 (async): Claude AI enhancements (semantic names, harmonies)

    This allows progressive/streaming results instead of waiting for Claude.

    Args:
        request: ExtractColorRequest with image data
        db: Database session

    Returns:
        StreamingResponse with newline-delimited JSON events
    """

    async def color_extraction_stream():
        try:
            # Verify project exists
            result = await db.execute(select(Project).where(Project.id == request.project_id))
            project = result.scalar_one_or_none()
            if not project:
                yield f'data: {json.dumps({"error": f"Project {request.project_id} not found"})}\n\n'
                return

            # Phase 1: Fast local color extraction (instant)
            logger.info(f"[Phase 1] Starting fast color extraction for project {request.project_id}")
            extractor = AIColorExtractor()

            if request.image_base64:
                extraction_result = extractor.extract_colors_from_base64(
                    request.image_base64, media_type="image/png", max_colors=request.max_colors
                )
            else:
                extraction_result = extractor.extract_colors_from_image_url(
                    request.image_url, max_colors=request.max_colors
                )

            # Send Phase 1 results immediately
            yield f'data: {json.dumps({
                "phase": 1,
                "status": "colors_extracted",
                "color_count": len(extraction_result.colors),
                "message": f"Extracted {len(extraction_result.colors)} colors using fast algorithms"
            })}\n\n'

            # Create extraction job record
            source_identifier = request.image_url or "base64_upload"
            extraction_job = ExtractionJob(
                project_id=request.project_id,
                source_url=source_identifier,
                extraction_type="color",
                status="completed",
                result_data=json.dumps({
                    "color_count": len(extraction_result.colors),
                    "palette": extraction_result.color_palette
                })
            )
            db.add(extraction_job)
            await db.flush()

            # Store color tokens
            for i, color in enumerate(extraction_result.colors):
                color_token = ColorToken(
                    project_id=request.project_id,
                    extraction_job_id=extraction_job.id,
                    hex=color.hex,
                    rgb=color.rgb,
                    hsl=color.hsl,
                    hsv=color.hsv,
                    name=color.name,
                    semantic_name=color.semantic_name,
                    harmony=color.harmony,
                    temperature=color.temperature,
                    saturation_level=color.saturation_level,
                    lightness_level=color.lightness_level,
                    confidence=color.confidence,
                    usage=json.dumps(color.usage) if color.usage else None,
                    count=color.count,
                    wcag_contrast_on_white=color.wcag_contrast_on_white,
                    wcag_contrast_on_black=color.wcag_contrast_on_black,
                    wcag_aa_compliant_text=color.wcag_aa_compliant_text,
                    wcag_aaa_compliant_text=color.wcag_aaa_compliant_text,
                    wcag_aa_compliant_normal=color.wcag_aa_compliant_normal,
                    wcag_aaa_compliant_normal=color.wcag_aaa_compliant_normal,
                    colorblind_safe=color.colorblind_safe,
                    tint_color=color.tint_color,
                    shade_color=color.shade_color,
                    tone_color=color.tone_color,
                    closest_web_safe=color.closest_web_safe,
                    closest_css_named=color.closest_css_named,
                    delta_e_to_dominant=color.delta_e_to_dominant,
                    is_neutral=color.is_neutral,
                )
                db.add(color_token)

                # Stream each color as it's processed
                if (i + 1) % 5 == 0 or i == len(extraction_result.colors) - 1:
                    yield f'data: {json.dumps({
                        "phase": 1,
                        "status": "colors_streaming",
                        "progress": (i + 1) / len(extraction_result.colors),
                        "message": f"Processed {i + 1}/{len(extraction_result.colors)} colors"
                    })}\n\n'

            await db.commit()

            # Fetch stored colors from database (which have all properties populated)
            result = await db.execute(
                select(ColorToken)
                .where(ColorToken.project_id == request.project_id)
                .order_by(ColorToken.created_at.desc())
                .limit(len(extraction_result.colors))
            )
            stored_colors = result.scalars().all()
            stored_colors.reverse()  # Restore original order

            # Phase 2: Return complete extraction with all color data from database
            yield f'data: {json.dumps({
                "phase": 2,
                "status": "extraction_complete",
                "summary": extraction_result.color_palette,
                "dominant_colors": extraction_result.dominant_colors,
                "extraction_confidence": extraction_result.extraction_confidence,
                "colors": [
                    {
                        "id": color.id,
                        "hex": color.hex,
                        "rgb": color.rgb,
                        "hsl": color.hsl,
                        "hsv": color.hsv,
                        "name": color.name,
                        "semantic_name": color.semantic_name,
                        "category": color.category,
                        "confidence": color.confidence,
                        "harmony": color.harmony,
                        "temperature": color.temperature,
                        "saturation_level": color.saturation_level,
                        "lightness_level": color.lightness_level,
                        "usage": json.loads(color.usage) if color.usage else None,
                        "count": color.count,
                        "prominence_percentage": color.prominence_percentage,
                        "wcag_contrast_on_white": color.wcag_contrast_on_white,
                        "wcag_contrast_on_black": color.wcag_contrast_on_black,
                        "wcag_aa_compliant_text": color.wcag_aa_compliant_text,
                        "wcag_aaa_compliant_text": color.wcag_aaa_compliant_text,
                        "wcag_aa_compliant_normal": color.wcag_aa_compliant_normal,
                        "wcag_aaa_compliant_normal": color.wcag_aaa_compliant_normal,
                        "colorblind_safe": color.colorblind_safe,
                        "tint_color": color.tint_color,
                        "shade_color": color.shade_color,
                        "tone_color": color.tone_color,
                        "closest_web_safe": color.closest_web_safe,
                        "closest_css_named": color.closest_css_named,
                        "delta_e_to_dominant": color.delta_e_to_dominant,
                        "is_neutral": color.is_neutral,
                    }
                    for color in stored_colors
                ]
            }, default=str)}\n\n'

            logger.info(f"Extracted {len(extraction_result.colors)} colors for project {request.project_id}")

        except Exception as e:
            logger.error(f"Color extraction streaming failed: {e}")
            yield f'data: {json.dumps({"error": f"Color extraction failed: {str(e)}"})}\n\n'

    return StreamingResponse(
        color_extraction_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )


@app.get("/api/v1/projects/{project_id}/colors", response_model=list[ColorTokenDetailResponse])
async def get_project_colors(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all color tokens for a project

    Args:
        project_id: Project ID
        db: Database session

    Returns:
        List of color tokens for the project

    Raises:
        HTTPException: If project not found
    """
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    # Get all colors for the project
    result = await db.execute(
        select(ColorToken).where(ColorToken.project_id == project_id).order_by(ColorToken.created_at.desc())
    )
    colors = result.scalars().all()

    return [
        ColorTokenDetailResponse(
            id=color.id,
            project_id=color.project_id,
            extraction_job_id=color.extraction_job_id,
            hex=color.hex,
            rgb=color.rgb,
            name=color.name,
            semantic_name=color.semantic_name,
            confidence=color.confidence,
            harmony=color.harmony,
            usage=color.usage,
            created_at=color.created_at.isoformat()
        )
        for color in colors
    ]


@app.post("/api/v1/colors", response_model=ColorTokenDetailResponse, status_code=201)
async def create_color_token(
    request: ColorTokenCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new color token

    Args:
        request: ColorTokenCreateRequest with color details
        db: Database session

    Returns:
        Created color token

    Raises:
        HTTPException: If project not found
    """
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == request.project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {request.project_id} not found"
        )

    # Create color token
    color_token = ColorToken(
        project_id=request.project_id,
        extraction_job_id=request.extraction_job_id,
        hex=request.hex,
        rgb=request.rgb,
        name=request.name,
        semantic_name=request.semantic_name,
        confidence=request.confidence,
        harmony=request.harmony,
        usage=request.usage
    )
    db.add(color_token)
    await db.commit()
    await db.refresh(color_token)

    return ColorTokenDetailResponse(
        id=color_token.id,
        project_id=color_token.project_id,
        extraction_job_id=color_token.extraction_job_id,
        hex=color_token.hex,
        rgb=color_token.rgb,
        name=color_token.name,
        semantic_name=color_token.semantic_name,
        confidence=color_token.confidence,
        harmony=color_token.harmony,
        usage=color_token.usage,
        created_at=color_token.created_at.isoformat()
    )


@app.get("/api/v1/colors/{color_id}", response_model=ColorTokenDetailResponse)
async def get_color_token(
    color_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific color token

    Args:
        color_id: Color token ID
        db: Database session

    Returns:
        Color token details

    Raises:
        HTTPException: If color not found
    """
    result = await db.execute(select(ColorToken).where(ColorToken.id == color_id))
    color = result.scalar_one_or_none()
    if not color:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Color token {color_id} not found"
        )

    return ColorTokenDetailResponse(
        id=color.id,
        project_id=color.project_id,
        extraction_job_id=color.extraction_job_id,
        hex=color.hex,
        rgb=color.rgb,
        name=color.name,
        semantic_name=color.semantic_name,
        confidence=color.confidence,
        harmony=color.harmony,
        usage=color.usage,
        created_at=color.created_at.isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
