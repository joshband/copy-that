"""
AI Spacing Extractor

AI-powered spacing extraction using Claude Sonnet 4.5.
Follows the pattern of AIColorExtractor from color_extractor.py.
"""

import base64
import logging
import re
from collections import Counter
from pathlib import Path

import anthropic
import requests

from .spacing_models import SpacingExtractionResult, SpacingScale, SpacingToken, SpacingType
from .spacing_utils import compute_all_spacing_properties_with_metadata

logger = logging.getLogger(__name__)


class AISpacingExtractor:
    """
    AI-powered spacing extractor using Claude Sonnet 4.5.

    Follows the pattern of AIColorExtractor from copy_that.application.color_extractor.

    Example:
        >>> extractor = AISpacingExtractor()
        >>> result = extractor.extract_spacing_from_image_url(
        ...     "https://example.com/design.png",
        ...     max_tokens=15
        ... )
        >>> print(f"Found {len(result.tokens)} spacing values")
        >>> print(f"Base unit: {result.base_unit}px")
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize the spacing extractor.

        Args:
            api_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY env var
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def extract_spacing_from_image_url(
        self, image_url: str, max_tokens: int = 15
    ) -> SpacingExtractionResult:
        """
        Extract spacing tokens from an image URL.

        Args:
            image_url: URL of the image to analyze
            max_tokens: Maximum number of spacing tokens to extract

        Returns:
            SpacingExtractionResult with extracted tokens

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

        return self.extract_spacing_from_base64(image_data, media_type, max_tokens)

    def extract_spacing_from_file(
        self, file_path: str, max_tokens: int = 15
    ) -> SpacingExtractionResult:
        """
        Extract spacing tokens from a local image file.

        Args:
            file_path: Path to the image file
            max_tokens: Maximum number of spacing tokens to extract

        Returns:
            SpacingExtractionResult with extracted tokens

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

        return self.extract_spacing_from_base64(image_data, media_type, max_tokens)

    def extract_spacing_from_base64(
        self, image_data: str, media_type: str, max_tokens: int = 15
    ) -> SpacingExtractionResult:
        """
        Extract spacing tokens from base64-encoded image data.

        Args:
            image_data: Base64-encoded image data
            media_type: MIME type of the image (e.g., image/jpeg)
            max_tokens: Maximum number of spacing tokens to extract

        Returns:
            SpacingExtractionResult with extracted tokens

        Raises:
            anthropic.APIError: If Claude API call fails
        """
        prompt = self._build_extraction_prompt(max_tokens)

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
            result = self._parse_spacing_response(response_text, max_tokens)

            logger.info(f"Successfully extracted {len(result.tokens)} spacing values from image")
            return result

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise

    def _build_extraction_prompt(self, max_tokens: int) -> str:
        """
        Build the extraction prompt for Claude.

        Args:
            max_tokens: Maximum number of tokens to request

        Returns:
            Formatted prompt string
        """
        return f"""Analyze this UI/design image and extract the spacing system used.

Identify up to {max_tokens} distinct spacing values that represent the design's spacing scale.

For each spacing value, provide:
1. Value in pixels (e.g., 4, 8, 16, 24, 32)
2. Suggested token name (e.g., "spacing-xs", "spacing-sm", "gap-md", "padding-lg")
3. Semantic role - choose from: margin, padding, gap, inset, stack, inline, section, component, element
4. Usage context (e.g., "between buttons", "card padding", "section margins")
5. Confidence score (0-1) based on how clearly the spacing is detected

Also analyze:
- The overall scale system (4pt grid, 8pt grid, fibonacci, golden ratio, custom)
- The base unit of the scale (e.g., 4px, 8px)
- What percentage of detected values align to the grid

Format each spacing as:
SPACING: [value]px | [name] | [role] | [usage] | confidence: [score]

Then provide:
SCALE_SYSTEM: [system type]
BASE_UNIT: [unit]px
GRID_COMPLIANCE: [percentage]%

