"""Shadow token helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.tokens.model import RelationType, Token, TokenRelation, TokenType


@dataclass(slots=True)
class ShadowLayer:
    """
    A single shadow layer.

    All distances are in px; W3C adapter will wrap these as dimensions.
    `color_token_id` must be a valid Token.id of type COLOR.
    """

    x: float
    y: float
    blur: float
    spread: float
    color_token_id: str
    inset: bool = False


def make_shadow_token(
    token_id: str,
    layers: list[ShadowLayer],
    attributes: dict[str, Any] | None = None,
) -> Token:
    attributes = attributes or {}

    value: list[dict[str, Any]] = []
    relations: list[TokenRelation] = []

    for layer in layers:
        value.append(
            {
                "x": float(layer.x),
                "y": float(layer.y),
                "blur": float(layer.blur),
                "spread": float(layer.spread),
                "color": layer.color_token_id,
                "inset": bool(layer.inset),
            }
        )
        relations.append(
            TokenRelation(
                type=RelationType.COMPOSES,
                target=layer.color_token_id,
                meta={"role": "shadow-color"},
            )
        )
    return Token(
        id=token_id,
        type=TokenType.SHADOW,
        value=value,
        attributes=attributes,
        relations=relations,
    )
