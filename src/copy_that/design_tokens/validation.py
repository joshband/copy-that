"""W3C Design Tokens schema validation helpers."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

_SCHEMA_DIR = Path(__file__).resolve().parent / "schemas" / "2025_10"


@cache
def _load_schema(name: str) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads((_SCHEMA_DIR / name).read_text(encoding="utf-8")))


def validate_schema(schema_name: str, payload: dict[str, Any]) -> None:
    """Validate payload against a schema file; raises on failure."""
    Draft202012Validator(_load_schema(schema_name)).validate(payload)


def validate_w3c_export(payload: dict[str, Any], *, validate_color: bool = False) -> None:
    """Validate a W3C export payload against format (and optionally color) schemas."""
    validate_schema("format.schema.json", payload)
    if validate_color and "color" in payload:
        color_section = payload.get("color")
        if isinstance(color_section, dict):
            validate_schema("color.schema.json", color_section)
