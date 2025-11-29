from fastapi import APIRouter

from copy_that.application.shadow_extractor import ShadowExtractor

router = APIRouter(prefix="/api/v1/shadows", tags=["shadows"])


@router.get("", summary="List shadow tokens (stub)")
def list_shadows() -> dict:
    """
    Stub shadow endpoint returning a sample shadow token.
    Replace with real layer/shadow extraction when available.
    """
    sample = ShadowExtractor().extract_shadow_tokens([])
    if not sample:
        sample = {
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
    return {"tokens": sample}
