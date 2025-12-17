from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class User:
    id: str
    email: str
    hashed_password: str
    full_name: str | None
    roles: list[str]
    is_active: bool
    created_at: datetime
