"""Color extraction orchestration and payload construction independent of HTTP."""

from __future__ import annotations

import base64
import inspect
import json
import logging
from collections.abc import AsyncIterator, Callable, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

import requests

from copy_that.application.color_science_artifacts import build_color_science_artifacts
from copy_that.application.cost_tracker import cost_tracker
from copy_that.application.perf import track_perf
from copy_that.application.ports.color_token_records import ColorTokenRepository
from copy_that.core_tokens.adapters.w3c import tokens_to_w3c_flat
from copy_that.core_tokens.color import make_color_ramp, ramp_to_dict
from copy_that.core_tokens.model import Token
from copy_that.core_tokens.repository import InMemoryTokenRepository, TokenRepository
from copy_that.domain.color_tokens import ColorTokenCreate
from copy_that.extractors.color.adapters import CVColorExtractorAdapter, KMeansColorExtractorAdapter
from copy_that.extractors.color.cv_extractor import CVColorExtractor
from copy_that.extractors.color.extractor import ColorExtractionResult, ExtractedColorToken
from copy_that.extractors.color.orchestrator import MultiExtractorOrchestrator
from copy_that.infrastructure.cache.extraction_cache import compute_input_hash, get_extraction_cache
from copy_that.services.artifact_models import (
    ArtifactBundle,
    ArtifactImage,
    ArtifactJson,
    sanitize_json_value,
)
from copy_that.services.colors_service import (
    add_colors_to_repo as _add_colors_to_repo,
)
from copy_that.services.colors_service import (
    add_role_tokens,
    default_shadow_tokens,
    find_accent_hex,
    get_extractor,
    parse_metadata,
    post_process_colors,
)
from copy_that.tokens.color.aggregator import ColorAggregator

logger = logging.getLogger(__name__)


class ColorExtractionInput(Protocol):
    project_id: int
    image_url: str | None
    image_base64: str | None
    max_colors: int
    extractor: str | None
    include_science_artifacts: bool


class ColorBatchInput(Protocol):
    image_urls: list[str]
    project_id: int | None
    max_colors: int
    include_science_artifacts: bool


@dataclass(frozen=True)
class ColorPipelineDependencies:
    """Factories injected at the boundary for extractor and infrastructure selection."""

    get_extractor: Callable[[str], tuple[Any, str]] = get_extractor
    cv_extractor: Callable[..., Any] = CVColorExtractor
    get_cache: Callable[..., Any] = get_extraction_cache
    cost_tracker: Any = cost_tracker
    kmeans_adapter: Callable[..., Any] = KMeansColorExtractorAdapter
    cv_adapter: Callable[..., Any] = CVColorExtractorAdapter
    aggregator: Callable[..., Any] = ColorAggregator
    orchestrator: Callable[..., Any] = MultiExtractorOrchestrator


class ColorQuotaExceeded(Exception):
    def __init__(self, detail: dict[str, Any]) -> None:
        self.detail = detail
        super().__init__(f"402: {detail}")


def _add_color_ramps(
    repo: TokenRepository, colors: Sequence[Any], namespace: str
) -> dict[str, Token]:
    """Add accent ramps to the repo; return the created tokens."""
    accent_hex = find_accent_hex(colors)
    if not accent_hex:
        return {}
    ramp_tokens = make_color_ramp(accent_hex, prefix=f"{namespace}/accent")
    for tok in ramp_tokens.values():
        repo.upsert_token(tok)
    return ramp_tokens


