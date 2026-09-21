from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ProjectSnapshot:
    id: int
    project_id: int
    version: int
    data: str
    created_at: datetime
