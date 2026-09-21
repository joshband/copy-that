"""Deterministic normals-from-depth tests (no HF models)."""

from __future__ import annotations

import numpy as np
import torch

from copy_that.extractors.geometry.depth_normals import _resolve_device_and_profile
from copy_that.extractors.geometry.normals_from_depth import (
    compute_normals_from_depth,
    normals_from_depth,
)
from copy_that.extractors.geometry.profile import GeometryProfile


def test_compute_normals_from_depth_unit_length_and_shape():
    # Planar ramp: depth increases along x → normals tilt.
    ys, xs = np.mgrid[0:16, 0:16]
    depth = (xs.astype("float32") / 15.0) * 0.5 + 0.5

    result = compute_normals_from_depth(depth, smoothing=0.0, device="cpu")

    assert result.normals.shape == (16, 16, 3)
    assert result.confidence.shape == (16, 16)
    assert result.gradients.shape == (16, 16, 2)
    norms = torch.linalg.norm(result.normals, dim=-1)
    assert torch.allclose(norms, torch.ones_like(norms), atol=1e-5)
    assert result.metadata["method"] == "depth_gradient"
    assert result.metadata["device"] == "cpu"


def test_normals_from_depth_wrapper_returns_float32():
    depth = np.linspace(0.2, 0.9, 64, dtype="float32").reshape(8, 8)
    normals = normals_from_depth(depth)
    assert normals.dtype == np.float32
    assert normals.shape == (8, 8, 3)


def test_resolve_device_and_profile_cpu_profiles_force_cpu(monkeypatch):
    monkeypatch.setattr(
        "copy_that.extractors.geometry.depth_normals.gpu_enabled",
        lambda: True,
    )
    monkeypatch.setattr(
        "copy_that.extractors.geometry.depth_normals.torch.cuda.is_available",
        lambda: True,
    )

    device, resolved, warnings = _resolve_device_and_profile(GeometryProfile.CPU_FAST)
    assert device == "cpu"
    assert resolved == GeometryProfile.CPU_FAST
    assert "cpu_profile_forced" in warnings

    device, resolved, warnings = _resolve_device_and_profile(GeometryProfile.CPU_ACCURATE)
    assert device == "cpu"
    assert resolved == GeometryProfile.CPU_ACCURATE
    assert "cpu_profile_forced" in warnings


def test_resolve_auto_falls_back_when_gpu_unavailable(monkeypatch):
    monkeypatch.setattr(
        "copy_that.extractors.geometry.depth_normals.gpu_enabled",
        lambda: False,
    )

    device, resolved, warnings = _resolve_device_and_profile(GeometryProfile.AUTO)
    assert device == "cpu"
    assert resolved == GeometryProfile.CPU_FAST
    assert warnings == []


def test_resolve_auto_on_mps_selects_gpu_full_depth_only(monkeypatch):
    """Apple Silicon: auto → gpu_full on MPS; Marigold still CUDA-only at extract time."""
    monkeypatch.setattr(
        "copy_that.extractors.geometry.depth_normals.gpu_enabled",
        lambda: True,
    )
    monkeypatch.setattr(
        "copy_that.extractors.geometry.depth_normals.torch.cuda.is_available",
        lambda: False,
    )
    monkeypatch.setattr(
        "copy_that.extractors.geometry.depth_normals.torch.backends.mps.is_available",
        lambda: True,
    )

    device, resolved, warnings = _resolve_device_and_profile(GeometryProfile.AUTO)
    assert device == "mps"
    assert resolved == GeometryProfile.GPU_FULL
    assert "gpu_non_cuda_depth_only" in warnings


def test_resolve_gpu_full_on_mps_keeps_mps_with_warning(monkeypatch):
    monkeypatch.setattr(
        "copy_that.extractors.geometry.depth_normals.gpu_enabled",
        lambda: True,
    )
    monkeypatch.setattr(
        "copy_that.extractors.geometry.depth_normals.torch.cuda.is_available",
        lambda: False,
    )
    monkeypatch.setattr(
        "copy_that.extractors.geometry.depth_normals.torch.backends.mps.is_available",
        lambda: True,
    )

    device, resolved, warnings = _resolve_device_and_profile(GeometryProfile.GPU_FULL)
    assert device == "mps"
    assert resolved == GeometryProfile.GPU_FULL
    assert "gpu_non_cuda_depth_only" in warnings


def test_resolve_gpu_full_without_accelerator_falls_back_cpu_fast(monkeypatch):
    monkeypatch.setattr(
        "copy_that.extractors.geometry.depth_normals.gpu_enabled",
        lambda: False,
    )

    device, resolved, warnings = _resolve_device_and_profile(GeometryProfile.GPU_FULL)
    assert device == "cpu"
    assert resolved == GeometryProfile.CPU_FAST
    assert "gpu_unavailable_fallback_cpu_fast" in warnings


def test_resolve_auto_on_cuda_selects_gpu_full(monkeypatch):
    monkeypatch.setattr(
        "copy_that.extractors.geometry.depth_normals.gpu_enabled",
        lambda: True,
    )
    monkeypatch.setattr(
        "copy_that.extractors.geometry.depth_normals.torch.cuda.is_available",
        lambda: True,
    )

    device, resolved, warnings = _resolve_device_and_profile(GeometryProfile.AUTO)
    assert device == "cuda"
    assert resolved == GeometryProfile.GPU_FULL
    assert warnings == []
