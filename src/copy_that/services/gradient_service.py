"""Service helpers for gradient API handlers and export."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository, TokenRepository


def db_gradients_to_repo(gradients: Sequence[Any], namespace: str) -> TokenRepository:
    """Build a TokenRepository from DB GradientToken rows."""
    repo = InMemoryTokenRepository()
    for index, row in enumerate(gradients, start=1):
        name = getattr(row, "name", None) or f"linear-cv-{index:02d}"
        token_id = name if str(name).startswith(namespace) else f"{namespace}.{name}"
        stops_raw = getattr(row, "stops_json", "[]")
        try:
            stops = json.loads(stops_raw) if isinstance(stops_raw, str) else (stops_raw or [])
        except (TypeError, json.JSONDecodeError):
            stops = []
        if not isinstance(stops, list) or len(stops) < 2:
            continue

        source = str(getattr(row, "source", None) or "extracted")
        # Normalize DB persistence sources to extract-family for prefer_extracted.
        if source in {"cv", "ai"}:
            pass
        elif source not in {"extracted", "synth", "derive", "preset"}:
            source = "extracted"

        attrs: dict[str, Any] = {
            "$type": "gradient",
            "role": "gradient",
            "source": source if source in {"cv", "ai", "extracted"} else "extracted",
            "confidence": float(getattr(row, "confidence", 0.0) or 0.0),
        }
        axis = getattr(row, "axis", None)
        if axis:
            attrs["axis"] = axis
        confirmed_by = getattr(row, "confirmed_by", None)
        if confirmed_by:
            attrs["confirmed_by"] = confirmed_by
            if source == "cv":
                attrs["source"] = "ai"

        repo.upsert_token(
            Token(
                id=token_id,
                type=TokenType.GRADIENT,
                value={
                    "type": str(getattr(row, "gradient_type", None) or "linear"),
                    "angle": int(float(getattr(row, "angle", 90) or 90)),
                    "stops": [
                        {
                            "position": float(s.get("position", 0)),
                            "color": str(s.get("color")),
                        }
                        for s in stops
                        if isinstance(s, dict) and s.get("color")
                    ],
                },
                attributes=attrs,
            )
        )
    return repo
