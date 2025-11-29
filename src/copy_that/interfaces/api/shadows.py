from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from copy_that.application.shadow_extractor import ShadowExtractor

router = APIRouter(prefix="/api/v1/shadows", tags=["shadows"])


@router.get("", summary="List shadow tokens (stub)")
def list_shadows() -> dict[str, dict[str, Any]]:
    """
    Stub shadow endpoint returning a sample shadow token.
    Replace with real layer/shadow extraction when available.
    """
    sample = ShadowExtractor().extract_shadow_tokens([])
    fallback: dict[str, dict[str, Any]] = {
        "shadow.1": {
            "$type": "shadow",
            "$value": {
                "color": "#00000033",
                "x": {"value": 0, "unit": "px"},
                "y": {"value": 4, "unit": "px"},
                "blur": {"value": 8, "unit": "px"},
                "spread": {"value": 0, "unit": "px"},
            },
        }
    }
    return {"tokens": sample if sample else fallback}
