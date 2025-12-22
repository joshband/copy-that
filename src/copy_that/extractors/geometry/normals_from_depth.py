"""
Deterministic surface normals from depth using analytical gradients.
Supports CPU and Apple MPS without external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F


@dataclass
class NormalResult:
    normals: torch.Tensor  # (H, W, 3), unit vectors
    confidence: torch.Tensor  # (H, W), [0..1]
    gradients: torch.Tensor  # (H, W, 2), dx, dy
    metadata: dict[str, Any]


def _sobel_kernels(device: torch.device, dtype: torch.dtype) -> tuple[torch.Tensor, torch.Tensor]:
    kx = (
        torch.tensor(
            [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
            device=device,
            dtype=dtype,
        )
        / 8.0
    )

    ky = (
        torch.tensor(
            [[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
            device=device,
            dtype=dtype,
        )
        / 8.0
    )

    return kx.view(1, 1, 3, 3), ky.view(1, 1, 3, 3)


def _gaussian_kernel_1d(sigma: float, device: torch.device, dtype: torch.dtype) -> torch.Tensor:
    if sigma <= 0:
        return torch.tensor([1.0], device=device, dtype=dtype)

    size = int(2 * round(2 * sigma) + 1)
    if size < 3:
        size = 3
    if size % 2 == 0:
        size += 1

    center = (size - 1) / 2.0
    x = torch.arange(size, device=device, dtype=dtype) - center
    kernel = torch.exp(-(x**2) / (2 * sigma**2))
    kernel = kernel / kernel.sum()
    return kernel


def _gaussian_blur(depth: torch.Tensor, sigma: float) -> torch.Tensor:
    kernel = _gaussian_kernel_1d(sigma, depth.device, depth.dtype)
    if kernel.numel() == 1:
        return depth

    radius = kernel.numel() // 2
    depth = F.pad(depth, (radius, radius, radius, radius), mode="replicate")
    kernel_x = kernel.view(1, 1, 1, -1)
    kernel_y = kernel.view(1, 1, -1, 1)
    depth = F.conv2d(depth, kernel_x)
    depth = F.conv2d(depth, kernel_y)
    return depth


def _prepare_depth(
    depth: torch.Tensor | np.ndarray,
    device: str | None = None,
) -> torch.Tensor:
    if not torch.is_tensor(depth):
        depth_tensor = torch.as_tensor(depth)
    else:
        depth_tensor = depth

    if depth_tensor.ndim == 2:
        depth_tensor = depth_tensor.unsqueeze(0).unsqueeze(0)
    elif depth_tensor.ndim == 3 and depth_tensor.shape[0] == 1:
        depth_tensor = depth_tensor.unsqueeze(0)
    else:
        raise ValueError("Depth must be (H, W) or (1, H, W)")

    if device is None:
        device = depth_tensor.device
    depth_tensor = depth_tensor.to(device=device, dtype=torch.float32)
    depth_tensor = torch.clamp(depth_tensor, min=1e-6)
    return depth_tensor


def compute_normals_from_depth(
    depth: torch.Tensor | np.ndarray,
    fx: float | None = None,
    fy: float | None = None,
    smoothing: float = 1.0,
    device: str | None = None,
) -> NormalResult:
    """
    Compute surface normals from a depth map using Sobel gradients.

    Parameters
    ----------
    depth : torch.Tensor or np.ndarray
        Shape (H, W) or (1, H, W). Depth must be positive.
    fx, fy : float, optional
        Focal lengths. If None, assume normalized camera.
    smoothing : float
        Gaussian blur sigma applied before gradients.
    device : str, optional
        'cpu', 'mps', or 'cuda'. Defaults to depth device.
    """

    depth_tensor = _prepare_depth(depth, device=device)
    if smoothing > 0:
        depth_tensor = _gaussian_blur(depth_tensor, smoothing)

    kx, ky = _sobel_kernels(depth_tensor.device, depth_tensor.dtype)
    dzdx = F.conv2d(depth_tensor, kx, padding=1)
    dzdy = F.conv2d(depth_tensor, ky, padding=1)

    dzdx = dzdx.squeeze(0).squeeze(0)
    dzdy = dzdy.squeeze(0).squeeze(0)

    fx = 1.0 if fx is None else float(fx)
    fy = 1.0 if fy is None else float(fy)

    nx = -dzdx * fx
    ny = -dzdy * fy
    nz = torch.ones_like(nx)

    normals = torch.stack([nx, ny, nz], dim=-1)
    normals = F.normalize(normals, dim=-1, eps=1e-6)

    grad_mag = torch.sqrt(dzdx**2 + dzdy**2)
    confidence = torch.exp(-grad_mag)
    gradients = torch.stack([dzdx, dzdy], dim=-1)

    return NormalResult(
        normals=normals,
        confidence=confidence,
        gradients=gradients,
        metadata={
            "method": "depth_gradient",
            "smoothing_sigma": float(smoothing),
            "fx": fx,
            "fy": fy,
            "device": str(depth_tensor.device),
        },
    )


def normals_from_depth(depth01: np.ndarray) -> np.ndarray:
    """Backwards-compatible wrapper returning normals as numpy."""
    result = compute_normals_from_depth(depth01, smoothing=0.0)
    return result.normals.detach().cpu().numpy().astype("float32")
