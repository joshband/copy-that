from __future__ import annotations

from typing import Any, TypedDict

from copy_that.application.font_mapping import STYLE_TO_FONT_CATEGORY, font_category_for_style
from core.tokens.model import Token
from core.tokens.typography import make_typography_token


class StyleAttributes(TypedDict, total=False):
    primary_style: str
    color_temperature: str
    visual_weight: str
    contrast_level: str
    vlm_style: str
    vlm_mood: str
    vlm_confidence: float
    vlm_complexity: str


class TypographyRecommendationResult(TypedDict):
    tokens: list[Token]
    style_attributes: StyleAttributes
    confidence: float


class TypographyRecommender:
    def recommend(self, style: StyleAttributes) -> list[Token]:
        tokens: list[Token] = []

        primary_style = style.get("primary_style", "minimalist")
        temperature = style.get("color_temperature", "neutral")
        visual_weight = style.get("visual_weight", "balanced")

        family_category = font_category_for_style(primary_style)
        font_family_token_id = f"font.family.{family_category}"

        heading_weight = 700 if visual_weight != "light" else 500
        if visual_weight == "heavy":
            heading_weight = 800
        body_weight = 400 if visual_weight == "light" else 450
        if visual_weight == "heavy":
            body_weight = 500

        heading_size_px = 32 if primary_style in ("minimalist", "technical") else 28
        if primary_style == "brutalist":
            heading_size_px = 30
        body_size_px = 16
        caption_size_px = 13

        heading_token = make_typography_token(
            "typography.heading.lg",
            font_family_token_id=font_family_token_id,
            font_size_px=heading_size_px,
            line_height_px=heading_size_px * 1.25,
            font_weight=heading_weight,
            color_token_id="color.text.primary",
            attributes={
                "role": "heading",
                "level": "h1",
                "style": primary_style,
                "temperature": temperature,
            },
        )
        body_token = make_typography_token(
            "typography.body",
            font_family_token_id=font_family_token_id,
            font_size_px=body_size_px,
            line_height_px=body_size_px * 1.5,
            font_weight=body_weight,
            color_token_id="color.text.primary",
            attributes={"role": "body", "style": primary_style, "temperature": temperature},
        )
        caption_token = make_typography_token(
            "typography.caption",
            font_family_token_id=font_family_token_id,
            font_size_px=caption_size_px,
            line_height_px=caption_size_px * 1.4,
            font_weight=body_weight,
            color_token_id="color.text.muted",
            attributes={"role": "caption", "style": primary_style, "temperature": temperature},
        )

        tokens.extend([heading_token, body_token, caption_token])
        return tokens

    def attributes_from_vlm(self, vlm_result: dict[str, Any]) -> StyleAttributes:
        style: StyleAttributes = {}
        style["primary_style"] = vlm_result.get("primary_style", "minimalist")
        style["color_temperature"] = vlm_result.get("color_temperature", "neutral")
        style["visual_weight"] = vlm_result.get("visual_weight", "balanced")
        style["contrast_level"] = vlm_result.get("contrast_level", "medium")
        style["vlm_style"] = vlm_result.get("primary_style", "")
        style["vlm_mood"] = vlm_result.get("mood", "")
        style["vlm_confidence"] = float(vlm_result.get("confidence", 0.0))
        style["vlm_complexity"] = vlm_result.get("complexity", "")
        return style

    def recommend_with_confidence(self, style: StyleAttributes) -> TypographyRecommendationResult:
        tokens = self.recommend(style)
        vlm_conf = float(style.get("vlm_confidence", 0.5))
        style_known = 1.0 if style.get("primary_style") in STYLE_TO_FONT_CATEGORY else 0.5
        confidence = (0.6 * vlm_conf) + (0.4 * style_known)
        return {
            "tokens": tokens,
            "style_attributes": style,
            "confidence": round(confidence, 3),
        }