def _color_artifacts_from_debug(debug: dict[str, Any] | None) -> ArtifactBundle:
    """Build an artifact bundle from extractor debug payloads."""
    images: list[ArtifactImage] = []
    json_items: list[ArtifactJson] = []
    if not isinstance(debug, dict):
        return ArtifactBundle(images=images, json_=json_items)

    normalized = debug.get("normalized_rgb_base64")
    if isinstance(normalized, str) and normalized:
        images.append(
            ArtifactImage(
                type="normalized-rgb",
                mime="image/png",
                base64=normalized,
                stage="ingest",
                description="Orientation-corrected, downsampled RGB input",
            )
        )

    gray_blur = debug.get("gray_blur_base64")
    if isinstance(gray_blur, str) and gray_blur:
        images.append(
            ArtifactImage(
                type="gray-blur",
                mime="image/png",
                base64=gray_blur,
                stage="ingest",
                description="Blurred grayscale view used for edge cues",
            )
        )

    overlay = debug.get("overlay_png_base64")
    if isinstance(overlay, str) and overlay:
        images.append(
            ArtifactImage(
                type="overlay",
                mime="image/png",
                base64=overlay,
                stage="cv",
                description="Superpixel + palette overlay",
            )
        )

    edge_map = debug.get("edge_map_base64")
    if isinstance(edge_map, str) and edge_map:
        images.append(
            ArtifactImage(
                type="edge-map",
                mime="image/png",
                base64=edge_map,
                stage="cv",
                description="Canny edge map for segmentation cues",
            )
        )

    quantized = debug.get("quantized_base64")
    if isinstance(quantized, str) and quantized:
        images.append(
            ArtifactImage(
                type="quantized",
                mime="image/png",
                base64=quantized,
                stage="cv",
                description="Quantized preview for palette simplification",
            )
        )

    superpixel_boundaries = debug.get("superpixel_boundaries_png_base64")
    if isinstance(superpixel_boundaries, str) and superpixel_boundaries:
        images.append(
            ArtifactImage(
                type="superpixel-boundaries",
                mime="image/png",
                base64=superpixel_boundaries,
                stage="cv",
                description="Superpixel boundary map",
            )
        )

    palette_assignment = debug.get("palette_assignment_png_base64")
    if isinstance(palette_assignment, str) and palette_assignment:
        images.append(
            ArtifactImage(
                type="palette-assignment",
                mime="image/png",
                base64=palette_assignment,
                stage="cv",
                description="Palette assignment by superpixel",
            )
        )

    palette_strip = debug.get("palette_strip_png_base64")
    if isinstance(palette_strip, str) and palette_strip:
        images.append(
            ArtifactImage(
                type="palette-strip",
                mime="image/png",
                base64=palette_strip,
                stage="analysis",
                description="Palette swatch strip",
            )
        )

    palette_histogram_img = debug.get("palette_histogram_png_base64")
    if isinstance(palette_histogram_img, str) and palette_histogram_img:
        images.append(
            ArtifactImage(
                type="palette-histogram",
                mime="image/png",
                base64=palette_histogram_img,
                stage="analysis",
                description="Palette prominence histogram",
            )
        )

    bg_overlay = debug.get("background_samples_overlay_base64")
    if isinstance(bg_overlay, str) and bg_overlay:
        images.append(
            ArtifactImage(
                type="background-samples",
                mime="image/png",
                base64=bg_overlay,
                stage="cv",
                description="Background sampling patches",
            )
        )

    segmented = debug.get("segmented_palette")
    if segmented:
        json_items.append(
            ArtifactJson(
                type="segmented-palette",
                payload={"segments": sanitize_json_value(segmented)},
                stage="cv",
            )
        )

    palette_histogram = debug.get("palette_histogram")
    if palette_histogram:
        json_items.append(
            ArtifactJson(
                type="palette-histogram",
                payload={"entries": sanitize_json_value(palette_histogram)},
                stage="analysis",
            )
        )

    superpixel_stats = debug.get("superpixel_stats")
    if superpixel_stats:
        json_items.append(
            ArtifactJson(
                type="superpixel-stats",
                payload=sanitize_json_value(superpixel_stats),
                stage="cv",
            )
        )

    histograms = debug.get("histograms")
    if histograms:
        json_items.append(
            ArtifactJson(
                type="histograms",
                payload=sanitize_json_value(histograms),
                stage="analysis",
            )
        )

    hue_distribution = debug.get("hue_distribution")
    if hue_distribution:
        json_items.append(
            ArtifactJson(
                type="hue-distribution",
                payload=sanitize_json_value(hue_distribution),
                stage="analysis",
            )
        )

    dominant_regions = debug.get("dominant_regions")
    if dominant_regions:
        json_items.append(
            ArtifactJson(
                type="dominant-regions",
                payload={"regions": sanitize_json_value(dominant_regions)},
                stage="analysis",
            )
        )

    image_properties = debug.get("image_properties")
    if image_properties:
        json_items.append(
            ArtifactJson(
                type="image-properties",
                payload=sanitize_json_value(image_properties),
                stage="analysis",
            )
        )

    background_samples = debug.get("background_samples")
    if background_samples:
        json_items.append(
            ArtifactJson(
                type="background-samples",
                payload=sanitize_json_value(background_samples),
                stage="cv",
            )
        )

    contrast = debug.get("contrast_matrix")
    if contrast:
        json_items.append(
            ArtifactJson(
                type="contrast-matrix",
                payload=sanitize_json_value(contrast),
                stage="analysis",
            )
        )

    return ArtifactBundle(images=images, json_=json_items)


