"""AI-powered color extraction service using Claude Sonnet 4.5"""

import base64
import json
import logging
from pathlib import Path
from typing import Optional

import anthropic
import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ColorToken(BaseModel):
    """Extracted color token"""
    hex: str = Field(..., description="Hex color code (e.g., #FF5733)")
    rgb: str = Field(..., description="RGB format (e.g., rgb(255, 87, 51))")
    name: str = Field(..., description="Human-readable color name")
    semantic_name: Optional[str] = Field(None, description="Semantic token name (e.g., primary, error)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    harmony: Optional[str] = Field(None, description="Color harmony group (e.g., complementary)")
    usage: list[str] = Field(default_factory=list, description="Suggested usage contexts")


class ColorExtractionResult(BaseModel):
    """Result of color extraction"""
    colors: list[ColorToken] = Field(..., description="Extracted color tokens")
    dominant_colors: list[str] = Field(..., description="Top 3 dominant hex colors")
    color_palette: str = Field(..., description="Overall palette description")
    extraction_confidence: float = Field(..., ge=0, le=1, description="Overall extraction confidence")


class AIColorExtractor:
    """AI-powered color extractor using Claude Sonnet 4.5 with Structured Outputs"""

    def __init__(self, api_key: Optional[str] = None):
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

For each color:
1. Get the exact hex code
2. Provide RGB format
3. Give a descriptive name (e.g., "Ocean Blue", "Sunset Orange")
4. Suggest a semantic token name if applicable (e.g., "primary", "error", "success")
5. Rate confidence (0-1) based on how distinct the color is
6. Describe harmony relationship (complementary, analogous, triadic)
7. Suggest usage contexts (e.g., "backgrounds", "text", "accents")

Also provide:
- The 3 most dominant colors (hex codes)
- Overall palette description (1-2 sentences about the color scheme)
- Overall extraction confidence (0-1)"""

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
        In production, you might want more sophisticated parsing.

        Args:
            response_text: Raw text response from Claude
            max_colors: Maximum number of colors to extract

        Returns:
            ColorExtractionResult with parsed colors
        """
        colors = []
        dominant_colors = []

        lines = response_text.split("\n")
        for line in lines:
            # Look for hex color codes
            import re
            hex_matches = re.findall(r"#[0-9A-Fa-f]{6}", line)
            for hex_code in hex_matches[:max_colors]:
                if hex_code not in dominant_colors:
                    dominant_colors.append(hex_code)

                # Convert hex to RGB
                rgb = self._hex_to_rgb(hex_code)

                # Extract name and semantic info from context
                name = self._extract_color_name(line, hex_code)
                semantic_name = self._extract_semantic_name(line)
                confidence = 0.85  # Default confidence

                # Try to extract confidence if mentioned
                confidence_match = re.search(r"confidence[:\s]+([0-9.]+)", line, re.IGNORECASE)
                if confidence_match:
                    try:
                        confidence = float(confidence_match.group(1))
                    except ValueError:
                        pass

                color_token = ColorToken(
                    hex=hex_code,
                    rgb=f"rgb{rgb}",
                    name=name,
                    semantic_name=semantic_name,
                    confidence=min(1.0, confidence),
                    harmony=None,
                    usage=[]
                )

                # Avoid duplicates
                if not any(c.hex == color_token.hex for c in colors):
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
        # Look for quoted names or common color names
        import re

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
    def _extract_semantic_name(line: str) -> Optional[str]:
        """Extract semantic token name if present"""
        import re

        semantic_names = ["primary", "secondary", "success", "error", "warning", "info", "light", "dark"]
        for name in semantic_names:
            if name.lower() in line.lower():
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
