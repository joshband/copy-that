"""Computer vision-based typography extraction using OCR and image analysis"""

import io
import logging
from collections import defaultdict

from PIL import Image

from copy_that.application.typography_extractor import ExtractedTypographyToken

logger = logging.getLogger(__name__)

try:
    import pytesseract

    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available - OCR-based typography extraction disabled")


class CVTypographyExtractor:
    """Computer vision-based typography extraction using OCR and image analysis.

    Serves as a fallback when AI extraction fails or needs verification.
    Analyzes text regions in the image to infer typography properties.
    """

    def __init__(self):
        """Initialize CV typography extractor"""
        self.min_text_height = 8  # Minimum font size in pixels
        self.max_text_height = 120  # Maximum font size in pixels
        self.min_ocr_confidence = 0.35  # Drop junk OCR boxes before grouping
        self.min_bbox_area = 24  # width*height floor (tiny noise)

    async def extract(self, image_data: bytes) -> list[ExtractedTypographyToken]:
        """Extract typography using OCR and image analysis.

        Args:
            image_data: Raw image bytes

        Returns:
            List of extracted typography tokens

        Raises:
            ValueError: If image cannot be processed
        """
        if not PYTESSERACT_AVAILABLE:
            logger.warning("pytesseract not available, returning empty typography tokens")
            return []

        try:
            image = Image.open(io.BytesIO(image_data))
            return await self._extract_from_image(image)
        except Exception as e:
            logger.error("CV typography extraction failed: %s", str(e))
            return []

    async def extract_from_file(self, file_path: str) -> list[ExtractedTypographyToken]:
        """Extract typography from an image file.

        Args:
            file_path: Path to image file

        Returns:
            List of extracted typography tokens
        """
        try:
            image = Image.open(file_path)
            return await self._extract_from_image(image)
        except Exception as e:
            logger.error("CV typography extraction from file failed: %s", str(e))
            return []

    async def _extract_from_image(self, image: Image.Image) -> list[ExtractedTypographyToken]:
        """Extract typography from PIL Image object.

        Args:
            image: PIL Image object

        Returns:
            List of extracted typography tokens
        """
        try:
            # Use pytesseract to detect text and estimate positions/sizes
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            if not data or not data.get("text"):
                logger.warning("No text detected in image via OCR")
                return []

            # Group text by estimated size to identify typography styles
            typography_groups = self._group_by_typography(data, image)

            # Convert groups to typography tokens
            tokens = self._groups_to_tokens(typography_groups, image.width)

            logger.info("Extracted %d typography styles via CV", len(tokens))
            return tokens

        except Exception as e:
            logger.error("Error extracting typography from image: %s", str(e))
            return []

    def _group_by_typography(self, ocr_data: dict, image: Image.Image) -> dict:
        """Group detected text by typography characteristics.

        Analyzes text height, position, and confidence to identify distinct typography styles.

        Args:
            ocr_data: Pytesseract OCR data
            image: Original PIL Image

        Returns:
            Dictionary mapping typography characteristics to text regions
        """
        groups = defaultdict(list)

        for i, text in enumerate(ocr_data["text"]):
            if not text.strip():
                continue

            # Get text metrics
            height = ocr_data["height"][i]
            left = ocr_data["left"][i]
            top = ocr_data["top"][i]
            width = ocr_data["width"][i]
            conf = ocr_data["conf"][i] / 100.0

            # Skip very small text (likely noise)
            if height < self.min_text_height:
                continue
            if conf < self.min_ocr_confidence:
                continue
            if width * height < self.min_bbox_area:
                continue
            if width < 2 or height < 2:
                continue

            # Group by approximate height (represents font size)
            size_bucket = round(height / 4) * 4  # Group into 4-pixel buckets
            size_bucket = max(self.min_text_height, min(self.max_text_height, size_bucket))

            # Infer vertical position (top, middle, bottom of page)
            image_height = image.height
            vertical_position = (
                "top"
                if top < image_height / 3
                else "bottom"
                if top > 2 * image_height / 3
                else "middle"
            )

            # Create key for grouping
            key = (size_bucket, vertical_position, conf > 0.7)

            groups[key].append(
                {
                    "text": text,
                    "height": height,
                    "left": left,
                    "top": top,
                    "width": width,
                    "confidence": conf,
                }
            )

        return groups

    def _groups_to_tokens(self, groups: dict, image_width: int) -> list[ExtractedTypographyToken]:
        """Convert typography groups to ExtractedTypographyToken instances.

        Args:
            groups: Dictionary of grouped text regions

        Returns:
            List of typography tokens
        """
        tokens = []

        for (size_bucket, vertical_position, _high_confidence), text_items in sorted(
            groups.items()
        ):
            if not text_items:
                continue

            # Calculate statistics for this group
            avg_height = sum(t["height"] for t in text_items) / len(text_items)
            avg_confidence = sum(t["confidence"] for t in text_items) / len(text_items)
            text_count = len(text_items)
            line_height_px = max(int(round(avg_height * 1.4)), int(round(avg_height)) + 1)
            line_height_multiplier = round(line_height_px / max(avg_height, 1.0), 2)
            text_align = self._infer_text_alignment(text_items, image_width)

            # Infer semantic role from size and position
            semantic_role = self._infer_semantic_role(size_bucket, vertical_position, text_count)

            # Cap stays ≤0.7 unless filtered OCR mean is strong.
            token_conf = (
                min(0.7, avg_confidence) if avg_confidence < 0.85 else min(0.78, avg_confidence)
            )

            # Create token
            token = ExtractedTypographyToken(
                font_family="System",  # CV can't reliably detect font family
                font_weight=400,  # Default regular weight
                font_style="normal",
                font_size=int(avg_height),
                line_height=min(3.0, max(0.8, line_height_multiplier)),
                letter_spacing=None,
                text_transform=None,
                text_align=text_align,
                semantic_role=semantic_role,
                category=self._infer_category(semantic_role),
                name=None,
                confidence=token_conf,
                # Schema expects a 0–1 fraction (not 0–100). Scale the rough count estimate.
                prominence=min(1.0, (text_count * 2.0) / 100.0),
                is_readable=True,
                readability_score=avg_confidence,
                extraction_metadata={
                    "source": "cv_ocr_extractor",
                    "text_count": text_count,
                    "avg_confidence": float(avg_confidence),
                    "line_height_px": line_height_px,
                    "baseline_spacing_px": line_height_px,
                    "text_align": text_align,
                },
            )

            if groups:
                try:
                    # Use overall image height if available to build a rhythm overlay
                    overlay = self._build_baseline_overlay(
                        height=max(t["height"] + t["top"] for t in text_items),
                        width=max(t["left"] + t["width"] for t in text_items),
                        spacing_px=line_height_px,
                    )
                    if overlay:
                        metadata = token.extraction_metadata or {}
                        metadata["baseline_overlay"] = overlay
                        token.extraction_metadata = metadata
                except Exception:
                    pass

            tokens.append(token)

        return tokens

    @staticmethod
    def _build_baseline_overlay(height: int, width: int, spacing_px: int) -> str | None:
        """Render a simple baseline grid overlay to base64 PNG."""
        import base64
        from io import BytesIO

        from PIL import Image, ImageDraw  # Local import to avoid hard dependency in tests

        if spacing_px <= 0 or height <= 0 or width <= 0:
            return None
        canvas = Image.new("RGBA", (max(width, 1), max(height, 1)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        for y in range(0, height, spacing_px):
            draw.line((0, y, width, y), fill=(120, 255, 120, 160), width=1)
        buf = BytesIO()
        canvas.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def _infer_semantic_role(
        self, size_bucket: int, vertical_position: str, text_count: int
    ) -> str:
        """Infer semantic role from typography characteristics.

        Args:
            size_bucket: Approximate font size in pixels
            vertical_position: Position in page (top, middle, bottom)
            text_count: Number of text regions of this size

        Returns:
            Semantic role string
        """
        # Size-based inference
        if size_bucket >= 48:
            return "heading"
        elif size_bucket >= 32:
            return "subheading"
        elif size_bucket < 14:
            return "caption"
        elif vertical_position == "top" and size_bucket >= 24:
            return "heading"
        else:
            return "body"

    @staticmethod
    def _infer_text_alignment(text_items: list[dict], image_width: int) -> str | None:
        """Infer text alignment using bounding box positions."""
        if not text_items or image_width <= 0:
            return None

        lefts = [item["left"] for item in text_items]
        rights = [item["left"] + item["width"] for item in text_items]
        centers = [item["left"] + item["width"] / 2 for item in text_items]

        avg_left = sum(lefts) / len(lefts)
        avg_right = sum(rights) / len(rights)
        avg_center = sum(centers) / len(centers)

        left_margin = avg_left
        right_margin = image_width - avg_right
        margin_threshold = max(image_width * 0.08, 8)

        if abs(avg_center - image_width / 2) <= image_width * 0.05:
            return "center"
        if right_margin <= margin_threshold and right_margin < left_margin:
            return "right"
        if left_margin <= margin_threshold and left_margin <= right_margin:
            return "left"
        if left_margin <= margin_threshold and right_margin <= margin_threshold:
            return "justify"
        return None

    @staticmethod
    def _infer_category(semantic_role: str) -> str:
        """Infer category from semantic role.

        Args:
            semantic_role: Semantic role (heading, body, etc.)

        Returns:
            Category string
        """
        role_to_category = {
            "heading": "display",
            "subheading": "display",
            "body": "text",
            "caption": "label",
            "label": "label",
            "display": "display",
            "nav": "label",
            "hero": "display",
            "footer": "label",
        }
        return role_to_category.get(semantic_role, "text")
