"""Lighting API wires through real geometry extract (mocked)."""

from __future__ import annotations

import base64
import io
from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image


def _tiny_png_b64() -> str:
    img = Image.new("RGB", (32, 32), color=(120, 140, 160))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _fake_geometry_payload(h: int = 32, w: int = 32):
    depth01 = np.linspace(0.2, 0.8, h * w, dtype="float32").reshape(h, w)
    normals = np.zeros((h, w, 3), dtype="float32")
    normals[..., 2] = 1.0
    return {
        "depth01": depth01,
        "normals_xyz": normals,
        "normals_confidence": None,
        "normals_gradients": None,
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
async def test_lighting_analyze_uses_geometry_extract(async_client):
    with patch(
        "copy_that.shadowlab.tokens.extract_depth_and_normals",
        return_value=_fake_geometry_payload(),
    ) as mock_extract:
        response = await async_client.post(
            "/api/v1/lighting/analyze",
            json={
                "image_base64": _tiny_png_b64(),
                "image_media_type": "image/png",
                "use_geometry": True,
                "device": "cpu",
                "geometry_profile": "cpu_fast",
            },
        )

    assert response.status_code == 200, response.text
    data = response.json()
    mock_extract.assert_called_once()
    assert data["geometry_used"] is True
    assert data["geometry_meta"]["depth_model"].startswith("depth-anything/")
    assert data["geometry_meta"]["normals_source"] == "depth_gradient"
    assert data["analysis_source"] == "shadowlab"
    assert "style_key_direction" in data
    assert "css_box_shadow" in data
    assert data["geometry_images"] is not None
    assert "depth_png" in data["geometry_images"]
    assert "normals_png" in data["geometry_images"]
    assert len(data["geometry_images"]["depth_png"]) > 16
    assert len(data["geometry_images"]["normals_png"]) > 16


@pytest.mark.asyncio
async def test_lighting_analyze_without_geometry_skips_extract(async_client):
    with patch(
        "copy_that.shadowlab.tokens.extract_depth_and_normals",
    ) as mock_extract:
        response = await async_client.post(
            "/api/v1/lighting/analyze",
            json={
                "image_base64": _tiny_png_b64(),
                "use_geometry": False,
            },
        )

    assert response.status_code == 200, response.text
    data = response.json()
    mock_extract.assert_not_called()
    assert data["geometry_used"] is False
    assert data["geometry_meta"] is None
    assert data.get("geometry_images") is None
