from __future__ import annotations

import logging
import os

import numpy as np
import torch
from PIL import Image

from copy_that.application.gpu import gpu_enabled

from .geometry_models import (
    OptionalDependencyError,
    _silence_transformers_warnings,
    depth_anything,
    marigold_normals,
)
from .normals_from_depth import compute_normals_from_depth
from .profile import GeometryProfile

logger = logging.getLogger(__name__)

_NORMALS_SMOOTHING_DEFAULTS = {
    GeometryProfile.CPU_FAST: 1.5,
    GeometryProfile.CPU_ACCURATE: 1.0,
    GeometryProfile.GPU_FULL: 0.75,
}


def _to_pil(img) -> Image.Image:
    if isinstance(img, Image.Image):
        return img.convert("RGB")
    return Image.fromarray(img).convert("RGB")


def _norm01(x: torch.Tensor) -> torch.Tensor:
    x = x.to(dtype=torch.float32)
    x = torch.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    x_min = torch.amin(x)
    x_max = torch.amax(x)
    return (x - x_min) / torch.clamp(x_max - x_min, min=1e-6)


def _extract_depth_tensor(depth_out) -> torch.Tensor:
    depth = None
    if isinstance(depth_out, dict):
        if depth_out.get("predicted_depth") is not None:
            depth = depth_out.get("predicted_depth")
        else:
            depth = depth_out.get("depth")
    else:
        depth = getattr(depth_out, "predicted_depth", None)
        if depth is None:
            depth = getattr(depth_out, "depth", None)

    if depth is None:
        raise RuntimeError("DepthAnything output missing depth tensor")

    if isinstance(depth, Image.Image):
        depth_tensor = torch.from_numpy(np.array(depth))
    elif torch.is_tensor(depth):
        depth_tensor = depth
    else:
        depth_tensor = torch.as_tensor(depth)

    depth_tensor = depth_tensor.squeeze()
    if depth_tensor.ndim != 2:
        raise RuntimeError(f"DepthAnything output shape unexpected: {tuple(depth_tensor.shape)}")

    return depth_tensor.to(dtype=torch.float32)


def _extract_normals_tensor(normals_out) -> torch.Tensor:
    normals = None
    if isinstance(normals_out, dict):
        normals = normals_out.get("prediction")
    else:
        normals = getattr(normals_out, "prediction", None)

    if normals is None:
        raise RuntimeError("Marigold output missing prediction tensor")

    if torch.is_tensor(normals):
        normals_tensor = normals
    else:
        normals_tensor = torch.as_tensor(normals)

    normals_tensor = normals_tensor.squeeze()
    if normals_tensor.ndim != 3 or normals_tensor.shape[2] != 3:
        raise RuntimeError(f"Marigold output shape unexpected: {tuple(normals_tensor.shape)}")

    return normals_tensor.to(dtype=torch.float32)


def _resolve_device_and_profile(profile: GeometryProfile) -> tuple[str, GeometryProfile, list[str]]:
    warnings: list[str] = []
    device = "cpu"
    if gpu_enabled():
        if torch.cuda.is_available():
            device = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"
    resolved_profile = profile

    if profile == GeometryProfile.AUTO:
        resolved_profile = GeometryProfile.GPU_FULL if device != "cpu" else GeometryProfile.CPU_FAST

    if resolved_profile in (GeometryProfile.CPU_FAST, GeometryProfile.CPU_ACCURATE):
        if device != "cpu":
            warnings.append("cpu_profile_forced")
        device = "cpu"

    if resolved_profile == GeometryProfile.GPU_FULL and device != "cuda":
        if device == "cpu":
            warnings.append("gpu_unavailable_fallback_cpu_fast")
            resolved_profile = GeometryProfile.CPU_FAST
        else:
            warnings.append("gpu_non_cuda_depth_only")

    return device, resolved_profile, warnings


def _resolve_normals_smoothing(profile: GeometryProfile, warnings: list[str]) -> float:
    env_value = os.getenv("GEOMETRY_NORMALS_SMOOTHING", "").strip()
    if env_value:
        try:
            return float(env_value)
        except ValueError:
            warnings.append("normals_smoothing_env_invalid")

    return _NORMALS_SMOOTHING_DEFAULTS.get(profile, 1.0)


def extract_depth_and_normals(
    image,
    *,
    profile: GeometryProfile = GeometryProfile.AUTO,
):
    device, resolved_profile, warnings = _resolve_device_and_profile(profile)
    if resolved_profile == GeometryProfile.GPU_FULL and device == "mps":
        logger.info(
            "MPS available; using depth on MPS with depth-gradient normals (Marigold requires CUDA)."
        )

    pil = _to_pil(image)

    # --- Depth ---
    depth_model = (
        "depth-anything/Depth-Anything-V2-Small-hf"
        if resolved_profile == GeometryProfile.CPU_FAST
        else "depth-anything/Depth-Anything-V2-Base-hf"
    )

    depth_pipe = depth_anything(depth_model, device)
    with _silence_transformers_warnings(), torch.inference_mode():
        depth_out = depth_pipe(pil)
    depth = _extract_depth_tensor(depth_out)
    depth01 = _norm01(depth)

    # --- Normals ---
    normals = None
    normals_confidence = None
    normals_gradients = None
    normals_source = "depth_gradient"
    if resolved_profile == GeometryProfile.GPU_FULL and device == "cuda":
        try:
            normals_pipe = marigold_normals(
                "prs-eth/marigold-normals-v1-1",
                device,
            )
            with torch.inference_mode():
                normals_out = normals_pipe(pil)
            normals = _extract_normals_tensor(normals_out)
            normals_source = "marigold"
        except OptionalDependencyError as exc:
            logger.warning("Marigold normals unavailable, using depth gradients: %s", exc)
            warnings.append("marigold_unavailable_depth_gradient")
    elif resolved_profile == GeometryProfile.GPU_FULL and device != "cuda":
        warnings.append("marigold_requires_cuda_depth_gradient")

    if normals is None:
        smoothing_sigma = _resolve_normals_smoothing(resolved_profile, warnings)
        normals_result = compute_normals_from_depth(depth01, smoothing=smoothing_sigma)
        normals = normals_result.normals
        normals_confidence = normals_result.confidence
        normals_gradients = normals_result.gradients
    else:
        smoothing_sigma = None

    depth01_np = depth01.detach().cpu().numpy().astype("float32")
    normals_np = normals.detach().cpu().numpy().astype("float32")
    normals_confidence_np = (
        None
        if normals_confidence is None
        else normals_confidence.detach().cpu().numpy().astype("float32")
    )
    normals_gradients_np = (
        None
        if normals_gradients is None
        else normals_gradients.detach().cpu().numpy().astype("float32")
    )

    return {
        "depth01": depth01_np,
        "normals_xyz": normals_np,
        "normals_confidence": normals_confidence_np,
        "normals_gradients": normals_gradients_np,
        "meta": {
            "profile_requested": profile.value,
            "profile_resolved": resolved_profile.value,
            "device": device,
            "depth_model": depth_model,
            "normals_source": normals_source,
            "normals_smoothing_sigma": smoothing_sigma,
            "warnings": warnings,
        },
    }
