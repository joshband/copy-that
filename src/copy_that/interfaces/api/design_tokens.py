"""Unified design token export (color, spacing, typography)."""

from __future__ import annotations

import json
import math
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from jsonschema import ValidationError  # type: ignore[import-untyped]
from pydantic import BaseModel, Field

from copy_that.application.ports.color_token_records import ColorTokenRepository
from copy_that.application.ports.gradient_tokens import GradientTokenRepository
from copy_that.application.ports.layout_tokens import LayoutTokenRepository
from copy_that.application.ports.projects import ProjectRepository
from copy_that.application.ports.shadow_tokens import ShadowTokenRepository
from copy_that.application.ports.spacing_tokens import SpacingTokenRepository
from copy_that.application.ports.typography_tokens import TypographyTokenRepository
from copy_that.application.typography_recommender import StyleAttributes, TypographyRecommender
from copy_that.core_tokens.adapters.w3c import tokens_to_w3c_flat
from copy_that.core_tokens.model import RelationType, Token, TokenRelation, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository, TokenRepository
from copy_that.design_tokens.validation import validate_w3c_export
from copy_that.domain.color_tokens import ColorToken
from copy_that.generators.plugins import generator_registry
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.auth import get_current_user
from copy_that.interfaces.api.utils import sanitize_json_value
from copy_that.services.colors_service import db_colors_to_repo
from copy_that.services.gradient_service import db_gradients_to_repo
from copy_that.services.layout_service import (
    db_layout_to_repo,
    synthesize_opacity_tokens_from_shadows,
)
from copy_that.services.motion_service import (
    synthesize_gradient_tokens_from_colors,
    synthesize_transition_tokens,
)
from copy_that.services.shadow_service import db_shadows_to_repo
from copy_that.services.spacing_service import build_spacing_repo_from_db
from copy_that.services.type_coverage_service import apply_type_coverage_synthesis
from copy_that.services.typography_recommendation import infer_style_from_colors
from copy_that.services.typography_service import build_typography_repo_from_db

router = APIRouter(
    prefix="/api/v1/design-tokens",
    tags=["design-tokens"],
    responses={404: {"description": "Not found"}},
)


class GeneratorRequest(BaseModel):
    """Request for code generation from TokenGraph + optional component semantics."""

    format: str = Field(
        description="Generator identifier (react, css, w3c)", examples=["react", "css", "w3c"]
    )
    component_meta: dict[str, Any] | None = Field(
        default=None,
        description="Optional component semantics/anatomy metadata for slot binding.",
    )


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


