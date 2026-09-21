from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ShadowToken:
    id: int
    project_id: int
    extraction_job_id: int | None
    x_offset: float
    y_offset: float
    blur_radius: float
    spread_radius: float
    color_hex: str
    opacity: float
    name: str
    shadow_type: str | None
    semantic_role: str | None
    confidence: float
    extraction_metadata: str | None
    usage: str | None
    category: str | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ShadowTokenCreate:
    x_offset: float
    y_offset: float
    blur_radius: float
    spread_radius: float
    color_hex: str
    opacity: float
    name: str
    shadow_type: str | None
    semantic_role: str | None
    confidence: float
    extraction_metadata: str | None = None
    usage: str | None = None
    category: str | None = None
