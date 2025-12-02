"""AI-powered shadow extraction service using Claude Sonnet 4.5"""

import logging

import anthropic
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ExtractedShadowToken(BaseModel):
    """Shadow token extracted from UI images using AI"""

    # Shadow positioning
    x_offset: float = Field(..., description="Horizontal offset in pixels")
    y_offset: float = Field(..., description="Vertical offset in pixels")
    blur_radius: float = Field(..., description="Blur radius in pixels")
    spread_radius: float = Field(default=0.0, description="Spread radius in pixels")

    # Shadow color and opacity
    color_hex: str = Field(..., description="Shadow color in hex format (e.g., #000000)")
    opacity: float = Field(..., ge=0, le=1, description="Shadow opacity 0-1")

    # Classification
    shadow_type: str = Field(..., description="Type: 'drop', 'inner', or 'text'")
    semantic_name: str = Field(
        ..., description="Human-readable name (e.g., 'subtle-drop', 'strong-inner')"
    )

    # Quality metrics
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    is_inset: bool = Field(default=False, description="Is this an inset/inner shadow")
    affects_text: bool = Field(default=False, description="Does this shadow apply to text")


class ShadowExtractionResult(BaseModel):
    """Result of shadow extraction from an image"""

    shadows: list[ExtractedShadowToken] = Field(default_factory=list)
    shadow_count: int = Field(default=0)
    extraction_confidence: float = Field(default=0.0)
    extractor_used: str = "ai_claude_sonnet"


class AIShadowExtractor:
    """Extract shadows from UI images using Claude Sonnet 4.5 with vision"""

    def __init__(self, api_key: str | None = None):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-1-20250805"

    def extract_shadows(
        self,
        image_url: str | None = None,
        base64_image: str | None = None,
        media_type: str = "image/png",
    ) -> ShadowExtractionResult:
        """
        Extract shadows from an image using Claude vision.

        Args:
            image_url: HTTP URL to image
            base64_image: Base64-encoded image data
            media_type: Media type (image/png, image/jpeg, etc.)

        Returns:
            ShadowExtractionResult with detected shadows
        """
        if not image_url and not base64_image:
            logger.warning("No image provided to shadow extractor")
            return ShadowExtractionResult(shadow_count=0, extraction_confidence=0.0)

        try:
            # Build vision content
            image_content = None
            if image_url:
                image_content = {
                    "type": "image",
                    "source": {"type": "url", "url": image_url},
                }
            elif base64_image:
                image_content = {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": base64_image,
                    },
                }

            # Call Claude with Structured Outputs
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                thinking={"type": "enabled", "budget_tokens": 2000},
                messages=[
                    {
                        "role": "user",
                        "content": [
                            image_content,
                            {
                                "type": "text",
                                "text": """Analyze this UI image and extract all shadows.

For each shadow detected, provide:
1. x_offset: Horizontal distance (positive = right, negative = left)
2. y_offset: Vertical distance (positive = down, negative = up)
3. blur_radius: How blurred the shadow edge is
4. spread_radius: How much the shadow extends beyond its source
5. color_hex: Shadow color (usually dark, like #000000)
6. opacity: Shadow transparency (0.0-1.0)
7. shadow_type: 'drop' (below), 'inner' (inset), or 'text' (on text)
8. semantic_name: Short descriptive name (e.g., 'subtle-drop', 'card-shadow', 'text-glow')
9. confidence: How confident you are (0.0-1.0)
10. is_inset: True if this is an inset shadow
11. affects_text: True if this shadow is on text elements

Look for:
- Drop shadows on cards, buttons, floating elements
- Inner shadows (inset)
- Text shadows on headings/labels
- Subtle shadows for depth
- Strong shadows for emphasis

Return 'shadows': [] if no shadows detected.""",
                            },
                        ],
                    }
                ],
                response_model={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "ShadowExtractionResult",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "shadows": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "x_offset": {"type": "number"},
                                            "y_offset": {"type": "number"},
                                            "blur_radius": {"type": "number"},
                                            "spread_radius": {"type": "number"},
                                            "color_hex": {"type": "string"},
                                            "opacity": {"type": "number"},
                                            "shadow_type": {"type": "string"},
                                            "semantic_name": {"type": "string"},
                                            "confidence": {"type": "number"},
                                            "is_inset": {"type": "boolean"},
                                            "affects_text": {"type": "boolean"},
                                        },
                                        "required": [
                                            "x_offset",
                                            "y_offset",
                                            "blur_radius",
                                            "spread_radius",
                                            "color_hex",
                                            "opacity",
                                            "shadow_type",
                                            "semantic_name",
                                            "confidence",
                                            "is_inset",
                                            "affects_text",
                                        ],
                                    },
                                }
                            },
                            "required": ["shadows"],
                        },
                    },
                },
            )

            # Parse response
            if not response.content or not response.content[0]:
                logger.warning("Empty response from Claude shadow extractor")
                return ShadowExtractionResult(shadow_count=0, extraction_confidence=0.0)

            # Extract structured data
            content = response.content[0]
            if content.type != "text":
                logger.warning(f"Unexpected response type: {content.type}")
                return ShadowExtractionResult(shadow_count=0, extraction_confidence=0.0)

            import json

            data = json.loads(content.text)

            # Validate and convert
            shadows = []
            total_confidence = 0.0

            for shadow_data in data.get("shadows", []):
                try:
                    shadow = ExtractedShadowToken(**shadow_data)
                    shadows.append(shadow)
                    total_confidence += shadow.confidence
                except Exception as e:
                    logger.warning(f"Failed to parse shadow: {e}")
                    continue

            avg_confidence = total_confidence / len(shadows) if shadows else 0.0

            result = ShadowExtractionResult(
                shadows=shadows,
                shadow_count=len(shadows),
                extraction_confidence=avg_confidence,
                extractor_used="ai_claude_sonnet",
            )

            logger.info(
                f"Extracted {len(shadows)} shadows with avg confidence {avg_confidence:.2f}"
            )
            return result

        except Exception as e:
            logger.exception(f"Shadow extraction failed: {e}")
            return ShadowExtractionResult(shadow_count=0, extraction_confidence=0.0)

    def extract_shadows_streaming(
        self,
        image_url: str | None = None,
        base64_image: str | None = None,
        media_type: str = "image/png",
    ):
        """Streaming version of shadow extraction (yields partial results)"""
        # For now, just call the batch version
        # TODO: Implement actual streaming
        yield self.extract_shadows(image_url, base64_image, media_type)
