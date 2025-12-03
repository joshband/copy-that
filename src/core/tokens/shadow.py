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
    layers: list[ShadowLayer] | None = None,
    attributes: dict[str, Any] | None = None,
    # Individual shadow parameters (alternative to layers)
    x: float | None = None,
    y: float | None = None,
    blur: float | None = None,
    spread: float | None = None,
    color_hex: str | None = None,
    opacity: float | None = None,
    shadow_type: str | None = None,
    **kwargs: Any,
) -> Token:
    """
    Create a shadow token from either:
    1. A list of ShadowLayer objects (formal W3C representation), or
    2. Individual shadow parameters (simplified API for extraction).

    When using individual parameters, a single shadow layer is created.
    """
    attributes = attributes or {}

    # Merge additional kwargs into attributes
    if kwargs:
        attributes.update(kwargs)

    # Store extraction metadata in attributes
    if opacity is not None:
        attributes["opacity"] = opacity
    if shadow_type is not None:
        attributes["shadow_type"] = shadow_type

    value: list[dict[str, Any]] = []
    relations: list[TokenRelation] = []

    # Handle individual parameters (create single layer)
    if layers is None and x is not None:
        layers = [
            ShadowLayer(
                x=float(x),
                y=float(y or 0),
                blur=float(blur or 0),
                spread=float(spread or 0),
                color_token_id=color_hex or "#000000",  # Use hex directly if no token reference
                inset=attributes.get("is_inset", False),
            )
        ]

    # Default to empty layers if nothing provided
    if layers is None:
        layers = []

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
