"""Typography token helpers (graph-aware)."""

from __future__ import annotations

import re
from typing import Any

from .model import RelationType, Token, TokenRelation, TokenType


def slug_token_part(value: str) -> str:
    """Stable slug for atom token ids (fontFamily.inter, …)."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "token"


def font_family_atom_id(family: str) -> str:
    return f"fontFamily.{slug_token_part(family)}"


def font_weight_atom_id(weight: int | str) -> str:
    return f"fontWeight.{int(weight)}"


def make_font_family_token(
    family: str,
    *,
    source: str = "extracted",
    attributes: dict[str, Any] | None = None,
) -> Token:
    """Atomic DTCG fontFamily token (Phase 2 persist)."""
    attrs = {
        "$type": "fontFamily",
        "role": "font-family",
        "source": source,
        **(attributes or {}),
    }
    return Token(
        id=font_family_atom_id(family),
        type=TokenType.FONT_FAMILY_DTCG,
        value=family,
        attributes=attrs,
    )


def make_font_weight_token(
    weight: int | str,
    *,
    source: str = "extracted",
    attributes: dict[str, Any] | None = None,
) -> Token:
    """Atomic DTCG fontWeight token (Phase 2 persist)."""
    w = int(weight)
    attrs = {
        "$type": "fontWeight",
        "role": "font-weight",
        "source": source,
        **(attributes or {}),
    }
    return Token(
        id=font_weight_atom_id(w),
        type=TokenType.FONT_WEIGHT,
        value=w,
        attributes=attrs,
    )


def make_typography_token(
    token_id: str,
    *,
    font_family_token_id: str | None = None,
    font_weight_token_id: str | None = None,
    font_size_token_id: str | None = None,
    color_token_id: str | None = None,
    font_family: str | None = None,
    font_size_px: float | None = None,
    font_size: str | None = None,
    line_height_px: float | None = None,
    line_height: str | float | int | None = None,
    font_weight: str | int | None = None,
    font_style: str | None = None,
    letter_spacing_em: float | None = None,
    casing: str | None = None,
    text_align: str | None = None,
    attributes: dict[str, Any] | None = None,
) -> Token:
    """
    Create a normalized typography token with optional references to font/color tokens.

    relations:
      - COMPOSES edges to any referenced font family/weight/size/color tokens.
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

    if font_weight_token_id:
        value["fontWeight"] = font_weight_token_id
        relations.append(
            TokenRelation(
                type=RelationType.COMPOSES,
                target=font_weight_token_id,
                meta={"role": "font-weight"},
            )
        )
    elif font_weight is not None:
        value["fontWeight"] = font_weight

    if font_style:
        value["fontStyle"] = font_style

    if letter_spacing_em is not None:
        value["letterSpacing"] = {"em": float(letter_spacing_em)}

    if casing:
        value["casing"] = casing

    if text_align:
        value["textAlign"] = text_align

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
