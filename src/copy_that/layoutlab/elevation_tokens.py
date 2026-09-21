"""Elevation and lighting token helpers derived from depth and shadow cues."""

from __future__ import annotations

import math
from typing import Any

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None  # type: ignore[assignment]

from copy_that.core_tokens.model import Token, TokenType


def _to_array(depth_map: Any) -> Any:
    if np is None:
        return depth_map
    if depth_map is None:
        return None
    if isinstance(depth_map, np.ndarray):
        return depth_map.astype("float32")
    try:
        return np.array(depth_map, dtype="float32")
    except Exception:
        return None


def _quantile_slices(depth_map: Any, levels: int) -> list[float]:
    if np is None:
        # Deterministic fallback bands
        return [round(i / levels, 2) for i in range(1, levels + 1)]
    if depth_map is None:
        return [round(i / levels, 2) for i in range(1, levels + 1)]
    flat = depth_map.flatten()
    if flat.size == 0:
        return [round(i / levels, 2) for i in range(1, levels + 1)]
    qs = [float(np.quantile(flat, q)) for q in np.linspace(0.35, 0.95, levels)]
    max_val = max(max(qs), 1e-6)
    return [round(q / max_val, 3) for q in qs]


def _shadow_light_hint(light_direction: tuple[float, float] | None) -> float:
    if not light_direction:
        return 0.0
    azimuth, elevation = light_direction
    # Favor horizontal offset from azimuth, dampened by elevation (overhead -> smaller offset)
    return float(math.cos(azimuth) * max(0.35, 1.0 - elevation / math.pi))


def derive_elevation_tokens(
    depth_map: Any | None,
    shadow_cues: dict[str, Any] | None = None,
    levels: int = 3,
    base_id: str = "token/elevation",
) -> list[Token]:
    """
    Convert depth and optional shadow cues into layered elevation/lighting tokens.

    Returns a small stack of shadow tokens that encode elevation levels with
    lighting-aware offsets. Keeps output deterministic for testing and demo use.
    """

    depth_arr = _to_array(depth_map)
    bands = _quantile_slices(depth_arr, max(1, levels))
    light_dir = None
    lighting_style = None
    if shadow_cues:
        light_dir = shadow_cues.get("light_direction") or shadow_cues.get(
            "dominant_light_direction"
        )
        lighting_style = shadow_cues.get("lighting_style")
    light_bias = _shadow_light_hint(light_dir if isinstance(light_dir, tuple) else None)

    tokens: list[Token] = []
    for idx, band in enumerate(bands, start=1):
        # Depth band drives blur/offset; clamp for stability
        intensity = max(0.15, min(0.9, band))
        y_offset = round(2 + 6 * intensity, 2)
        x_offset = round(light_bias * (4 + 2 * intensity), 2)
        blur = round(4 + 12 * intensity, 2)
        opacity = round(0.08 + 0.07 * idx, 3)
        layer = {
            "x": x_offset,
            "y": y_offset,
            "blur": blur,
            "spread": 0,
            "color": f"rgba(0,0,0,{opacity})",
        }
        attributes = {
            "role": "elevation",
            "level": idx,
            "source": "depth+shadow",
            "lighting_style": lighting_style or "unknown",
        }
        tokens.append(
            Token(
                id=f"{base_id}/{idx}",
                type=TokenType.SHADOW,
                value=[layer],
                attributes=attributes,
            )
        )
    return tokens


def summarize_lighting(
    depth_map: Any | None, shadow_strength: float | None = None
) -> dict[str, Any]:
    """Simple lighting summary used to annotate elevation tokens in debug payloads."""

    depth_arr = _to_array(depth_map)
    mean_depth = float(depth_arr.mean()) if np is not None and depth_arr is not None else 0.5
    depth_range = (
        float(depth_arr.max() - depth_arr.min())
        if np is not None and depth_arr is not None
        else 0.0
    )
    return {
        "lighting_style": "directional" if (shadow_strength or 0) > 0.35 else "diffuse",
        "depth_mean": round(mean_depth, 4),
        "depth_range": round(depth_range, 4),
    }
