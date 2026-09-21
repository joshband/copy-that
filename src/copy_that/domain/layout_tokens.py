from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class LayoutToken:
    id: int
    project_id: int
    extraction_job_id: int | None
    name: str
    role: str
    value_px: float
    value_json: str | None
    confidence: float
    created_at: datetime


@dataclass(frozen=True, slots=True)
class LayoutTokenCreate:
    name: str
    role: str
    value_px: float
    value_json: str | None = None
    confidence: float = 0.8
