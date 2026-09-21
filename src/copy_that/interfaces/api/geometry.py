"""Geometry extraction API endpoints.

Parked P4 surface: mounted for API/tests, off default App nav until gates pass.
See docs/planning/P4_GEOMETRY_GATES.md.
"""

from __future__ import annotations

import base64
import io
import logging
from typing import Any

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from numpy.typing import NDArray
from PIL import Image
from pydantic import BaseModel, Field

from copy_that.application.execution.async_executor import AsyncExecutor
from copy_that.extractors.geometry.depth_normals import extract_depth_and_normals
from copy_that.extractors.geometry.geometry_models import OptionalDependencyError
from copy_that.extractors.geometry.profile import GeometryProfile
from copy_that.infrastructure.security.rate_limiter import rate_limit
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.utils import enforce_payload_size
from copy_that.interfaces.api.validators import validate_base64_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/geometry", tags=["geometry"])

NumericArray = NDArray[np.number[Any]]


class GeometryExtractRequest(BaseModel):
    image_base64: str = Field(..., description="Data URL or raw base64 image")
    image_media_type: str | None = Field("image/png", description="Media type for image")
    profile: GeometryProfile = Field(GeometryProfile.AUTO, description="Geometry profile")


class GeometryExtractResponse(BaseModel):
    meta: dict[str, object]
    images: dict[str, str]


def _decode_image(image_base64: str) -> Image.Image:
    raw = image_base64.split(",", 1)[1] if "," in image_base64 else image_base64
    image_bytes = validate_base64_image(raw)
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


def _png_base64(arr: NumericArray) -> str:
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


def _gradients_to_rgb(gradients: NumericArray) -> NumericArray:
    if gradients.ndim != 3 or gradients.shape[2] != 2:
        raise ValueError(f"Unexpected gradients shape for PNG: {gradients.shape}")

    max_abs = float(np.max(np.abs(gradients)))
    if max_abs <= 1e-6:
        max_abs = 1.0

    dx = gradients[:, :, 0] / max_abs
    dy = gradients[:, :, 1] / max_abs
    mag = np.linalg.norm(gradients, axis=2) / max_abs

    dx_img = (dx * 0.5) + 0.5
    dy_img = (dy * 0.5) + 0.5
    mag_img = np.clip(mag, 0.0, 1.0)
    return np.stack([dx_img, dy_img, mag_img], axis=2)


@router.post("/extract", response_model=GeometryExtractResponse)
async def geometry_extract(
    request: GeometryExtractRequest,
    async_executor: AsyncExecutor = Depends(deps.get_async_executor),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
) -> GeometryExtractResponse:
    enforce_payload_size(request.image_base64, field_name="image_base64")

    try:
        pil = _decode_image(request.image_base64)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image payload: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to decode image payload",
        ) from exc

    try:
        geo = await async_executor.run(
            lambda: extract_depth_and_normals(pil, profile=request.profile)
        )
    except OptionalDependencyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Geometry extraction failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Geometry extraction failed",
        ) from exc

    return GeometryExtractResponse(
        meta=geo["meta"],
        images={
            "depth_png": _png_base64(geo["depth01"]),
            "normals_png": _png_base64((geo["normals_xyz"] * 0.5) + 0.5),
            **(
                {}
                if geo.get("normals_confidence") is None
                else {"normals_confidence_png": _png_base64(geo["normals_confidence"])}
            ),
            **(
                {}
                if geo.get("normals_gradients") is None
                else {
                    "normals_gradients_png": _png_base64(
                        _gradients_to_rgb(geo["normals_gradients"])
                    )
                }
            ),
        },
    )
