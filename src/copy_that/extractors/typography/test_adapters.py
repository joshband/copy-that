"""Unit tests for typography extractors"""

import pytest

from .adapters import AITypographyExtractorAdapter


class TestAITypographyExtractorAdapter:
    """Test AI typography extractor adapter"""

    def test_name_property(self):
        """Test adapter name property"""
        adapter = AITypographyExtractorAdapter()
        assert adapter.name == "claude-typography"

    def test_initialization(self):
        """Test adapter initialization"""
        adapter = AITypographyExtractorAdapter()
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