Important:
- Look for consistent patterns (margins, paddings, gaps between elements)
- Identify the most common spacing values
- Note any spacing that appears to deviate from the grid
- Focus on intentional design spacing, not arbitrary values"""

    def _parse_spacing_response(
        self, response_text: str, max_tokens: int
    ) -> SpacingExtractionResult:
        """
        Parse Claude's response into structured spacing data.

        Args:
            response_text: Raw text response from Claude
            max_tokens: Maximum number of tokens to extract

        Returns:
            SpacingExtractionResult with parsed tokens
        """
        tokens = []
        unique_values = set()
        scale_system = SpacingScale.CUSTOM
        base_unit = 8  # Default
        grid_compliance = 0.8  # Default

        lines = response_text.split("\n")

        for line in lines:
            # Parse spacing entries
            if line.strip().startswith("SPACING:"):
                token = self._parse_spacing_line(line)
                if token and len(tokens) < max_tokens:
                    tokens.append(token)
                    unique_values.add(token.value_px)

            # Parse scale system
            elif "SCALE_SYSTEM:" in line:
                system_match = re.search(r"SCALE_SYSTEM:\s*(.+)", line)
                if system_match:
                    system_str = system_match.group(1).strip().lower()
                    scale_system = self._parse_scale_system(system_str)

            # Parse base unit
            elif "BASE_UNIT:" in line:
                unit_match = re.search(r"BASE_UNIT:\s*(\d+)", line)
                if unit_match:
                    base_unit = int(unit_match.group(1))

            # Parse grid compliance
            elif "GRID_COMPLIANCE:" in line:
                compliance_match = re.search(r"GRID_COMPLIANCE:\s*(\d+(?:\.\d+)?)", line)
                if compliance_match:
                    grid_compliance = float(compliance_match.group(1)) / 100

        # Fallback: extract any pixel values mentioned
        if not tokens:
            logger.warning("No structured spacing found, falling back to regex extraction")
            tokens = self._fallback_extraction(response_text, max_tokens)
            unique_values = {t.value_px for t in tokens}

        # Compute all properties for each token
        all_values = list(unique_values)
        for token in tokens:
            properties, metadata = compute_all_spacing_properties_with_metadata(
                token.value_px, all_values
            )

            # Update token with computed properties
            token.scale_position = properties.get("scale_position")
            token.scale_system = scale_system
            token.base_unit = base_unit
            token.grid_aligned = properties.get("grid_aligned")
            token.grid_deviation_px = properties.get("grid_deviation_px")
            token.responsive_scales = properties.get("responsive_scales")
            token.extraction_metadata = metadata
            token.extraction_metadata["semantic_role"] = "claude_ai_extractor"

        # Create result
        sorted_values = sorted(unique_values)

        return SpacingExtractionResult(
            tokens=tokens[:max_tokens],
            scale_system=scale_system,
            base_unit=base_unit,
            grid_compliance=grid_compliance,
            extraction_confidence=sum(t.confidence for t in tokens) / len(tokens)
            if tokens
            else 0.5,
            min_spacing=min(sorted_values) if sorted_values else 0,
            max_spacing=max(sorted_values) if sorted_values else 0,
            unique_values=sorted_values,
        )

    def _parse_spacing_line(self, line: str) -> SpacingToken | None:
        """
        Parse a single spacing line from the response.

        Expected format:
        SPACING: 16px | spacing-md | padding | card padding | confidence: 0.92

        Args:
            line: Line to parse

        Returns:
            SpacingToken or None if parsing fails
        """
        try:
            # Remove "SPACING:" prefix
            content = line.replace("SPACING:", "").strip()

            # Split by pipe
            parts = [p.strip() for p in content.split("|")]

            if len(parts) < 2:
                return None

            # Parse value (first part)
            value_match = re.search(r"(\d+)", parts[0])
            if not value_match:
                return None
            value_px = int(value_match.group(1))

            # Parse name (second part)
            name = parts[1] if len(parts) > 1 else f"spacing-{value_px}"

            # Parse role (third part)
            semantic_role = parts[2] if len(parts) > 2 else None
            spacing_type = self._parse_spacing_type(semantic_role) if semantic_role else None

            # Parse usage (fourth part)
            usage = [parts[3]] if len(parts) > 3 and "confidence" not in parts[3].lower() else []

            # Parse confidence (last part or default)
            confidence = 0.85
            for part in parts:
                conf_match = re.search(r"confidence[:\s]+([0-9.]+)", part, re.IGNORECASE)
                if conf_match:
                    confidence = float(conf_match.group(1))
                    break

            return SpacingToken(
                value_px=value_px,
                name=name,
                semantic_role=semantic_role,
                spacing_type=spacing_type,
                confidence=min(1.0, confidence),
                usage=usage,
            )

        except Exception as e:
            logger.warning(f"Failed to parse spacing line '{line}': {e}")
            return None

    def _parse_spacing_type(self, role: str) -> SpacingType | None:
        """Map semantic role string to SpacingType enum."""
        role_lower = role.lower()

        type_map = {
            "margin": SpacingType.MARGIN,
            "padding": SpacingType.PADDING,
            "gap": SpacingType.GAP,
            "inset": SpacingType.INSET,
            "stack": SpacingType.STACK,
            "inline": SpacingType.INLINE,
            "section": SpacingType.SECTION,
            "component": SpacingType.COMPONENT,
            "element": SpacingType.ELEMENT,
            "border": SpacingType.BORDER,
            "radius": SpacingType.RADIUS,
        }

        for key, value in type_map.items():
            if key in role_lower:
                return value

        return None

    def _parse_scale_system(self, system_str: str) -> SpacingScale:
        """Map scale system string to SpacingScale enum."""
        if "4pt" in system_str or "4-point" in system_str:
            return SpacingScale.FOUR_POINT
        elif "8pt" in system_str or "8-point" in system_str:
            return SpacingScale.EIGHT_POINT
        elif "golden" in system_str:
            return SpacingScale.GOLDEN_RATIO
        elif "fibonacci" in system_str or "fib" in system_str:
            return SpacingScale.FIBONACCI
        elif "linear" in system_str:
            return SpacingScale.LINEAR
        elif "exponential" in system_str or "exp" in system_str:
            return SpacingScale.EXPONENTIAL
        else:
            return SpacingScale.CUSTOM

    def _fallback_extraction(self, response_text: str, max_tokens: int) -> list[SpacingToken]:
        """
        Fallback extraction using regex to find pixel values.

        Args:
            response_text: Raw response text
            max_tokens: Maximum tokens to extract

        Returns:
            List of SpacingToken objects
        """
        # Find all pixel values mentioned
        px_matches = re.findall(r"(\d+)\s*(?:px|pixels?)", response_text, re.IGNORECASE)

        # Count occurrences and filter
        value_counts = Counter(int(m) for m in px_matches)

        # Get most common values
        common_values = value_counts.most_common(max_tokens)

        tokens = []
        for value, count in common_values:
            if 0 < value <= 200:  # Reasonable spacing range
                token = SpacingToken(
                    value_px=value,
                    name=f"spacing-{value}",
                    confidence=min(0.7, 0.5 + (count * 0.05)),  # Higher count = higher confidence
                    count=count,
                )
                tokens.append(token)

        return tokens


# Convenience functions for common use cases


def extract_spacing(image_url: str, max_tokens: int = 15) -> SpacingExtractionResult:
    """
    Quick function to extract spacing from an image URL.

    Args:
        image_url: URL of the image to analyze
        max_tokens: Maximum number of spacing tokens to extract

    Returns:
        SpacingExtractionResult with extracted tokens
    """
    extractor = AISpacingExtractor()
    return extractor.extract_spacing_from_image_url(image_url, max_tokens)


def extract_spacing_from_file(file_path: str, max_tokens: int = 15) -> SpacingExtractionResult:
    """
    Quick function to extract spacing from a local image file.

    Args:
        file_path: Path to the image file
        max_tokens: Maximum number of spacing tokens to extract

    Returns:
        SpacingExtractionResult with extracted tokens
    """
    extractor = AISpacingExtractor()
    return extractor.extract_spacing_from_file(file_path, max_tokens)
