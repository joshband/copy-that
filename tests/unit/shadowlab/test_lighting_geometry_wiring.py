"""Lighting analyze must consume P4 geometry extract — not shadowlab stand-in."""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest

from copy_that.extractors.geometry.geometry_models import OptionalDependencyError
from copy_that.extractors.geometry.profile import GeometryProfile
from copy_that.shadowlab.tokens import (
    _device_to_geometry_profile,
    analyze_image_for_shadows,
)


def _fake_geometry_payload(h: int = 32, w: int = 32):
    depth01 = np.linspace(0.1, 0.9, h * w, dtype="float32").reshape(h, w)
    normals = np.zeros((h, w, 3), dtype="float32")
    normals[..., 2] = 1.0
    return {
        "depth01": depth01,
        "normals_xyz": normals,
        "normals_confidence": np.ones((h, w), dtype="float32") * 0.75,
        "normals_gradients": np.zeros((h, w, 2), dtype="float32"),
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


@pytest.mark.parametrize(
    ("device", "expected"),
    [
        ("cpu", GeometryProfile.CPU_FAST),
        ("cpu_fast", GeometryProfile.CPU_FAST),
        ("cpu_accurate", GeometryProfile.CPU_ACCURATE),
        ("cuda", GeometryProfile.GPU_FULL),
        ("mps", GeometryProfile.GPU_FULL),
        ("auto", GeometryProfile.AUTO),
    ],
)
def test_device_to_geometry_profile(device, expected):
    assert _device_to_geometry_profile(device) == expected


def test_analyze_uses_real_geometry_extract_not_standin():
    image = np.ones((32, 32, 3), dtype=np.uint8) * 180
    image[8:20, 8:20] = 60
    fake = _fake_geometry_payload()

    with (
        patch(
            "copy_that.shadowlab.tokens.extract_depth_and_normals",
            return_value=fake,
        ) as mock_extract,
        patch(
            "copy_that.shadowlab.depth_normals.estimate_depth_and_normals",
        ) as mock_standin,
    ):
        result = analyze_image_for_shadows(image, use_geometry=True, device="cpu")

    mock_extract.assert_called_once()
    call_kwargs = mock_extract.call_args
    assert call_kwargs.kwargs.get("profile") == GeometryProfile.CPU_FAST
    mock_standin.assert_not_called()

    assert result["depth"] is not None
    assert result["normals"] is not None
    assert result["geometry_meta"]["depth_model"] == fake["meta"]["depth_model"]
    assert result["geometry_meta"]["normals_source"] == "depth_gradient"
    np.testing.assert_array_equal(result["depth"], fake["depth01"])
    np.testing.assert_array_equal(result["normals"], fake["normals_xyz"])


def test_analyze_geometry_optional_deps_leaves_depth_none_no_standin():
    image = np.ones((24, 24, 3), dtype=np.uint8) * 200

    with (
        patch(
            "copy_that.shadowlab.tokens.extract_depth_and_normals",
            side_effect=OptionalDependencyError("transformers missing"),
        ),
        patch(
            "copy_that.shadowlab.depth_normals.estimate_depth_and_normals",
        ) as mock_standin,
    ):
        result = analyze_image_for_shadows(image, use_geometry=True)

    mock_standin.assert_not_called()
    assert result["depth"] is None
    assert result["normals"] is None
    assert result["geometry_meta"]["error"] == "optional_dependency"
    assert "tokens" in result


def test_analyze_respects_explicit_geometry_profile():
    image = np.ones((16, 16, 3), dtype=np.uint8) * 160
    fake = _fake_geometry_payload(16, 16)
    fake["meta"]["profile_resolved"] = "cpu_accurate"

    with patch(
        "copy_that.shadowlab.tokens.extract_depth_and_normals",
        return_value=fake,
    ) as mock_extract:
        analyze_image_for_shadows(
            image,
            use_geometry=True,
            device="cpu",
            geometry_profile=GeometryProfile.CPU_ACCURATE,
        )

    assert mock_extract.call_args.kwargs["profile"] == GeometryProfile.CPU_ACCURATE


def test_analyze_skips_geometry_when_disabled():
    image = np.ones((20, 20, 3), dtype=np.uint8) * 190

    with patch(
        "copy_that.shadowlab.tokens.extract_depth_and_normals",
    ) as mock_extract:
        result = analyze_image_for_shadows(image, use_geometry=False)

    mock_extract.assert_not_called()
    assert result["depth"] is None
    assert result["geometry_meta"] is None