async def _build_export_repo(
    *,
    project_id: int | None,
    project_repo: ProjectRepository,
    color_token_repo: ColorTokenRepository,
    spacing_token_repo: SpacingTokenRepository,
    typography_token_repo: TypographyTokenRepository,
    shadow_token_repo: ShadowTokenRepository,
    layout_token_repo: LayoutTokenRepository | None = None,
    gradient_token_repo: GradientTokenRepository | None = None,
    style_hint: str | None = None,
) -> tuple[TokenRepository, list[ColorToken], bool]:
    """Collect tokens from all repositories into a single TokenRepository."""
    repo = InMemoryTokenRepository()

    colors: list[ColorToken] = []
    if project_id is not None:
        project = await project_repo.get(project_id=project_id)
        if project is None:  # pragma: no cover
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
            )

    colors = await color_token_repo.list_all(project_id=project_id)
    if colors:
        color_export_repo = db_colors_to_repo(
            colors,
            namespace=f"token/color/export/project/{project_id}"
            if project_id
            else "token/color/export/all",
        )
        _merge_repo(repo, color_export_repo)
        base_color_id = _first_color_id(color_export_repo)
        if base_color_id:
            _add_text_alias(repo, base_color_id)

    # Prefer CV/AI extracted gradients before color-pair synth
    gradient_rows: list[Any] = []
    if gradient_token_repo is not None:
        gradient_rows = list(await gradient_token_repo.list_all(project_id=project_id))
        if gradient_rows:
            gradient_export_repo = db_gradients_to_repo(
                gradient_rows,
                namespace=f"token/gradient/export/project/{project_id}"
                if project_id
                else "token/gradient/export/all",
            )
            _merge_repo(repo, gradient_export_repo)

    if colors:
        # Phase 4: skip color-pair synth when CV/AI gradients already on the graph
        for gradient_token in synthesize_gradient_tokens_from_colors(colors, repo=repo):
            repo.upsert_token(gradient_token)

    spacing = await spacing_token_repo.list_all(project_id=project_id)
    if spacing:
        spacing_export_repo = build_spacing_repo_from_db(
            spacing,
            namespace=f"token/spacing/export/project/{project_id}"
            if project_id
            else "token/spacing/export/all",
        )
        _merge_repo(repo, spacing_export_repo)

    shadows = await shadow_token_repo.list_all(project_id=project_id)
    if shadows:
        shadow_export_repo = db_shadows_to_repo(
            shadows,
            namespace=f"token/shadow/export/project/{project_id}"
            if project_id
            else "token/shadow/export/all",
        )
        _merge_repo(repo, shadow_export_repo)
        for opacity_token in synthesize_opacity_tokens_from_shadows(shadows):
            repo.upsert_token(opacity_token)

    layout_rows: list[Any] = []
    if layout_token_repo is not None:
        layout_rows = list(await layout_token_repo.list_all(project_id=project_id))
        if layout_rows:
            layout_export_repo = db_layout_to_repo(
                layout_rows,
                namespace=f"token/layout/export/project/{project_id}"
                if project_id
                else "token/layout/export/all",
            )
            _merge_repo(repo, layout_export_repo)

    typography_db = await typography_token_repo.list_all(project_id=project_id)
    has_typography = bool(typography_db)
    if typography_db:
        typography_export_repo = build_typography_repo_from_db(
            typography_db,
            namespace=f"token/typography/export/project/{project_id}"
            if project_id
            else "token/typography/export/all",
        )
        _merge_repo(repo, typography_export_repo)

    # Phase 5: UI-kit / style-cue motion before presets; presets only fill gaps
    has_any = bool(colors or spacing or shadows or typography_db or layout_rows or gradient_rows)
    if has_any:
        try:
            from copy_that.extractors.motion_extract import upsert_motion_from_repo

            upsert_motion_from_repo(repo, style_hint=style_hint)
        except Exception:
            pass
        for motion_token in synthesize_transition_tokens(repo=repo):
            repo.upsert_token(motion_token)
        # P2c: fill remaining DTCG types (fontFamily, border, transition, …)
        apply_type_coverage_synthesis(
            repo,
            colors=colors,
            typography_rows=typography_db,
            has_any_tokens=True,
        )

    return repo, colors, has_typography


@router.get("/export/w3c")
async def export_design_tokens_w3c(
    project_id: int | None = Query(default=None, description="Optional project scope"),
    style_hint: str | None = Query(default=None, description="Optional style hint for typography"),
    validate: bool = Query(default=False, description="Validate output against W3C schemas"),
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    color_token_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
    spacing_token_repo: SpacingTokenRepository = Depends(deps.get_spacing_repo),
    typography_token_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
    shadow_token_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    layout_token_repo: LayoutTokenRepository = Depends(deps.get_layout_repo),
    gradient_token_repo: GradientTokenRepository = Depends(deps.get_gradient_repo),
) -> dict[str, Any]:
    """Export combined design tokens (color, spacing, typography) as W3C JSON."""
    repo, colors, has_typography = await _build_export_repo(
        project_id=project_id,
        project_repo=project_repo,
        color_token_repo=color_token_repo,
        spacing_token_repo=spacing_token_repo,
        typography_token_repo=typography_token_repo,
        shadow_token_repo=shadow_token_repo,
        layout_token_repo=layout_token_repo,
        gradient_token_repo=gradient_token_repo,
        style_hint=style_hint,
    )

    # Typography recommendations (rule-based MVP)
    style_attributes = infer_style_from_colors(colors, style_hint)
    typographer = TypographyRecommender()
    recommendation = typographer.recommend_with_confidence(style_attributes)
    typography_tokens = recommendation["tokens"]

    if not has_typography:
        # Ensure the referenced font family token exists to avoid dangling refs
        family_ids = {
            t.value.get("fontFamily") for t in typography_tokens if isinstance(t.value, dict)
        }
        for family_id in family_ids:
            if isinstance(family_id, str):
                repo.upsert_token(
                    Token(id=family_id, type=TokenType.FONT_FAMILY, value=family_id.split(".")[-1])
                )

        for token in typography_tokens:
            repo.upsert_token(token)
        # Re-run coverage so recommended typography yields fontFamily/fontWeight/number
        apply_type_coverage_synthesis(
            repo,
            colors=colors,
            typography_rows=[],
            has_any_tokens=True,
        )

    payload = tokens_to_w3c_flat(repo)
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
    sanitized = cast(dict[str, Any], sanitize_json_value(payload))
    if validate:
        payload_for_validation = {k: v for k, v in sanitized.items() if k != "meta"}
        try:
            validate_w3c_export(payload_for_validation, validate_color=True)
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"W3C export failed validation: {exc.message}",
            ) from exc
    return sanitized


