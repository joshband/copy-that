"""AI-powered typography extraction service using Claude Sonnet 4.5"""

import base64
import logging
from pathlib import Path

import anthropic
import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ExtractedTypographyToken(BaseModel):
    """Typography token extracted from an image.

    Note: This is the Pydantic model for AI-extracted typography.
    For the database model, see domain.models.TypographyToken
    """

    # Core Typography Properties
    font_family: str = Field(..., description="Font family name (e.g., 'Inter', 'Roboto')")
    font_weight: int = Field(
        ..., ge=100, le=900, description="Font weight (100-900, e.g., 400=regular, 700=bold)"
    )
    font_size: int = Field(..., ge=8, le=120, description="Font size in pixels")
    line_height: float = Field(
        ..., ge=0.8, le=3.0, description="Line height as multiplier (e.g., 1.5)"
    )
    letter_spacing: float | None = Field(
        default=None, ge=-1.0, le=1.0, description="Letter spacing in em units"
    )
    text_transform: str | None = Field(
        default=None,
        description="Text transformation (uppercase, lowercase, capitalize, none)",
    )

    # Design Properties
    semantic_role: str = Field(
        ..., description="Semantic role: heading, subheading, body, caption, label, etc."
    )
    category: str | None = Field(
        default=None,
        description="Category for typography system (display, text, label, mono, etc.)",
    )
    name: str | None = Field(
        default=None, description="Human-readable name (e.g., 'Heading 1', 'Body Text')"
    )

    # Quality Metrics
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score (0-1) for extraction accuracy"
    )
    prominence: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Approximate percentage of text using this typography",
    )

    # Accessibility Properties
    is_readable: bool | None = Field(
        default=None, description="Is this typography readable and accessible?"
    )
    readability_score: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Readability score (0-1)"
    )

    # Advanced Properties
    extraction_metadata: dict | None = Field(
        default=None, description="Metadata about extraction (source, model, etc.)"
    )


class TypographyExtractionResult(BaseModel):
    """Result of typography extraction"""

    tokens: list[ExtractedTypographyToken] = Field(..., description="Extracted typography tokens")
    typography_palette: str | None = Field(
        default=None, description="Overall typography system description"
    )
    extraction_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Overall extraction confidence (0-1)"
    )
    extractor_used: str = Field(
        default="claude-sonnet-4-5", description="AI model used for extraction"
    )
    color_associations: dict | None = Field(
        default=None,
        description="Associated colors for typography (text color, background, etc.)",
    )