def _color_science_artifacts_from_colors(
    colors: Sequence[ExtractedColorToken],
    *,
    max_colors: int | None = None,
) -> ArtifactBundle:
    """Build palette-level color science artifacts from extracted colors."""
    effective_max_colors = max_colors if max_colors is not None else len(colors) or 10
    science = build_color_science_artifacts(colors, max_colors=effective_max_colors)
    images = [
        ArtifactImage(
            type=item["type"],
            mime="image/png",
            base64=item["base64"],
            stage="science",
            description=item.get("description"),
        )
        for item in science.images
    ]
    json_items = [
        ArtifactJson(
            type=item["type"],
            payload=sanitize_json_value(item["payload"]),
            stage="science",
        )
        for item in science.json
    ]
    return ArtifactBundle(images=images, json_=json_items)


def _merge_artifact_bundles(*bundles: ArtifactBundle | None) -> ArtifactBundle:
    images: list[ArtifactImage] = []
    json_items: list[ArtifactJson] = []
    for bundle in bundles:
        if bundle is None:
            continue
        images.extend(bundle.images)
        json_items.extend(bundle.json_)
    return ArtifactBundle(images=images, json_=json_items)


def _select_debug_payload(*results: ColorExtractionResult | None) -> dict[str, Any] | None:
    """Prefer the first non-empty debug payload from extraction results."""
    for result in results:
        debug = getattr(result, "debug", None)
        if isinstance(debug, dict) and debug:
            return debug
    return None


def color_result_payload(
    result: ColorExtractionResult,
    namespace: str = "token/color/api",
    *,
    science_artifacts: ArtifactBundle | None = None,
) -> dict[str, Any]:
    """Build API response from extraction result."""
    repo = InMemoryTokenRepository()
    _add_colors_to_repo(repo, result.colors, namespace)
    add_role_tokens(repo, namespace, result.background_colors)
    _add_color_ramps(repo, result.colors, namespace)
    debug_bundle = _color_artifacts_from_debug(getattr(result, "debug", None))
    artifacts = (
        _merge_artifact_bundles(debug_bundle, science_artifacts)
        if science_artifacts
        else debug_bundle
    )
    return {
        "colors": [color.model_dump() for color in result.colors],
        "dominant_colors": result.dominant_colors,
        "color_palette": result.color_palette,
        "extraction_confidence": result.extraction_confidence,
        "extractor_used": result.extractor_used,
        "design_tokens": tokens_to_w3c_flat(repo),
        "artifacts": artifacts.model_dump(by_alias=True),
    }


def _safe_str(value: Any) -> str:
    """Coerce arbitrary objects (including MagicMock) to string safely."""
    try:
        return "" if value is None else str(value)
    except Exception:
        return ""


def _json_or_none(value: Any) -> str | None:
    """Serialize common JSON-ish values, returning None for empty containers."""
    if value is None:
        return None
    if isinstance(value, (list, dict)) and not value:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, default=str)


