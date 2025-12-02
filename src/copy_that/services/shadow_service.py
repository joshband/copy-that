"""Service helpers for shadow API handlers."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from copy_that.application.ai_shadow_extractor import (
    AIShadowExtractor,
    ExtractedShadowToken,
    ShadowExtractionResult,
)
from core.tokens.adapters.w3c import tokens_to_w3c
from core.tokens.repository import InMemoryTokenRepository, TokenRepository
from core.tokens.shadow import make_shadow_token

logger = logging.getLogger(__name__)


def shadow_token_responses(shadows: Sequence[ExtractedShadowToken]) -> list[dict[str, Any]]:
    """Convert extracted shadow tokens into response dicts."""
    return [s.model_dump() for s in shadows]


def add_shadows_to_repo(
    repo: TokenRepository, shadows: Sequence[ExtractedShadowToken], namespace: str
) -> None:
    """Upsert extracted shadows into a TokenRepository."""
    for index, shadow in enumerate(shadows, start=1):
        attributes = shadow.model_dump(exclude_none=True)
        repo.upsert_token(
            make_shadow_token(
                token_id=f"{namespace}/{index:02d}",
                x=shadow.x_offset,
                y=shadow.y_offset,
                blur=shadow.blur_radius,
                spread=shadow.spread_radius,
                color_hex=shadow.color_hex,
                opacity=shadow.opacity,
                shadow_type=shadow.shadow_type,
                **attributes,
            )
        )


def result_to_response(
    result: ShadowExtractionResult, namespace: str = "token/shadow/api"
) -> dict[str, Any]:
    """Build the API response payload (including W3C export) from an extraction result."""
    repo = InMemoryTokenRepository()
    add_shadows_to_repo(repo, result.shadows, namespace)
    return {
        "shadows": shadow_token_responses(result.shadows),
        "shadow_count": result.shadow_count,
        "extraction_confidence": result.extraction_confidence,
        "extractor_used": result.extractor_used,
        "design_tokens": tokens_to_w3c(repo),
    }


def db_shadows_to_repo(shadows: Sequence[Any], namespace: str) -> TokenRepository:
    """Build a TokenRepository from DB ShadowToken rows."""
    repo = InMemoryTokenRepository()
    for index, shadow in enumerate(shadows, start=1):
        attrs = {
            "id": getattr(shadow, "id", None),
            "project_id": getattr(shadow, "project_id", None),
            "extraction_job_id": getattr(shadow, "extraction_job_id", None),
            "x_offset": getattr(shadow, "x_offset", None),
            "y_offset": getattr(shadow, "y_offset", None),
            "blur_radius": getattr(shadow, "blur_radius", None),
            "spread_radius": getattr(shadow, "spread_radius", None),
            "color_hex": getattr(shadow, "color_hex", None),
            "opacity": getattr(shadow, "opacity", None),
            "name": getattr(shadow, "name", None),
            "shadow_type": getattr(shadow, "shadow_type", None),
            "semantic_role": getattr(shadow, "semantic_role", None),
            "confidence": getattr(shadow, "confidence", None),
            "extraction_metadata": getattr(shadow, "extraction_metadata", None),
            "category": getattr(shadow, "category", None),
            "usage": getattr(shadow, "usage", None),
        }
        repo.upsert_token(
            make_shadow_token(
                token_id=f"{namespace}/{index:02d}",
                x=attrs["x_offset"],
                y=attrs["y_offset"],
                blur=attrs["blur_radius"],
                spread=attrs["spread_radius"],
                color_hex=attrs["color_hex"],
                opacity=attrs["opacity"],
                shadow_type=attrs["shadow_type"],
                **{k: v for k, v in attrs.items() if v is not None},
            )
        )
    return repo


def aggregate_shadow_batch(shadows: Sequence[ExtractedShadowToken]) -> list[ExtractedShadowToken]:
    """
    Deduplicate shadows using a simple similarity metric.
    Shadows are considered similar if they have:
    - Nearly identical x, y, blur, spread (within 10%)
    - Same color
    - Similar opacity (within 10%)
    """
    if not shadows:
        return []

    def shadow_key(s: ExtractedShadowToken) -> tuple[str, str]:
        """Create a simplified key for shadow grouping"""
        # Round values to nearest 2 pixels for comparison
        x_key = round(s.x_offset / 2) * 2
        y_key = round(s.y_offset / 2) * 2
        blur_key = round(s.blur_radius / 2) * 2
        spread_key = round(s.spread_radius / 2) * 2
        opacity_key = round(s.opacity * 10) / 10  # Group by 0.1 increments

        return (
            f"{x_key}_{y_key}_{blur_key}_{spread_key}_{opacity_key}_{s.color_hex.lower()}",
            s.shadow_type,
        )

    seen: dict[tuple[str, str], ExtractedShadowToken] = {}
    aggregated: list[ExtractedShadowToken] = []

    for shadow in shadows:
        key = shadow_key(shadow)
        if key not in seen:
            seen[key] = shadow
            aggregated.append(shadow)

    logger.info(f"Aggregated {len(shadows)} shadows into {len(aggregated)} unique shadows")
    return aggregated


def get_extractor() -> tuple[AIShadowExtractor, str]:
    """Get the configured shadow extractor instance and name."""
    return AIShadowExtractor(), "claude_sonnet"