class AITypographyExtractor:
    """AI-powered typography extractor using Claude Sonnet 4.5"""

    def __init__(self, api_key: str | None = None):
        """Initialize the typography extractor

        Args:
            api_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY env var
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def extract_typography_from_image_url(
        self, image_url: str, max_tokens: int = 15
    ) -> TypographyExtractionResult:
        """Extract typography from an image URL

        Args:
            image_url: URL of the image to analyze
            max_tokens: Maximum number of typography tokens to extract

        Returns:
            TypographyExtractionResult with extracted typography

        Raises:
            requests.RequestException: If image URL is invalid
            anthropic.APIError: If Claude API call fails
        """
        # Download image and convert to base64
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error("Failed to download image: %s", str(e))
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

        return self.extract_typography_from_base64(image_data, media_type, max_tokens)

    def extract_typography_from_file(
        self, file_path: str, max_tokens: int = 15
    ) -> TypographyExtractionResult:
        """Extract typography from a local image file

        Args:
            file_path: Path to the image file
            max_tokens: Maximum number of typography tokens to extract

        Returns:
            TypographyExtractionResult with extracted typography

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

        return self.extract_typography_from_base64(image_data, media_type, max_tokens)

    def extract_typography_from_base64(
        self, image_data: str, media_type: str, max_tokens: int = 15
    ) -> TypographyExtractionResult:
        """Extract typography from base64-encoded image data

        Args:
            image_data: Base64-encoded image data
            media_type: MIME type of the image (e.g., image/jpeg)
            max_tokens: Maximum number of typography tokens to extract

        Returns:
            TypographyExtractionResult with extracted typography

        Raises:
            anthropic.APIError: If Claude API call fails
        """
        # Handle both raw base64 and data URL formats
        if image_data.startswith("data:"):
            import re

            match = re.match(r"data:([^;]+);base64,(.+)", image_data)
            if match:
                media_type = match.group(1)
                image_data = match.group(2)

        prompt = f"""Analyze this image and extract typography tokens for a design system.

Extract the {max_tokens} most important typography styles that represent the design system.

For each typography style, identify:
1. Font family name (e.g., "Inter", "Roboto", "Georgia")
2. Font weight (100-900: 100=thin, 400=regular, 700=bold, 900=black)
3. Font size in pixels (approximate)
4. Line height as a multiplier (e.g., 1.5 for 150% line height)
5. Letter spacing (if visible, in em units)
6. Text transformation if applied (uppercase, lowercase, capitalize, none)
7. Semantic role: Choose from: heading, subheading, body, caption, label, display, or create a descriptive one (e.g., "nav", "hero", "footer")
8. Category: display, text, label, mono, or other
9. Confidence score (0-1) based on how clearly you can identify the typography
10. Approximate prominence (percentage of text using this style)
11. Is it readable and accessible? (yes/no)

Also provide:
- Overall typography palette description (1-2 sentences)
- Overall extraction confidence (0-1)
- Any color associations (text color, background color, etc.)

Important: Be specific about font family names. Analyze the design intent of each typography style."""

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
            result = self._parse_typography_response(response_text, max_tokens)

            logger.info(
                "Successfully extracted %d typography tokens from image", len(result.tokens)
            )
            return result

        except anthropic.APIError as e:
            logger.error("Claude API error: %s", str(e))
            raise

    def _parse_typography_response(
        self, response_text: str, max_tokens: int
    ) -> TypographyExtractionResult:
        """Parse Claude's response into structured typography data

        Args:
            response_text: Raw text response from Claude
            max_tokens: Maximum number of typography tokens to extract

        Returns:
            TypographyExtractionResult with parsed typography
        """
        import re

        tokens = []

        lines = response_text.split("\n")
        current_token_data = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Extract font family
            if re.search(r"font\s*family", line, re.IGNORECASE):
                match = re.search(r'(["\']?)([A-Za-z\s\-,]+)\1', line)
                if match:
                    current_token_data["font_family"] = match.group(2).strip()
                else:
                    # Try to extract any quoted value or after colon
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        family = parts[1].strip().strip("\"'")
                        if family and family not in ["", "none"]:
                            current_token_data["font_family"] = family

            # Extract font weight
            weight_match = re.search(r"(?:font\s*)?weight[:\s]+(\d{3})", line, re.IGNORECASE)
            if weight_match:
                current_token_data["font_weight"] = int(weight_match.group(1))

            # Extract font size
            size_match = re.search(
                r"(?:font\s*)?size[:\s]+(\d+)\s*(?:px|pixels)?", line, re.IGNORECASE
            )
            if size_match:
                current_token_data["font_size"] = int(size_match.group(1))

            # Extract line height
            lh_match = re.search(r"(?:line\s*)?height[:\s]+([0-9.]+)", line, re.IGNORECASE)
            if lh_match:
                current_token_data["line_height"] = float(lh_match.group(1))

            # Extract letter spacing
            ls_match = re.search(
                r"(?:letter\s*)?spacing[:\s]+([0-9.\-]+)\s*(?:em)?", line, re.IGNORECASE
            )
            if ls_match:
                current_token_data["letter_spacing"] = float(ls_match.group(1))

            # Extract semantic role
            for role in [
                "heading",
                "subheading",
                "body",
                "caption",
                "label",
                "display",
                "nav",
                "hero",
                "footer",
            ]:
                if role.lower() in line.lower():
                    current_token_data["semantic_role"] = role

            # Extract confidence
            conf_match = re.search(r"confidence[:\s]+([0-9.]+)", line, re.IGNORECASE)
            if conf_match:
                current_token_data["confidence"] = float(conf_match.group(1))

            # If we have accumulated enough data for a token, create it
            if (
                "font_family" in current_token_data
                and "font_weight" in current_token_data
                and "font_size" in current_token_data
                and "line_height" in current_token_data
                and "semantic_role" in current_token_data
                and len(tokens) < max_tokens
            ):
                # Set defaults for optional fields
                token_dict = {
                    "font_family": current_token_data.get("font_family", "System"),
                    "font_weight": current_token_data.get("font_weight", 400),
                    "font_size": current_token_data.get("font_size", 16),
                    "line_height": current_token_data.get("line_height", 1.5),
                    "letter_spacing": current_token_data.get("letter_spacing"),
                    "text_transform": current_token_data.get("text_transform"),
                    "semantic_role": current_token_data.get("semantic_role", "body"),
                    "category": current_token_data.get("category"),
                    "name": current_token_data.get("name"),
                    "confidence": min(1.0, current_token_data.get("confidence", 0.8)),
                    "prominence": current_token_data.get("prominence"),
                    "is_readable": current_token_data.get("is_readable"),
                    "readability_score": current_token_data.get("readability_score"),
                    "extraction_metadata": {
                        "model": self.model,
                        "extraction_source": "claude_ai_extractor",
                    },
                }

                try:
                    token = ExtractedTypographyToken(**token_dict)
                    tokens.append(token)
                    current_token_data = {}
                except ValueError as e:
                    logger.warning("Failed to create typography token: %s", str(e))
                    current_token_data = {}

        # If we didn't extract any tokens, create reasonable defaults
        if not tokens:
            logger.warning("No typography parsed from response, using fallback tokens")
            tokens = [
                ExtractedTypographyToken(
                    font_family="System",
                    font_weight=700,
                    font_size=32,
                    line_height=1.2,
                    semantic_role="heading",
                    confidence=0.5,
                    extraction_metadata={
                        "model": self.model,
                        "extraction_source": "fallback",
                    },
                ),
                ExtractedTypographyToken(
                    font_family="System",
                    font_weight=400,
                    font_size=16,
                    line_height=1.6,
                    semantic_role="body",
                    confidence=0.5,
                    extraction_metadata={
                        "model": self.model,
                        "extraction_source": "fallback",
                    },
                ),
            ]

        return TypographyExtractionResult(
            tokens=tokens[:max_tokens],
            typography_palette="Extracted typography system from image",
            extraction_confidence=sum(t.confidence for t in tokens) / len(tokens)
            if tokens
            else 0.5,
            extractor_used=self.model,
        )


# Convenience functions for common use cases
def extract_typography(image_url: str, max_tokens: int = 15) -> TypographyExtractionResult:
    """Quick function to extract typography from an image URL

    Args:
        image_url: URL of the image to analyze
        max_tokens: Maximum number of typography tokens to extract

    Returns:
        TypographyExtractionResult with extracted typography
    """
    extractor = AITypographyExtractor()
    return extractor.extract_typography_from_image_url(image_url, max_tokens)


def extract_typography_from_file(
    file_path: str, max_tokens: int = 15
) -> TypographyExtractionResult:
    """Quick function to extract typography from a local image file

    Args:
        file_path: Path to the image file
        max_tokens: Maximum number of typography tokens to extract

    Returns:
        TypographyExtractionResult with extracted typography
    """
    extractor = AITypographyExtractor()
    return extractor.extract_typography_from_file(file_path, max_tokens)
