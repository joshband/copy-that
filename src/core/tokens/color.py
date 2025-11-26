"""Helpers for working with color tokens."""

from __future__ import annotations

from typing import Any

from coloraide import Color

from core.tokens.model import Token


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
    return Token(id=token_id, type="color", value=value, attributes=attributes or {})
