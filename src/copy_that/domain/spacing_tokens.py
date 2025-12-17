from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class SpacingToken:
    id: int
    project_id: int
    extraction_job_id: int | None
    value_px: int
    name: str
    semantic_role: str | None
    spacing_type: str | None
    category: str | None
    confidence: float | None
    usage: str | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class SpacingTokenCreate:
    value_px: int
    name: str
    semantic_role: str | None
    spacing_type: str | None
    category: str | None
    confidence: float | None
    usage: str | None
