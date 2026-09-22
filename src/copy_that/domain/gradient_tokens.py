from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class GradientToken:
    id: int
    project_id: int
    extraction_job_id: int | None
    name: str
    gradient_type: str
    angle: float
    stops_json: str
    source: str
    confidence: float
    axis: str | None
    confirmed_by: str | None
    extraction_metadata: str | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class GradientTokenCreate:
    name: str
    gradient_type: str
    angle: float
    stops_json: str
    source: str = "cv"
    confidence: float = 0.0
    axis: str | None = None
    confirmed_by: str | None = None
    extraction_metadata: str | None = None
