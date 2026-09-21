"""Geometry extract API: thin extract→response path (mocked model stack)."""

from __future__ import annotations

import base64
import io
from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image


def _tiny_png_b64() -> str:
    # Validators require ≥16×16
    img = Image.new("RGB", (16, 16), color=(180, 90, 40))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _fake_geometry_payload():
    h, w = 16, 16
    depth01 = np.linspace(0.1, 0.9, h * w, dtype="float32").reshape(h, w)
    # Unit-ish normals pointing mostly +Z
    normals = np.zeros((h, w, 3), dtype="float32")
    normals[..., 2] = 1.0
    confidence = np.ones((h, w), dtype="float32") * 0.8
    gradients = np.zeros((h, w, 2), dtype="float32")
    return {
        "depth01": depth01,
        "normals_xyz": normals,
        "normals_confidence": confidence,
        "normals_gradients": gradients,
        "meta": {
            "profile_requested": "cpu_fast",
            "profile_resolved": "cpu_fast",
            "device": "cpu",
            "depth_model": "depth-anything/Depth-Anything-V2-Small-hf",
            "normals_source": "depth_gradient",
            "normals_smoothing_sigma": 1.5,
            "warnings": [],
        },
    }


@pytest.mark.asyncio
async def test_geometry_extract_response_shape(async_client):
    with patch(
        "copy_that.interfaces.api.geometry.extract_depth_and_normals",
        return_value=_fake_geometry_payload(),
    ):
        response = await async_client.post(
            "/api/v1/geometry/extract",
            json={
                "image_base64": _tiny_png_b64(),
                "image_media_type": "image/png",
                "profile": "cpu_fast",
            },
        )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["meta"]["device"] == "cpu"
    assert data["meta"]["normals_source"] == "depth_gradient"
    assert set(data["images"]) >= {
        "depth_png",
        "normals_png",
        "normals_confidence_png",
        "normals_gradients_png",
    }
    # PNG payloads are non-empty base64
    for key in ("depth_png", "normals_png"):
        raw = base64.b64decode(data["images"][key])
        assert raw[:8] == b"\x89PNG\r\n\x1a\n"


@pytest.mark.asyncio
async def test_geometry_extract_invalid_image_returns_400(async_client):
    response = await async_client.post(
        "/api/v1/geometry/extract",
        json={
            "image_base64": "not-valid-base64!!!",
            "image_media_type": "image/png",
            "profile": "cpu_fast",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_geometry_extract_missing_deps_returns_503(async_client):
    """Dedicated geometry path fails loud (G4); lighting degrades separately."""
    from copy_that.extractors.geometry.geometry_models import OptionalDependencyError

    with patch(
        "copy_that.interfaces.api.geometry.extract_depth_and_normals",
        side_effect=OptionalDependencyError("Missing dependency: transformers"),
    ):
        response = await async_client.post(
            "/api/v1/geometry/extract",
            json={
                "image_base64": _tiny_png_b64(),
                "image_media_type": "image/png",
                "profile": "cpu_fast",
            },
        )

    assert response.status_code == 503
    assert "transformers" in response.json()["detail"]
