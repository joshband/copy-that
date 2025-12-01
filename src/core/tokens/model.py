"""Token model for the token graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

TokenValue = str | int | float | list[Any] | dict[str, Any]


class TokenType(str, Enum):
    COLOR = "color"
    SPACING = "spacing"
    SHADOW = "shadow"
    TYPOGRAPHY = "typography"
    LAYOUT = "layout"
    GRID = "layout.grid"
    FONT_FAMILY = "font.family"
    FONT_SIZE = "font.size"


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