def _palette_records(colors: Sequence[ExtractedColorToken]) -> list[ColorTokenCreate]:
    """Serialize the minimal records persisted by single and batch extraction."""
    return [
        ColorTokenCreate(
            hex=color.hex,
            rgb=color.rgb,
            hsl=None,
            hsv=None,
            name=color.name,
            design_intent=color.design_intent,
            semantic_names=_json_or_none(color.semantic_names),
            extraction_metadata=_json_or_none(color.extraction_metadata),
            category=None,
            confidence=float(color.confidence or 0.0),
            harmony=color.harmony,
            temperature=None,
            saturation_level=None,
            lightness_level=None,
            usage=_json_or_none(color.usage),
            count=1,
            prominence_percentage=None,
            wcag_contrast_on_white=None,
            wcag_contrast_on_black=None,
            wcag_aa_compliant_text=None,
            wcag_aaa_compliant_text=None,
            wcag_aa_compliant_normal=None,
            wcag_aaa_compliant_normal=None,
            colorblind_safe=None,
            tint_color=None,
            shade_color=None,
            tone_color=None,
            closest_web_safe=None,
            closest_css_named=None,
            delta_e_to_dominant=None,
            is_neutral=None,
            background_role=None,
            foreground_role=None,
            contrast_category=None,
            harmony_confidence=None,
            hue_angles=None,
            is_accent=None,
            state_variants=None,
            kmeans_cluster_id=None,
            sam_segmentation_mask=None,
            clip_embeddings=None,
            histogram_significance=None,
            library_id=None,
            role=None,
            provenance=None,
        )
        for color in colors
    ]


async def extract_color_payload(
    request: ColorExtractionInput,
    color_repo: ColorTokenRepository,
    dependencies: ColorPipelineDependencies,
) -> dict[str, Any]:
    # CV-first fast pass
    cv_result = None
    if request.image_base64:
        cv_result = dependencies.cv_extractor(max_colors=request.max_colors).extract_from_base64(
            request.image_base64
        )
    elif request.image_url:
        try:
            # Download and convert to base64 for CV extractor
            resp = requests.get(request.image_url, timeout=10)
            resp.raise_for_status()
            import base64

            cv_b64 = base64.b64encode(resp.content).decode("utf-8")
            cv_result = dependencies.cv_extractor(
                max_colors=request.max_colors
            ).extract_from_base64(cv_b64)
        except requests.RequestException as e:
            logger.debug("CV pre-pass skipped - failed to fetch image: %s", e)
            cv_result = None

    # AI refinement
    extractor, extractor_name = dependencies.get_extractor(request.extractor or "auto")
    if request.image_base64:
        ai_result = extractor.extract_colors_from_base64(
            request.image_base64, media_type="image/png", max_colors=request.max_colors
        )
    else:
        ai_result = extractor.extract_colors_from_image_url(
            request.image_url, max_colors=request.max_colors
        )

    # Merge CV + AI
    merged_colors = []
    ai_by_hex = {c.hex.lower(): c for c in ai_result.colors}
    cv_by_hex = {c.hex.lower(): c for c in cv_result.colors} if cv_result else {}
    seen = set()
    for hx, tok in ai_by_hex.items():
        merged_colors.append(tok)
        seen.add(hx)
    for hx, tok in cv_by_hex.items():
        if hx in seen:
            continue
        merged_colors.append(tok)

    processed_colors, backgrounds = post_process_colors(
        merged_colors, ai_result.dominant_colors if ai_result else None
    )

    # Normalize possibly mocked fields into concrete types
    palette_source = ai_result if ai_result else cv_result
    color_palette = _safe_str(getattr(palette_source, "color_palette", ""))
    extractor_used = _safe_str(
        extractor_name or getattr(palette_source, "extractor_used", extractor_name)
    )
    dominant_colors = list(
        getattr(palette_source, "dominant_colors", [])
        or (cv_result.dominant_colors if cv_result else [])
    )
    try:
        extraction_confidence = float(getattr(palette_source, "extraction_confidence", 0.0) or 0.0)
    except (ValueError, TypeError):
        extraction_confidence = 0.0

    debug_payload = _select_debug_payload(cv_result, ai_result)
    extraction_result = ColorExtractionResult(
        colors=processed_colors,
        dominant_colors=dominant_colors,
        color_palette=color_palette,
        extraction_confidence=extraction_confidence,
        extractor_used=extractor_used,
        background_colors=backgrounds,
        debug=debug_payload,
    )

    source_identifier = request.image_url or "base64_upload"
    tokens = _palette_records(extraction_result.colors)
    job_id = await color_repo.record_extraction(
        project_id=request.project_id,
        source_url=source_identifier,
        tokens=tokens,
        result_data={
            "color_count": len(extraction_result.colors),
            "palette": extraction_result.color_palette,
        },
    )
    response = color_result_payload(
        extraction_result,
        namespace=f"token/color/project/{request.project_id}/job/{job_id}",
        science_artifacts=(
            _color_science_artifacts_from_colors(
                extraction_result.colors, max_colors=request.max_colors
            )
            if request.include_science_artifacts
            else None
        ),
    )
    logger.info(
        "Extracted %d colors for project %d", len(extraction_result.colors), request.project_id
    )

    return response


