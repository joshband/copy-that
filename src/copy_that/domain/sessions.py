from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ExtractionSession:
    id: int
    project_id: int
    name: str
    description: str | None
    image_count: int
    created_at: datetime
    updated_at: datetime
