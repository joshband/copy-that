"""Service helpers for color API handlers."""

from __future__ import annotations

import json as _json
import logging
import os
from collections.abc import Sequence
from typing import Any, cast

from coloraide import Color

from copy_that.application import color_utils
from copy_that.application.color_extractor import (
    AIColorExtractor,
    ColorExtractionResult,
    ExtractedColorToken,
)
from copy_that.application.openai_color_extractor import OpenAIColorExtractor
from core.tokens.adapters.w3c import tokens_to_w3c
from core.tokens.color import make_color_ramp, make_color_token
from core.tokens.model import Token
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


def get_extractor(extractor_type: str = "auto"):
    """Get the appropriate color extractor based on type and available API keys.

    Returns:
        tuple: (extractor instance, model name string)
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if extractor_type == "openai":
        if not openai_key:
            raise ValueError("OPENAI_API_KEY not set")
        return OpenAIColorExtractor(), "gpt-4o"
    elif extractor_type == "claude":
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        return AIColorExtractor(), "claude-sonnet-4-5"
    else:  # auto
        # Prefer OpenAI if available, fallback to Claude
        if openai_key:
            return OpenAIColorExtractor(), "gpt-4o"
        elif anthropic_key:
            return AIColorExtractor(), "claude-sonnet-4-5"
        else:
            raise ValueError("No API key available. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")


def parse_metadata(meta: Any) -> dict[str, Any]:
    """Best-effort metadata parser (supports dict or JSON string)."""
    if not meta:
        return {}
    if isinstance(meta, dict):
        return meta
    if isinstance(meta, str):
        try:
            loaded = _json.loads(meta)
            return loaded if isinstance(loaded, dict) else {}
        except _json.JSONDecodeError:
            return {}
    return {}


def find_accent_hex(colors: Sequence[Any]) -> str | None:
    """Pick the first accent-flagged color hex."""
    for color in colors:
        hex_val = cast(str | None, getattr(color, "hex", None))
        meta = parse_metadata(getattr(color, "extraction_metadata", None))
        if bool(meta.get("accent")) and hex_val:
            return hex_val
    return None


def post_process_colors(
    colors: list[ExtractedColorToken], background_palette: list[str] | None = None
) -> tuple[list[ExtractedColorToken], list[str]]:
    """Cluster near-duplicate colors, assign background roles, and label contrast."""
    clustered = cast(
        list[ExtractedColorToken], color_utils.cluster_color_tokens(colors, threshold=2.5)
    )
    backgrounds = color_utils.assign_background_roles(clustered)
    primary_bg = (
        backgrounds[0] if backgrounds else (background_palette[0] if background_palette else None)
    )
    color_utils.apply_contrast_categories(clustered, primary_bg)
    color_utils.tag_foreground_colors(clustered, primary_bg)
    return clustered, backgrounds


def default_shadow_tokens(colors: Sequence[Any]) -> list[dict[str, Any]]:
    """Generate a small set of shadow tokens referencing the darkest color."""
    if not colors:
        return []
    try:
        darkest = min(colors, key=lambda c: color_utils.relative_luminance(c.hex))
    except (ValueError, TypeError):
        darkest = colors[0]

    hex_val = darkest.hex or "#000000"
    shadow_value = {
        "color": f"{hex_val}59" if not hex_val.startswith("{") else hex_val,
        "x": {"value": 0, "unit": "px"},
        "y": {"value": 4, "unit": "px"},
        "blur": {"value": 8, "unit": "px"},
        "spread": {"value": 0, "unit": "px"},
    }
    return [{"id": "shadow.1", "$type": "shadow", "$value": shadow_value}]


def add_role_tokens(
    repo: TokenRepository, namespace: str, background_hexes: list[str] | None = None
) -> None:
    """Add semantic role tokens (background, text/onDark, text/onLight) to repo."""
    colors = repo.find_by_type("color")
    if not colors:
        return

    # Background alias
    bg_hexes = [hx.lower() for hx in (background_hexes or []) if hx]
    primary_bg = None
    primary_bg_id = None
    for tok in colors:
        tok_hex = tok.attributes.get("hex", "").lower()
        if tok.attributes.get("background_role") == "primary":
            primary_bg = tok_hex
            primary_bg_id = tok.id
            break
        if not primary_bg and tok_hex in bg_hexes:
            primary_bg = tok_hex
            primary_bg_id = tok.id
    if primary_bg_id:
        repo.upsert_token(
            Token(
                id=f"{namespace}/background",
                type="color",
                value=f"{{{primary_bg_id}}}",
                attributes={"role": "background"},
            )
        )

    if not primary_bg:
        return

    # Choose best contrast color for text roles
    def best_contrast(lighter: bool) -> Token | None:
        candidates = []
        for tok in colors:
            if tok.id == primary_bg_id:
                continue
            tok_hex = tok.attributes.get("hex")
            if not tok_hex:
                continue
            ratio = color_utils.contrast_ratio(tok_hex, primary_bg)
            lum = color_utils.relative_luminance(tok_hex)
            candidates.append((ratio, lum, tok))
        if not candidates:
            return None
        # Filter by direction (lighter/darker than background)
        bg_lum = color_utils.relative_luminance(primary_bg)
        filtered = [(ratio, tok) for ratio, lum, tok in candidates if (lum > bg_lum) == lighter]
        if not filtered:
            filtered = [(ratio, tok) for ratio, _lum, tok in candidates]
        filtered.sort(key=lambda x: (-x[0], x[1].id))
        best_ratio, best_tok = filtered[0]
        return best_tok if best_ratio >= 4.5 else None

    # If background is dark, pick a light text; if light, pick dark text
    bg_lum = color_utils.relative_luminance(primary_bg)
    light_text = best_contrast(lighter=True)
    dark_text = best_contrast(lighter=False)

    if bg_lum < 0.5 and light_text:
        repo.upsert_token(
            Token(
                id=f"{namespace}/text/onDark",
                type="color",
                value=f"{{{light_text.id}}}",
                attributes={"role": "text-on-dark"},
            )
        )
    if bg_lum >= 0.5 and dark_text:
        repo.upsert_token(
            Token(
                id=f"{namespace}/text/onLight",
                type="color",
                value=f"{{{dark_text.id}}}",
                attributes={"role": "text-on-light"},
            )
        )


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
