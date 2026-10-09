"""Spacing extraction orchestration and token projection, independent of HTTP routing."""

import base64
import json
import logging
from collections.abc import AsyncGenerator, Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any

import anthropic
import requests

from copy_that.application.execution.async_executor import AsyncExecutor
from copy_that.application.ports.layout_tokens import LayoutTokenRepository
from copy_that.application.ports.spacing_tokens import SpacingTokenRepository
from copy_that.application.spacing_extractor import AISpacingExtractor
from copy_that.application.spacing_models import SpacingExtractionResult, SpacingScale
from copy_that.application.spacing_models import SpacingToken as SpacingTokenModel
from copy_that.core_tokens.adapters.w3c import tokens_to_w3c_flat
from copy_that.core_tokens.model import RelationType, Token, TokenRelation, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository, TokenRepository
from copy_that.core_tokens.spacing import make_spacing_token
from copy_that.domain.spacing_tokens import SpacingTokenCreate
from copy_that.extractors.spacing import utils as su
from copy_that.services.artifact_models import (
    ArtifactBundle,
    ArtifactImage,
    ArtifactJson,
    sanitize_json_value,
)
from copy_that.services.layout_service import tokens_to_creates
from copy_that.services.spacing_models import (
    BatchExtractionResponse,
    BatchSpacingExtractionRequest,
    SpacingCommonValue,
    SpacingExtractionRequest,
    SpacingExtractionResponse,
    SpacingTokenResponse,
)
from copy_that.tokens.spacing.aggregator import SpacingAggregator

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SpacingPipelineDependencies:
    get_extractor: Callable[..., AISpacingExtractor]
    cv_extractor: Callable[..., Any]
    download_image: Callable[[str], tuple[bytes, str]]
    validate_image_url: Callable[[str], str]
    enforce_payload_size: Callable[..., None]
    extract_slot: Callable[..., Any]
    cache: Callable[..., Any]
    input_hash: Callable[..., str]
    track_perf: Callable[..., Any]
    cost_tracker: Any


class SpacingPipelineError(Exception):
    def __init__(self, status_code: int, detail: Any) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"{status_code}: {detail}")


def get_extractor(quality: str = "standard") -> AISpacingExtractor:
    """Get spacing extractor instance."""
    from copy_that.application.quality import QualityTier, spacing_model_for_quality

    tier = QualityTier.from_str(quality)
    return AISpacingExtractor(model=spacing_model_for_quality(tier))


async def _persist_spacing_extraction(
    *,
    spacing_repo: SpacingTokenRepository,
    layout_repo: LayoutTokenRepository,
    project_id: int,
    source_url: str,
    merged: SpacingExtractionResult,
) -> tuple[int, str]:
    """Persist spacing scale + CV shape/layout tokens; return (job_id, namespace)."""
    job_id = await spacing_repo.record_extraction(
        project_id=project_id,
        source_url=source_url,
        tokens=[
            SpacingTokenCreate(
                value_px=t.value_px,
                name=t.name,
                semantic_role=t.semantic_role,
                spacing_type=t.spacing_type.value
                if hasattr(t.spacing_type, "value")
                else t.spacing_type,
                category=t.category,
                confidence=t.confidence,
                usage=json.dumps(t.usage) if t.usage else None,
            )
            for t in merged.tokens
        ],
        result_data={"token_count": len(merged.tokens)},
    )

    namespace = f"token/spacing/project/{project_id}/job/{job_id}"
    shape_tokens = _shape_tokens_from_graph(
        getattr(merged, "token_graph", None), namespace=namespace
    )
    layout_tokens = _layout_tokens_from_spacing(merged, namespace=namespace)
    persistable = tokens_to_creates([*shape_tokens, *layout_tokens])
    if persistable:
        await layout_repo.record_extraction(
            project_id=project_id,
            extraction_job_id=job_id,
            tokens=persistable,
        )
    return job_id, namespace


def _failed_extractors_payload(
    failed: list[tuple[str, str]],
) -> list[dict[str, str]] | None:
    if not failed:
        return None
    return [{"name": name, "error": error} for name, error in failed]


