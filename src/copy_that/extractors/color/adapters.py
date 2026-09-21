"""Adapters for existing color extractors to implement ColorExtractorProtocol

This module wraps the three existing extractors:
1. AIColorExtractor (Claude Sonnet 4.5)
2. ColorKMeansClustering (K-means palette extraction)
3. CVColorExtractor (Fast computer vision extraction)

Each adapter implements the ColorExtractorProtocol for parallel execution.
"""

import base64
import logging

import cv2
import numpy as np

from copy_that.extractors.color.base import ExtractionResult
from copy_that.extractors.color.clustering import ColorKMeansClustering
from copy_that.extractors.color.cv_extractor import CVColorExtractor
from copy_that.extractors.color.extractor import AIColorExtractor, ExtractedColorToken

logger = logging.getLogger(__name__)


class AIColorExtractorAdapter:
    """Adapter for AIColorExtractor (Claude-powered extraction)

    Converts bytes input to the Claude extractor's expected format and
    wraps results as ExtractionResult.
    """

    def __init__(self, api_key: str | None = None, max_colors: int = 10):
        """Initialize the AI extractor adapter

        Args:
            api_key: Anthropic API key (uses env var if not provided)
            max_colors: Maximum colors to extract
        """
        self.extractor = AIColorExtractor(api_key=api_key)
        self.max_colors = max_colors

    @property
    def name(self) -> str:
        """Extractor name for provenance tracking"""
        return "claude-sonnet-4.5"

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """Extract colors using Claude Sonnet 4.5

        Args:
            image_data: Raw image bytes (PNG, JPG, etc.)

        Returns:
            ExtractionResult with colors and metadata
        """
        try:
            # Convert bytes to base64
            base64_data = base64.standard_b64encode(image_data).decode("utf-8")

            # Detect media type from image data
            media_type = self._detect_media_type(image_data)

            # Extract colors using Claude
            result = self.extractor.extract_colors_from_base64(
                base64_data, media_type, self.max_colors
            )

            # Calculate confidence range from extracted colors
            confidence_values = [c.confidence for c in result.colors] if result.colors else [0.5]
            confidence_range = (min(confidence_values), max(confidence_values))

            return ExtractionResult(
                colors=result.colors,
                extractor_name=self.name,
                execution_time_ms=0.0,  # Not tracked in sync version
                confidence_range=confidence_range,
            )
        except Exception as e:
            logger.error("Claude extraction failed: %s", str(e))
            raise

    @staticmethod
    def _detect_media_type(image_data: bytes) -> str:
        """Detect image media type from magic bytes"""
        if image_data.startswith(b"\x89PNG"):
            return "image/png"
        elif image_data.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        elif image_data.startswith(b"RIFF") and b"WEBP" in image_data[:12]:
            return "image/webp"
        elif image_data.startswith(b"GIF8"):
            return "image/gif"
        else:
            return "image/jpeg"  # Default fallback


class KMeansExtractorAdapter:
    """Adapter for ColorKMeansClustering (K-means palette extraction)

    Converts bytes to numpy array and wraps ColorClusterResult as ExtractedColorToken.
    """

    def __init__(self, k: int = 12, max_colors: int = 8):
        """Initialize K-means adapter

        Args:
            k: Number of clusters
            max_colors: Maximum colors in final palette
        """
        self.extractor = ColorKMeansClustering(k=k)
        self.max_colors = max_colors

    @property
    def name(self) -> str:
        """Extractor name for provenance tracking"""
        return "kmeans-clustering"

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """Extract colors using K-means clustering

        Args:
            image_data: Raw image bytes (PNG, JPG, etc.)

        Returns:
            ExtractionResult with colors and metadata
        """
        try:
            # Decode bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is None:
                raise ValueError("Failed to decode image data")

            # Extract palette using K-means
            clusters = self.extractor.extract_palette(image)

            # Convert clusters to ExtractedColorToken
            colors = [self._cluster_to_token(cluster) for cluster in clusters]
            colors = colors[: self.max_colors]  # Limit to max_colors

            # Calculate confidence range
            confidence_values = [c.confidence for c in colors] if colors else [0.9]
            confidence_range = (min(confidence_values), max(confidence_values))

            return ExtractionResult(
                colors=colors,
                extractor_name=self.name,
                execution_time_ms=0.0,  # Not tracked in sync version
                confidence_range=confidence_range,
            )
        except Exception as e:
            logger.error("K-means extraction failed: %s", str(e))
            raise

    @staticmethod
    def _cluster_to_token(cluster) -> ExtractedColorToken:
        """Convert ColorClusterResult to ExtractedColorToken"""
        r, g, b = cluster.rgb
        return ExtractedColorToken(
            hex=cluster.hex_color,
            rgb=f"rgb({r}, {g}, {b})",
            hsl=None,
            hsv=None,
            name=cluster.hex_color,
            design_intent=None,
            semantic_names=None,
            category="kmeans",
            confidence=cluster.confidence,
            harmony=None,
            harmony_confidence=None,
            hue_angles=None,
            temperature=None,
            saturation_level=None,
            lightness_level=None,
            usage=[],
            count=1,
            prominence_percentage=cluster.prominence_percentage,
            wcag_contrast_on_white=None,
            wcag_contrast_on_black=None,
            wcag_aa_compliant_text=None,
            wcag_aaa_compliant_text=None,
            wcag_aa_compliant_normal=None,
            wcag_aaa_compliant_normal=None,
            colorblind_safe=None,
            tint_color=None,
            shade_color=None,
            tone_color=None,
            closest_web_safe=None,
            closest_css_named=None,
            delta_e_to_dominant=None,
            is_neutral=None,
            background_role=None,
            contrast_category=None,
            foreground_role=None,
            is_accent=None,
            state_variants=None,
            kmeans_cluster_id=cluster.cluster_id,
            sam_segmentation_mask=None,
            clip_embeddings=None,
            extraction_metadata={"cluster_id": cluster.cluster_id},
            histogram_significance=None,
        )


class CVExtractorAdapter:
    """Adapter for CVColorExtractor (Fast computer vision extraction)

    Wraps the existing CV extractor to return ExtractionResult.
    """

    def __init__(self, max_colors: int = 8, use_superpixels: bool = True):
        """Initialize CV adapter

        Args:
            max_colors: Maximum colors in palette
            use_superpixels: Use superpixel extraction for better results
        """
        self.extractor = CVColorExtractor(max_colors=max_colors, use_superpixels=use_superpixels)

    @property
    def name(self) -> str:
        """Extractor name for provenance tracking"""
        return "computer-vision"

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """Extract colors using fast computer vision

        Args:
            image_data: Raw image bytes (PNG, JPG, etc.)

        Returns:
            ExtractionResult with colors and metadata
        """
        try:
            # Extract colors using CV extractor
            result = self.extractor.extract_from_bytes(image_data)

            # Calculate confidence range
            confidence_values = [c.confidence for c in result.colors] if result.colors else [0.6]
            confidence_range = (min(confidence_values), max(confidence_values))

            return ExtractionResult(
                colors=result.colors,
                extractor_name=self.name,
                execution_time_ms=0.0,
                confidence_range=confidence_range,
            )
        except Exception as e:
            logger.error("CV extraction failed: %s", str(e))
            raise


# Aliases for API imports (backward compatibility with expected naming)
ClaudeColorExtractorAdapter = AIColorExtractorAdapter
KMeansColorExtractorAdapter = KMeansExtractorAdapter
CVColorExtractorAdapter = CVExtractorAdapter