@router.get("/export/css")
async def export_design_tokens_css(
    project_id: int | None = Query(default=None, description="Optional project scope"),
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    color_token_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
    spacing_token_repo: SpacingTokenRepository = Depends(deps.get_spacing_repo),
    typography_token_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
    shadow_token_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    layout_token_repo: LayoutTokenRepository = Depends(deps.get_layout_repo),
    gradient_token_repo: GradientTokenRepository = Depends(deps.get_gradient_repo),
) -> dict[str, Any]:
    """Export combined design tokens as CSS custom properties (:root variables).

    Same auth posture as ``/export/w3c`` (no login required) so the MVP Export
    tab can download CSS after a normal extract session.
    """
    from copy_that.generators.plugins.css import CSSGenerator
    from copy_that.guide_pack import build_guide_pack

    repo, _colors, _has_typography = await _build_export_repo(
        project_id=project_id,
        project_repo=project_repo,
        color_token_repo=color_token_repo,
        spacing_token_repo=spacing_token_repo,
        typography_token_repo=typography_token_repo,
        shadow_token_repo=shadow_token_repo,
        layout_token_repo=layout_token_repo,
        gradient_token_repo=gradient_token_repo,
    )
    tokens_flat = tokens_to_w3c_flat(repo)
    pack = build_guide_pack(repo, project_id=project_id)
    content = CSSGenerator(tokens=tokens_flat, component_meta=pack.to_component_meta()).generate()
    return {"format": "css", "content": content, "filename": "tokens.css"}


@router.get("/export/react")
async def export_design_tokens_react(
    project_id: int | None = Query(default=None, description="Optional project scope"),
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    color_token_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
    spacing_token_repo: SpacingTokenRepository = Depends(deps.get_spacing_repo),
    typography_token_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
    shadow_token_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    layout_token_repo: LayoutTokenRepository = Depends(deps.get_layout_repo),
    gradient_token_repo: GradientTokenRepository = Depends(deps.get_gradient_repo),
) -> dict[str, Any]:
    """Export design tokens as a TypeScript theme module.

    Same auth posture as ``/export/css`` (no login required).
    """
    from copy_that.generators.plugins.react import ReactGenerator
    from copy_that.guide_pack import build_guide_pack

    repo, _colors, _has_typography = await _build_export_repo(
        project_id=project_id,
        project_repo=project_repo,
        color_token_repo=color_token_repo,
        spacing_token_repo=spacing_token_repo,
        typography_token_repo=typography_token_repo,
        shadow_token_repo=shadow_token_repo,
        layout_token_repo=layout_token_repo,
        gradient_token_repo=gradient_token_repo,
    )
    tokens_flat = tokens_to_w3c_flat(repo)
    pack = build_guide_pack(repo, project_id=project_id)
    content = ReactGenerator(tokens=tokens_flat, component_meta=pack.to_component_meta()).generate()
    return {"format": "react", "content": content, "filename": "tokens.theme.ts"}


@router.get("/export/tailwind")
async def export_design_tokens_tailwind(
    project_id: int | None = Query(default=None, description="Optional project scope"),
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    color_token_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
    spacing_token_repo: SpacingTokenRepository = Depends(deps.get_spacing_repo),
    typography_token_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
    shadow_token_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    layout_token_repo: LayoutTokenRepository = Depends(deps.get_layout_repo),
    gradient_token_repo: GradientTokenRepository = Depends(deps.get_gradient_repo),
) -> dict[str, Any]:
    """Export design tokens as a Tailwind theme.extend config snippet.

    Same auth posture as ``/export/css`` (no login required).
    """
    from copy_that.generators.plugins.tailwind import TailwindGenerator
    from copy_that.guide_pack import build_guide_pack

    repo, _colors, _has_typography = await _build_export_repo(
        project_id=project_id,
        project_repo=project_repo,
        color_token_repo=color_token_repo,
        spacing_token_repo=spacing_token_repo,
        typography_token_repo=typography_token_repo,
        shadow_token_repo=shadow_token_repo,
        layout_token_repo=layout_token_repo,
        gradient_token_repo=gradient_token_repo,
    )
    tokens_flat = tokens_to_w3c_flat(repo)
    pack = build_guide_pack(repo, project_id=project_id)
    content = TailwindGenerator(
        tokens=tokens_flat, component_meta=pack.to_component_meta()
    ).generate()
    return {"format": "tailwind", "content": content, "filename": "tailwind.theme.js"}


