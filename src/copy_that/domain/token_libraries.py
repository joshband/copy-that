from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TokenLibrary:
    id: int
    session_id: int
    token_type: str
    name: str | None
    statistics: str | None
    is_curated: bool
    curation_notes: str | None
    created_at: datetime
    updated_at: datetime
