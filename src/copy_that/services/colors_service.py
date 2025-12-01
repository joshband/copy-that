"""Service helpers for color API handlers."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from coloraide import Color

from copy_that.application.color_extractor import ColorExtractionResult, ExtractedColorToken
from core.tokens.adapters.w3c import tokens_to_w3c
from core.tokens.color import make_color_ramp, make_color_token
from core.tokens.repository import InMemoryTokenRepository, TokenRepository

logger = logging.getLogger(__name__)


def color_token_responses(colors: Sequence[ExtractedColorToken]) -> list[dict[str, Any]]:
    """Convert extracted color tokens into response dicts."""
    return [c.model_dump() for c in colors]


def add_colors_to_repo(
    repo: TokenRepository, colors: Sequence[ExtractedColorToken], namespace: str
) -> None:
    """Upsert extracted colors into a TokenRepository."""
    for index, color in enumerate(colors, start=1):
        attributes = color.model_dump(exclude_none=True)
        repo.upsert_token(
            make_color_token(f"{namespace}/{index:02d}", Color(color.hex), attributes)
        )


def add_color_ramps_to_repo(
    repo: TokenRepository, colors: Sequence[ExtractedColorToken], namespace: str
) -> None:
    """Add accent ramps if an accent color is flagged."""
    accent_hex = next(
        (c.hex for c in colors if (c.extraction_metadata or {}).get("accent") and c.hex), None
    )
    if not accent_hex:
        return
    ramp = make_color_ramp(accent_hex, prefix=f"{namespace}/accent")
    for tok in ramp.values():
        repo.upsert_token(tok)


def result_to_response(
    result: ColorExtractionResult, namespace: str = "token/color/api"
) -> dict[str, Any]:
    """Build the API response payload (including W3C export) from an extraction result."""
    repo = InMemoryTokenRepository()
    add_colors_to_repo(repo, result.colors, namespace)
    add_color_ramps_to_repo(repo, result.colors, namespace)
    return {
        "colors": color_token_responses(result.colors),
        "dominant_colors": result.dominant_colors,
        "color_palette": result.color_palette,
        "extraction_confidence": result.extraction_confidence,
        "extractor_used": result.extractor_used,
        "design_tokens": tokens_to_w3c(repo),
    }


def db_colors_to_repo(colors: Sequence[Any], namespace: str) -> TokenRepository:
    """Build a TokenRepository from DB ColorToken rows."""
    repo = InMemoryTokenRepository()
    accent_hex: str | None = None
    for index, color in enumerate(colors, start=1):
        attrs = {
            "id": getattr(color, "id", None),
            "project_id": getattr(color, "project_id", None),
            "extraction_job_id": getattr(color, "extraction_job_id", None),
            "hex": getattr(color, "hex", None),
            "rgb": getattr(color, "rgb", None),
            "hsl": getattr(color, "hsl", None),
            "hsv": getattr(color, "hsv", None),
            "name": getattr(color, "name", None),
            "design_intent": getattr(color, "design_intent", None),
            "semantic_names": getattr(color, "semantic_names", None),
            "extraction_metadata": getattr(color, "extraction_metadata", None),
            "category": getattr(color, "category", None),
            "confidence": getattr(color, "confidence", None),
            "harmony": getattr(color, "harmony", None),
            "temperature": getattr(color, "temperature", None),
            "saturation_level": getattr(color, "saturation_level", None),
            "lightness_level": getattr(color, "lightness_level", None),
            "usage": getattr(color, "usage", None),
            "count": getattr(color, "count", None),
            "prominence_percentage": getattr(color, "prominence_percentage", None),
            "wcag_contrast_on_white": getattr(color, "wcag_contrast_on_white", None),
            "wcag_contrast_on_black": getattr(color, "wcag_contrast_on_black", None),
            "wcag_aa_compliant_text": getattr(color, "wcag_aa_compliant_text", None),
            "wcag_aaa_compliant_text": getattr(color, "wcag_aaa_compliant_text", None),
            "wcag_aa_compliant_normal": getattr(color, "wcag_aa_compliant_normal", None),
            "wcag_aaa_compliant_normal": getattr(color, "wcag_aaa_compliant_normal", None),
            "colorblind_safe": getattr(color, "colorblind_safe", None),
            "tint_color": getattr(color, "tint_color", None),
            "shade_color": getattr(color, "shade_color", None),
            "tone_color": getattr(color, "tone_color", None),
            "closest_web_safe": getattr(color, "closest_web_safe", None),
            "closest_css_named": getattr(color, "closest_css_named", None),
            "delta_e_to_dominant": getattr(color, "delta_e_to_dominant", None),
            "is_neutral": getattr(color, "is_neutral", None),
        }
        hex_value = attrs.get("hex") or "#000000"
        repo.upsert_token(make_color_token(f"{namespace}/{index:02d}", Color(hex_value), attrs))
        if not accent_hex:
            meta = attrs.get("extraction_metadata")
            if isinstance(meta, str):
                import json

                try:
                    meta = json.loads(meta)
                except Exception as e:
                    logger.debug(f"Failed to parse extraction_metadata JSON: {e}")
                    meta = None
            if isinstance(meta, dict) and meta.get("accent"):
                accent_hex = hex_value
    if accent_hex:
        ramp = make_color_ramp(accent_hex, prefix=f"{namespace}/accent")
        for tok in ramp.values():
            repo.upsert_token(tok)
    return repo


def serialize_color_token(color: Any) -> dict[str, Any]:
    """Serialize a ColorToken database model to a dictionary for JSON response.

    This is the canonical serialization function for ColorToken models.
    Used by both the colors API router and colors service.
    """
    return {
        "id": color.id,
        "hex": color.hex,
        "rgb": color.rgb,
        "hsl": color.hsl,
        "hsv": color.hsv,
        "name": color.name,
        "design_intent": color.design_intent,
        "semantic_names": json_loads(color.semantic_names),
        "extraction_metadata": json_loads(color.extraction_metadata),
        "category": color.category,
        "confidence": color.confidence,
        "harmony": color.harmony,
        "temperature": color.temperature,
        "saturation_level": color.saturation_level,
        "lightness_level": color.lightness_level,
        "usage": json_loads(color.usage),
        "count": color.count,
        "prominence_percentage": color.prominence_percentage,
        "wcag_contrast_on_white": color.wcag_contrast_on_white,
        "wcag_contrast_on_black": color.wcag_contrast_on_black,
        "wcag_aa_compliant_text": color.wcag_aa_compliant_text,
        "wcag_aaa_compliant_text": color.wcag_aaa_compliant_text,
        "wcag_aa_compliant_normal": color.wcag_aa_compliant_normal,
        "wcag_aaa_compliant_normal": color.wcag_aaa_compliant_normal,
        "colorblind_safe": color.colorblind_safe,
        "tint_color": color.tint_color,
        "shade_color": color.shade_color,
        "tone_color": color.tone_color,
        "closest_web_safe": color.closest_web_safe,
        "closest_css_named": color.closest_css_named,
        "delta_e_to_dominant": color.delta_e_to_dominant,
        "is_neutral": color.is_neutral,
        # Optional role attributes (may not exist on all models)
        "background_role": getattr(color, "background_role", None),
        "foreground_role": getattr(color, "foreground_role", None),
        "contrast_category": getattr(color, "contrast_category", None),
    }


def json_loads(value: str | None) -> Any | None:
    """Safe JSON loader for optional string fields."""
    if value is None:
        return None
    try:
        import json

        return json.loads(value)
    except Exception as e:
        logger.debug(f"Failed to parse JSON value: {e}")
        return None
