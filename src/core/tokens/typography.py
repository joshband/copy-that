"""Typography token helpers (graph-aware)."""

from __future__ import annotations

from typing import Any

from core.tokens.model import RelationType, Token, TokenRelation, TokenType


def make_typography_token(
    token_id: str,
    *,
    font_family_token_id: str | None = None,
    font_size_token_id: str | None = None,
    color_token_id: str | None = None,
    font_family: str | None = None,
    font_size_px: float | None = None,
    font_size: str | None = None,
    line_height_px: float | None = None,
    line_height: str | None = None,
    font_weight: str | int | None = None,
    letter_spacing_em: float | None = None,
    casing: str | None = None,
    attributes: dict[str, Any] | None = None,
) -> Token:
    """
    Create a normalized typography token with optional references to font/color tokens.

    relations:
      - COMPOSES edges to any referenced font family/size/color tokens.
    """
    attributes = attributes or {}

    value: dict[str, Any] = {}
    relations: list[TokenRelation] = []

    if font_family_token_id:
        value["fontFamily"] = font_family_token_id
        relations.append(
            TokenRelation(
                type=RelationType.COMPOSES,
                target=font_family_token_id,
                meta={"role": "font-family"},
            )
        )
    elif font_family:
        value["fontFamily"] = font_family

    if font_size_token_id:
        value["fontSize"] = {"token": font_size_token_id}
        relations.append(
            TokenRelation(
                type=RelationType.COMPOSES, target=font_size_token_id, meta={"role": "font-size"}
            )
        )
    elif font_size_px is not None:
        value["fontSize"] = {"px": float(font_size_px)}
    elif font_size:
        value["fontSize"] = font_size

    if line_height_px is not None:
        value["lineHeight"] = {"px": float(line_height_px)}
    elif line_height:
        value["lineHeight"] = line_height

    if font_weight is not None:
        value["fontWeight"] = font_weight

    if letter_spacing_em is not None:
        value["letterSpacing"] = {"em": float(letter_spacing_em)}

    if casing:
        value["casing"] = casing

    if color_token_id:
        value["color"] = color_token_id
        relations.append(
            TokenRelation(
                type=RelationType.COMPOSES, target=color_token_id, meta={"role": "text-color"}
            )
        )
    return Token(
        id=token_id,
        type=TokenType.TYPOGRAPHY,
        value=value,
        attributes=attributes,
        relations=relations,
    )
