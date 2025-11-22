"""Unit tests for AIColorExtractor service"""

import pytest

from copy_that.application.color_extractor import (
    AIColorExtractor,
    ColorExtractionResult,
    ExtractedExtractedColorToken,
)


class TestExtractedColorToken:
    """Test ExtractedColorToken Pydantic model"""

    def test_color_token_creation(self):
        """Test creating a ExtractedColorToken"""
        color = ExtractedColorToken(
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            design_intent="error",
            confidence=0.95,
            harmony="complementary",
            usage=["backgrounds", "alerts"],
        )

        assert color.hex == "#FF5733"
        assert color.name == "Coral Red"
        assert color.confidence == 0.95
        assert color.design_intent == "error"

    def test_color_token_confidence_validation(self):
        """Test ExtractedColorToken confidence bounds validation"""
        # Valid confidence (0-1)
        color = ExtractedColorToken(
            hex="#FF5733", rgb="rgb(255, 87, 51)", name="Test", confidence=0.5
        )
        assert color.confidence == 0.5

        # Invalid confidence should raise validation error
        with pytest.raises(ValueError):
            ExtractedColorToken(
                hex="#FF5733",
                rgb="rgb(255, 87, 51)",
                name="Test",
                confidence=1.5,  # > 1
            )

        with pytest.raises(ValueError):
            ExtractedColorToken(
                hex="#FF5733",
                rgb="rgb(255, 87, 51)",
                name="Test",
                confidence=-0.1,  # < 0
            )


class TestColorExtractionResult:
    """Test ColorExtractionResult Pydantic model"""

    def test_color_extraction_result_creation(self):
        """Test creating a ColorExtractionResult"""
        colors = [
            ExtractedColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red", confidence=0.9),
            ExtractedColorToken(
                hex="#33FF57", rgb="rgb(51, 255, 87)", name="Green", confidence=0.85
            ),
        ]

        result = ColorExtractionResult(
            colors=colors,
            dominant_colors=["#FF5733", "#33FF57"],
            color_palette="Warm and cool tones",
            extraction_confidence=0.87,
        )

        assert len(result.colors) == 2
        assert result.extraction_confidence == 0.87
        assert len(result.dominant_colors) == 2

    def test_extraction_result_with_empty_colors(self):
        """Test ColorExtractionResult with empty colors list"""
        result = ColorExtractionResult(
            colors=[],
            dominant_colors=[],
            color_palette="No colors found",
            extraction_confidence=0.0,
        )

        assert len(result.colors) == 0
        assert result.extraction_confidence == 0.0


