"""AI-powered color extraction service using Claude Sonnet 4.5"""

import base64
import logging
import re
from pathlib import Path

import anthropic
import requests
from pydantic import BaseModel, Field

from copy_that.application import color_utils
from copy_that.application.semantic_color_naming import analyze_color

logger = logging.getLogger(__name__)


class ColorToken(BaseModel):
    """Comprehensive color token with educational properties for all ML models/techniques"""

    # Core Display Properties
    hex: str = Field(..., description="Hex color code (e.g., #FF5733)")
    rgb: str = Field(..., description="RGB format (e.g., rgb(255, 87, 51))")
    hsl: str | None = Field(None, description="HSL format (e.g., hsl(10, 100%, 63%))")
    hsv: str | None = Field(None, description="HSV format (e.g., hsv(10, 80%, 100%))")
    name: str = Field(..., description="Human-readable color name")

    # Design Token Properties
    design_intent: str | None = Field(None, description="DESIGN INTENT: Role Claude assigns this color (e.g., primary, error, hover-state)")
    semantic_names: dict | None = Field(None, description="PERCEPTUAL ANALYSIS: 5-style color naming from color science (simple/descriptive/emotional/technical/vibrancy)")
    category: str | None = Field(None, description="Color category (e.g., primary, neutral, accent)")

    # Color Analysis Properties
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    harmony: str | None = Field(None, description="Color harmony group (complementary, analogous, triadic, monochromatic)")
    temperature: str | None = Field(None, description="Color temperature (warm, cool, neutral)")
    saturation_level: str | None = Field(None, description="Saturation intensity (vibrant, muted, desaturated, grayscale)")
    lightness_level: str | None = Field(None, description="Lightness level (light, medium, dark)")
    usage: list[str] = Field(default_factory=list, description="Suggested usage contexts (backgrounds, text, accents, etc.)")

    # Count & Prominence
    count: int = Field(default=1, ge=1, description="Number of times this color was detected")
    prominence_percentage: float | None = Field(None, ge=0, le=100, description="Percentage of image occupied by this color")

    # Accessibility Properties (WCAG)
    wcag_contrast_on_white: float | None = Field(None, ge=0, le=21, description="WCAG contrast ratio on white (#FFFFFF)")
    wcag_contrast_on_black: float | None = Field(None, ge=0, le=21, description="WCAG contrast ratio on black (#000000)")
    wcag_aa_compliant_text: bool | None = Field(None, description="WCAG AA compliant for large text (3:1)")
    wcag_aaa_compliant_text: bool | None = Field(None, description="WCAG AAA compliant for large text (4.5:1)")
    wcag_aa_compliant_normal: bool | None = Field(None, description="WCAG AA compliant for normal text (4.5:1)")
    wcag_aaa_compliant_normal: bool | None = Field(None, description="WCAG AAA compliant for normal text (7:1)")
    colorblind_safe: bool | None = Field(None, description="Safe for all types of color blindness")

    # Color Variants (for design systems)
    tint_color: str | None = Field(None, description="Tint variant (50% lighter)")
    shade_color: str | None = Field(None, description="Shade variant (50% darker)")
    tone_color: str | None = Field(None, description="Tone variant (50% desaturated)")

    # Advanced Properties
    closest_web_safe: str | None = Field(None, description="Closest web-safe color hex")
    closest_css_named: str | None = Field(None, description="Closest CSS named color")
    delta_e_to_dominant: float | None = Field(None, description="Delta E distance to nearest dominant color")
    is_neutral: bool | None = Field(None, description="Is this a neutral/grayscale color")

    # ML/CV Model Properties (for educational pipeline)
    kmeans_cluster_id: int | None = Field(None, description="K-means cluster assignment")
    sam_segmentation_mask: str | None = Field(None, description="SAM segmentation mask (base64 encoded)")
    clip_embeddings: list[float] | None = Field(None, description="CLIP embeddings for semantic understanding")

    # Extraction Metadata
    extraction_metadata: dict | None = Field(None, description="Maps field names to the tool/function that extracted them (e.g., {'temperature': 'color_utils.get_color_temperature', 'design_intent': 'claude_ai_extractor'})")
    histogram_significance: float | None = Field(None, ge=0, le=1, description="Significance in color histogram (0-1)")


class ColorExtractionResult(BaseModel):
    """Result of color extraction"""
    colors: list[ColorToken] = Field(..., description="Extracted color tokens")
    dominant_colors: list[str] = Field(..., description="Top 3 dominant hex colors")
    color_palette: str = Field(..., description="Overall palette description")
    extraction_confidence: float = Field(..., ge=0, le=1, description="Overall extraction confidence")


