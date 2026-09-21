from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TokenExport:
    id: int
    library_id: int
    format: str
    file_path: str | None
    file_size: int | None
    exported_at: datetime