async def batch_color_payloads(
    request: ColorBatchInput,
    color_repo: ColorTokenRepository,
    dependencies: ColorPipelineDependencies,
) -> list[dict[str, Any]]:
    """Batch extract colors from multiple image URLs."""
    extractor, extractor_name = dependencies.get_extractor("auto")
    responses: list[dict[str, Any]] = []
    for url in request.image_urls:
        try:
            extraction_result = extractor.extract_colors_from_image_url(url, request.max_colors)
            extraction_result.extractor_used = extractor_name
            job_id: int | None = None
            # Optional persistence
            if request.project_id:
                tokens = _palette_records(extraction_result.colors)
                job_id = await color_repo.record_extraction(
                    project_id=request.project_id,
                    source_url=url,
                    tokens=tokens,
                    result_data={"color_count": len(extraction_result.colors)},
                )
            namespace = (
                f"token/color/project/{request.project_id}/job/{job_id}"
                if job_id is not None and request.project_id
                else f"token/color/batch/{len(responses) + 1:02d}"
            )
            responses.append(
                color_result_payload(
                    extraction_result,
                    namespace=namespace,
                    science_artifacts=(
                        _color_science_artifacts_from_colors(
                            extraction_result.colors, max_colors=request.max_colors
                        )
                        if request.include_science_artifacts
                        else None
                    ),
                )
            )
        except Exception as e:
            logger.error("Batch color extraction failed for %s: %s", url, str(e))
            continue
    return responses


