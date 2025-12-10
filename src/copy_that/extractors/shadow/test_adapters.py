"""Unit tests for shadow extractors"""

import pytest

from .adapters import AIShadowExtractorAdapter, CVShadowExtractorAdapter


class TestAIShadowExtractorAdapter:
    """Test AI shadow extractor adapter"""

    def test_name_property(self):
        """Test adapter name property"""
        adapter = AIShadowExtractorAdapter()
        assert adapter.name == "claude-shadow"

    def test_initialization(self):
        """Test adapter initialization"""
        adapter = AIShadowExtractorAdapter()
        assert adapter.extractor is not None


class TestCVShadowExtractorAdapter:
    """Test CV shadow extractor adapter"""

    def test_name_property(self):
        """Test adapter name property"""
        adapter = CVShadowExtractorAdapter()
        assert adapter.name == "cv-shadow"

    def test_initialization(self):
        """Test adapter initialization"""
        adapter = CVShadowExtractorAdapter()
        assert adapter.extractor is not None


@pytest.fixture
def sample_image_bytes():
    """Sample image for testing"""
    from pathlib import Path

    test_file = Path(__file__).parent.parent.parent.parent.parent / "test_images" / "IMG_8405.jpeg"
    if test_file.exists():
        with open(test_file, "rb") as f:
            return f.read()
    return None
