"""OpenAI GPT-4 Vision color extraction service - alternative to Claude"""

import json
import logging
import os

import coloraide
from openai import OpenAI
from pydantic import BaseModel, Field

from copy_that.application import color_utils
from copy_that.application.semantic_color_naming import analyze_color

logger = logging.getLogger(__name__)


class ExtractedColorToken(BaseModel):
    """Color token matching the main extractor format

    Note: This is the Pydantic model for AI-extracted colors.
    For the database model, see domain.models.ColorToken
    """

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

    colors: list[ExtractedColorToken]
    dominant_colors: list[str]
    color_palette: str
    extraction_confidence: float
    extractor_used: str = ""  # Will be set by the endpoint
    background_colors: list[str] = []
    debug: dict | None = None


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
        # Handle both raw base64 and data URL formats
        if image_data.startswith("data:"):
            # Already a data URL, use as-is
            data_url = image_data
        else:
            # Raw base64, construct data URL
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
                response_format={"type": "json_object"},  # Use OpenAI's native JSON mode
                max_tokens=2000,
                temperature=0.3,
            )

            # Parse response - JSON mode guarantees valid JSON
            content = response.choices[0].message.content
            data = json.loads(content)

            # Enrich colors with calculated properties
            enriched_colors = []
            dominant_colors = data.get("dominant_colors", [])

            for color_data in data.get("colors", []):
                hex_color = color_data.get("hex", "#000000")

                # Calculate RGB
                rgb = color_utils.hex_to_rgb(hex_color)
                rgb_str = f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"

                # Compute all color properties using the same helper as Claude extractor
                all_properties, extraction_metadata = (
                    color_utils.compute_all_properties_with_metadata(
                        hex_color, dominant_colors[:3] if dominant_colors else []
                    )
                )

                # Get semantic names
                semantic_names = analyze_color(hex_color)

                # Calculate color harmony with advanced metadata based on palette
                harmony_data = color_utils.get_color_harmony_advanced(
                    hex_color,
                    dominant_colors[:3] if dominant_colors else None,
                    return_metadata=True,
                )
                harmony = (
                    harmony_data.get("harmony") if isinstance(harmony_data, dict) else harmony_data
                )
                harmony_confidence = (
                    harmony_data.get("confidence") if isinstance(harmony_data, dict) else None
                )
                hue_angles = (
                    harmony_data.get("hue_angles") if isinstance(harmony_data, dict) else None
                )

                # Generate state variants (hover/active colors using OKLCH lightness adjustments)
                try:
                    # Extract OKLCH components
                    color_okl = coloraide.Color(hex_color).convert("oklch")
                    l, c_val, h = color_okl["lightness"], color_okl["chroma"], color_okl["hue"]

                    # Create hover (lighter) and active (darker) variants
                    hover_okl = coloraide.Color("oklch", [min(1.0, l + 0.06), c_val, h])
                    active_okl = coloraide.Color("oklch", [max(0.0, l - 0.06), c_val, h])

                    state_variants = {
                        "default": hex_color,
                        "hover": hover_okl.convert("srgb").to_string(hex=True),
                        "active": active_okl.convert("srgb").to_string(hex=True),
                    }
                except Exception as e:
                    logger.warning(
                        "Failed to generate state variants for %s: %s", hex_color, str(e)
                    )
                    state_variants = None

                # Add OpenAI extraction metadata
                extraction_metadata["extractor"] = "openai_gpt4v"
                extraction_metadata["model"] = self.model
                extraction_metadata["design_intent"] = "openai_gpt4v"
                extraction_metadata["name"] = "openai_gpt4v"
                extraction_metadata["confidence"] = "openai_gpt4v"

                enriched_color = ExtractedColorToken(
                    hex=hex_color,
                    rgb=rgb_str,
                    hsl=all_properties.get("hsl"),
                    hsv=all_properties.get("hsv"),
                    name=color_data.get("name", "Unknown"),
                    design_intent=color_data.get("design_intent"),
                    semantic_names=semantic_names,
                    confidence=color_data.get("confidence", 0.8),
                    harmony=harmony,
                    harmony_confidence=harmony_confidence,
                    hue_angles=hue_angles,
                    temperature=all_properties.get("temperature"),
                    saturation_level=all_properties.get("saturation_level"),
                    lightness_level=all_properties.get("lightness_level"),
                    usage=color_data.get("usage", []),
                    prominence_percentage=color_data.get("prominence_percentage"),
                    wcag_contrast_on_white=all_properties.get("wcag_contrast_on_white"),
                    wcag_contrast_on_black=all_properties.get("wcag_contrast_on_black"),
                    wcag_aa_compliant_text=all_properties.get("wcag_aa_compliant_text"),
                    wcag_aaa_compliant_text=all_properties.get("wcag_aaa_compliant_text"),
                    wcag_aa_compliant_normal=all_properties.get("wcag_aa_compliant_normal"),
                    wcag_aaa_compliant_normal=all_properties.get("wcag_aaa_compliant_normal"),
                    colorblind_safe=all_properties.get("colorblind_safe"),
                    tint_color=all_properties.get("tint_color"),
                    shade_color=all_properties.get("shade_color"),
                    tone_color=all_properties.get("tone_color"),
                    closest_web_safe=all_properties.get("closest_web_safe"),
                    closest_css_named=all_properties.get("closest_css_named"),
                    delta_e_to_dominant=all_properties.get("delta_e_to_dominant"),
                    is_neutral=all_properties.get("is_neutral"),
                    state_variants=state_variants,
                    extraction_metadata=extraction_metadata,
                )
                enriched_colors.append(enriched_color)

            # Mark accent colors (requires background color for contrast calculation)
            # For OpenAI extractor, attempt to identify primary background
            primary_bg = None
            if enriched_colors:
                # Use darkest color as potential background
                darkest = min(
                    enriched_colors,
                    key=lambda c: color_utils.relative_luminance(c.hex),
                    default=None,
                )
                primary_bg = darkest.hex if darkest else None

            accent_token = color_utils.select_accent_token(enriched_colors, primary_bg)
            if accent_token:
                accent_hex = getattr(accent_token, "hex", None)
                if accent_hex:
                    for color in enriched_colors:
                        if color.hex == accent_hex:
                            color.is_accent = True

            # Calculate palette diversity
            hex_colors = [c.hex for c in enriched_colors]
            palette_diversity = (
                color_utils.get_perceptual_distance_summary(hex_colors)
                if len(hex_colors) > 1
                else None
            )

            return ColorExtractionResult(
                colors=enriched_colors,
                dominant_colors=data.get("dominant_colors", []),
                color_palette=data.get("color_palette", ""),
                extraction_confidence=0.85,
                palette_diversity=palette_diversity,
            )

        except Exception as e:
            logger.error(f"OpenAI color extraction failed: {e}")
            raise