@router.post("/export/generator")
async def generate_tokens(
    request: GeneratorRequest,
    project_id: int | None = Query(default=None, description="Optional project scope"),
    _user=Depends(get_current_user),
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    color_token_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
    spacing_token_repo: SpacingTokenRepository = Depends(deps.get_spacing_repo),
    typography_token_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
    shadow_token_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    layout_token_repo: LayoutTokenRepository = Depends(deps.get_layout_repo),
    gradient_token_repo: GradientTokenRepository = Depends(deps.get_gradient_repo),
) -> dict[str, Any]:
    """Generate code/config from TokenGraph + optional component semantics metadata."""
    # Basic payload guard to avoid huge inlined component metadata
    if request.component_meta:
        meta_bytes = len(json.dumps(request.component_meta))
        if meta_bytes > 50_000:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="component_meta too large; please reduce payload (50KB limit).",
            )

    tokens_repo, _colors, _has_typography = await _build_export_repo(
        project_id=project_id,
        project_repo=project_repo,
        color_token_repo=color_token_repo,
        spacing_token_repo=spacing_token_repo,
        typography_token_repo=typography_token_repo,
        shadow_token_repo=shadow_token_repo,
        layout_token_repo=layout_token_repo,
        gradient_token_repo=gradient_token_repo,
    )
    tokens_flat = tokens_to_w3c_flat(tokens_repo)

    if request.format == "w3c":
        content = json.dumps(tokens_flat, indent=2)
        return {"format": "w3c", "content": content}

    generator_cls = generator_registry.get(request.format)
    if not generator_cls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown generator '{request.format}'. Available: {', '.join(generator_registry.available())}",
        )

    generator = generator_cls(tokens=tokens_flat, component_meta=request.component_meta or {})
    content = generator.generate()
    return {"format": request.format, "content": content}


@router.get("/overview/metrics")
async def get_overview_metrics(
    project_id: int | None = Query(None, description="Optional project to analyze"),
    color_token_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
    spacing_token_repo: SpacingTokenRepository = Depends(deps.get_spacing_repo),
    typography_token_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
    shadow_token_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
) -> dict[str, Any]:
    """Get inferred design system metrics for project overview.

    Analyzes extracted tokens to infer insights about:
    - Spacing scale system (4pt, 8pt, golden ratio, etc.)
    - Color palette characteristics (warm/cool, saturation, harmony)
    - Typography hierarchy depth and scale type
    - Overall design system maturity and organization quality

    Args:
        project_id: Optional project to filter tokens

    Returns:
        Dict with inferred metrics and human-readable insights
    """
    from copy_that.services.overview_metrics_service import infer_metrics

    colors = await color_token_repo.list_all(project_id=project_id)
    spacing = await spacing_token_repo.list_all(project_id=project_id)
    typography = await typography_token_repo.list_all(project_id=project_id)
    shadows = await shadow_token_repo.list_all(project_id=project_id)

    # Infer metrics
    metrics = infer_metrics(colors, spacing, typography, shadows)

    # Helper to convert elaborated metrics to dict
    def elaborated_to_dict(metric):
        if metric is None:
            return None
        return {
            "primary": metric.primary,
            "elaborations": metric.elaborations,
            "confidence": metric.confidence,
        }

    return {
        "spacing_scale_system": metrics.spacing_scale_system,
        "spacing_uniformity": round(metrics.spacing_uniformity, 2),
        "color_harmony_type": metrics.color_harmony_type,
        "color_palette_type": metrics.color_palette_type,
        "color_temperature": metrics.color_temperature,
        "typography_hierarchy_depth": metrics.typography_hierarchy_depth,
        "typography_scale_type": metrics.typography_scale_type,
        "design_system_maturity": metrics.design_system_maturity,
        "token_organization_quality": metrics.token_organization_quality,
        "insights": metrics.insights,
        # NEW: Enhanced elaborated metrics
        "art_movement": elaborated_to_dict(metrics.art_movement),
        "emotional_tone": elaborated_to_dict(metrics.emotional_tone),
        "design_complexity": elaborated_to_dict(metrics.design_complexity),
        "saturation_character": elaborated_to_dict(metrics.saturation_character),
        "temperature_profile": elaborated_to_dict(metrics.temperature_profile),
        "design_system_insight": elaborated_to_dict(metrics.design_system_insight),
        "summary": {
            "total_colors": len(colors),
            "total_spacing": len(spacing),
            "total_typography": len(typography),
            "total_shadows": len(shadows),
        },
        # Source tracking: indicates which token types were extracted
        "source": {
            "has_extracted_colors": len(colors) > 0,
            "has_extracted_spacing": len(spacing) > 0,
            "has_extracted_typography": len(typography) > 0,
        },
    }


