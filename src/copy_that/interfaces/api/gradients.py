"""Gradient extraction API (CV linear-band / stop clustering)."""

from __future__ import annotations

import base64
import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl

from copy_that.application.execution.async_executor import AsyncExecutor
from copy_that.application.ports.gradient_tokens import GradientTokenRepository
from copy_that.application.ports.projects import ProjectRepository
from copy_that.domain.gradient_tokens import GradientTokenCreate
from copy_that.extractors.gradient_extract import gradient_tokens_from_image
from copy_that.infrastructure.security.rate_limiter import rate_limit
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.utils import enforce_payload_size

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/gradients", tags=["gradients"])


class GradientTokenResponse(BaseModel):
    """Response model for a single gradient token."""

    id: str = Field(..., description="Token id")
    name: str = Field(..., description="Gradient token name")
    gradient_type: str = Field(default="linear", description="Gradient type")
    angle: float = Field(..., description="Angle in degrees")
    stops: list[dict[str, Any]] = Field(..., description="Color stops")
    source: str = Field(..., description="Extraction source (cv/ai/extracted)")
    confidence: float = Field(..., ge=0, le=1, description="Extraction confidence")
    axis: str | None = Field(None, description="Detection axis")
    confirmed_by: str | None = Field(None, description="Optional confirm modality")


class GradientExtractionRequest(BaseModel):
    """Request model for gradient extraction."""

    image_url: HttpUrl | None = Field(None, description="URL of the image to analyze")
    image_base64: str | None = Field(None, description="Base64-encoded image data")
    image_media_type: str | None = Field("image/png", description="MIME type of base64 image")
    project_id: int | None = Field(None, description="Optional project to persist into")
    max_tokens: int = Field(default=2, ge=1, le=10, description="Max gradients to return")
    palette_hexes: list[str] | None = Field(
        default=None, description="Optional palette for AI/palette confirm"
    )


class GradientExtractionResponse(BaseModel):
    """Response model for gradient extraction."""

    tokens: list[GradientTokenResponse]
    gradient_count: int
    extraction_confidence: float
    extractor_used: str = "gradient_cv"
    extraction_metadata: dict[str, Any] | None = None


def _token_to_response(payload: dict[str, Any]) -> GradientTokenResponse:
    value = payload.get("value") or {}
    attrs = payload.get("attributes") or {}
    token_id = str(payload.get("id") or "gradient")
    stops = value.get("stops") if isinstance(value, dict) else []
    return GradientTokenResponse(
        id=token_id,
        name=token_id.split(".")[-1] if "." in token_id else token_id,
        gradient_type=str(value.get("type") or "linear") if isinstance(value, dict) else "linear",
        angle=float(value.get("angle") or 90) if isinstance(value, dict) else 90.0,
        stops=list(stops) if isinstance(stops, list) else [],
        source=str(attrs.get("source") or "cv"),
        confidence=float(attrs.get("confidence") or 0.0),
        axis=attrs.get("axis"),
        confirmed_by=attrs.get("confirmed_by"),
    )


def _creates_from_payloads(payloads: list[dict[str, Any]]) -> list[GradientTokenCreate]:
    creates: list[GradientTokenCreate] = []
    for payload in payloads:
        resp = _token_to_response(payload)
        creates.append(
            GradientTokenCreate(
                name=resp.name,
                gradient_type=resp.gradient_type,
                angle=resp.angle,
                stops_json=json.dumps(resp.stops),
                source=resp.source,
                confidence=resp.confidence,
                axis=resp.axis,
                confirmed_by=resp.confirmed_by,
                extraction_metadata=json.dumps(
                    {"id": resp.id, "attributes": payload.get("attributes") or {}}
                ),
            )
        )
    return creates


@router.post("/extract", response_model=GradientExtractionResponse)
async def extract_gradients(
    request: GradientExtractionRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    gradient_repo: GradientTokenRepository = Depends(deps.get_gradient_repo),
    async_executor: AsyncExecutor = Depends(deps.get_async_executor),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
) -> GradientExtractionResponse:
    """Extract gradient tokens from an image via CV band detection."""
    if request.project_id:
        project = await project_repo.get(project_id=request.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {request.project_id} not found",
            )

    if not request.image_url and not request.image_base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either image_url or image_base64 must be provided",
        )

    try:
        cv_b64 = request.image_base64
        if request.image_url and not request.image_base64:
            try:
                import requests

                resp = requests.get(str(request.image_url), timeout=10)
                resp.raise_for_status()
                cv_b64 = base64.b64encode(resp.content).decode("utf-8")
            except Exception as e:
                logger.error("Failed to download image from URL: %s", e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to fetch image: {str(e)}",
                ) from e

        enforce_payload_size(request.image_base64)
        image_bytes = base64.b64decode(cv_b64 or "")

        tokens = await async_executor.run(
            lambda: gradient_tokens_from_image(
                image_bytes,
                palette_hexes=request.palette_hexes,
                max_gradients=request.max_tokens,
            )
        )
        payloads = [
            {
                "id": t.id,
                "type": "gradient",
                "value": t.value,
                "attributes": t.attributes,
            }
            for t in tokens
        ]

        responses = [_token_to_response(p) for p in payloads]
        avg_conf = sum(r.confidence for r in responses) / len(responses) if responses else 0.0

        if request.project_id and responses:
            await gradient_repo.record_extraction(
                project_id=request.project_id,
                source_url=str(request.image_url) if request.image_url else "upload://base64",
                gradients=_creates_from_payloads(payloads),
            )

        return GradientExtractionResponse(
            tokens=responses,
            gradient_count=len(responses),
            extraction_confidence=avg_conf,
            extractor_used="gradient_cv",
            extraction_metadata={
                "max_tokens": request.max_tokens,
                "palette_confirm": bool(request.palette_hexes),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Gradient extraction failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gradient extraction failed: {e}",
        ) from e


@router.get("/projects/{project_id}")
async def list_project_gradients(
    project_id: int,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    gradient_repo: GradientTokenRepository = Depends(deps.get_gradient_repo),
) -> dict[str, Any]:
    """List persisted gradient tokens for a project."""
    project = await project_repo.get(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    rows = await gradient_repo.list_by_project(project_id=project_id)
    tokens = []
    for row in rows:
        try:
            stops = json.loads(row.stops_json)
        except (TypeError, json.JSONDecodeError):
            stops = []
        tokens.append(
            {
                "id": row.id,
                "name": row.name,
                "gradient_type": row.gradient_type,
                "angle": row.angle,
                "stops": stops,
                "source": row.source,
                "confidence": row.confidence,
                "axis": row.axis,
                "confirmed_by": row.confirmed_by,
            }
        )
    return {"project_id": project_id, "tokens": tokens, "gradient_count": len(tokens)}
