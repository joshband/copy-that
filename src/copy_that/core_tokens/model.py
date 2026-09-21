"""Token model for the token graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

TokenValue = str | int | float | list[Any] | dict[str, Any]


class TokenType(str, Enum):
    # Extracted MVP + Compat+ section types
    COLOR = "color"
    SPACING = "spacing"
    SHADOW = "shadow"
    TYPOGRAPHY = "typography"
    LAYOUT = "layout"
    GRID = "layout.grid"
    FONT_FAMILY = "font.family"  # legacy recommender path → maps to fontFamily in W3C
    FONT_SIZE = "font.size"  # maps to dimension in W3C

    # Official DTCG Format 2025.10 $type values (string-typed synth/derive today)
    DIMENSION = "dimension"
    FONT_FAMILY_DTCG = "fontFamily"
    FONT_WEIGHT = "fontWeight"
    DURATION = "duration"
    CUBIC_BEZIER = "cubicBezier"
    NUMBER = "number"
    STROKE_STYLE = "strokeStyle"
    BORDER = "border"
    TRANSITION = "transition"
    GRADIENT = "gradient"
    OPACITY = "opacity"  # Compat+ section; values usually $type number on export


class RelationType(str, Enum):
    ALIAS_OF = "aliasOf"
    MULTIPLE_OF = "multipleOf"
    ROLE_OF = "roleOf"
    COMPOSES = "composes"
    CONTAINS = "contains"


@dataclass(slots=True)
class TokenRelation:
    type: RelationType
    target: str
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Token:
    """A normalized design token representation."""

    id: str
    type: TokenType | str
    value: TokenValue | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    relations: list[TokenRelation] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
