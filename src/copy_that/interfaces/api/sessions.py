"""
Session/Library/Export Router
"""

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from copy_that.application.ports.color_token_library import ColorTokenLibraryRepository
from copy_that.application.ports.color_tokens import ColorTokenWriter
from copy_that.application.ports.projects import ProjectRepository
from copy_that.application.ports.sessions import SessionRepository
from copy_that.application.ports.token_exports import TokenExportRepository
from copy_that.application.ports.token_libraries import TokenLibraryRepository
from copy_that.constants import DEFAULT_DELTA_E_THRESHOLD
from copy_that.core_tokens.adapters.w3c import tokens_to_w3c_flat
from copy_that.core_tokens.repository import TokenRepository
from copy_that.generators import (
    CSSTokenGenerator,
    HTMLDemoGenerator,
    ReactTokenGenerator,
    W3CTokenGenerator,
)
from copy_that.generators.library_models import AggregatedColorToken
from copy_that.generators.library_models import TokenLibrary as AggregatedLibrary
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.schemas import (
    BatchExtractRequest,
    CurateRequest,
    ExportResponse,
    LibraryResponse,
    SessionCreateRequest,
    SessionResponse,
)
from copy_that.interfaces.api.token_mappers import colors_to_repo

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
async def create_session(
    request: SessionCreateRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    session_repo: SessionRepository = Depends(deps.get_session_repo),
):
    """Create an extraction session for batch image processing"""
    project = await project_repo.get(project_id=request.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {request.project_id} not found"
        )

    session = await session_repo.create(
        project_id=request.project_id, name=request.name, description=request.description
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


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    session_repo: SessionRepository = Depends(deps.get_session_repo),
):
    """Get extraction session details"""
    session = await session_repo.get(session_id=session_id)
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
async def get_library(
    session_id: int,
    session_repo: SessionRepository = Depends(deps.get_session_repo),
    token_library_repo: TokenLibraryRepository = Depends(deps.get_token_library_repo),
    color_library_repo: ColorTokenLibraryRepository = Depends(deps.get_color_token_library_repo),
):
    """Get aggregated token library for a session"""
    # Get session
    session = await session_repo.get(session_id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found"
        )

    library = await token_library_repo.get(session_id=session_id, token_type="color")
    if not library:
        library = await token_library_repo.create(
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

    _color_tokens = await color_library_repo.list_by_library_id(library_id=library.id)
    repo = colors_to_repo(
        _color_tokens,
        namespace=f"token/color/project/{session.project_id}/session/{session_id}",
    )

    stats = safe_json_loads(library.statistics)

    return LibraryResponse(
        id=library.id,
        session_id=library.session_id,
        token_type=library.token_type,
        tokens=[],
        statistics={
            "color_count": stats.get("color_count", 0),
            "image_count": stats.get("image_count", 0),
            "avg_confidence": stats.get("avg_confidence", 0.0),
            "min_confidence": stats.get("min_confidence", 0.0),
            "max_confidence": stats.get("max_confidence", 0.0),
            "dominant_colors": stats.get("dominant_colors", []),
            "multi_image_colors": stats.get("multi_image_colors", 0),
        },
        design_tokens=tokens_to_w3c_flat(repo),
        is_curated=library.is_curated,
        created_at=library.created_at.isoformat(),
        updated_at=library.updated_at.isoformat(),
    )


@router.post("/{session_id}/library/curate")
async def curate_library(
    session_id: int,
    request: CurateRequest,
    token_library_repo: TokenLibraryRepository = Depends(deps.get_token_library_repo),
    color_library_repo: ColorTokenLibraryRepository = Depends(deps.get_color_token_library_repo),
):
    """Curate token library - assign roles to tokens"""
    # Get library
    library = await token_library_repo.get(session_id=session_id, token_type="color")
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

    role_map = {a.token_id: a.role for a in request.role_assignments}
    await color_library_repo.assign_roles(library_id=library.id, role_by_token_id=role_map)
    await token_library_repo.mark_curated(library_id=library.id, notes=request.notes)

    return {"status": "success", "message": f"Curated {len(request.role_assignments)} tokens"}


@router.post("/{session_id}/extract")
async def batch_extract_colors(
    session_id: int,
    request: BatchExtractRequest,
    session_repo: SessionRepository = Depends(deps.get_session_repo),
    token_library_repo: TokenLibraryRepository = Depends(deps.get_token_library_repo),
    color_writer: ColorTokenWriter = Depends(deps.get_color_token_writer),
):
    """Extract colors from multiple images and aggregate into library"""
    # Get session and verify it exists
    session = await session_repo.get(session_id=session_id)
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
        library = await token_library_repo.get_or_create(
            session_id=session_id,
            token_type="color",
            statistics=json.dumps(statistics, default=str),
        )

        # Persist aggregated tokens to database
        token_count = await extractor.persist_aggregated_library(
            color_writer,
            library_id=library.id,
            project_id=session.project_id,
            aggregated_tokens=tokens,
            statistics=statistics,
        )

        # Update session image count
        await session_repo.set_image_count(
            session_id=session_id, image_count=len(request.image_urls)
        )

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
async def export_library(
    session_id: int,
    format: str = "w3c",
    token_library_repo: TokenLibraryRepository = Depends(deps.get_token_library_repo),
    color_library_repo: ColorTokenLibraryRepository = Depends(deps.get_color_token_library_repo),
    token_export_repo: TokenExportRepository = Depends(deps.get_token_export_repo),
):
    """Export library in specified format (w3c, css, react, html)"""
    valid_formats = {"w3c", "css", "react", "html"}
    if format not in valid_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid format '{format}'. Valid formats: {', '.join(valid_formats)}",
        )

    # Get library
    library = await token_library_repo.get(session_id=session_id, token_type="color")
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library for session {session_id} not found",
        )

    db_tokens = await color_library_repo.list_by_library_id(library_id=library.id)

    repo = colors_to_repo(db_tokens, namespace=f"token/color/library/{library.id}")
    stats = safe_json_loads(library.statistics)

    # Generate output
    generators = {
        "w3c": W3CTokenGenerator,
        "css": CSSTokenGenerator,
        "react": ReactTokenGenerator,
        "html": HTMLDemoGenerator,
    }
    generator_class = generators[format]
    if format == "w3c":
        content = json.dumps(tokens_to_w3c_flat(repo), indent=2)
    else:
        agg_library = _color_library_from_repo(repo, stats)
        generator = generator_class(agg_library)
        content = generator.generate()

    await token_export_repo.create(library_id=library.id, format=format, file_size=len(content))

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


def _color_library_from_repo(
    repo: TokenRepository, statistics: dict[str, Any] | None = None
) -> AggregatedLibrary:
    """Build AggregatedLibrary-style view from a TokenRepository."""
    agg_tokens: list[AggregatedColorToken] = []
    for token in repo.find_by_type("color"):
        attrs = token.attributes
        hex_val = attrs.get("hex")
        if isinstance(hex_val, dict):
            hex_str = str(hex_val)
        elif hex_val is None and isinstance(token.value, dict):
            hex_str = str(token.value)
        else:
            hex_str = str(hex_val or token.value)
        agg_tokens.append(
            AggregatedColorToken(
                hex=hex_str,
                rgb=str(attrs.get("rgb", "")),
                name=str(attrs.get("name", "")),
                confidence=float(attrs.get("confidence") or 0),
                harmony=attrs.get("harmony"),
                temperature=attrs.get("temperature"),
                role=attrs.get("role"),
                provenance=attrs.get("provenance") or {},
            )
        )

    return AggregatedLibrary(tokens=agg_tokens, statistics=statistics or {}, token_type="color")
