from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Project:
    id: int
    name: str
    description: str | None
    owner_id: str | None
    created_at: datetime
    updated_at: datetime
