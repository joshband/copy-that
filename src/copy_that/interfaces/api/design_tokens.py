"""Unified design token export (color, spacing, typography)."""

from __future__ import annotations

import math
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.application.typography_recommender import StyleAttributes, TypographyRecommender
from copy_that.domain.models import ColorToken, Project, SpacingToken
from copy_that.infrastructure.database import get_db
from copy_that.services.colors_service import db_colors_to_repo
from copy_that.services.spacing_service import build_spacing_repo_from_db
from core.tokens.adapters.w3c import tokens_to_w3c
from core.tokens.model import RelationType, Token, TokenRelation, TokenType
from core.tokens.repository import InMemoryTokenRepository, TokenRepository

router = APIRouter(
    prefix="/api/v1/design-tokens",
    tags=["design-tokens"],
    responses={404: {"description": "Not found"}},
)


def _sanitize_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _sanitize_json_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_json_value(v) for v in value]
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def _merge_repo(target: TokenRepository, source: TokenRepository) -> None:
    """Copy tokens from `source` into `target`."""
    if hasattr(source, "_tokens"):
        for token in source._tokens.values():  # type: ignore[attr-defined]
            target.upsert_token(token)
        return
    for token_type in TokenType:
        for token in source.find_by_type(token_type):
            target.upsert_token(token)


def _first_color_id(repo: TokenRepository) -> str | None:
    colors = repo.find_by_type(TokenType.COLOR)
    return colors[0].id if colors else None


def _infer_style_from_colors(colors: list[ColorToken], style_hint: str | None) -> StyleAttributes:
    temperature = next(
        (c.temperature for c in colors if getattr(c, "temperature", None)), "neutral"
    )
    saturation = next(
        (c.saturation_level for c in colors if getattr(c, "saturation_level", None)), None
    )
    visual_weight = "heavy" if saturation in {"high", "vibrant"} else "balanced"
    return {
        "primary_style": style_hint or "minimalist",
        "color_temperature": temperature or "neutral",
        "visual_weight": visual_weight,
        "contrast_level": "medium",
    }


def _add_text_alias(repo: TokenRepository, base_color_id: str) -> None:
    repo.upsert_token(
        Token(
            id="color.text.primary",
            type=TokenType.COLOR,
            value=None,
            relations=[TokenRelation(type=RelationType.ALIAS_OF, target=base_color_id)],
            attributes={"role": "text"},
        )
    )


@router.get("/export/w3c")
async def export_design_tokens_w3c(
    project_id: int | None = Query(default=None, description="Optional project scope"),
    style_hint: str | None = Query(default=None, description="Optional style hint for typography"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Export combined design tokens (color, spacing, typography) as W3C JSON."""
    repo = InMemoryTokenRepository()

    # Verify project if provided
    colors: list[ColorToken] = []
    spacing: list[SpacingToken] = []
    if project_id is not None:
        project = await db.get(Project, project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
            )

    # Colors
    color_query = select(ColorToken)
    if project_id is not None:
        color_query = color_query.where(ColorToken.project_id == project_id)
    color_result = await db.execute(color_query)
    colors = list(color_result.scalars().all())
    if colors:
        color_repo = db_colors_to_repo(
            colors,
            namespace=f"token/color/export/project/{project_id}"
            if project_id
            else "token/color/export/all",
        )
        _merge_repo(repo, color_repo)
        base_color_id = _first_color_id(color_repo)
        if base_color_id:
            _add_text_alias(repo, base_color_id)

    # Spacing
    spacing_query = select(SpacingToken)
    if project_id is not None:
        spacing_query = spacing_query.where(SpacingToken.project_id == project_id)
    spacing_result = await db.execute(spacing_query)
    spacing = list(spacing_result.scalars().all())
    if spacing:
        spacing_repo = build_spacing_repo_from_db(
            spacing,
            namespace=f"token/spacing/export/project/{project_id}"
            if project_id
            else "token/spacing/export/all",
        )
        _merge_repo(repo, spacing_repo)

    # Typography recommendations (rule-based MVP)
    style_attributes = _infer_style_from_colors(colors, style_hint)
    typographer = TypographyRecommender()
    recommendation = typographer.recommend_with_confidence(style_attributes)
    typography_tokens = recommendation["tokens"]

    # Ensure the referenced font family token exists to avoid dangling refs
    family_ids = {t.value.get("fontFamily") for t in typography_tokens if isinstance(t.value, dict)}
    for family_id in family_ids:
        if isinstance(family_id, str):
            repo.upsert_token(
                Token(id=family_id, type=TokenType.FONT_FAMILY, value=family_id.split(".")[-1])
            )

    for token in typography_tokens:
        repo.upsert_token(token)

    payload = tokens_to_w3c(repo)
    # Sanitize recommendation fields to avoid propagating unexpected types.
    confidence_raw = recommendation.get("confidence")
    confidence: float | None
    if (
        isinstance(confidence_raw, (int, float))
        and not math.isnan(confidence_raw)
        and not math.isinf(confidence_raw)
    ):
        confidence = float(confidence_raw)
    else:
        confidence = None
    style_attrs_raw = recommendation.get("style_attributes")
    style_attrs: StyleAttributes | dict[str, Any]
    if isinstance(style_attrs_raw, dict):
        style_attrs = style_attrs_raw
    else:
        style_attrs = {}
    payload["meta"] = {
        "typography_recommendation": {
            "style_attributes": style_attrs,
            "confidence": confidence,
        }
    }

    return cast(dict[str, Any], _sanitize_json_value(payload))
