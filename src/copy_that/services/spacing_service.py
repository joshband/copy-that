"""Service helpers for spacing API handlers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from copy_that.application.spacing_models import SpacingExtractionResult
from core.tokens.repository import InMemoryTokenRepository, TokenRepository
from core.tokens.spacing import make_spacing_token


def spacing_attributes(token: Any) -> dict[str, Any]:
    """Normalize spacing token attributes from dataclass/orm/pydantic."""
    data: dict[str, Any]
    if hasattr(token, "model_dump"):
        data = token.model_dump(exclude_none=True)
    elif hasattr(token, "__dict__"):
        data = {k: v for k, v in vars(token).items() if not k.startswith("_")}
    else:
        data = {}
    value_px = data.get("value_px", getattr(token, "value_px", None))
    data["value_px"] = value_px
    data.setdefault("value_rem", getattr(token, "value_rem", round((value_px or 0) / 16, 4)))
    return data


def build_spacing_repo(
    tokens: Sequence[Any], namespace: str = "token/spacing/api"
) -> TokenRepository:
    """Create a TokenRepository of spacing tokens for API responses."""
    repo = InMemoryTokenRepository()
    for index, token in enumerate(tokens, start=1):
        attrs = spacing_attributes(token)
        value_px = attrs["value_px"]
        value_rem = attrs["value_rem"]
        repo.upsert_token(
            make_spacing_token(
                f"{namespace}/{index:02d}",
                value_px,
                value_rem,
                attrs,
            )
        )
    return repo


def build_spacing_repo_from_db(
    tokens: Sequence[Any], namespace: str = "token/spacing/export"
) -> TokenRepository:
    """Create a TokenRepository for DB spacing tokens."""
    return build_spacing_repo(tokens, namespace=namespace)


def merge_spacing(
    cv: SpacingExtractionResult, ai: SpacingExtractionResult
) -> SpacingExtractionResult:
    """Merge AI tokens onto CV tokens by value/name to avoid duplicates."""
    ai_by_value = {(t.value_px, t.name): t for t in ai.tokens}
    merged_tokens = list(ai.tokens)
    for t in cv.tokens:
        key = (t.value_px, t.name)
        if key not in ai_by_value:
            merged_tokens.append(t)

    return SpacingExtractionResult(
        tokens=merged_tokens,
        scale_system=ai.scale_system or cv.scale_system,
        base_unit=ai.base_unit or cv.base_unit,
        base_unit_confidence=ai.base_unit_confidence or cv.base_unit_confidence,
        grid_compliance=ai.grid_compliance or cv.grid_compliance,
        extraction_confidence=ai.extraction_confidence or cv.extraction_confidence,
        unique_values=ai.unique_values or cv.unique_values,
        min_spacing=ai.min_spacing or cv.min_spacing,
        max_spacing=ai.max_spacing or cv.max_spacing,
    )


def aggregate_spacing_batch(
    spacing_batch: list[list[Any]],
    similarity_threshold: float | None = None,
    namespace: str = "token/spacing/batch",
) -> tuple[TokenRepository, dict[str, Any]]:
    """Minimal spacing aggregation using the token graph."""
    merged: dict[int, dict[str, Any]] = {}
    total = 0
    for token_list in spacing_batch:
        for token in token_list:
            total += 1
            attrs = spacing_attributes(token)
            key = attrs.get("value_px")
            if key is None:
                continue
            current = merged.get(key)
            if current is None:
                merged[key] = attrs
                continue
            prev_conf = float(current.get("confidence") or 0)
            new_conf = float(attrs.get("confidence") or 0)
            if new_conf >= prev_conf:
                merged[key] = attrs

    repo = InMemoryTokenRepository()
    for index, (value_px, attrs) in enumerate(sorted(merged.items()), start=1):
        value_rem = attrs.get("value_rem") or round(value_px / 16, 4)
        repo.upsert_token(
            make_spacing_token(
                f"{namespace}/{index:02d}",
                value_px,
                value_rem,
                attrs,
            )
        )

    stats = {
        "total_extracted": total,
        "unique": len(merged),
        "similarity_threshold": similarity_threshold,
    }
    return repo, stats