def _spacing_result_from_orchestrated_tokens(
    tokens: list[Any],
    overall_confidence: float,
) -> SpacingExtractionResult:
    """Build a SpacingExtractionResult from orchestrator aggregated tokens."""
    app_tokens: list[SpacingTokenModel] = []
    for token in tokens:
        if isinstance(token, SpacingTokenModel):
            app_tokens.append(token)
        elif hasattr(token, "model_dump"):
            app_tokens.append(SpacingTokenModel.model_validate(token.model_dump()))
        else:
            app_tokens.append(
                SpacingTokenModel(
                    value_px=int(getattr(token, "value_px", 0) or 0),
                    name=str(getattr(token, "name", "spacing")),
                    confidence=float(getattr(token, "confidence", 0.5) or 0.5),
                    semantic_role=getattr(token, "semantic_role", None),
                    extraction_metadata=getattr(token, "extraction_metadata", None),
                )
            )
    values = [t.value_px for t in app_tokens if t.value_px > 0]
    return SpacingExtractionResult(
        tokens=app_tokens,
        scale_system=SpacingScale.CUSTOM,
        base_unit=min(values) if values else 4,
        grid_compliance=0.0,
        extraction_confidence=float(overall_confidence or 0.0),
        unique_values=sorted(set(values)),
        min_spacing=min(values) if values else 0,
        max_spacing=max(values) if values else 0,
    )


def _spacing_attributes(token: Any) -> dict[str, Any]:
    if hasattr(token, "model_dump"):
        data = token.model_dump(exclude_none=True)
    elif is_dataclass(token):
        data = asdict(token)
    else:
        data = {k: v for k, v in vars(token).items() if not k.startswith("_")}
    value_px = data.get("value_px", token.value_px)
    data["value_px"] = value_px
    data.setdefault("value_rem", getattr(token, "value_rem", round(value_px / 16, 4)))
    return data


def _build_spacing_repo(
    tokens: Sequence[Any],
    namespace: str = "token/spacing/api",
    layout_tokens: Sequence[Token] | None = None,
    shape_tokens: Sequence[Token] | None = None,
    elevation_tokens: Sequence[Token] | None = None,
) -> TokenRepository:
    repo = InMemoryTokenRepository()
    for index, token in enumerate(tokens, start=1):
        attributes = _spacing_attributes(token)
        value_px = attributes["value_px"]
        value_rem = attributes["value_rem"]
        repo.upsert_token(
            make_spacing_token(
                f"{namespace}/{index:02d}",
                value_px,
                value_rem,
                attributes,
            )
        )
    for extra in layout_tokens or []:
        repo.upsert_token(extra)
    for extra in shape_tokens or []:
        repo.upsert_token(extra)
    for extra in elevation_tokens or []:
        repo.upsert_token(extra)
    return repo