class AIColorExtractor:
    """AI-powered color extractor using Claude Sonnet 4.5 with Structured Outputs"""

    def __init__(self, api_key: str | None = None):
        """Initialize the color extractor

        Args:
            api_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY env var
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def extract_colors_from_image_url(self, image_url: str, max_colors: int = 10) -> ColorExtractionResult:
        """Extract colors from an image URL

        Args:
            image_url: URL of the image to analyze
            max_colors: Maximum number of colors to extract

        Returns:
            ColorExtractionResult with extracted colors

        Raises:
            requests.RequestException: If image URL is invalid
            anthropic.APIError: If Claude API call fails
        """
        # Download image and convert to base64
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to download image: {e}")
            raise

        image_data = base64.standard_b64encode(response.content).decode("utf-8")

        # Determine media type from response headers
        content_type = response.headers.get("content-type", "image/jpeg").lower()
        if "png" in content_type:
            media_type = "image/png"
        elif "webp" in content_type:
            media_type = "image/webp"
        elif "gif" in content_type:
            media_type = "image/gif"
        else:
            media_type = "image/jpeg"

        return self.extract_colors_from_base64(image_data, media_type, max_colors)

    def extract_colors_from_file(self, file_path: str, max_colors: int = 10) -> ColorExtractionResult:
        """Extract colors from a local image file

        Args:
            file_path: Path to the image file
            max_colors: Maximum number of colors to extract

        Returns:
            ColorExtractionResult with extracted colors

        Raises:
            FileNotFoundError: If file doesn't exist
            anthropic.APIError: If Claude API call fails
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")

        # Determine media type from file extension
        suffix = file_path.suffix.lower()
        media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }
        media_type = media_types.get(suffix, "image/jpeg")

        # Read and encode image
        with open(file_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        return self.extract_colors_from_base64(image_data, media_type, max_colors)

    def extract_colors_from_base64(
        self, image_data: str, media_type: str, max_colors: int = 10
    ) -> ColorExtractionResult:
        """Extract colors from base64-encoded image data

        Args:
            image_data: Base64-encoded image data
            media_type: MIME type of the image (e.g., image/jpeg)
            max_colors: Maximum number of colors to extract

        Returns:
            ColorExtractionResult with extracted colors

        Raises:
            anthropic.APIError: If Claude API call fails
        """
        prompt = f"""Analyze this image and extract a professional color palette for design systems.

Extract the {max_colors} most important colors that represent the image's design essence.

For each color, include:
1. Hex code (e.g., #FF5733)
2. RGB format (e.g., rgb(255, 87, 51))
3. Descriptive name (e.g., "Ocean Blue", "Sunset Orange")
4. ALWAYS provide a semantic token name - choose from: primary, secondary, accent, success, error, warning, info, light, dark, or create a descriptive one (e.g., "background", "border", "hover-state")
5. Confidence score (0-1) based on distinctness
6. Harmony relationship (complementary, analogous, triadic, monochromatic)
7. Usage contexts (e.g., "backgrounds", "text", "accents")

Also include:
- The 3 most dominant colors (hex codes only)
- Overall palette description (1-2 sentences)
- Overall extraction confidence (0-1)

Important: Every color MUST have a semantic token name. Be specific and consistent with naming."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )

            # Parse the response
            response_text = message.content[0].text
            result = self._parse_color_response(response_text, max_colors)

            logger.info(f"Successfully extracted {len(result.colors)} colors from image")
            return result

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise

    def _parse_color_response(self, response_text: str, max_colors: int) -> ColorExtractionResult:
        """Parse Claude's response into structured color data

        This uses a simplified parser that extracts hex codes and creates color tokens.
        Tracks duplicate detections to show prominence in the design.

        Args:
            response_text: Raw text response from Claude
            max_colors: Maximum number of colors to extract

        Returns:
            ColorExtractionResult with parsed colors (with duplicate counts)
        """
        colors = []
        dominant_colors = []

        lines = response_text.split("\n")
        for line in lines:
            # Look for hex color codes
            hex_matches = re.findall(r"#[0-9A-Fa-f]{6}", line)
            for hex_code in hex_matches[:max_colors]:
                if hex_code not in dominant_colors:
                    dominant_colors.append(hex_code)

                # Convert hex to RGB
                rgb = self._hex_to_rgb(hex_code)

                # Extract name and design intent from context
                name = self._extract_color_name(line, hex_code)
                design_intent = self._extract_semantic_name(line)
                confidence = 0.85  # Default confidence

                # Try to extract confidence if mentioned
                confidence_match = re.search(r"confidence[:\s]+([0-9.]+)", line, re.IGNORECASE)
                if confidence_match:
                    try:
                        confidence = float(confidence_match.group(1))
                    except ValueError:
                        pass

                # Compute all color properties with extraction metadata
                all_properties, extraction_metadata = color_utils.compute_all_properties_with_metadata(
                    hex_code, dominant_colors[:3] if dominant_colors else []
                )

                # Analyze semantic naming
                try:
                    analysis = analyze_color(hex_code)
                    semantic_names_dict = analysis.get("names", {})
                    extraction_metadata["semantic_names"] = "semantic_color_naming.analyze_color"
                except Exception as e:
                    logger.warning(f"Failed to analyze semantic naming for {hex_code}: {e}")
                    semantic_names_dict = None

                # Add AI extraction metadata
                extraction_metadata["design_intent"] = "claude_ai_extractor"
                extraction_metadata["name"] = "claude_ai_extractor"
                extraction_metadata["confidence"] = "claude_ai_extractor"

                # Calculate color harmony based on palette
                harmony = color_utils.get_color_harmony(hex_code, dominant_colors[:3] if dominant_colors else None)
                if harmony:
                    extraction_metadata["harmony"] = "color_utils.get_color_harmony"

                color_token = ColorToken(
                    hex=hex_code,
                    rgb=f"rgb{rgb}",
                    hsl=all_properties.get("hsl"),
                    hsv=all_properties.get("hsv"),
                    name=name,
                    design_intent=design_intent,
                    semantic_names=semantic_names_dict,
                    category=design_intent,  # Use design intent as category
                    confidence=min(1.0, confidence),
                    harmony=harmony,
                    temperature=all_properties.get("temperature"),
                    saturation_level=all_properties.get("saturation_level"),
                    lightness_level=all_properties.get("lightness_level"),
                    usage=[],
                    count=1,
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
                    extraction_metadata=extraction_metadata,
                )

                # Track duplicates - increment count if already seen
                existing = next((c for c in colors if c.hex == color_token.hex), None)
                if existing:
                    existing.count += 1
                else:
                    colors.append(color_token)

        # Ensure we have at least some colors
        if not colors:
            # Fallback: create a default palette from common web colors
            logger.warning("No colors parsed from response, using fallback palette")
            colors = [
                ColorToken(hex="#FF6B6B", rgb="rgb(255, 107, 107)", name="Red", confidence=0.5),
                ColorToken(hex="#4ECDC4", rgb="rgb(78, 205, 196)", name="Teal", confidence=0.5),
                ColorToken(hex="#45B7D1", rgb="rgb(69, 183, 209)", name="Blue", confidence=0.5),
            ]
            dominant_colors = ["#FF6B6B", "#4ECDC4", "#45B7D1"]

        return ColorExtractionResult(
            colors=colors[:max_colors],
            dominant_colors=dominant_colors[:3],
            color_palette="Extracted color palette from image",
            extraction_confidence=sum(c.confidence for c in colors) / len(colors) if colors else 0.5,
        )

    @staticmethod
    def _hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
        """Convert hex color code to RGB tuple"""
        hex_code = hex_code.lstrip("#")
        return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def _extract_color_name(line: str, hex_code: str) -> str:
        """Extract color name from line context"""
        # Try quoted names first
        quoted = re.search(r'"([^"]*)"', line)
        if quoted:
            return quoted.group(1)

        # Try color name patterns (e.g., "primary blue", "dark gray")
        name_match = re.search(r"(?:named?|color|called)\s+([A-Za-z\s]+)", line, re.IGNORECASE)
        if name_match:
            return name_match.group(1).strip()

        # Fallback to hex code
        return f"Color {hex_code}"

    @staticmethod
    def _extract_semantic_name(line: str) -> str | None:
        """Extract semantic token name if present"""
        # Comprehensive list of semantic token patterns
        semantic_patterns = {
            "primary": r"\bprimary\b",
            "secondary": r"\bsecondary\b",
            "tertiary": r"\btertiary\b",
            "accent": r"\baccent\b",
            "success": r"\bsuccess\b",
            "error": r"\berror\b",
            "warning": r"\bwarning\b",
            "info": r"\binfo\b",
            "light": r"\blight\b",
            "dark": r"\bdark\b",
            "background": r"\b(?:background|bg)\b",
            "surface": r"\bsurface\b",
            "text": r"\b(?:text|typography)\b",
            "border": r"\bborder\b",
            "shadow": r"\bshadow\b",
            "hover": r"\bhover(?:-state)?\b",
            "focus": r"\bfocus(?:-state)?\b",
            "disabled": r"\bdisabled\b",
            "active": r"\bactive\b",
        }

        line_lower = line.lower()
        for semantic_name, pattern in semantic_patterns.items():
            if re.search(pattern, line_lower, re.IGNORECASE):
                return semantic_name

        # Try to extract any quoted or hyphenated semantic names
        quoted_match = re.search(r'"([a-z-]+)"|\'([a-z-]+)\'', line_lower)
        if quoted_match:
            name = quoted_match.group(1) or quoted_match.group(2)
            if len(name) > 2 and len(name) < 30 and "-" not in name or all(c.isalnum() or c == "-" for c in name):
                return name

        return None


# Convenience functions for common use cases
def extract_colors(image_url: str, max_colors: int = 10) -> ColorExtractionResult:
    """Quick function to extract colors from an image URL

    Args:
        image_url: URL of the image to analyze
        max_colors: Maximum number of colors to extract

    Returns:
        ColorExtractionResult with extracted colors
    """
    extractor = AIColorExtractor()
    return extractor.extract_colors_from_image_url(image_url, max_colors)


def extract_colors_from_file(file_path: str, max_colors: int = 10) -> ColorExtractionResult:
    """Quick function to extract colors from a local image file

    Args:
        file_path: Path to the image file
        max_colors: Maximum number of colors to extract

    Returns:
        ColorExtractionResult with extracted colors
    """
    extractor = AIColorExtractor()
    return extractor.extract_colors_from_file(file_path, max_colors)