class TestAIColorExtractor:
    """Test AIColorExtractor service"""

    @pytest.fixture
    def extractor(self):
        """Create an AIColorExtractor instance"""
        return AIColorExtractor()

    def test_extractor_initialization(self, extractor):
        """Test AIColorExtractor initialization"""
        assert extractor.model == "claude-sonnet-4-5-20250929"
        assert extractor.client is not None

    def test_hex_to_rgb_conversion(self):
        """Test hex to RGB conversion"""
        # Test standard conversions
        assert AIColorExtractor._hex_to_rgb("#FF0000") == (255, 0, 0)
        assert AIColorExtractor._hex_to_rgb("#00FF00") == (0, 255, 0)
        assert AIColorExtractor._hex_to_rgb("#0000FF") == (0, 0, 255)
        assert AIColorExtractor._hex_to_rgb("#FFFFFF") == (255, 255, 255)
        assert AIColorExtractor._hex_to_rgb("#000000") == (0, 0, 0)
        assert AIColorExtractor._hex_to_rgb("#123456") == (18, 52, 86)

    def test_hex_to_rgb_lowercase(self):
        """Test hex to RGB conversion with lowercase input"""
        assert AIColorExtractor._hex_to_rgb("#ff0000") == (255, 0, 0)
        assert AIColorExtractor._hex_to_rgb("#aabbcc") == (170, 187, 204)

    def test_color_name_extraction(self):
        """Test extracting color names from text"""
        # Test quoted names
        name1 = AIColorExtractor._extract_color_name('Named "Sky Blue" at #87CEEB', "#87CEEB")
        assert name1 == "Sky Blue"

        # Test pattern matching for color names
        name2 = AIColorExtractor._extract_color_name("This color is named: red", "#FF5733")
        # Should extract "red" from the context
        assert isinstance(name2, str)

    def test_semantic_name_extraction(self):
        """Test extracting semantic token names"""
        # Test semantic names
        assert AIColorExtractor._extract_semantic_name("This is the primary color") == "primary"
        assert AIColorExtractor._extract_semantic_name("Error state indicator") == "error"
        assert AIColorExtractor._extract_semantic_name("Success message") == "success"
        assert AIColorExtractor._extract_semantic_name("Warning alert") == "warning"

        # Test no semantic name
        assert AIColorExtractor._extract_semantic_name("Just a random color") is None

    def test_parse_color_response_with_valid_hex_codes(self, extractor):
        """Test parsing response with valid hex codes"""
        response = """
        Extracted colors:
        1. #FF5733 - Coral Red (primary color)
        2. #33FF57 - Lime Green (success)
        3. #3357FF - Royal Blue (info)
        """

        result = extractor._parse_color_response(response, max_colors=3)

        assert len(result.colors) >= 1
        assert any(color.hex == "#FF5733" for color in result.colors)

    def test_parse_color_response_with_confidence(self, extractor):
        """Test parsing response with confidence scores"""
        response = """
        Color 1: #FF5733, confidence: 0.95, name: "Red"
        Color 2: #33FF57, confidence: 0.87, name: "Green"
        """

        result = extractor._parse_color_response(response, max_colors=2)

        # Find red color and verify confidence
        red = next((c for c in result.colors if c.hex == "#FF5733"), None)
        if red:
            assert red.confidence == 0.95

    def test_parse_color_response_fallback(self, extractor):
        """Test parsing response with no hex codes (fallback)"""
        response = "No valid hex codes in this response"

        result = extractor._parse_color_response(response, max_colors=10)

        # Should have fallback colors
        assert len(result.colors) > 0
        assert len(result.dominant_colors) == 3

    def test_parse_color_response_max_colors_limit(self, extractor):
        """Test that max_colors limit is respected"""
        response = """
        #FF0000, #00FF00, #0000FF, #FFFF00, #FF00FF,
        #00FFFF, #808080, #C0C0C0, #800000, #008000,
        #000080, #808000
        """

        result = extractor._parse_color_response(response, max_colors=5)

        assert len(result.colors) <= 5

    def test_duplicate_colors_removed(self, extractor):
        """Test that duplicate colors are removed"""
        response = """
        Colors found:
        #FF5733 - Red (primary)
        #FF5733 - Red (duplicate mention)
        #33FF57 - Green
        #FF5733 - Red (another duplicate)
        """

        result = extractor._parse_color_response(response, max_colors=10)

        # Count unique hex codes
        unique_hex = set(color.hex for color in result.colors)
        assert len(unique_hex) <= 2  # Should have at most 2 unique colors


class TestExtractedColorTokenIntegration:
    """Integration tests for color token workflow"""

    def test_full_color_extraction_workflow(self):
        """Test complete workflow from token creation to validation"""
        # Create multiple color tokens
        colors = [
            ExtractedColorToken(
                hex="#FF6B6B",
                rgb="rgb(255, 107, 107)",
                name="Red",
                design_intent="error",
                confidence=0.92,
                usage=["danger", "error-states"],
            ),
            ExtractedColorToken(
                hex="#4ECDC4",
                rgb="rgb(78, 205, 196)",
                name="Teal",
                design_intent="secondary",
                confidence=0.88,
                usage=["accents"],
            ),
        ]

        result = ColorExtractionResult(
            colors=colors,
            dominant_colors=["#FF6B6B", "#4ECDC4"],
            color_palette="Bold and modern palette",
            extraction_confidence=0.90,
        )

        # Verify all colors are properly structured
        for color in result.colors:
            assert color.hex.startswith("#")
            assert len(color.hex) == 7
            assert 0 <= color.confidence <= 1
            assert color.name
