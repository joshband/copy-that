"""Lighting and geometric shadow analysis API endpoints."""

from __future__ import annotations

import base64
import io
import logging
from typing import Any

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from numpy.typing import NDArray
from PIL import Image
from pydantic import BaseModel, Field, HttpUrl

from copy_that.application.execution.async_executor import AsyncExecutor
from copy_that.extractors.geometry.profile import GeometryProfile
from copy_that.infrastructure.security.rate_limiter import rate_limit
from copy_that.interfaces.api import dependencies as deps
from copy_that.shadowlab import analyze_image_for_shadows
from copy_that.shadowlab.integration import ShadowTokenIntegration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/lighting", tags=["lighting"])

NumericArray = NDArray[np.number[Any]]


def _png_base64(arr: NumericArray) -> str:
    """Encode a float map (0..1) or RGB normals map as PNG base64."""
    arr = np.clip(arr, 0.0, 1.0)
    if arr.ndim == 2:
        img = Image.fromarray((arr * 255).astype("uint8"), mode="L")
    elif arr.ndim == 3 and arr.shape[2] == 3:
        img = Image.fromarray((arr * 255).astype("uint8"), mode="RGB")
    else:
        raise ValueError(f"Unexpected array shape for PNG: {arr.shape}")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _geometry_preview_images(
    depth: object | None,
    normals: object | None,
) -> dict[str, str] | None:
    """Build optional depth/normals PNG previews for flag-gated UI."""
    if depth is None or normals is None:
        return None
    try:
        depth_arr = np.asarray(depth, dtype=np.float32)
        normals_arr = np.asarray(normals, dtype=np.float32)
        # normals_xyz typically in [-1, 1] — map to 0..1 for display
        if normals_arr.min() < -0.01 or normals_arr.max() > 1.01:
            normals_vis = (normals_arr * 0.5) + 0.5
        else:
            normals_vis = normals_arr
        return {
            "depth_png": _png_base64(depth_arr),
            "normals_png": _png_base64(normals_vis),
        }
    except Exception as exc:
        logger.debug("Skipping geometry preview images: %s", exc)
        return None


class LightingAnalysisRequest(BaseModel):
    """Request for lighting and shadow analysis."""

    image_url: HttpUrl | None = Field(None, description="URL of image to analyze")
    image_base64: str | None = Field(None, description="Base64 image data (without data: prefix)")
    image_media_type: str | None = Field(
        "image/png", description="Media type (image/png, image/jpeg)"
    )
    image_id: str | None = Field(None, description="Optional image identifier")
    use_geometry: bool = Field(
        True,
        description="Use P4 geometry extract (depth/normals) — not the legacy shadowlab stand-in",
    )
    device: str = Field(
        "cpu",
        description="Device hint mapped to geometry profile: cpu, cuda, mps, cpu_fast, …",
    )
    geometry_profile: GeometryProfile | None = Field(
        None,
        description="Optional explicit geometry profile (overrides device mapping)",
    )


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
    geometry_meta: dict[str, object] | None = Field(
        None,
        description="P4 geometry extract meta when use_geometry ran (depth_model, normals_source, …)",
    )
    geometry_used: bool = Field(
        False,
        description="True when real geometry depth/normals were applied (not stand-in)",
    )
    geometry_images: dict[str, str] | None = Field(
        None,
        description="Optional PNG base64 previews: depth_png, normals_png (when geometry_used)",
    )


@router.post("/analyze", response_model=LightingAnalysisResponse)
async def analyze_lighting(
    request: LightingAnalysisRequest,
    async_executor: AsyncExecutor = Depends(deps.get_async_executor),
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

        # Run shadow analysis in executor (blocking). Geometry uses real P4 extract.
        analysis = await async_executor.run(
            lambda: analyze_image_for_shadows(
                image_bgr,
                use_geometry=request.use_geometry,
                device=request.device,
                geometry_profile=request.geometry_profile,
            )
        )

        # Extract results
        tokens = analysis.get("tokens", {})
        features = analysis.get("features", {})
        geometry_meta = analysis.get("geometry_meta")
        geometry_used = (
            request.use_geometry
            and analysis.get("depth") is not None
            and analysis.get("normals") is not None
            and isinstance(geometry_meta, dict)
            and "error" not in geometry_meta
        )
        geometry_images = (
            _geometry_preview_images(analysis.get("depth"), analysis.get("normals"))
            if geometry_used
            else None
        )

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
            geometry_meta=geometry_meta if isinstance(geometry_meta, dict) else None,
            geometry_used=bool(geometry_used),
            geometry_images=geometry_images,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Lighting analysis failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        ) from e
