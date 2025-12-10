"""Unit tests for spacing extractors"""

import pytest

from .adapters import CVSpacingExtractorAdapter


class TestCVSpacingExtractorAdapter:
    """Test CV spacing extractor adapter"""

    def test_name_property(self):
        """Test adapter name property"""
        adapter = CVSpacingExtractorAdapter()
        assert adapter.name == "cv-spacing"

    def test_initialization(self):
        """Test adapter initialization"""
        adapter = CVSpacingExtractorAdapter(max_tokens=15)
        assert adapter.max_tokens == 15
        assert adapter.extractor is not None

    @pytest.mark.asyncio
    async def test_extract_returns_result_type(self, sample_image_bytes):
        """Test that extract returns proper ExtractionResult"""
        if sample_image_bytes is None:
            pytest.skip("No sample image")

        adapter = CVSpacingExtractorAdapter()
        result = await adapter.extract(sample_image_bytes)

        assert result is not None
        assert result.extractor_name == "cv-spacing"
        assert result.execution_time_ms > 0
        assert len(result.confidence_range) == 2
        assert 0 <= result.confidence_range[0] <= result.confidence_range[1] <= 1


@pytest.fixture
def sample_image_bytes():
    """Sample image for testing - returns None if not available"""
    from pathlib import Path

    test_file = Path(__file__).parent.parent.parent.parent.parent / "test_images" / "IMG_8405.jpeg"
    if test_file.exists():
        with open(test_file, "rb") as f:
            return f.read()
    return None
