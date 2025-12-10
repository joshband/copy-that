"""Unit tests for color extractor adapters

Tests that all three adapters properly implement the ColorExtractorProtocol.
"""

import io

import pytest
from PIL import Image

from copy_that.extractors.color.adapters import (
    AIColorExtractorAdapter,
    CVExtractorAdapter,
    KMeansExtractorAdapter,
)
from copy_that.extractors.color.base import ExtractionResult


@pytest.fixture
def sample_image_bytes():
    """Create a simple test image as bytes"""
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))  # Red image
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    return img_bytes.getvalue()


class TestAIColorExtractorAdapter:
    """Test Claude Sonnet adapter"""

    def test_name_property(self):
        """Test adapter has correct name"""
        adapter = AIColorExtractorAdapter()
        assert adapter.name == "claude-sonnet-4.5"

    def test_media_type_detection_png(self):
        """Test PNG detection"""
        png_magic = b"\x89PNG\r\n\x1a\n"
        media_type = AIColorExtractorAdapter._detect_media_type(png_magic)
        assert media_type == "image/png"

    def test_media_type_detection_jpeg(self):
        """Test JPEG detection"""
        jpeg_magic = b"\xff\xd8\xff"
        media_type = AIColorExtractorAdapter._detect_media_type(jpeg_magic)
        assert media_type == "image/jpeg"

    def test_media_type_detection_gif(self):
        """Test GIF detection"""
        gif_magic = b"GIF8"
        media_type = AIColorExtractorAdapter._detect_media_type(gif_magic)
        assert media_type == "image/gif"

    def test_media_type_detection_fallback(self):
        """Test fallback to JPEG for unknown format"""
        unknown = b"random data"
        media_type = AIColorExtractorAdapter._detect_media_type(unknown)
        assert media_type == "image/jpeg"

    @pytest.mark.asyncio
    async def test_extract_integration(self, sample_image_bytes):
        """Test extract method signature and return type"""
        adapter = AIColorExtractorAdapter()
        # Note: This requires API key, so we're testing interface only
        # Real integration tests would use mock or actual API
        assert hasattr(adapter, "extract")
        assert callable(adapter.extract)


class TestKMeansExtractorAdapter:
    """Test K-means adapter"""

    def test_name_property(self):
        """Test adapter has correct name"""
        adapter = KMeansExtractorAdapter()
        assert adapter.name == "kmeans-clustering"

    def test_initialization(self):
        """Test adapter initialization with custom params"""
        adapter = KMeansExtractorAdapter(k=8, max_colors=5)
        assert adapter.extractor.k == 8
        assert adapter.max_colors == 5

    @pytest.mark.asyncio
    async def test_extract_with_image(self, sample_image_bytes):
        """Test extract method with actual image data"""
        adapter = KMeansExtractorAdapter(k=3, max_colors=3)
        result = await adapter.extract(sample_image_bytes)

        assert isinstance(result, ExtractionResult)
        assert result.extractor_name == "kmeans-clustering"
        assert len(result.colors) > 0
        assert len(result.colors) <= 3
        assert result.confidence_range[0] >= 0
        assert result.confidence_range[1] <= 1

    @pytest.mark.asyncio
    async def test_extract_handles_invalid_bytes(self):
        """Test extract gracefully handles invalid image data"""
        adapter = KMeansExtractorAdapter()
        with pytest.raises((ValueError, RuntimeError)):
            await adapter.extract(b"invalid image data")

    def test_cluster_to_token_conversion(self):
        """Test cluster to token conversion"""
        from copy_that.extractors.color.clustering import ColorClusterResult

        cluster = ColorClusterResult(
            hex_color="#FF0000",
            rgb=(255, 0, 0),
            center_lab=(50.0, 75.0, 50.0),
            pixel_count=100,
            prominence_percentage=10.5,
            cluster_id=0,
            confidence=0.95,
        )

        token = KMeansExtractorAdapter._cluster_to_token(cluster)
        assert token.hex == "#FF0000"
        assert token.rgb == "rgb(255, 0, 0)"
        assert token.confidence == 0.95
        assert token.kmeans_cluster_id == 0
        assert token.prominence_percentage == 10.5


class TestCVExtractorAdapter:
    """Test Computer Vision adapter"""

    def test_name_property(self):
        """Test adapter has correct name"""
        adapter = CVExtractorAdapter()
        assert adapter.name == "computer-vision"

    def test_initialization(self):
        """Test adapter initialization"""
        adapter = CVExtractorAdapter(max_colors=6, use_superpixels=False)
        assert adapter.extractor.max_colors == 6
        assert adapter.extractor.use_superpixels is False

    @pytest.mark.asyncio
    async def test_extract_with_image(self, sample_image_bytes):
        """Test extract method with actual image data"""
        adapter = CVExtractorAdapter(max_colors=5)
        result = await adapter.extract(sample_image_bytes)

        assert isinstance(result, ExtractionResult)
        assert result.extractor_name == "computer-vision"
        assert len(result.colors) > 0
        assert len(result.colors) <= 5
        assert result.confidence_range[0] >= 0
        assert result.confidence_range[1] <= 1

    @pytest.mark.asyncio
    async def test_extract_handles_invalid_bytes(self):
        """Test extract gracefully handles invalid image data"""
        adapter = CVExtractorAdapter()
        with pytest.raises((ValueError, RuntimeError)):
            await adapter.extract(b"invalid image data")


class TestExtractorProtocolCompliance:
    """Test that all adapters comply with ColorExtractorProtocol"""

    @pytest.mark.asyncio
    async def test_kmeans_protocol_compliance(self, sample_image_bytes):
        """Test K-means adapter is protocol-compliant"""
        adapter = KMeansExtractorAdapter()

        # Check protocol requirements
        assert hasattr(adapter, "name")
        assert isinstance(adapter.name, str)
        assert callable(adapter.extract)

        # Test it works
        result = await adapter.extract(sample_image_bytes)
        assert isinstance(result, ExtractionResult)

    @pytest.mark.asyncio
    async def test_cv_protocol_compliance(self, sample_image_bytes):
        """Test CV adapter is protocol-compliant"""
        adapter = CVExtractorAdapter()

        # Check protocol requirements
        assert hasattr(adapter, "name")
        assert isinstance(adapter.name, str)
        assert callable(adapter.extract)

        # Test it works
        result = await adapter.extract(sample_image_bytes)
        assert isinstance(result, ExtractionResult)

    def test_ai_protocol_signature(self):
        """Test AI adapter has correct protocol signature"""
        adapter = AIColorExtractorAdapter()

        # Check protocol requirements
        assert hasattr(adapter, "name")
        assert isinstance(adapter.name, str)
        assert callable(adapter.extract)
        assert adapter.name == "claude-sonnet-4.5"