def _layout_tokens_from_spacing(
    result: SpacingExtractionResult, namespace: str = "token/spacing/api"
) -> list[Token]:
    """
    Heuristic grid/layout tokens derived from clustered spacing values.
    """
    values = result.unique_values or [t.value_px for t in result.tokens]
    values = [v for v in values if v is not None]
    if not values:
        return []
    sorted_vals = sorted(set(values))
    base_unit = result.base_unit or su.detect_base_unit(sorted_vals)
    gutter = sorted_vals[len(sorted_vals) // 2]
    margin = sorted_vals[-1]
    columns = 12

    grid_info = getattr(result, "grid_detection", None) or {}
    gutter = int(grid_info.get("gutter_px", gutter))
    margin_left = int(grid_info.get("margin_left", margin))
    margin_right = int(grid_info.get("margin_right", margin))
    margin = max(margin_left, margin_right, margin)
    columns = int(grid_info.get("columns", columns))

    def _reference_for_value(val: int) -> str | None:
        for idx, token in enumerate(result.tokens, start=1):
            if token.value_px == val:
                return f"{namespace}/{idx:02d}"
        return None

    gutter_ref = _reference_for_value(gutter)
    margin_ref = _reference_for_value(margin)

    tokens: list[Token] = []
    gutter_rel = (
        [TokenRelation(type=RelationType.COMPOSES, target=gutter_ref)] if gutter_ref else []
    )
    margin_rel = (
        [TokenRelation(type=RelationType.COMPOSES, target=margin_ref)] if margin_ref else []
    )
    tokens.append(
        Token(
            id=f"{namespace}/layout/gutter",
            type=TokenType.LAYOUT,
            value={"px": gutter},
            attributes={
                "role": "gutter",
                "$type": "dimension",
                "base_unit": base_unit,
                "spacing_reference": gutter_ref,
            },
            relations=gutter_rel,
        )
    )
    tokens.append(
        Token(
            id=f"{namespace}/layout/margin",
            type=TokenType.LAYOUT,
            value={"px": margin},
            attributes={
                "role": "margin",
                "$type": "dimension",
                "base_unit": base_unit,
                "spacing_reference": margin_ref,
            },
            relations=margin_rel,
        )
    )
    tokens.append(
        Token(
            id=f"{namespace}/layout/gridColumns",
            type="spacing",
            value={"px": columns},
            attributes={"role": "grid_columns"},
        )
    )
    return tokens


def _shape_tokens_from_graph(
    token_graph: Sequence[Mapping[str, Any]] | None, namespace: str = "token/spacing/api"
) -> list[Token]:
    """
    Build layout tokens for border width and corner radius derived from token graph metadata.
    """
    if not token_graph:
        return []
    radius_vals: set[int] = set()
    border_vals: set[int] = set()
    for node in token_graph:
        meta = node.get("meta") or {}
        r = meta.get("corner_radius")
        b = meta.get("border_width")
        try:
            if r is not None:
                radius_vals.add(int(r))
            if b is not None:
                border_vals.add(int(b))
        except Exception:
            continue
    tokens: list[Token] = []
    for idx, val in enumerate(sorted(v for v in radius_vals if v > 0), start=1):
        tokens.append(
            Token(
                id=f"{namespace}/layout/radius/{idx}",
                type=TokenType.LAYOUT,
                value={"radius": val},
                attributes={"role": "corner_radius"},
            )
        )
    for idx, val in enumerate(sorted(v for v in border_vals if v > 0), start=1):
        tokens.append(
            Token(
                id=f"{namespace}/layout/border/{idx}",
                type=TokenType.LAYOUT,
                value={"border": {"width": val}},
                attributes={"role": "border_width"},
            )
        )
    return tokens


def _elevation_tokens_from_result(
    elevation_entries: Sequence[Mapping[str, Any]] | None,
    namespace: str = "token/spacing/api",
) -> list[Token]:
    """
    Convert elevation/shadow entries (id, value, attributes) into Token objects.
    """
    if not elevation_entries:
        return []
    tokens: list[Token] = []
    for idx, entry in enumerate(elevation_entries, start=1):
        tok_id = entry.get("id") or f"{namespace}/elevation/{idx}"
        tokens.append(
            Token(
                id=str(tok_id),
                type=TokenType.SHADOW,
                value=entry.get("value"),
                attributes=entry.get("attributes", {}),
            )
        )
    return tokens


def _spacing_artifacts_from_result(result: SpacingExtractionResult) -> ArtifactBundle:
    """Build an artifact bundle from spacing extraction diagnostics."""
    images: list[ArtifactImage] = []
    json_items: list[ArtifactJson] = []

    overlay = result.debug_overlay
    if not overlay and isinstance(result.debug, dict):
        overlay = result.debug.get("overlay_png_base64")
    if isinstance(overlay, str) and overlay:
        images.append(
            ArtifactImage(
                type="overlay",
                mime="image/png",
                base64=overlay,
                stage="cv",
                description="Spacing overlay with guides",
            )
        )

    if result.cv_gap_diagnostics:
        json_items.append(
            ArtifactJson(
                type="gap-diagnostics",
                payload=sanitize_json_value(result.cv_gap_diagnostics),
                stage="cv",
            )
        )
    if result.gap_clusters:
        json_items.append(
            ArtifactJson(
                type="gap-clusters",
                payload=sanitize_json_value(result.gap_clusters),
                stage="cv",
            )
        )
    if result.grid_detection:
        json_items.append(
            ArtifactJson(
                type="grid-detection",
                payload=sanitize_json_value(result.grid_detection),
                stage="analysis",
            )
        )
    if result.baseline_spacing:
        json_items.append(
            ArtifactJson(
                type="baseline-spacing",
                payload=sanitize_json_value(result.baseline_spacing),
                stage="analysis",
            )
        )

    return ArtifactBundle(images=images, json_=json_items)


def _result_to_response(
    result: SpacingExtractionResult, namespace: str = "token/spacing/api"
) -> SpacingExtractionResponse:
    """Convert extraction result to response model."""
    token_responses = [
        SpacingTokenResponse(
            value_px=t.value_px,
            value_rem=t.value_rem,
            name=t.name,
            confidence=t.confidence,
            semantic_role=t.semantic_role,
            spacing_type=t.spacing_type.value if t.spacing_type else None,
            grid_aligned=t.grid_aligned,
            tailwind_class=t.tailwind_class,
        )
        for t in result.tokens
    ]

    layout_tokens = _layout_tokens_from_spacing(result, namespace=namespace)
    shape_tokens = _shape_tokens_from_graph(
        getattr(result, "token_graph", None), namespace=namespace
    )
    elevation_tokens = _elevation_tokens_from_result(
        getattr(result, "elevation_tokens", None), namespace=namespace
    )
    repo = _build_spacing_repo(
        result.tokens,
        namespace,
        layout_tokens=layout_tokens,
        shape_tokens=shape_tokens,
        elevation_tokens=elevation_tokens,
    )
    component_metrics = getattr(result, "component_spacing_metrics", None) or []
    common_spacings = su.compute_common_spacings(component_metrics)

    return SpacingExtractionResponse(
        tokens=token_responses,
        scale_system=result.scale_system.value,
        base_unit=result.base_unit,
        grid_compliance=result.grid_compliance,
        extraction_confidence=result.extraction_confidence,
        unique_values=result.unique_values,
        min_spacing=result.min_spacing,
        max_spacing=result.max_spacing,
        cv_gap_diagnostics=getattr(result, "cv_gap_diagnostics", None),
        base_alignment=getattr(result, "base_alignment", None),
        cv_gaps_sample=getattr(result, "cv_gaps_sample", None),
        cv_distance_candidates=getattr(result, "cv_distance_candidates", None),
        baseline_spacing=getattr(result, "baseline_spacing", None),
        component_spacing_metrics=component_metrics or None,
        grid_detection=getattr(result, "grid_detection", None),
        debug_overlay=getattr(result, "debug_overlay", None),
        design_tokens=tokens_to_w3c_flat(repo),
        artifacts=_spacing_artifacts_from_result(result),
        common_spacings=[SpacingCommonValue(**item) for item in common_spacings]
        if common_spacings
        else None,
        warnings=getattr(result, "warnings", None),
        spacing_confidence_breakdown=getattr(result, "spacing_confidence_breakdown", None),
        alignment=getattr(result, "alignment", None),
        gap_clusters=getattr(result, "gap_clusters", None),
        token_graph=getattr(result, "token_graph", None),
        fastsam_regions=getattr(result, "fastsam_regions", None),
        fastsam_tokens=getattr(result, "fastsam_tokens", None),
        text_tokens=getattr(result, "text_tokens", None),
        uied_tokens=getattr(result, "uied_tokens", None),
        elevation_tokens=getattr(result, "elevation_tokens", None),
    )


def _normalize_spacing_tokens(
    tokens: list[Any], fallback_scale: Any
) -> tuple[list[SpacingTokenModel], int | None, float | None, Any]:
    """Cluster spacing values and re-label tokens to a normalized scale."""
    values = [t.value_px for t in tokens if getattr(t, "value_px", 0) > 0]
    base_unit: int | None = None
    base_confidence: float | None = None
    normalized_values: list[int] = []
    if values:
        inferred_base, inferred_conf, normalized_values = su.infer_base_spacing_robust(values)
        base_unit = inferred_base
        base_confidence = inferred_conf
    if not normalized_values:
        normalized_values = su.cluster_spacing_values(values, tolerance=0.12)
    if not normalized_values:
        return tokens, None, None, fallback_scale

    scale_system_raw = su.detect_scale_system(normalized_values)
    try:
        scale_system = SpacingScale(scale_system_raw) if scale_system_raw else fallback_scale
    except ValueError:
        scale_system = fallback_scale

    normalized: list[SpacingTokenModel] = []
    for idx, val in enumerate(normalized_values):
        source = min(tokens, key=lambda t: abs(t.value_px - val))
        props, meta = su.compute_all_spacing_properties_with_metadata(val, normalized_values)
        usage = getattr(source, "usage", [])
        if isinstance(usage, str):
            usage = [usage] if usage else []
        src_conf = getattr(source, "confidence", None)
        try:
            confidence = float(src_conf) if src_conf is not None else 0.6
        except (TypeError, ValueError):
            confidence = 0.6
        normalized.append(
            SpacingTokenModel(
                value_px=val,
                name=source.name or f"spacing-{idx}",
                semantic_role=source.semantic_role,
                spacing_type=source.spacing_type,
                category=source.category or "merged",
                confidence=confidence,
                usage=usage,
            )
        )

    return normalized, base_unit, base_confidence, scale_system


def _cv_spacing_is_fallback(cv: SpacingExtractionResult) -> bool:
    """True when CV could not measure gaps and returned the 4pt preset."""
    breakdown = getattr(cv, "spacing_confidence_breakdown", None) or {}
    if isinstance(breakdown, dict) and float(breakdown.get("fallback") or 0) >= 1:
        return True
    warnings = getattr(cv, "warnings", None) or []
    return any("fallback" in str(w).lower() for w in warnings)


def _merged_spacing_confidence(
    cv: SpacingExtractionResult, ai: SpacingExtractionResult
) -> tuple[float, float | None, dict[str, float] | None]:
    """Prefer measured CV scores; never let AI inflate a CV fallback."""
    breakdown = getattr(cv, "spacing_confidence_breakdown", None) or getattr(
        ai, "spacing_confidence_breakdown", None
    )
    cv_conf = float(getattr(cv, "extraction_confidence", 0) or 0)
    ai_conf = float(getattr(ai, "extraction_confidence", 0) or 0)
    cv_base = getattr(cv, "base_unit_confidence", None)
    ai_base = getattr(ai, "base_unit_confidence", None)
    base: float | None

    if _cv_spacing_is_fallback(cv):
        conf = cv_conf if cv_conf > 0 else 0.15
        base = float(cv_base) if cv_base is not None else conf
        return (
            conf,
            base,
            getattr(cv, "spacing_confidence_breakdown", None)
            or {
                "measurement_confidence": 0.0,
                "grid_confidence": 0.0,
                "semantic_confidence": 0.0,
                "overall": conf,
                "fallback": 1.0,
            },
        )

    if cv_conf > 0:
        conf = cv_conf
        base = (
            float(cv_base)
            if cv_base is not None
            else (float(ai_base) if ai_base is not None else None)
        )
    else:
        conf = ai_conf
        base = float(ai_base) if ai_base is not None else None
    return conf, base, breakdown


def _merge_spacing(
    cv: SpacingExtractionResult, ai: SpacingExtractionResult
) -> SpacingExtractionResult:
    """Merge AI tokens onto CV tokens by value/name to avoid duplicates."""
    ai_by_value = {(t.value_px, t.name): t for t in ai.tokens}
    merged_tokens = list(ai.tokens)
    for t in cv.tokens:
        key = (t.value_px, t.name)
        if key not in ai_by_value:
            merged_tokens.append(t)

    normalized_tokens, base_unit, base_confidence, scale_system = _normalize_spacing_tokens(
        merged_tokens, ai.scale_system or cv.scale_system
    )

    grid_compliance = sum(1 for t in normalized_tokens if getattr(t, "grid_aligned", False)) / max(
        len(normalized_tokens), 1
    )

    unique_values = sorted({t.value_px for t in normalized_tokens})

    merged_warnings = []
    for source in (ai, cv):
        source_warnings = getattr(source, "warnings", None) or []
        merged_warnings.extend([w for w in source_warnings if w])

    extraction_confidence, preferred_base_conf, confidence_breakdown = _merged_spacing_confidence(
        cv, ai
    )
    if preferred_base_conf is not None:
        base_confidence = preferred_base_conf

    fastsam_regions = getattr(cv, "fastsam_regions", None) or getattr(ai, "fastsam_regions", None)
    fastsam_tokens = getattr(cv, "fastsam_tokens", None) or getattr(ai, "fastsam_tokens", None)
    debug_overlay = getattr(ai, "debug_overlay", None) or getattr(cv, "debug_overlay", None)
    alignment = getattr(ai, "alignment", None) or getattr(cv, "alignment", None)
    gap_clusters = getattr(ai, "gap_clusters", None) or getattr(cv, "gap_clusters", None)
    token_graph = getattr(ai, "token_graph", None) or getattr(cv, "token_graph", None)
    cv_distance_candidates = getattr(cv, "cv_distance_candidates", None) or getattr(
        ai, "cv_distance_candidates", None
    )
    text_tokens = getattr(ai, "text_tokens", None) or getattr(cv, "text_tokens", None)
    uied_tokens = getattr(ai, "uied_tokens", None) or getattr(cv, "uied_tokens", None)

    return SpacingExtractionResult(
        tokens=normalized_tokens,
        scale_system=scale_system or ai.scale_system or cv.scale_system,
        base_unit=base_unit or ai.base_unit or cv.base_unit,
        base_unit_confidence=base_confidence or ai.base_unit_confidence or cv.base_unit_confidence,
        grid_compliance=grid_compliance or ai.grid_compliance or cv.grid_compliance,
        extraction_confidence=extraction_confidence,
        unique_values=unique_values,
        min_spacing=min(unique_values) if unique_values else ai.min_spacing or cv.min_spacing,
        max_spacing=max(unique_values) if unique_values else ai.max_spacing or cv.max_spacing,
        cv_gap_diagnostics=ai.cv_gap_diagnostics or cv.cv_gap_diagnostics,
        base_alignment=ai.base_alignment or cv.base_alignment,
        cv_gaps_sample=ai.cv_gaps_sample or cv.cv_gaps_sample,
        cv_distance_candidates=cv_distance_candidates,
        baseline_spacing=ai.baseline_spacing or cv.baseline_spacing,
        component_spacing_metrics=ai.component_spacing_metrics or cv.component_spacing_metrics,
        grid_detection=ai.grid_detection or cv.grid_detection,
        warnings=merged_warnings or None,
        spacing_confidence_breakdown=confidence_breakdown,
        fastsam_regions=fastsam_regions,
        fastsam_tokens=fastsam_tokens,
        token_graph=token_graph,
        debug_overlay=debug_overlay,
        alignment=alignment,
        gap_clusters=gap_clusters,
        text_tokens=text_tokens,
        uied_tokens=uied_tokens,
    )


async def _extract_cv_from_url(
    url: str,
    max_tokens: int,
    expected_base_px: int | None,
    async_executor: AsyncExecutor,
    dependencies: SpacingPipelineDependencies,
) -> tuple[SpacingExtractionResult, str, str]:
    data, content_type = await async_executor.run(lambda: dependencies.download_image(url))
    extractor = dependencies.cv_extractor(max_tokens=max_tokens, expected_base_px=expected_base_px)
    cv_result = await async_executor.run(lambda: extractor.extract_from_bytes(data))
    return (cv_result, base64.b64encode(data).decode("utf-8"), content_type)


async def _image_bytes_from_spacing_request(
    request: SpacingExtractionRequest,
    async_executor: AsyncExecutor,
    dependencies: SpacingPipelineDependencies,
) -> tuple[bytes, str]:
    """Resolve image bytes + media type from URL or base64."""
    if request.image_base64:
        payload = request.image_base64
        if "," in payload:
            payload = payload.split(",", 1)[1]
        return (base64.b64decode(payload), request.image_media_type or "image/png")
    if request.image_url:
        data, content_type = await async_executor.run(
            lambda: dependencies.download_image(str(request.image_url))
        )
        return (data, content_type)
    raise SpacingPipelineError(status_code=400, detail="Provide image_url or image_base64")


async def extract_single(
    request: SpacingExtractionRequest,
    spacing_repo: SpacingTokenRepository,
    layout_repo: LayoutTokenRepository,
    async_executor: AsyncExecutor,
    dependencies: SpacingPipelineDependencies,
) -> SpacingExtractionResponse:
    dependencies.enforce_payload_size(request.image_base64)
    async with dependencies.extract_slot():
        extractor = dependencies.get_extractor(request.quality)
    cv_b64 = None
    media_type = request.image_media_type or "image/png"
    if request.image_base64:
        cv_b64 = request.image_base64
        cv_result = await async_executor.run(
            lambda: dependencies.cv_extractor(
                max_tokens=request.max_tokens, expected_base_px=request.expected_base_px
            ).extract_from_base64(request.image_base64 or "")
        )
    elif request.image_url:
        cv_result, cv_b64, media_type = await _extract_cv_from_url(
            str(request.image_url),
            request.max_tokens,
            request.expected_base_px,
            async_executor,
            dependencies,
        )
    else:
        raise SpacingPipelineError(status_code=400, detail="Provide image_url or image_base64")
    try:
        ai_result = await async_executor.run(
            lambda: extractor.extract_spacing_from_base64(
                request.image_base64 or cv_b64 or "", media_type, request.max_tokens
            )
        )
        merged = _merge_spacing(cv_result, ai_result)
    except (anthropic.APIError, requests.RequestException) as e:
        logger.warning("AI spacing refinement failed, using CV only: %s", e)
        merged = cv_result
    project_id = request.project_id or 0
    job_id, namespace = await _persist_spacing_extraction(
        spacing_repo=spacing_repo,
        layout_repo=layout_repo,
        project_id=project_id,
        source_url=str(request.image_url) if request.image_url else "base64_upload",
        merged=merged,
    )
    return _result_to_response(merged, namespace=namespace)


async def extract_multi(
    request: SpacingExtractionRequest,
    spacing_repo: SpacingTokenRepository,
    layout_repo: LayoutTokenRepository,
    async_executor: AsyncExecutor,
    dependencies: SpacingPipelineDependencies,
) -> SpacingExtractionResponse:
    from copy_that.extractors.spacing.adapters import (
        AISpacingExtractorAdapter,
        CVSpacingExtractorAdapter,
    )
    from copy_that.extractors.spacing.orchestrator import (
        SpacingAggregator as OrchestratorSpacingAggregator,
    )
    from copy_that.extractors.spacing.orchestrator import SpacingExtractionOrchestrator

    dependencies.enforce_payload_size(request.image_base64)
    image_bytes, _media = await _image_bytes_from_spacing_request(
        request, async_executor, dependencies
    )
    extractors = [
        CVSpacingExtractorAdapter(max_tokens=request.max_tokens),
        AISpacingExtractorAdapter(max_tokens=request.max_tokens),
    ]
    orchestrator = SpacingExtractionOrchestrator(
        extractors=extractors,
        aggregator=OrchestratorSpacingAggregator(pixel_distance_threshold=4.0),
    )
    import uuid

    image_id = f"spacing_multi_{uuid.uuid4().hex[:8]}"
    async with dependencies.extract_slot():
        result = await orchestrator.extract_all_safe(image_bytes, image_id)
    merged = _spacing_result_from_orchestrated_tokens(
        result.aggregated_tokens, result.overall_confidence
    )
    project_id = request.project_id or 0
    job_id, namespace = await _persist_spacing_extraction(
        spacing_repo=spacing_repo,
        layout_repo=layout_repo,
        project_id=project_id,
        source_url=str(request.image_url) if request.image_url else "base64_upload",
        merged=merged,
    )
    response = _result_to_response(merged, namespace=namespace)
    return response.model_copy(
        update={
            "extractor_used": "multi-extractor-orchestrator",
            "failed_extractors": _failed_extractors_payload(result.failed_extractors),
        }
    )


async def extract_batch(
    request: BatchSpacingExtractionRequest,
    async_executor: AsyncExecutor,
    dependencies: SpacingPipelineDependencies,
) -> BatchExtractionResponse:
    extractor = dependencies.get_extractor()
    all_tokens = []
    for url in request.image_urls:
        try:
            safe_url = dependencies.validate_image_url(str(url))
            cv_result, _, _ = await _extract_cv_from_url(
                safe_url, request.max_tokens, None, async_executor, dependencies
            )
            ai_result = await async_executor.run(
                lambda u=safe_url: extractor.extract_spacing_from_image_url(u, request.max_tokens)
            )
            merged = _merge_spacing(cv_result, ai_result)
            all_tokens.append(merged.tokens)
        except (anthropic.APIError, requests.RequestException) as e:
            logger.warning("Batch spacing extraction failed for %s: %s", url, e)
            continue
    library = SpacingAggregator.aggregate_batch(all_tokens, request.similarity_threshold)
    library = SpacingAggregator.suggest_token_roles(library)
    token_responses = [
        SpacingTokenResponse(
            value_px=t.value_px,
            value_rem=t.value_rem,
            name=t.name,
            confidence=t.confidence,
            semantic_role=t.semantic_role,
            spacing_type=t.spacing_type,
            role=t.role,
            grid_aligned=t.grid_aligned,
        )
        for t in library.tokens
    ]
    repo = _build_spacing_repo(library.tokens, namespace="token/spacing/batch/library")
    return BatchExtractionResponse(
        tokens=token_responses,
        statistics=library.statistics,
        design_tokens=tokens_to_w3c_flat(repo),
    )


async def stream_events(
    request: SpacingExtractionRequest,
    safe_url: str,
    spacing_repo: SpacingTokenRepository,
    layout_repo: LayoutTokenRepository,
    async_executor: AsyncExecutor,
    session: Any,
    cost_headers: dict[str, str],
    dependencies: SpacingPipelineDependencies,
) -> AsyncGenerator[tuple[str, dict[str, Any]], None]:
    empty_artifacts = ArtifactBundle().model_dump(by_alias=True)
    try:
        extractor = dependencies.get_extractor(request.quality)
        cost_state = dependencies.cost_tracker.record(project_id=request.project_id, amount=0.02)
        if cost_state.blocked:
            raise SpacingPipelineError(
                status_code=402,
                detail={
                    "error": "Cost quota exceeded",
                    "total": cost_state.total,
                    "hard_limit": cost_state.hard_limit,
                    "window": cost_state.window,
                },
            )
        if cost_state.warned:
            cost_headers["X-Cost-Warning"] = (
                f"Soft limit nearing: ${cost_state.total:.2f}/${cost_state.soft_limit:.2f}"
            )
        cost_headers["X-Cost-Usage"] = f"{cost_state.total:.2f}"
        await dependencies.cost_tracker.persist(
            session, project_id=request.project_id, state=cost_state
        )
        yield (
            "progress",
            {
                "status": "started",
                "progress": 0.0,
                "message": "Starting extraction...",
                "artifacts": empty_artifacts,
            },
        )
        yield (
            "progress",
            {
                "status": "downloading",
                "progress": 0.2,
                "message": "Downloading image...",
                "artifacts": empty_artifacts,
            },
        )
        yield (
            "progress",
            {
                "status": "analyzing",
                "progress": 0.4,
                "message": "Analyzing spacing (CV + AI)...",
                "artifacts": empty_artifacts,
            },
        )
        cache_namespace = f"project:{request.project_id}"
        cache = dependencies.cache()
        input_hash = dependencies.input_hash(
            None,
            safe_url,
            {
                "max_tokens": request.max_tokens,
                "extractor": "spacing_openai",
                "quality": request.quality,
            },
        )
        with dependencies.track_perf(
            "upload.first_token",
            {"extractor": "spacing_openai", "image_url": safe_url},
            measure_memory=True,
        ):
            cached = cache.get("spacing.full", input_hash, cache_namespace)
            if cached:
                result = SpacingExtractionResult.model_validate(cached)
            else:
                cv_result, cv_b64, media_type = await _extract_cv_from_url(
                    safe_url,
                    request.max_tokens,
                    request.expected_base_px,
                    async_executor,
                    dependencies,
                )
                try:
                    ai_result = await async_executor.run(
                        lambda: extractor.extract_spacing_from_base64(
                            cv_b64, media_type, request.max_tokens
                        )
                    )
                    result = _merge_spacing(cv_result, ai_result)
                except (anthropic.APIError, requests.RequestException) as e:
                    logger.warning(
                        "AI spacing refinement failed in streaming, using CV only: %s", e
                    )
                    result = cv_result
        yield (
            "progress",
            {
                "status": "processing",
                "progress": 0.8,
                "message": "Processing tokens...",
                "artifacts": empty_artifacts,
            },
        )
        project_id = request.project_id or 0
        job_id, namespace = await _persist_spacing_extraction(
            spacing_repo=spacing_repo,
            layout_repo=layout_repo,
            project_id=project_id,
            source_url=safe_url,
            merged=result,
        )
        for token in result.tokens:
            yield (
                "token",
                {
                    "value_px": token.value_px,
                    "name": token.name,
                    "confidence": token.confidence,
                    "artifacts": empty_artifacts,
                },
            )
        response = _result_to_response(result, namespace=namespace)
        yield ("complete", {**response.model_dump(), "job_id": job_id, "project_id": project_id})
    except Exception as e:
        logger.exception("Streaming extraction failed")
        error_type = "HTTPException" if isinstance(e, SpacingPipelineError) else type(e).__name__
        yield ("error", {"message": str(e), "type": error_type, "artifacts": empty_artifacts})