async def _guide_pack_for_project(
    *,
    project_id: int | None,
    project_repo: ProjectRepository,
    color_token_repo: ColorTokenRepository,
    spacing_token_repo: SpacingTokenRepository,
    typography_token_repo: TypographyTokenRepository,
    shadow_token_repo: ShadowTokenRepository,
    layout_token_repo: LayoutTokenRepository,
    gradient_token_repo: GradientTokenRepository,
) -> tuple[Any, dict[str, Any]]:
    """Build GuidePack + W3C flat from the same export repo."""
    from copy_that.guide_pack import build_guide_pack
    from copy_that.services.overview_metrics_service import infer_metrics

    repo, colors, _has_typo = await _build_export_repo(
        project_id=project_id,
        project_repo=project_repo,
        color_token_repo=color_token_repo,
        spacing_token_repo=spacing_token_repo,
        typography_token_repo=typography_token_repo,
        shadow_token_repo=shadow_token_repo,
        layout_token_repo=layout_token_repo,
        gradient_token_repo=gradient_token_repo,
    )
    spacing = await spacing_token_repo.list_all(project_id=project_id)
    typography = await typography_token_repo.list_all(project_id=project_id)
    shadows = await shadow_token_repo.list_all(project_id=project_id)
    metrics = infer_metrics(colors, spacing, typography, shadows)

    project_name: str | None = None
    if project_id is not None:
        project = await project_repo.get(project_id=project_id)
        if project is not None:
            project_name = getattr(project, "name", None)

    pack = build_guide_pack(
        repo,
        project_id=project_id,
        project_name=project_name,
        insights=list(getattr(metrics, "insights", []) or []),
        metrics=metrics,
    )
    return pack, tokens_to_w3c_flat(repo)


@router.get("/export/guide-pack")
async def export_guide_pack(
    project_id: int | None = Query(default=None, description="Optional project scope"),
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    color_token_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
    spacing_token_repo: SpacingTokenRepository = Depends(deps.get_spacing_repo),
    typography_token_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
    shadow_token_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    layout_token_repo: LayoutTokenRepository = Depends(deps.get_layout_repo),
    gradient_token_repo: GradientTokenRepository = Depends(deps.get_gradient_repo),
) -> dict[str, Any]:
    """Export Design Guide Pack JSON (foundations + illustrative components)."""
    pack, _flat = await _guide_pack_for_project(
        project_id=project_id,
        project_repo=project_repo,
        color_token_repo=color_token_repo,
        spacing_token_repo=spacing_token_repo,
        typography_token_repo=typography_token_repo,
        shadow_token_repo=shadow_token_repo,
        layout_token_repo=layout_token_repo,
        gradient_token_repo=gradient_token_repo,
    )
    return cast(dict[str, Any], sanitize_json_value(pack.model_dump()))


@router.get("/export/guide-html")
async def export_guide_html(
    project_id: int | None = Query(default=None, description="Optional project scope"),
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    color_token_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
    spacing_token_repo: SpacingTokenRepository = Depends(deps.get_spacing_repo),
    typography_token_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
    shadow_token_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    layout_token_repo: LayoutTokenRepository = Depends(deps.get_layout_repo),
    gradient_token_repo: GradientTokenRepository = Depends(deps.get_gradient_repo),
) -> dict[str, Any]:
    """Export self-contained Design Guide HTML (inline CSS)."""
    from copy_that.guide_pack import render_guide_html

    pack, flat = await _guide_pack_for_project(
        project_id=project_id,
        project_repo=project_repo,
        color_token_repo=color_token_repo,
        spacing_token_repo=spacing_token_repo,
        typography_token_repo=typography_token_repo,
        shadow_token_repo=shadow_token_repo,
        layout_token_repo=layout_token_repo,
        gradient_token_repo=gradient_token_repo,
    )
    content = render_guide_html(pack, w3c_flat=flat)
    filename = (
        f"copy-that-project-{project_id}.guide.html"
        if project_id is not None
        else "copy-that.guide.html"
    )
    return {"format": "guide-html", "content": content, "filename": filename}
