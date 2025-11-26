"""Token model for the token graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

TokenValue = str | int | float | list[Any] | dict[str, Any]


@dataclass(slots=True)
class Token:
    """A normalized design token representation."""

    id: str
    type: str
    value: TokenValue | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    relations: dict[str, str] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
