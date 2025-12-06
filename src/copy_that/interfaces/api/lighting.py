"""Lighting and geometric shadow analysis API endpoints."""

from __future__ import annotations

import asyncio
import base64
import logging

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.infrastructure.database import get_db
from copy_that.infrastructure.security.rate_limiter import rate_limit
from copy_that.shadowlab import analyze_image_for_shadows
from copy_that.shadowlab.integration import ShadowTokenIntegration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/lighting", tags=["lighting"])


class LightingAnalysisRequest(BaseModel):
    """Request for lighting and shadow analysis."""

    image_url: HttpUrl | None = Field(None, description="URL of image to analyze")
    image_base64: str | None = Field(None, description="Base64 image data (without data: prefix)")
    image_media_type: str | None = Field(
        "image/png", description="Media type (image/png, image/jpeg)"
    )
    image_id: str | None = Field(None, description="Optional image identifier")
    use_geometry: bool = Field(
        True, description="Estimate depth/normals for geometry-aware analysis"
    )
    device: str = Field("cpu", description="Device: 'cpu' or 'cuda'")


class LightingAnalysisResponse(BaseModel):
    """Response with lighting and shadow analysis."""

    # High-level tokens
    style_key_direction: str = Field(
        ..., description="Light direction: upper_left, right, overhead, etc."
    )
    style_softness: str = Field(
        ..., description="Edge softness: very_hard, hard, medium, soft, very_soft"
    )
    style_contrast: str = Field(..., description="Shadow contrast: low, medium, high, very_high")
    style_density: str = Field(..., description="Shadow coverage: sparse, moderate, heavy, full")
    intensity_shadow: str = Field(..., description="Shadow darkness: very_light to very_dark")
    intensity_lit: str = Field(..., description="Lit region brightness: very_dark to very_bright")
    lighting_style: str = Field(
        ..., description="Overall style: directional, rim, diffuse, mixed, complex"
    )

    # Numeric features
    shadow_area_fraction: float = Field(..., ge=0, le=1, description="Fraction of image in shadow")
    mean_shadow_intensity: float = Field(..., ge=0, le=1, description="Average shadow brightness")
    mean_lit_intensity: float = Field(..., ge=0, le=1, description="Average lit region brightness")
    shadow_contrast: float = Field(..., ge=0, le=1, description="Contrast between shadow and lit")
    edge_softness_mean: float = Field(..., ge=0, le=1, description="Average edge softness")

    # Light direction
    light_direction: dict[str, float] | None = Field(
        None, description="Light direction (azimuth/elevation in radians)"
    )
    light_direction_confidence: float = Field(
        ..., ge=0, le=1, description="Confidence in light direction"
    )

    # Diagnostics
    extraction_confidence: float = Field(
        ..., ge=0, le=1, description="Overall extraction confidence"
    )
    shadow_count_major: int = Field(..., description="Number of significant shadow regions")

    # CSS suggestions
    css_box_shadow: dict[str, str] = Field(..., description="Suggested CSS box-shadow values")

    # Metadata
    image_id: str | None = Field(None, description="Image identifier from request")
    analysis_source: str = Field("shadowlab", description="Analysis library used")


@router.post("/analyze", response_model=LightingAnalysisResponse)
async def analyze_lighting(
    request: LightingAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
) -> LightingAnalysisResponse:
    """
    Analyze lighting and shadow characteristics of an image.

    Uses shadowlab geometric shadow analysis to extract:
    - Light direction and quality
    - Shadow softness and coverage
    - Intensity characteristics
    - CSS-ready shadow suggestions

    Args:
        request: Image and analysis options
        db: Database session

    Returns:
        LightingAnalysisResponse with detailed lighting analysis
    """
    # Validate at least one image source
    if not request.image_url and not request.image_base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either image_url or image_base64 must be provided",
        )

    try:
        loop = asyncio.get_event_loop()

        # Download/decode image
        image_b64 = request.image_base64

        if request.image_url and not request.image_base64:
            try:
                import requests

                resp = requests.get(str(request.image_url), timeout=10)
                resp.raise_for_status()
                image_b64 = base64.b64encode(resp.content).decode("utf-8")
            except Exception as e:
                logger.error("Failed to download image: %s", e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to fetch image: {str(e)}",
                ) from e

        # Decode image
        try:
            import cv2

            image_data = base64.b64decode(image_b64)
            image_bgr = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

            if image_bgr is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to decode image",
                )
        except Exception as e:
            logger.error("Image decode failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image processing failed: {str(e)}",
            ) from e

        # Run shadow analysis in executor (blocking operation)
        analysis = await loop.run_in_executor(
            None,
            lambda: analyze_image_for_shadows(
                image_bgr,
                use_geometry=request.use_geometry,
                device=request.device,
            ),
        )

        # Extract results
        tokens = analysis.get("tokens", {})
        features = analysis.get("features", {})

        # Get CSS suggestions
        css_shadows = ShadowTokenIntegration.suggest_css_box_shadow(analysis)

        return LightingAnalysisResponse(
            # Tokens
            style_key_direction=tokens.get("style_key_direction", "unknown"),
            style_softness=tokens.get("style_softness", "unknown"),
            style_contrast=tokens.get("style_contrast", "unknown"),
            style_density=tokens.get("style_density", "unknown"),
            intensity_shadow=tokens.get("intensity_shadow", "unknown"),
            intensity_lit=tokens.get("intensity_lit", "unknown"),
            lighting_style=tokens.get("lighting_style", "unknown"),
            # Features
            shadow_area_fraction=float(features.get("shadow_area_fraction", 0)),
            mean_shadow_intensity=float(features.get("mean_shadow_intensity", 0)),
            mean_lit_intensity=float(features.get("mean_lit_intensity", 0)),
            shadow_contrast=float(features.get("shadow_contrast", 0)),
            edge_softness_mean=float(features.get("edge_softness_mean", 0)),
            # Light
            light_direction=None,  # TODO: format properly if available
            light_direction_confidence=float(features.get("light_direction_confidence", 0)),
            # Overall
            extraction_confidence=tokens.get("extraction_confidence", 0),
            shadow_count_major=int(features.get("shadow_count_major", 0)),
            # CSS
            css_box_shadow=css_shadows,
            # Metadata
            image_id=request.image_id,
            analysis_source="shadowlab",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Lighting analysis failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        ) from e
