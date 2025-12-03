"""Computer vision-based typography extraction using OCR and image analysis"""

import io
import logging
from collections import defaultdict

from PIL import Image

from copy_that.application.ai_typography_extractor import ExtractedTypographyToken

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
            tokens = self._groups_to_tokens(typography_groups)

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

    def _groups_to_tokens(self, groups: dict) -> list[ExtractedTypographyToken]:
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

            # Infer semantic role from size and position
            semantic_role = self._infer_semantic_role(size_bucket, vertical_position, text_count)

            # Create token
            token = ExtractedTypographyToken(
                font_family="System",  # CV can't reliably detect font family
                font_weight=400,  # Default regular weight
                font_size=int(avg_height),
                line_height=1.5,  # Default line height
                letter_spacing=None,
                text_transform=None,
                semantic_role=semantic_role,
                category=self._infer_category(semantic_role),
                name=None,
                confidence=min(0.7, avg_confidence),  # Lower confidence for CV extraction
                prominence=min(100.0, text_count * 2.0),  # Rough estimate
                is_readable=True,
                readability_score=avg_confidence,
                extraction_metadata={
                    "source": "cv_ocr_extractor",
                    "text_count": text_count,
                    "avg_confidence": float(avg_confidence),
                },
            )

            tokens.append(token)

        return tokens

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
