"""Service helpers for typography API handlers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from copy_that.application.ai_typography_extractor import TypographyExtractionResult
from core.tokens.repository import InMemoryTokenRepository, TokenRepository
from core.tokens.typography import make_typography_token


def typography_attributes(token: Any) -> dict[str, Any]:
    """Normalize typography token attributes from dataclass/orm/pydantic.

    Args:
        token: Token object (Pydantic model, SQLModel, or dict)

    Returns:
        Dictionary of normalized attributes
    """
    data: dict[str, Any]
    if hasattr(token, "model_dump"):
        data = token.model_dump(exclude_none=True)
    elif hasattr(token, "__dict__"):
        data = {k: v for k, v in vars(token).items() if not k.startswith("_")}
    else:
        data = dict(token) if isinstance(token, dict) else {}

    # Ensure core fields are present
    data.setdefault("font_family", getattr(token, "font_family", "System"))
    data.setdefault("font_weight", getattr(token, "font_weight", 400))
    data.setdefault("font_size", getattr(token, "font_size", 16))
    data.setdefault("line_height", getattr(token, "line_height", 1.5))
    data.setdefault("semantic_role", getattr(token, "semantic_role", "body"))

    return data


def build_typography_repo(
    tokens: Sequence[Any], namespace: str = "token/typography/api"
) -> TokenRepository:
    """Create a TokenRepository of typography tokens for API responses.

    Args:
        tokens: Sequence of typography token objects
        namespace: Namespace for token IDs

    Returns:
        TokenRepository with typography tokens
    """
    repo = InMemoryTokenRepository()
    for index, token in enumerate(tokens, start=1):
        attrs = typography_attributes(token)
        font_family = attrs.get("font_family", "System")
        font_size = attrs.get("font_size", 16)
        semantic_role = attrs.get("semantic_role", "body")

        repo.upsert_token(
            make_typography_token(
                f"{namespace}/{semantic_role}/{index:02d}",
                font_family,
                font_size,
                attrs,
            )
        )
    return repo


def build_typography_repo_from_db(
    tokens: Sequence[Any], namespace: str = "token/typography/export"
) -> TokenRepository:
    """Create a TokenRepository for DB typography tokens.

    Args:
        tokens: Sequence of typography tokens from database
        namespace: Namespace for token IDs

    Returns:
        TokenRepository with typography tokens
    """
    return build_typography_repo(tokens, namespace=namespace)


def merge_typography(
    cv: TypographyExtractionResult, ai: TypographyExtractionResult
) -> TypographyExtractionResult:
    """Merge AI typography tokens onto CV tokens by properties to avoid duplicates.

    Args:
        cv: CV extraction result
        ai: AI extraction result

    Returns:
        Merged TypographyExtractionResult preferring AI over CV
    """
    # Create map of AI tokens by key properties
    ai_by_key = {(t.font_family, t.font_weight, t.font_size, t.semantic_role): t for t in ai.tokens}

    # Start with AI tokens
    merged_tokens = list(ai.tokens)

    # Add CV tokens that aren't in AI
    for t in cv.tokens:
        key = (t.font_family, t.font_weight, t.font_size, t.semantic_role)
        if key not in ai_by_key:
            merged_tokens.append(t)

    return TypographyExtractionResult(
        tokens=merged_tokens,
        typography_palette=ai.typography_palette or cv.typography_palette,
        extraction_confidence=ai.extraction_confidence or cv.extraction_confidence,
        extractor_used=ai.extractor_used or cv.extractor_used,
        color_associations=ai.color_associations or cv.color_associations,
    )


def aggregate_typography_batch(
    typography_batch: list[list[Any]],
    namespace: str = "token/typography/batch",
) -> tuple[TokenRepository, dict[str, Any]]:
    """Aggregate typography tokens from a batch, deduplicating by properties.

    Args:
        typography_batch: List of lists of typography tokens
        namespace: Namespace for token IDs

    Returns:
        Tuple of (TokenRepository, aggregation stats)
    """
    merged: dict[tuple, dict[str, Any]] = {}
    total = 0

    for token_list in typography_batch:
        for token in token_list:
            total += 1
            attrs = typography_attributes(token)

            # Key by font properties
            key = (
                attrs.get("font_family", "System"),
                attrs.get("font_weight", 400),
                attrs.get("font_size", 16),
                attrs.get("semantic_role", "body"),
            )

            if key not in merged:
                merged[key] = attrs
            else:
                # Update with highest confidence
                existing_conf = merged[key].get("confidence", 0.5)
                new_conf = attrs.get("confidence", 0.5)
                if new_conf > existing_conf:
                    merged[key] = attrs

    # Build repository from merged tokens
    repo = InMemoryTokenRepository()
    for index, (key, attrs) in enumerate(merged.items(), start=1):
        font_family, font_weight, font_size, semantic_role = key
        repo.upsert_token(
            make_typography_token(
                f"{namespace}/{semantic_role}/{index:02d}",
                font_family,
                font_size,
                attrs,
            )
        )

    stats = {
        "total_input_tokens": total,
        "unique_after_merge": len(merged),
        "reduction_percentage": ((1 - len(merged) / total) * 100 if total > 0 else 0),
    }

    return repo, stats


def deduplicate_typography(tokens: list[Any]) -> list[Any]:
    """Deduplicate typography tokens by core properties.

    Args:
        tokens: List of typography tokens

    Returns:
        Deduplicated list, keeping highest confidence
    """
    seen: dict[tuple, Any] = {}

    for token in tokens:
        attrs = typography_attributes(token)
        key = (
            attrs.get("font_family", "System"),
            attrs.get("font_weight", 400),
            attrs.get("font_size", 16),
            attrs.get("semantic_role", "body"),
        )

        if key not in seen:
            seen[key] = token
        else:
            # Keep token with higher confidence
            existing_conf = typography_attributes(seen[key]).get("confidence", 0.5)
            new_conf = attrs.get("confidence", 0.5)
            if new_conf > existing_conf:
                seen[key] = token

    return list(seen.values())
