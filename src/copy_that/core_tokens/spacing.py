"""Spacing token helpers."""

from __future__ import annotations

import re
from typing import Any

from .model import RelationType, Token, TokenRelation, TokenType


def make_spacing_token(
    token_id: str, value_px: int, value_rem: float, attributes: dict[str, Any] | None = None
) -> Token:
    """Create a normalized spacing token representation."""
    value = {"px": value_px, "rem": value_rem}
    return Token(id=token_id, type=TokenType.SPACING, value=value, attributes=attributes or {})


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "token"


def dimension_companion_id(spacing_id: str) -> str:
    """Stable dimension companion id for a Compat+ spacing token."""
    leaf = spacing_id.split("/")[-1]
    return f"dimension.{_slug(leaf)}"


def make_dimension_companion(
    spacing: Token,
    *,
    source: str = "extracted",
) -> Token | None:
    """DTCG `$type: dimension` companion for a spacing token (keep spacing section).

    Adds a COMPOSES edge on the returned companion pointing at the spacing source.
    Caller should also attach COMPOSES from spacing → companion when dual-writing.
    """
    px: float | None = None
    if isinstance(spacing.value, (int, float)):
        px = float(spacing.value)
    elif isinstance(spacing.value, dict):
        if spacing.value.get("px") is not None:
            px = float(spacing.value["px"])
        elif spacing.value.get("value") is not None:
            px = float(spacing.value["value"])
    if px is None:
        return None

    dim_id = dimension_companion_id(spacing.id)
    return Token(
        id=dim_id,
        type=TokenType.DIMENSION,
        value={"value": px, "unit": "px"},
        attributes={
            "$type": "dimension",
            "role": "spacing-dimension",
            "source": source,
            "from": spacing.id,
        },
        relations=[
            TokenRelation(
                type=RelationType.COMPOSES,
                target=spacing.id,
                meta={"role": "spacing-source"},
            )
        ],
    )


def attach_dimension_companion(spacing: Token, companion: Token) -> Token:
    """Return a copy of ``spacing`` with COMPOSES → companion (idempotent)."""
    if any(rel.target == companion.id for rel in spacing.relations):
        return spacing
    relations = list(spacing.relations) + [
        TokenRelation(
            type=RelationType.COMPOSES,
            target=companion.id,
            meta={"role": "dimension-companion"},
        )
    ]
    return Token(
        id=spacing.id,
        type=spacing.type,
        value=spacing.value,
        attributes=dict(spacing.attributes),
        relations=relations,
        meta=dict(spacing.meta),
    )
