"""CV-based shadow extraction using edge detection and morphology."""

import logging
from base64 import b64decode

import cv2
import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ExtractedShadowToken(BaseModel):
    """Shadow token extracted from UI images"""

    x_offset: float = Field(..., description="Horizontal offset in pixels")
    y_offset: float = Field(..., description="Vertical offset in pixels")
    blur_radius: float = Field(..., description="Blur radius in pixels")
    spread_radius: float = Field(default=0.0, description="Spread radius in pixels")
    color_hex: str = Field(..., description="Shadow color in hex format (e.g., #000000)")
    opacity: float = Field(..., ge=0, le=1, description="Shadow opacity 0-1")
    shadow_type: str = Field(..., description="Type: 'drop', 'inner', or 'text'")
    semantic_name: str = Field(..., description="Human-readable name")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    is_inset: bool = Field(default=False, description="Is this an inset/inner shadow")
    affects_text: bool = Field(default=False, description="Does this shadow apply to text")


class ShadowExtractionResult(BaseModel):
    """Result of CV shadow extraction"""

    shadows: list[ExtractedShadowToken] = Field(default_factory=list)
    shadow_count: int = Field(default=0)
    extraction_confidence: float = Field(default=0.0)
    extractor_used: str = "cv_edge_detection"


class CVShadowExtractor:
    """Extract shadows from UI images using edge detection and morphological operations."""

    def __init__(self):
        self.min_shadow_area = 10  # Minimum pixels for shadow candidate
        self.blur_kernel = (5, 5)
        self.morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    def extract_shadows(
        self,
        base64_image: str = "",
        media_type: str = "image/png",
    ) -> ShadowExtractionResult:
        """
        Extract shadows using edge detection and morphological analysis.

        Strategy:
        1. Convert to grayscale
        2. Detect dark regions (potential shadows)
        3. Analyze edges and gradients
        4. Extract shadow boundaries and properties
        """
        if not base64_image:
            logger.warning("No image provided to CV shadow extractor")
            return ShadowExtractionResult(shadow_count=0, extraction_confidence=0.0)

        try:
            # Decode image
            image_data = b64decode(base64_image)
            image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

            if image is None:
                logger.warning("Failed to decode image")
                return ShadowExtractionResult(shadow_count=0, extraction_confidence=0.0)

            return self._detect_shadows(image)

        except Exception as e:
            logger.exception(f"CV shadow extraction failed: {e}")
            return ShadowExtractionResult(shadow_count=0, extraction_confidence=0.0)

    def _detect_shadows(self, image: np.ndarray) -> ShadowExtractionResult:
        """Detect shadows in image using edge and darkness analysis."""
        height, width = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect dark regions (shadows are typically darker)
        _, dark_mask = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

        # Reduce noise
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, self.morph_kernel, iterations=1)
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, self.morph_kernel, iterations=1)

        # Find contours (shadow candidates)
        contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        shadows: list[ExtractedShadowToken] = []
        total_confidence = 0.0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_shadow_area:
                continue

            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)

            # Skip if shadow is too close to image edges (likely not a real shadow)
            edge_margin = 5
            if (
                x < edge_margin
                or y < edge_margin
                or x + w > width - edge_margin
                or y + h > height - edge_margin
            ):
                continue

            # Extract shadow properties
            roi = gray[y : y + h, x : x + w]
            avg_darkness = np.mean(255 - roi) / 255.0  # 0-1 darkness scale

            # Estimate shadow parameters
            shadow = ExtractedShadowToken(
                x_offset=float(x),
                y_offset=float(y),
                blur_radius=max(1.0, float(np.std(roi) / 25.0)),  # Estimate blur from variance
                spread_radius=0.0,  # CV can't reliably detect spread
                color_hex="#000000",  # Shadows are typically black
                opacity=min(1.0, avg_darkness),  # Use darkness as opacity
                shadow_type="drop",  # Default to drop shadow
                semantic_name=f"shadow-{len(shadows) + 1}",
                confidence=max(0.3, min(1.0, avg_darkness * 0.8)),  # Lower confidence for CV
                is_inset=False,
                affects_text=False,
            )

            shadows.append(shadow)
            total_confidence += shadow.confidence

        avg_confidence = total_confidence / len(shadows) if shadows else 0.0

        return ShadowExtractionResult(
            shadows=shadows,
            shadow_count=len(shadows),
            extraction_confidence=avg_confidence,
            extractor_used="cv_edge_detection",
        )
