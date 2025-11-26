"""Helpers to map ORM models into token graph repositories."""

from __future__ import annotations

from collections.abc import Sequence

from coloraide import Color

from copy_that.domain.models import ColorToken, SpacingToken
from core.tokens.color import make_color_token
from core.tokens.repository import InMemoryTokenRepository, TokenRepository
from core.tokens.spacing import make_spacing_token


def colors_to_repo(
    colors: Sequence[ColorToken], namespace: str = "token/color/export"
) -> TokenRepository:
    repo = InMemoryTokenRepository()
    for index, color in enumerate(colors, start=1):
        attributes = {
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
        token_id = f"{namespace}/{index:02d}"
        repo.upsert_token(make_color_token(token_id, Color(color.hex), attributes))
    return repo


def spacing_to_repo(
    tokens: Sequence[SpacingToken], namespace: str = "token/spacing/export"
) -> TokenRepository:
    repo = InMemoryTokenRepository()
    for index, token in enumerate(tokens, start=1):
        attributes = {
            "id": getattr(token, "id", None),
            "project_id": getattr(token, "project_id", None),
            "extraction_job_id": getattr(token, "extraction_job_id", None),
            "value_px": getattr(token, "value_px", None),
            "name": getattr(token, "name", None),
            "semantic_role": getattr(token, "semantic_role", None),
            "spacing_type": getattr(token, "spacing_type", None),
            "category": getattr(token, "category", None),
            "confidence": getattr(token, "confidence", None),
            "usage": getattr(token, "usage", None),
        }
        value_rem = round(token.value_px / 16, 4)
        repo.upsert_token(
            make_spacing_token(
                f"{namespace}/{index:02d}",
                token.value_px,
                value_rem,
                attributes,
            )
        )
    return repo
