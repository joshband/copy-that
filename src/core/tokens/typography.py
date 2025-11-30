"""Typography token helpers."""

from __future__ import annotations

from typing import Any

from core.tokens.model import RelationType, Token, TokenRelation, TokenType


def make_typography_token(
    token_id: str,
    *,
    font_family_ref: str,
    size_ref: str,
    line_height_ref: str | None = None,
    weight_ref: str | int | None = None,
    letter_spacing_ref: str | None = None,
    casing: str | None = None,
    color_ref: str,
    attributes: dict[str, Any] | None = None,
) -> Token:
    value: dict[str, Any] = {
        "fontFamily": font_family_ref,
        "fontSize": size_ref,
        "color": color_ref,
    }
    if line_height_ref:
        value["lineHeight"] = line_height_ref
    if weight_ref is not None:
        value["fontWeight"] = weight_ref
    if letter_spacing_ref:
        value["letterSpacing"] = letter_spacing_ref
    if casing:
        value["casing"] = casing
    relations: list[TokenRelation] = [
        TokenRelation(type=RelationType.COMPOSES, target=font_family_ref),
        TokenRelation(type=RelationType.COMPOSES, target=size_ref),
        TokenRelation(type=RelationType.COMPOSES, target=color_ref),
    ]
    if line_height_ref:
        relations.append(TokenRelation(type=RelationType.COMPOSES, target=line_height_ref))
    return Token(
        id=token_id,
        type=TokenType.TYPOGRAPHY,
        value=value,
        attributes=attributes or {},
        relations=relations,
    )
