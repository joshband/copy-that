"""Spacing token helpers."""

from __future__ import annotations

from typing import Any

from core.tokens.model import Token, TokenType


def make_spacing_token(
    token_id: str, value_px: int, value_rem: float, attributes: dict[str, Any] | None = None
) -> Token:
    """Create a normalized spacing token representation."""
    value = {"px": value_px, "rem": value_rem}
    return Token(id=token_id, type=TokenType.SPACING, value=value, attributes=attributes or {})
