"""OpenAI GPT-4 Vision color extraction service - alternative to Claude"""

import json
import logging
import os
import re

from openai import OpenAI
from pydantic import BaseModel, Field

from copy_that.application import color_utils
from copy_that.application.semantic_color_naming import analyze_color

logger = logging.getLogger(__name__)


class ColorToken(BaseModel):
    """Color token matching the main extractor format"""

    hex: str
    rgb: str
    hsl: str | None = None
    hsv: str | None = None
    name: str
    design_intent: str | None = None
    semantic_names: dict | None = None
    category: str | None = None
    confidence: float
    harmony: str | None = None
    temperature: str | None = None
    saturation_level: str | None = None
    lightness_level: str | None = None
    usage: list[str] = Field(default_factory=list)
    count: int = 1
    prominence_percentage: float | None = None
    wcag_contrast_on_white: float | None = None
    wcag_contrast_on_black: float | None = None
    wcag_aa_compliant_text: bool | None = None
    wcag_aaa_compliant_text: bool | None = None
    wcag_aa_compliant_normal: bool | None = None
    wcag_aaa_compliant_normal: bool | None = None
    colorblind_safe: bool | None = None
    tint_color: str | None = None
    shade_color: str | None = None
    tone_color: str | None = None
    closest_web_safe: str | None = None
    closest_css_named: str | None = None
    delta_e_to_dominant: float | None = None
    is_neutral: bool | None = None
    extraction_metadata: dict | None = None
    histogram_significance: float | None = None


class ColorExtractionResult(BaseModel):
    """Result of color extraction"""

    colors: list[ColorToken]
    dominant_colors: list[str]
    color_palette: str
    extraction_confidence: float


class OpenAIColorExtractor:
    """Color extractor using OpenAI GPT-4 Vision"""

    def __init__(self, api_key: str | None = None):
        """Initialize the color extractor

        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"  # GPT-4 with vision

    def extract_colors_from_image_url(
        self, image_url: str, max_colors: int = 10
    ) -> ColorExtractionResult:
        """Extract colors from an image URL"""
        return self._extract_colors(
            image_content={"type": "image_url", "image_url": {"url": image_url}},
            max_colors=max_colors,
        )

    def extract_colors_from_base64(
        self, image_data: str, media_type: str = "image/png", max_colors: int = 10
    ) -> ColorExtractionResult:
        """Extract colors from base64 encoded image"""
        data_url = f"data:{media_type};base64,{image_data}"
        return self._extract_colors(
            image_content={"type": "image_url", "image_url": {"url": data_url}},
            max_colors=max_colors,
        )

    def _extract_colors(self, image_content: dict, max_colors: int) -> ColorExtractionResult:
        """Internal method to extract colors using GPT-4 Vision"""

        prompt = f"""Analyze this image and extract the {max_colors} most important colors.

For each color, provide:
1. hex: The hex color code (e.g., "#FF5733")
2. name: A human-readable color name
3. design_intent: The role this color plays (e.g., "primary brand color", "background", "accent", "text")
4. confidence: How confident you are this is an important color (0.0-1.0)
5. usage: Array of suggested uses (e.g., ["backgrounds", "headers", "buttons"])
6. prominence_percentage: Estimated percentage of the image this color occupies

Also provide:
- dominant_colors: Array of the top 3 hex colors
- color_palette: A brief description of the overall palette style

Return ONLY valid JSON in this exact format:
{{
  "colors": [
    {{
      "hex": "#XXXXXX",
      "name": "Color Name",
      "design_intent": "purpose",
      "confidence": 0.95,
      "usage": ["use1", "use2"],
      "prominence_percentage": 25.0
    }}
  ],
  "dominant_colors": ["#XXX", "#YYY", "#ZZZ"],
  "color_palette": "Description of the palette"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": [{"type": "text", "text": prompt}, image_content]}
                ],
                max_tokens=2000,
                temperature=0.3,
            )

            # Parse response
            content = response.choices[0].message.content

            # Extract JSON from response
            json_match = re.search(r"\{[\s\S]*\}", content)
            if not json_match:
                raise ValueError("No JSON found in response")

            data = json.loads(json_match.group())

            # Enrich colors with calculated properties
            enriched_colors = []
            for color_data in data.get("colors", []):
                hex_color = color_data.get("hex", "#000000")

                # Calculate RGB
                rgb = color_utils.hex_to_rgb(hex_color)
                rgb_str = f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"

                # Calculate HSL/HSV
                hsl_str = color_utils.hex_to_hsl(hex_color)
                hsv_str = color_utils.hex_to_hsv(hex_color)

                # Calculate accessibility
                contrast_white = color_utils.calculate_contrast_ratio(hex_color, "#FFFFFF")
                contrast_black = color_utils.calculate_contrast_ratio(hex_color, "#000000")

                # Calculate color properties
                temperature = color_utils.get_color_temperature(hex_color)
                saturation_level = color_utils.get_saturation_level(hex_color)
                lightness_level = color_utils.get_lightness_level(hex_color)
                harmony = color_utils.get_harmony_type(hex_color)
                is_neutral = color_utils.is_neutral_color(hex_color)

                # Calculate variants
                tint = color_utils.get_tint(hex_color, 0.5)
                shade = color_utils.get_shade(hex_color, 0.5)
                tone = color_utils.get_tone(hex_color, 0.5)

                # Get semantic names
                semantic_names = analyze_color(hex_color)

                # Get closest named colors
                closest_web_safe = color_utils.get_closest_web_safe(hex_color)
                closest_css = color_utils.get_closest_css_named(hex_color)

                enriched_color = ColorToken(
                    hex=hex_color,
                    rgb=rgb_str,
                    hsl=hsl_str,
                    hsv=hsv_str,
                    name=color_data.get("name", "Unknown"),
                    design_intent=color_data.get("design_intent"),
                    semantic_names=semantic_names,
                    confidence=color_data.get("confidence", 0.8),
                    harmony=harmony,
                    temperature=temperature,
                    saturation_level=saturation_level,
                    lightness_level=lightness_level,
                    usage=color_data.get("usage", []),
                    prominence_percentage=color_data.get("prominence_percentage"),
                    wcag_contrast_on_white=round(contrast_white, 2),
                    wcag_contrast_on_black=round(contrast_black, 2),
                    wcag_aa_compliant_text=contrast_white >= 3.0 or contrast_black >= 3.0,
                    wcag_aaa_compliant_text=contrast_white >= 4.5 or contrast_black >= 4.5,
                    wcag_aa_compliant_normal=contrast_white >= 4.5 or contrast_black >= 4.5,
                    wcag_aaa_compliant_normal=contrast_white >= 7.0 or contrast_black >= 7.0,
                    colorblind_safe=color_utils.is_colorblind_safe(hex_color),
                    tint_color=tint,
                    shade_color=shade,
                    tone_color=tone,
                    closest_web_safe=closest_web_safe,
                    closest_css_named=closest_css,
                    is_neutral=is_neutral,
                    extraction_metadata={"extractor": "openai_gpt4v", "model": self.model},
                )
                enriched_colors.append(enriched_color)

            return ColorExtractionResult(
                colors=enriched_colors,
                dominant_colors=data.get("dominant_colors", []),
                color_palette=data.get("color_palette", ""),
                extraction_confidence=0.85,
            )

        except Exception as e:
            logger.error(f"OpenAI color extraction failed: {e}")
            raise
