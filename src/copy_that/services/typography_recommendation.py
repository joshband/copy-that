"""Helpers for typography recommendations based on existing tokens."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from copy_that.application.font_mapping import FONT_PROFILES
from copy_that.application.typography_extractor import ExtractedTypographyToken
from copy_that.application.typography_recommender import (
    StyleAttributes,
    TypographyRecommender,
)
from copy_that.domain.color_tokens import ColorToken
from core.tokens.model import Token, TokenType

_ROLE_CATEGORY = {
    "heading": "display",
    "subheading": "display",
    "display": "display",
    "body": "text",
    "caption": "label",
    "label": "label",
    "nav": "label",
    "hero": "display",
    "footer": "label",
}

_WEIGHT_MAP = {
    "thin": 100,
    "extra light": 200,
    "extralight": 200,
    "light": 300,
    "normal": 400,
    "regular": 400,
    "medium": 500,
    "semibold": 600,
    "semi bold": 600,
    "bold": 700,
    "extra bold": 800,
    "extrabold": 800,
    "black": 900,
}


def infer_style_from_colors(
    colors: Sequence[ColorToken], style_hint: str | None = None
) -> StyleAttributes:
    """Infer typography style attributes from color tokens."""
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


def recommend_typography_tokens(
    style_attributes: StyleAttributes,
) -> tuple[list[ExtractedTypographyToken], float]:
    """Return recommended typography tokens and a confidence score."""
    recommender = TypographyRecommender()
    recommendation = recommender.recommend_with_confidence(style_attributes)
    confidence_raw = recommendation.get("confidence", 0.5)
    confidence = float(confidence_raw) if isinstance(confidence_raw, (int, float)) else 0.5
    confidence = max(0.0, min(1.0, confidence))
    style_attrs = recommendation.get("style_attributes") or style_attributes

    tokens: list[ExtractedTypographyToken] = []
    for token in recommendation.get("tokens", []):
        if isinstance(token.type, TokenType) and token.type != TokenType.TYPOGRAPHY:
            continue
        if isinstance(token.type, str) and token.type != TokenType.TYPOGRAPHY.value:
            continue
        tokens.append(_token_to_extracted(token, confidence, style_attrs))
    return tokens, confidence


def _token_to_extracted(
    token: Token, confidence: float, style_attributes: StyleAttributes
) -> ExtractedTypographyToken:
    value = token.value if isinstance(token.value, dict) else {}
    attributes = token.attributes or {}

    font_family, family_category = _resolve_font_family(value.get("fontFamily"))
    font_weight = _parse_font_weight(value.get("fontWeight"))
    font_style = _normalize_str(value.get("fontStyle")) or "normal"
    font_size = _parse_font_size(value.get("fontSize"))
    line_height = _parse_line_height(value.get("lineHeight"), font_size)
    letter_spacing = _parse_letter_spacing(value.get("letterSpacing"))
    text_transform = _normalize_str(value.get("casing"))
    text_align = _normalize_str(value.get("textAlign"))

    semantic_role = _infer_semantic_role(token, attributes)
    category = _ROLE_CATEGORY.get(semantic_role, "text")
    name = _build_name(attributes, semantic_role, token.id)

    extraction_metadata: dict[str, Any] = {
        "source": "typography_recommender",
        "token_id": token.id,
        "style_attributes": style_attributes,
        "recommendation_confidence": confidence,
    }
    if family_category:
        extraction_metadata["font_family_category"] = family_category

    return ExtractedTypographyToken(
        font_family=font_family,
        font_weight=font_weight,
        font_style=font_style,
        font_size=font_size,
        line_height=line_height,
        letter_spacing=letter_spacing,
        text_transform=text_transform,
        text_align=text_align,
        semantic_role=semantic_role,
        category=category,
        name=name,
        confidence=confidence,
        prominence=None,
        is_readable=True,
        readability_score=None,
        extraction_metadata=extraction_metadata,
    )


def _normalize_str(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _resolve_font_family(value: Any) -> tuple[str, str | None]:
    if isinstance(value, list) and value:
        value = value[0]
    if not isinstance(value, str):
        return "System", None
    cleaned = _strip_token_ref(value)
    if cleaned.startswith("font.family."):
        category = cleaned.split("font.family.", 1)[1]
        profile = FONT_PROFILES.get(category, {})
        family = profile.get("google_font_family") or category.replace("_", " ").title()
        return family, category
    return cleaned, None


def _strip_token_ref(value: str) -> str:
    if value.startswith("{") and value.endswith("}"):
        return value[1:-1]
    return value


def _parse_font_weight(value: Any) -> int:
    if isinstance(value, (int, float)):
        weight = int(round(value))
    elif isinstance(value, str):
        stripped = value.strip().lower()
        if stripped.isdigit():
            weight = int(stripped)
        else:
            weight = _WEIGHT_MAP.get(stripped, 400)
    else:
        weight = 400
    return max(100, min(900, weight))


def _parse_font_size(value: Any) -> int:
    size: float | None = None
    if isinstance(value, (int, float)):
        size = float(value)
    elif isinstance(value, dict):
        if "px" in value and value["px"] is not None:
            size = float(value["px"])
        elif "value" in value and value["value"] is not None:
            size = float(value["value"])
            unit = str(value.get("unit", "px")).lower()
            if unit in {"rem", "em"}:
                size *= 16
    elif isinstance(value, str):
        match = re.match(r"^\s*([0-9.]+)\s*(px|rem|em)?\s*$", value, re.IGNORECASE)
        if match:
            size = float(match.group(1))
            unit = (match.group(2) or "px").lower()
            if unit in {"rem", "em"}:
                size *= 16
    if size is None:
        size = 16
    size = max(8.0, min(120.0, size))
    return int(round(size))


def _parse_line_height(value: Any, font_size: int) -> float:
    line_height: float | None = None
    if isinstance(value, (int, float)):
        line_height = float(value)
    elif isinstance(value, dict):
        if "px" in value and value["px"] is not None:
            line_height = float(value["px"]) / max(font_size, 1)
        elif "value" in value and value["value"] is not None:
            raw = float(value["value"])
            unit = str(value.get("unit", "")).lower()
            if unit in {"px", "rem", "em"}:
                if unit in {"rem", "em"}:
                    raw *= 16
                line_height = raw / max(font_size, 1)
            else:
                line_height = raw
    elif isinstance(value, str):
        match = re.match(r"^\s*([0-9.]+)\s*(px|rem|em)?\s*$", value, re.IGNORECASE)
        if match:
            raw = float(match.group(1))
            unit = (match.group(2) or "").lower()
            if unit in {"px", "rem", "em"}:
                if unit in {"rem", "em"}:
                    raw *= 16
                line_height = raw / max(font_size, 1)
            else:
                line_height = raw
    if line_height is None:
        line_height = 1.5
    return max(0.8, min(3.0, round(line_height, 2)))


def _parse_letter_spacing(value: Any) -> float | None:
    if isinstance(value, dict):
        if "em" in value and value["em"] is not None:
            return float(value["em"])
        if "value" in value and value["value"] is not None:
            unit = str(value.get("unit", "em")).lower()
            if unit == "em":
                return float(value["value"])
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.match(r"^\s*([0-9.\-]+)\s*(em)?\s*$", value, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def _infer_semantic_role(token: Token, attributes: dict[str, Any]) -> str:
    role = attributes.get("role")
    if isinstance(role, str) and role:
        return role
    token_id = token.id.lower()
    for candidate in _ROLE_CATEGORY:
        if candidate in token_id:
            return candidate
    return "body"


def _build_name(attributes: dict[str, Any], semantic_role: str, token_id: str) -> str | None:
    level = attributes.get("level")
    if isinstance(level, str) and level:
        return f"{semantic_role.title()} {level.upper()}"
    if semantic_role:
        return semantic_role.title()
    return token_id
