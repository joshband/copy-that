"""Shadow token helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.tokens.model import Token


@dataclass(slots=True)
class ShadowLayer:
    x: float
    y: float
    blur: float
    spread: float
    color_ref: str
    inset: bool = False


def make_shadow_token(
    token_id: str,
    layers: list[ShadowLayer],
    attributes: dict[str, Any] | None = None,
) -> Token:
    value = [
        {
            "x": layer.x,
            "y": layer.y,
            "blur": layer.blur,
            "spread": layer.spread,
            "color": layer.color_ref,
            "inset": layer.inset,
        }
        for layer in layers
    ]
    return Token(id=token_id, type="shadow", value=value, attributes=attributes or {})