async def stream_color_events(
    request: ColorExtractionInput,
    color_repo: ColorTokenRepository,
    session: Any,
    cost_headers: dict[str, str],
    dependencies: ColorPipelineDependencies,
) -> AsyncIterator[dict[str, Any]]:
    # Phase 1: Fast local color extraction (instant)
    logger.info("[Phase 1] Starting fast color extraction for project %d", request.project_id)
    extractor, extractor_name = dependencies.get_extractor(request.extractor or "auto")
    cache_namespace = f"project:{request.project_id}"
    cache = dependencies.get_cache()
    input_hash = compute_input_hash(
        request.image_base64,
        request.image_url,
        {"max_colors": request.max_colors, "extractor": extractor_name},
    )

    # Cost check/enforcement
    cost_state = dependencies.cost_tracker.record(project_id=request.project_id, amount=0.02)
    if cost_state.blocked:
        raise ColorQuotaExceeded(
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

    def call_with_supported_kwargs(func, *args, **kwargs):
        """Call func with only kwargs it accepts to support multiple extractor implementations."""
        sig = inspect.signature(func)
        filtered = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return func(*args, **filtered)

    with track_perf(
        "upload.first_token",
        {"project_id": request.project_id, "extractor": extractor_name},
        measure_memory=True,
    ):
        cached_result = cache.get("color.full", input_hash, cache_namespace)
        if cached_result:
            raw_result = ColorExtractionResult.model_validate(cached_result)
        else:
            if request.image_base64:
                raw_result = call_with_supported_kwargs(
                    extractor.extract_colors_from_base64,
                    request.image_base64,
                    media_type="image/png",
                    max_colors=request.max_colors,
                    cache_namespace=cache_namespace,
                    input_hash=input_hash,
                )
            else:
                raw_result = call_with_supported_kwargs(
                    extractor.extract_colors_from_image_url,
                    request.image_url,
                    max_colors=request.max_colors,
                    cache_namespace=cache_namespace,
                    input_hash=input_hash,
                )

    processed_colors, backgrounds = post_process_colors(
        raw_result.colors, getattr(raw_result, "dominant_colors", None)
    )
    color_palette = _safe_str(getattr(raw_result, "color_palette", ""))
    dominant_colors = list(getattr(raw_result, "dominant_colors", []) or [])
    try:
        extraction_confidence = float(getattr(raw_result, "extraction_confidence", 0.0) or 0.0)
    except (ValueError, TypeError):
        extraction_confidence = 0.0
    debug_payload = getattr(raw_result, "debug", None)
    if not isinstance(debug_payload, dict):
        debug_payload = None
    debug_bundle = _color_artifacts_from_debug(debug_payload)
    science_bundle = (
        _color_science_artifacts_from_colors(processed_colors, max_colors=request.max_colors)
        if request.include_science_artifacts
        else None
    )
    artifacts_payload = _merge_artifact_bundles(
        debug_bundle,
        science_bundle,
    ).model_dump(by_alias=True)
    # Send Phase 1 results immediately
    phase1_data = {
        "phase": 1,
        "status": "colors_extracted",
        "color_count": len(processed_colors),
        "message": f"Extracted {len(processed_colors)} colors using fast algorithms",
        "artifacts": artifacts_payload,
    }
    yield phase1_data

    source_identifier = request.image_url or "base64_upload"
    tokens_to_store: list[ColorTokenCreate] = []
    for i, color in enumerate(processed_colors):
        tokens_to_store.append(
            ColorTokenCreate(
                hex=color.hex,
                rgb=color.rgb,
                hsl=color.hsl,
                hsv=color.hsv,
                name=color.name,
                design_intent=color.design_intent,
                semantic_names=_json_or_none(color.semantic_names),
                extraction_metadata=_json_or_none(color.extraction_metadata),
                category=None,
                confidence=float(color.confidence or 0.0),
                harmony=color.harmony,
                temperature=color.temperature,
                saturation_level=color.saturation_level,
                lightness_level=color.lightness_level,
                usage=_json_or_none(color.usage),
                count=int(getattr(color, "count", 1) or 1),
                prominence_percentage=None,
                wcag_contrast_on_white=color.wcag_contrast_on_white,
                wcag_contrast_on_black=color.wcag_contrast_on_black,
                wcag_aa_compliant_text=color.wcag_aa_compliant_text,
                wcag_aaa_compliant_text=color.wcag_aaa_compliant_text,
                wcag_aa_compliant_normal=color.wcag_aa_compliant_normal,
                wcag_aaa_compliant_normal=color.wcag_aaa_compliant_normal,
                colorblind_safe=color.colorblind_safe,
                tint_color=color.tint_color,
                shade_color=color.shade_color,
                tone_color=color.tone_color,
                closest_web_safe=color.closest_web_safe,
                closest_css_named=color.closest_css_named,
                delta_e_to_dominant=color.delta_e_to_dominant,
                is_neutral=color.is_neutral,
                background_role=color.background_role,
                foreground_role=color.foreground_role,
                contrast_category=color.contrast_category,
                harmony_confidence=color.harmony_confidence,
                hue_angles=_json_or_none(color.hue_angles),
                is_accent=color.is_accent,
                state_variants=_json_or_none(color.state_variants),
                kmeans_cluster_id=None,
                sam_segmentation_mask=None,
                clip_embeddings=None,
                histogram_significance=None,
                library_id=None,
                role=None,
                provenance=None,
            )
        )

        # Stream each color as it's processed
        if (i + 1) % 5 == 0 or i == len(processed_colors) - 1:
            streaming_data = {
                "phase": 1,
                "status": "colors_streaming",
                "progress": (i + 1) / len(processed_colors),
                "message": f"Processed {i + 1}/{len(processed_colors)} colors",
                "artifacts": artifacts_payload,
            }
            yield streaming_data

    job_id = await color_repo.record_extraction(
        project_id=request.project_id,
        source_url=source_identifier,
        tokens=tokens_to_store,
        result_data={"color_count": len(processed_colors), "palette": color_palette},
    )
    stored_colors = await color_repo.list_by_job(extraction_job_id=job_id)

    # Phase 2: Return complete extraction with all color data from database
    shadow_tokens = default_shadow_tokens(stored_colors)
    ramp_repo = InMemoryTokenRepository()
    ramp_tokens = _add_color_ramps(ramp_repo, processed_colors, "token/color/stream")
    accent_tokens = []
    text_roles = []
    for stored_color in stored_colors:
        meta = parse_metadata(getattr(stored_color, "extraction_metadata", None))
        if meta.get("accent") or meta.get("state_role"):
            accent_tokens.append(
                {
                    "hex": stored_color.hex,
                    "role": meta.get("state_role") or ("accent" if meta.get("accent") else None),
                }
            )
        if meta.get("text_role"):
            text_roles.append(
                {
                    "hex": stored_color.hex,
                    "role": meta.get("text_role"),
                    "contrast": meta.get("contrast_to_background"),
                }
            )
    color_payloads: list[dict[str, Any]] = []
    for idx, color_model in enumerate(processed_colors):
        payload = color_model.model_dump(exclude_none=True)
        stored_color_model: Any | None = stored_colors[idx] if idx < len(stored_colors) else None
        if stored_color_model is not None:
            payload["id"] = stored_color_model.id
            payload["project_id"] = stored_color_model.project_id
            payload["extraction_job_id"] = stored_color_model.extraction_job_id
        color_payloads.append(sanitize_json_value(payload))

    debug_value = getattr(raw_result, "debug", None)
    if debug_value is not None and not isinstance(debug_value, (dict, list, str)):
        debug_value = None

    complete_payload = sanitize_json_value(
        {
            "phase": 2,
            "status": "extraction_complete",
            "summary": color_palette,
            "dominant_colors": dominant_colors,
            "extraction_confidence": extraction_confidence,
            "extractor_used": extractor_name,
            "colors": color_payloads,
            "shadows": shadow_tokens,
            "background_colors": backgrounds,
            "text_roles": text_roles,
            "accent_tokens": accent_tokens,
            "ramps": ramp_to_dict(ramp_tokens) if ramp_tokens else {},
            "debug": debug_value,
            "artifacts": artifacts_payload,
        }
    )
    yield complete_payload

    # Phase 3: AI enhancement with OpenAI GPT-4 Vision
    try:
        cached_phase3 = cache.get("color.post", input_hash, cache_namespace)
        if cached_phase3:
            yield cached_phase3
            logger.info("[Phase 3] Served cached AI enhancement for project %d", request.project_id)
        else:
            logger.info("[Phase 3] Starting AI enhancement for project %d", request.project_id)
            from copy_that.extractors.color.openai_extractor import OpenAIColorExtractor

            ai_extractor = OpenAIColorExtractor()

            # Extract enhanced colors using GPT-4 Vision
            if request.image_base64:
                ai_result = ai_extractor.extract_colors_from_base64(
                    request.image_base64,
                    media_type="image/png",
                    max_colors=request.max_colors,
                )
            else:
                ai_result = ai_extractor.extract_colors_from_image_url(
                    request.image_url, max_colors=request.max_colors
                )

            # Merge Phase 3 AI enhancements with stored colors
            enriched_colors = []
            for idx, ai_color in enumerate(ai_result.colors):
                if idx >= len(stored_colors):
                    break

                stored_color = stored_colors[idx]
                semantic_names = (
                    json.dumps(ai_color.semantic_names) if ai_color.semantic_names else None
                )
                design_intent = ai_color.design_intent if ai_color.design_intent else None
                if semantic_names is not None or design_intent is not None:
                    await color_repo.update(
                        color_id=stored_color.id,
                        semantic_names=semantic_names,
                        design_intent=design_intent,
                    )

                enriched_colors.append(
                    {
                        "id": stored_color.id,
                        "hex": ai_color.hex,
                        "name": ai_color.name,
                        "design_intent": ai_color.design_intent,
                        "semantic_names": ai_color.semantic_names,
                        "confidence": ai_color.confidence,
                        "usage": ai_color.usage,
                        "prominence_percentage": ai_color.prominence_percentage,
                    }
                )

            # Yield Phase 3 completion event
            phase3_payload = sanitize_json_value(
                {
                    "phase": 3,
                    "status": "ai_enhancement_complete",
                    "message": f"AI enhancement complete for {len(enriched_colors)} colors",
                    "colors": enriched_colors,
                    "artifacts": artifacts_payload,
                }
            )
            cache.set("color.post", input_hash, cache_namespace, phase3_payload)
            yield phase3_payload

            logger.info("[Phase 3] AI enhancement complete for project %d", request.project_id)
    except Exception as e:
        logger.warning("[Phase 3] AI enhancement failed: %s. Continuing without Phase 3.", str(e))
        # Don't fail the entire extraction if Phase 3 fails
        # Just log and continue
        phase3_error = {
            "phase": 3,
            "status": "ai_enhancement_failed",
            "message": str(e),
            "artifacts": artifacts_payload,
        }
        yield phase3_error

    logger.info("Extracted %d colors for project %d", len(processed_colors), request.project_id)


async def multi_color_payload(
    request: ColorExtractionInput,
    image_base64: str,
    dependencies: ColorPipelineDependencies,
) -> dict[str, Any]:
    # Phase 2.1-2.5: Multi-extractor orchestration
    # Instantiate three extractors: Claude AI, K-means, and Computer Vision
    extractors = [
        dependencies.kmeans_adapter(k=10),  # K-means with 10 clusters
        dependencies.cv_adapter(max_colors=8),  # CV with up to 8 colors
        # Claude adapter disabled by default (requires API key)
        # ClaudeColorExtractorAdapter(),  # AI-powered with Claude
    ]

    # Create ColorAggregator with Delta-E deduplication threshold of 2.3
    # This removes colors that are perceptually similar (within 2.3 ΔE units)
    aggregator = dependencies.aggregator(delta_e_threshold=2.3)

    # Create orchestrator for parallel execution with graceful degradation
    orchestrator = dependencies.orchestrator(
        extractors=extractors,
        aggregator=aggregator,
    )

    # Convert base64 image to bytes for orchestrator
    image_bytes = base64.b64decode(
        image_base64.split(",")[1] if "," in image_base64 else image_base64
    )

    # Generate image ID from project and request timestamp
    import uuid

    image_id = f"project_{request.project_id}_{uuid.uuid4().hex[:8]}"

    # Run extraction across all extractors in parallel
    result = await orchestrator.extract_all(image_bytes, image_id)

    # Convert aggregated colors to API response format
    dominant_colors = [c.hex for c in result.aggregated_colors[:3]]
    color_palette = "Multi-extractor orchestrated palette"
    science_bundle = (
        _color_science_artifacts_from_colors(
            result.aggregated_colors, max_colors=request.max_colors
        )
        if request.include_science_artifacts
        else ArtifactBundle()
    )

    return {
        "colors": [
            {
                "hex": color.hex,
                "name": color.name or f"Color {color.hex}",
                "confidence": color.confidence,
                "category": color.category or "palette",
                "provenance": color.extraction_metadata.get("extractor_sources", [])
                if color.extraction_metadata
                else [],
            }
            for color in result.aggregated_colors
        ],
        "dominant_colors": dominant_colors,
        "color_palette": color_palette,
        "extraction_confidence": result.overall_confidence,
        "extractor_used": "multi-extractor-orchestrator",
        "design_tokens": {},
        "artifacts": science_bundle.model_dump(by_alias=True),
    }
