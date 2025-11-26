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
            "id": color.id,
            "project_id": color.project_id,
            "extraction_job_id": color.extraction_job_id,
            "hex": color.hex,
            "rgb": color.rgb,
            "hsl": color.hsl,
            "hsv": color.hsv,
            "name": color.name,
            "design_intent": color.design_intent,
            "semantic_names": color.semantic_names,
            "extraction_metadata": color.extraction_metadata,
            "category": color.category,
            "confidence": color.confidence,
            "harmony": color.harmony,
            "temperature": color.temperature,
            "saturation_level": color.saturation_level,
            "lightness_level": color.lightness_level,
            "usage": color.usage,
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
            "id": token.id,
            "project_id": token.project_id,
            "extraction_job_id": token.extraction_job_id,
            "value_px": token.value_px,
            "name": token.name,
            "semantic_role": token.semantic_role,
            "spacing_type": token.spacing_type,
            "category": token.category,
            "confidence": token.confidence,
            "usage": token.usage,
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
