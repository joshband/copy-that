"""Helpers for working with color tokens."""

from __future__ import annotations

from typing import Any

from coloraide import Color

from core.tokens.model import Token, TokenType


def make_color_token(
    token_id: str, color: Color, attributes: dict[str, Any] | None = None
) -> Token:
    """Create a normalized color token storing value in OKLCH."""
    oklch = color.convert("oklch")
    l, c, h = oklch.coords()
    value = {
        "l": float(l),
        "c": float(c),
        "h": float(h),
        "alpha": float(oklch.alpha()),
        "space": "oklch",
    }
    return Token(id=token_id, type=TokenType.COLOR, value=value, attributes=attributes or {})


def make_color_ramp(
    base_color: str | Color,
    prefix: str = "color.accent",
    steps: list[int] | None = None,
) -> dict[str, Token]:
    """
    Generate a smooth OKLCH lightness ramp for a color family.

    Args:
        base_color: hex string or Color instance
        prefix: token id prefix (e.g., "color.accent")
        steps: list of ladder positions (e.g., [50, 100, ..., 900])

    Returns:
        Dict of token_id -> Token
    """
    steps = steps or [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]
    base = base_color if isinstance(base_color, Color) else Color(base_color)
    oklch = base.convert("oklch")
    l_base, c_base, h_base = oklch.coords()

    ramp: dict[str, Token] = {}
    for step in steps:
        # Map step (0-1000) to lightness band [0.04, 0.96]
        t = max(0.0, min(1.0, step / 1000.0))
        l_new = 0.04 + t * 0.92
        # Slightly taper chroma toward extremes to avoid clipping
        chroma_scale = 0.8 + 0.4 * (1 - abs(0.5 - t) * 2)
        c_new = max(0.0, min(c_base * chroma_scale, 0.4))
        col = Color("oklch", [l_new, c_new, h_base], alpha=oklch.alpha())
        token_id = f"{prefix}.{step}"
        ramp[token_id] = make_color_token(token_id, col)
    return ramp


def ramp_to_dict(ramp: dict[str, Token]) -> dict[str, Any]:
    """Convert ramp tokens to W3C/DTCG-compatible dict."""
    return {
        tok.id: {"$type": "color", "$value": tok.value, **(tok.attributes or {})}
        for tok in ramp.values()
    }
