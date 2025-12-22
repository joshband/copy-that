"""AI-powered typography extraction service using Claude Sonnet 4.5."""

from __future__ import annotations

import base64
import logging
import re
from pathlib import Path

import anthropic
import requests
from pydantic import BaseModel, Field

from copy_that.application.perf import track_perf
from copy_that.infrastructure.cache.extraction_cache import (
    compute_input_hash,
    get_extraction_cache,
)

logger = logging.getLogger(__name__)


class ExtractedTypographyToken(BaseModel):
    """Typography token extracted from an image.

    Note: This is the Pydantic model for AI-extracted typography.
    For the database model, see domain.typography.TypographyToken.
    """

    model_config = {"validate_assignment": True}

    # Core Typography Properties
    font_family: str = Field(..., description="Font family name (e.g., 'Inter', 'Roboto')")
    font_weight: int = Field(
        ..., ge=100, le=900, description="Font weight (100-900, e.g., 400=regular, 700=bold)"
    )
    font_style: str | None = Field(default=None, description="Font style (normal, italic, oblique)")
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
    text_align: str | None = Field(
        default=None, description="Text alignment (left, right, center, justify)"
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
    """Result of typography extraction."""

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
    """AI-powered typography extractor using Claude Sonnet 4.5."""

    def __init__(self, api_key: str | None = None):
        """Initialize the typography extractor.

        Args:
            api_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY env var
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def extract_typography_from_image_url(
        self,
        image_url: str,
        max_tokens: int = 15,
        cache_namespace: str | None = None,
        input_hash: str | None = None,
    ) -> TypographyExtractionResult:
        """Extract typography from an image URL."""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to download image: %s", str(exc))
            raise

        image_data = base64.standard_b64encode(response.content).decode("utf-8")

        content_type = response.headers.get("content-type", "image/jpeg").lower()
        if "png" in content_type:
            media_type = "image/png"
        elif "webp" in content_type:
            media_type = "image/webp"
        elif "gif" in content_type:
            media_type = "image/gif"
        else:
            media_type = "image/jpeg"

        return self.extract_typography_from_base64(
            image_data,
            media_type,
            max_tokens,
            cache_namespace=cache_namespace,
            input_hash=input_hash,
        )

    def extract_typography_from_file(
        self,
        file_path: str,
        max_tokens: int = 15,
        cache_namespace: str | None = None,
        input_hash: str | None = None,
    ) -> TypographyExtractionResult:
        """Extract typography from a local image file."""
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Image file not found: {file_path_obj}")

        suffix = file_path_obj.suffix.lower()
        media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }
        media_type = media_types.get(suffix, "image/jpeg")

        with open(file_path_obj, "rb") as handle:
            image_data = base64.standard_b64encode(handle.read()).decode("utf-8")

        return self.extract_typography_from_base64(
            image_data,
            media_type,
            max_tokens,
            cache_namespace=cache_namespace,
            input_hash=input_hash,
        )

    def extract_typography_from_base64(
        self,
        image_data: str,
        media_type: str,
        max_tokens: int = 15,
        cache_namespace: str | None = None,
        input_hash: str | None = None,
    ) -> TypographyExtractionResult:
        """Extract typography from base64-encoded image data."""
        if image_data.startswith("data:"):
            match = re.match(r"data:([^;]+);base64,(.+)", image_data)
            if match:
                media_type = match.group(1)
                image_data = match.group(2)

        cache = get_extraction_cache()
        input_hash = input_hash or compute_input_hash(
            image_data,
            None,
            {"media_type": media_type, "max_tokens": max_tokens, "model": self.model},
        )
        cached = cache.get("typography.full", input_hash, cache_namespace)
        if cached:
            return TypographyExtractionResult.model_validate(cached)

        prompt = f"""Analyze this image and extract typography tokens for a design system.

Extract the {max_tokens} most important typography styles that represent the design system.

For each typography style, identify:
1. Font family name (e.g., "Inter", "Roboto", "Georgia")
2. Font weight (100-900: 100=thin, 400=regular, 700=bold, 900=black)
3. Font style (normal, italic, oblique)
4. Font size in pixels (approximate)
5. Line height as a multiplier (e.g., 1.5 for 150% line height)
6. Letter spacing (if visible, in em units)
7. Text transformation if applied (uppercase, lowercase, capitalize, none)
8. Text alignment (left, right, center, justify)
9. Semantic role: Choose from: heading, subheading, body, caption, label, display, or create a descriptive one (e.g., "nav", "hero", "footer")
10. Category: display, text, label, mono, or other
11. Confidence score (0-1) based on how clearly you can identify the typography
12. Approximate prominence (percentage of text using this style)
13. Is it readable and accessible? (yes/no)

Also provide:
- Overall typography palette description (1-2 sentences)
- Overall extraction confidence (0-1)
- Any color associations (text color, background color, etc.)

Important: Be specific about font family names. Analyze the design intent of each typography style."""

        try:
            with track_perf(
                "extract.typography.ai",
                {"model": self.model, "max_tokens": max_tokens},
                measure_memory=True,
            ):
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

            response_text = message.content[0].text
            result = self._parse_typography_response(response_text, max_tokens)

            cache.set("typography.full", input_hash, cache_namespace, result.model_dump())
            logger.info("Successfully extracted %d typography tokens", len(result.tokens))
            return result

        except anthropic.APIError as exc:
            logger.error("Claude API error: %s", str(exc))
            raise

    def _parse_typography_response(
        self, response_text: str, max_tokens: int
    ) -> TypographyExtractionResult:
        """Parse Claude's response into structured typography data."""
        tokens: list[ExtractedTypographyToken] = []
        current: dict[str, object] = {}
        palette: str | None = None
        overall_confidence: float | None = None
        color_associations: dict | None = None

        def normalize_font_style(value: str | None) -> str | None:
            if not value:
                return None
            value = value.strip().lower()
            if value in {"italic", "oblique", "normal"}:
                return value
            if value in {"regular", "roman"}:
                return "normal"
            return None

        def normalize_text_transform(value: str | None) -> str | None:
            if not value:
                return None
            value = value.strip().lower()
            if value in {"uppercase", "lowercase", "capitalize", "none"}:
                return value
            if value in {"normal"}:
                return "none"
            return None

        def normalize_text_align(value: str | None) -> str | None:
            if not value:
                return None
            value = value.strip().lower()
            if value in {
                "left",
                "right",
                "center",
                "centre",
                "centered",
                "centred",
                "justify",
                "justified",
            }:
                if value in {"centre", "centred", "centered"}:
                    return "center"
                if value == "justified":
                    return "justify"
                return value
            return None

        def normalize_font_weight(value: str) -> int | None:
            weight_map = {
                "thin": 100,
                "extra light": 200,
                "extralight": 200,
                "light": 300,
                "normal": 400,
                "regular": 400,
                "medium": 500,
                "semibold": 600,
                "semi bold": 600,
                "bold": 700,
                "extra bold": 800,
                "extrabold": 800,
                "black": 900,
            }
            key = value.strip().lower()
            return weight_map.get(key)

        def _finalize_token(data: dict[str, object]) -> None:
            if len(tokens) >= max_tokens:
                return
            if not data.get("font_family"):
                return
            token_dict = {
                "font_family": data.get("font_family", "System"),
                "font_weight": data.get("font_weight", 400),
                "font_style": data.get("font_style") or "normal",
                "font_size": data.get("font_size", 16),
                "line_height": data.get("line_height", 1.5),
                "letter_spacing": data.get("letter_spacing"),
                "text_transform": data.get("text_transform"),
                "text_align": data.get("text_align"),
                "semantic_role": data.get("semantic_role", "body"),
                "category": data.get("category"),
                "name": data.get("name"),
                "confidence": min(1.0, float(data.get("confidence", 0.8))),
                "prominence": data.get("prominence"),
                "is_readable": data.get("is_readable"),
                "readability_score": data.get("readability_score"),
            }
            metadata = {
                "model": self.model,
                "extraction_source": "claude_ai_extractor",
            }
            for key in token_dict:
                if token_dict.get(key) is not None:
                    metadata[key] = "claude_ai_extractor"
            token_dict["extraction_metadata"] = metadata
            try:
                tokens.append(ExtractedTypographyToken(**token_dict))
            except ValueError as exc:
                logger.warning("Failed to create typography token: %s", str(exc))

        lines = response_text.split("\n")
        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            if re.match(r"^(token|style)\b", line, re.IGNORECASE) or re.match(r"^\d+\.", line):
                _finalize_token(current)
                current = {}

            palette_match = re.search(r"typography palette|palette description", line, re.I)
            if palette_match and ":" in line:
                palette = line.split(":", 1)[1].strip()
                continue

            conf_match = re.search(r"overall.*confidence[:\s]+([0-9.]+)", line, re.I)
            if conf_match:
                try:
                    overall_confidence = float(conf_match.group(1))
                except ValueError:
                    pass
                continue

            if re.search(r"color associations?", line, re.I) and ":" in line:
                try:
                    payload = line.split(":", 1)[1].strip()
                    if payload.startswith("{") and payload.endswith("}"):
                        import json

                        color_associations = json.loads(payload)
                except Exception:
                    pass

            if re.search(r"font\s*family", line, re.IGNORECASE):
                if current.get("font_family"):
                    _finalize_token(current)
                    current = {}
                match = re.search(r'(["\']?)([A-Za-z0-9\s\-,]+)\1', line)
                if match:
                    current["font_family"] = match.group(2).strip()
                else:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        family = parts[1].strip().strip("\"'")
                        if family and family.lower() not in {"none", "n/a"}:
                            current["font_family"] = family

            weight_match = re.search(r"(?:font\s*)?weight[:\s]+(\d{3})", line, re.IGNORECASE)
            if weight_match:
                current["font_weight"] = int(weight_match.group(1))
            elif re.search(r"(?:font\s*)?weight", line, re.IGNORECASE):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    weight = normalize_font_weight(parts[1])
                    if weight:
                        current["font_weight"] = weight

            size_match = re.search(
                r"(?:font\s*)?size[:\s]+(\d+)\s*(?:px|pixels)?", line, re.IGNORECASE
            )
            if size_match:
                current["font_size"] = int(size_match.group(1))

            style_match = re.search(
                r"(?:font\s*)?style[:\s]+(normal|italic|oblique)", line, re.IGNORECASE
            )
            if style_match:
                current["font_style"] = normalize_font_style(style_match.group(1))

            lh_match = re.search(r"(?:line\s*)?height[:\s]+([0-9.]+)", line, re.IGNORECASE)
            if lh_match:
                current["line_height"] = float(lh_match.group(1))

            ls_match = re.search(
                r"(?:letter\s*)?spacing[:\s]+([0-9.\-]+)\s*(?:em)?", line, re.IGNORECASE
            )
            if ls_match:
                current["letter_spacing"] = float(ls_match.group(1))

            transform_match = re.search(
                r"(?:text\s*)?(?:transform|case|casing)[:\s]+([A-Za-z]+)",
                line,
                re.IGNORECASE,
            )
            if transform_match:
                current["text_transform"] = normalize_text_transform(transform_match.group(1))

            align_match = re.search(
                r"(?:text\s*)?align(?:ment)?[:\s]+(left|right|center|centre|centered|centred|justify|justified)",
                line,
                re.IGNORECASE,
            )
            if align_match:
                current["text_align"] = normalize_text_align(align_match.group(1))

            category_match = re.search(r"category[:\s]+([A-Za-z0-9\-_ ]+)", line, re.IGNORECASE)
            if category_match:
                current["category"] = category_match.group(1).strip().lower()

            name_match = re.search(
                r"(?:name|style name)[:\s]+([A-Za-z0-9\-_ ]+)", line, re.IGNORECASE
            )
            if name_match:
                current["name"] = name_match.group(1).strip()

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
                    current["semantic_role"] = role

            conf_match = re.search(r"confidence[:\s]+([0-9.]+)", line, re.IGNORECASE)
            if conf_match:
                try:
                    current["confidence"] = float(conf_match.group(1))
                except ValueError:
                    pass

            prominence_match = re.search(r"(?:prominence|percentage)[:\s]+([0-9.]+)", line)
            if prominence_match:
                try:
                    current["prominence"] = float(prominence_match.group(1))
                except ValueError:
                    pass

            if re.search(r"readable|legible", line, re.IGNORECASE):
                if re.search(r"\b(no|false)\b", line, re.IGNORECASE):
                    current["is_readable"] = False
                elif re.search(r"\b(yes|true)\b", line, re.IGNORECASE):
                    current["is_readable"] = True

            read_score_match = re.search(r"readability[:\s]+([0-9.]+)", line, re.IGNORECASE)
            if read_score_match:
                try:
                    current["readability_score"] = float(read_score_match.group(1))
                except ValueError:
                    pass

        _finalize_token(current)

        if not tokens:
            logger.warning("No typography parsed from response, using fallback tokens")
            tokens = [
                ExtractedTypographyToken(
                    font_family="System",
                    font_weight=700,
                    font_style="normal",
                    font_size=32,
                    line_height=1.2,
                    text_align=None,
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
                    font_style="normal",
                    font_size=16,
                    line_height=1.6,
                    text_align=None,
                    semantic_role="body",
                    confidence=0.5,
                    extraction_metadata={
                        "model": self.model,
                        "extraction_source": "fallback",
                    },
                ),
            ]

        extraction_confidence = (
            overall_confidence
            if overall_confidence is not None
            else sum(t.confidence for t in tokens) / len(tokens)
        )

        return TypographyExtractionResult(
            tokens=tokens[:max_tokens],
            typography_palette=palette or "Extracted typography system from image",
            extraction_confidence=extraction_confidence,
            extractor_used=self.model,
            color_associations=color_associations,
        )


def extract_typography(image_url: str, max_tokens: int = 15) -> TypographyExtractionResult:
    """Quick function to extract typography from an image URL."""
    extractor = AITypographyExtractor()
    return extractor.extract_typography_from_image_url(image_url, max_tokens)


def extract_typography_from_file(
    file_path: str, max_tokens: int = 15
) -> TypographyExtractionResult:
    """Quick function to extract typography from a local image file."""
    extractor = AITypographyExtractor()
    return extractor.extract_typography_from_file(file_path, max_tokens)
