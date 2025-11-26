"""Typography token helpers."""

from __future__ import annotations

from typing import Any

from core.tokens.model import Token


def make_typography_token(
    token_id: str,
    *,
    font_family: str,
    size: str,
    line_height: str | None = None,
    weight: str | int | None = None,
    letter_spacing: str | None = None,
    casing: str | None = None,
    color_ref: str,
    attributes: dict[str, Any] | None = None,
) -> Token:
    value: dict[str, Any] = {
        "fontFamily": font_family,
        "fontSize": size,
        "color": color_ref,
    }
    if line_height:
        value["lineHeight"] = line_height
    if weight:
        value["fontWeight"] = weight
    if letter_spacing:
        value["letterSpacing"] = letter_spacing
    if casing:
        value["casing"] = casing
    return Token(id=token_id, type="typography", value=value, attributes=attributes or {})
