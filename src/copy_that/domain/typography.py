from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TypographyToken:
    id: int
    project_id: int
    extraction_job_id: int | None
    font_family: str
    font_weight: int
    font_style: str | None
    font_size: int
    line_height: float
    letter_spacing: float | None
    text_transform: str | None
    text_align: str | None
    name: str | None
    semantic_role: str | None
    category: str | None
    confidence: float
    prominence: float | None
    is_readable: bool | None
    readability_score: float | None
    extraction_metadata: str | None
    usage: str | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class TypographyTokenCreate:
    project_id: int
    extraction_job_id: int | None
    font_family: str
    font_weight: int
    font_style: str | None
    font_size: int
    line_height: float
    letter_spacing: float | None
    text_transform: str | None
    text_align: str | None
    name: str | None
    semantic_role: str | None
    category: str | None
    confidence: float
    prominence: float | None
    is_readable: bool | None
    readability_score: float | None
    extraction_metadata: str | None
