"""
Session/Library/Export Router
"""

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.constants import DEFAULT_DELTA_E_THRESHOLD
from copy_that.domain.models import (
    ColorToken,
    ExtractionSession,
    Project,
    TokenExport,
    TokenLibrary,
)
from copy_that.generators import (
    CSSTokenGenerator,
    HTMLDemoGenerator,
    ReactTokenGenerator,
    W3CTokenGenerator,
)
from copy_that.infrastructure.database import get_db
from copy_that.interfaces.api.schemas import (
    BatchExtractRequest,
    CurateRequest,
    ExportResponse,
    LibraryResponse,
    SessionCreateRequest,
    SessionResponse,
)
from copy_that.tokens.color.aggregator import (
    AggregatedColorToken,
)
from copy_that.tokens.color.aggregator import (
    TokenLibrary as AggregatedLibrary,
)

logger = logging.getLogger(__name__)


def safe_json_loads(data: str | None, default: dict[str, Any] | list[Any] | None = None) -> Any:
    """Safely parse JSON data, returning default on error

    Returns Any to allow flexible usage - caller should cast to expected type.
    """
    if not data:
        return default if default is not None else {}
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON data: {e}")
        return default if default is not None else {}


router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(request: SessionCreateRequest, db: AsyncSession = Depends(get_db)):
    """Create an extraction session for batch image processing"""
    result = await db.execute(select(Project).where(Project.id == request.project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {request.project_id} not found"
        )

    session = ExtractionSession(
        project_id=request.project_id,
        name=request.name,
        description=request.description,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return SessionResponse(
        id=session.id,
        project_id=session.project_id,
        name=session.name,
        description=session.description,
        image_count=session.image_count,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int, db: AsyncSession = Depends(get_db)):
    """Get extraction session details"""
    result = await db.execute(select(ExtractionSession).where(ExtractionSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found"
        )

    return SessionResponse(
        id=session.id,
        project_id=session.project_id,
        name=session.name,
        description=session.description,
        image_count=session.image_count,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
    )


@router.get("/{session_id}/library", response_model=LibraryResponse)
async def get_library(session_id: int, db: AsyncSession = Depends(get_db)):
    """Get aggregated token library for a session"""
    # Get session
    session_result = await db.execute(
        select(ExtractionSession).where(ExtractionSession.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found"
        )

    # Get or create library
    lib_result = await db.execute(
        select(TokenLibrary)
        .where(TokenLibrary.session_id == session_id)
        .where(TokenLibrary.token_type == "color")
    )
    library = lib_result.scalar_one_or_none()

    if not library:
        # Create empty library
        library = TokenLibrary(
            session_id=session_id,
            token_type="color",
            statistics=json.dumps(
                {
                    "color_count": 0,
                    "image_count": 0,
                    "avg_confidence": 0.0,
                    "min_confidence": 0.0,
                    "max_confidence": 0.0,
                    "dominant_colors": [],
                    "multi_image_colors": 0,
                }
            ),
        )
        db.add(library)
        await db.commit()
        await db.refresh(library)

    # Get all color tokens for this library
    tokens_result = await db.execute(select(ColorToken).where(ColorToken.library_id == library.id))
    _color_tokens = tokens_result.scalars().all()  # TODO: populate tokens in response

    # Build response
    stats = safe_json_loads(library.statistics)

    return LibraryResponse(
        id=library.id,
        session_id=library.session_id,
        token_type=library.token_type,
        tokens=[],  # Would populate from color_tokens
        statistics={
            "color_count": stats.get("color_count", 0),
            "image_count": stats.get("image_count", 0),
            "avg_confidence": stats.get("avg_confidence", 0.0),
            "min_confidence": stats.get("min_confidence", 0.0),
            "max_confidence": stats.get("max_confidence", 0.0),
            "dominant_colors": stats.get("dominant_colors", []),
            "multi_image_colors": stats.get("multi_image_colors", 0),
        },
        is_curated=library.is_curated,
        created_at=library.created_at.isoformat(),
        updated_at=library.updated_at.isoformat(),
    )


@router.post("/{session_id}/library/curate")
async def curate_library(
    session_id: int, request: CurateRequest, db: AsyncSession = Depends(get_db)
):
    """Curate token library - assign roles to tokens"""
    # Get library
    lib_result = await db.execute(
        select(TokenLibrary)
        .where(TokenLibrary.session_id == session_id)
        .where(TokenLibrary.token_type == "color")
    )
    library = lib_result.scalar_one_or_none()
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library for session {session_id} not found",
        )

    # Apply role assignments
    valid_roles = {
        "primary",
        "secondary",
        "accent",
        "neutral",
        "success",
        "warning",
        "danger",
        "info",
    }
    # Validate all roles first
    for assignment in request.role_assignments:
        if assignment.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role '{assignment.role}'. Valid roles: {', '.join(valid_roles)}",
            )

    # OPTIMIZED: Batch fetch all tokens instead of N+1 queries
    token_ids = [a.token_id for a in request.role_assignments]
    role_map = {a.token_id: a.role for a in request.role_assignments}

    tokens_result = await db.execute(
        select(ColorToken)
        .where(ColorToken.id.in_(token_ids))
        .where(ColorToken.library_id == library.id)
    )
    tokens = tokens_result.scalars().all()

    # Batch update roles
    for token in tokens:
        if token.id in role_map:
            token.role = role_map[token.id]

    # Mark as curated
    library.is_curated = True
    library.curation_notes = request.notes

    await db.commit()

    return {"status": "success", "message": f"Curated {len(request.role_assignments)} tokens"}


@router.post("/{session_id}/extract")
async def batch_extract_colors(
    session_id: int, request: BatchExtractRequest, db: AsyncSession = Depends(get_db)
):
    """Extract colors from multiple images and aggregate into library"""
    # Get session and verify it exists
    session_result = await db.execute(
        select(ExtractionSession).where(ExtractionSession.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found"
        )

    try:
        from copy_that.application.batch_extractor import BatchColorExtractor

        # Extract colors from all images
        extractor = BatchColorExtractor()
        tokens, statistics = await extractor.extract_batch(
            image_urls=request.image_urls,
            max_colors=request.max_colors,
            delta_e_threshold=DEFAULT_DELTA_E_THRESHOLD,
        )

        # Get or create library for this session
        lib_result = await db.execute(
            select(TokenLibrary)
            .where(TokenLibrary.session_id == session_id)
            .where(TokenLibrary.token_type == "color")
        )
        library = lib_result.scalar_one_or_none()

        if not library:
            library = TokenLibrary(
                session_id=session_id,
                token_type="color",
                statistics=json.dumps(statistics),
            )
            db.add(library)
            await db.commit()
            await db.refresh(library)
        else:
            # Update statistics
            library.statistics = json.dumps(statistics)
            await db.commit()

        # Persist aggregated tokens to database
        token_count = await extractor.persist_aggregated_library(
            db=db,
            library_id=library.id,
            project_id=session.project_id,
            aggregated_tokens=tokens,
            statistics=statistics,
        )

        # Update session image count
        session.image_count = len(request.image_urls)
        await db.commit()

        return {
            "status": "success",
            "session_id": session_id,
            "library_id": library.id,
            "extracted_tokens": token_count,
            "statistics": statistics,
        }

    except Exception as e:
        logger.error(f"Batch extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch extraction failed: {str(e)}",
        )


@router.get("/{session_id}/library/export")
async def export_library(session_id: int, format: str = "w3c", db: AsyncSession = Depends(get_db)):
    """Export library in specified format (w3c, css, react, html)"""
    valid_formats = {"w3c", "css", "react", "html"}
    if format not in valid_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid format '{format}'. Valid formats: {', '.join(valid_formats)}",
        )

    # Get library
    lib_result = await db.execute(
        select(TokenLibrary)
        .where(TokenLibrary.session_id == session_id)
        .where(TokenLibrary.token_type == "color")
    )
    library = lib_result.scalar_one_or_none()
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library for session {session_id} not found",
        )

    # Get color tokens for this library
    tokens_result = await db.execute(select(ColorToken).where(ColorToken.library_id == library.id))
    db_tokens = tokens_result.scalars().all()

    # Build aggregated library for generators
    agg_tokens = [
        AggregatedColorToken(
            hex=t.hex,
            rgb=t.rgb,
            name=t.name,
            confidence=t.confidence,
            harmony=t.harmony,
            temperature=t.temperature,
            role=t.role,
            provenance=safe_json_loads(t.provenance),
        )
        for t in db_tokens
    ]

    stats = safe_json_loads(library.statistics)
    agg_library = AggregatedLibrary(
        tokens=agg_tokens,
        statistics=stats,
        token_type="color",
    )

    # Generate output
    generators = {
        "w3c": W3CTokenGenerator,
        "css": CSSTokenGenerator,
        "react": ReactTokenGenerator,
        "html": HTMLDemoGenerator,
    }
    generator_class = generators[format]
    generator = generator_class(agg_library)
    content = generator.generate()

    # Record export
    export = TokenExport(
        library_id=library.id,
        format=format,
        file_size=len(content),
    )
    db.add(export)
    await db.commit()

    # Return with appropriate content type
    mime_types = {
        "w3c": "application/json",
        "css": "text/css",
        "react": "text/plain",
        "html": "text/html",
    }

    return ExportResponse(
        format=format,
        content=content,
        mime_type=mime_types[format],
    )
