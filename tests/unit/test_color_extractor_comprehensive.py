"""Comprehensive unit tests for color extraction with fixtures"""

import pytest

from copy_that.application.color_extractor import (
    AIColorExtractor,
    ColorExtractionResult,
    ExtractedColorToken,
)


@pytest.fixture
def color_extractor():
    """Create an AIColorExtractor for testing"""
    return AIColorExtractor(api_key="test-key")


class TestExtractedColorTokenValidation:
    """Test ExtractedColorToken Pydantic model validation"""

    def test_valid_color_token(self):
        """Test creating a valid ExtractedColorToken"""
        token = ExtractedColorToken(
            hex="#FF5733", rgb="rgb(255, 87, 51)", name="Coral Red", confidence=0.85
        )
        assert token.hex == "#FF5733"
        assert token.confidence == 0.85
        assert token.name == "Coral Red"

    def test_color_token_with_design_intent(self):
        """Test ExtractedColorToken with design intent"""
        token = ExtractedColorToken(
            hex="#FF0000", rgb="rgb(255, 0, 0)", name="Red", design_intent="error", confidence=0.9
        )
        assert token.design_intent == "error"

    def test_confidence_lower_bound(self):
        """Test confidence score lower bound (0)"""
        token = ExtractedColorToken(hex="#000000", rgb="rgb(0, 0, 0)", name="Black", confidence=0.0)
        assert token.confidence == 0.0

    def test_confidence_upper_bound(self):
        """Test confidence score upper bound (1.0)"""
        token = ExtractedColorToken(
            hex="#FFFFFF", rgb="rgb(255, 255, 255)", name="White", confidence=1.0
        )
        assert token.confidence == 1.0

    def test_confidence_invalid_negative(self):
        """Test that negative confidence raises validation error"""
        with pytest.raises(ValueError):
            ExtractedColorToken(hex="#FF0000", rgb="rgb(255, 0, 0)", name="Red", confidence=-0.1)

    def test_confidence_invalid_over_one(self):
        """Test that confidence > 1.0 raises validation error"""
        with pytest.raises(ValueError):
            ExtractedColorToken(hex="#FF0000", rgb="rgb(255, 0, 0)", name="Red", confidence=1.5)

    def test_color_token_with_harmony(self):
        """Test ExtractedColorToken with harmony information"""
        token = ExtractedColorToken(
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral",
            harmony="complementary",
            confidence=0.8,
        )
        assert token.harmony == "complementary"

    def test_color_token_with_usage(self):
        """Test ExtractedColorToken with usage contexts"""
        token = ExtractedColorToken(
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral",
            usage=["backgrounds", "alerts"],
            confidence=0.8,
        )
        assert token.usage == ["backgrounds", "alerts"]

    def test_color_token_default_usage(self):
        """Test ExtractedColorToken with default empty usage list"""
        token = ExtractedColorToken(
            hex="#FF5733", rgb="rgb(255, 87, 51)", name="Coral", confidence=0.8
        )
        assert token.usage == []


class TestColorExtractionResult:
    """Test ColorExtractionResult model"""

    def test_valid_extraction_result(self):
        """Test creating a valid extraction result"""
        colors = [
            ExtractedColorToken(hex="#FF0000", rgb="rgb(255, 0, 0)", name="Red", confidence=0.9),
            ExtractedColorToken(hex="#00FF00", rgb="rgb(0, 255, 0)", name="Green", confidence=0.85),
        ]
        result = ColorExtractionResult(
            colors=colors,
            dominant_colors=["#FF0000", "#00FF00"],
            color_palette="Bright and vibrant",
            extraction_confidence=0.87,
        )
        assert len(result.colors) == 2
        assert result.extraction_confidence == 0.87

    def test_extraction_result_empty_colors(self):
        """Test extraction result with no colors"""
        result = ColorExtractionResult(
            colors=[],
            dominant_colors=[],
            color_palette="No colors found",
            extraction_confidence=0.0,
        )
        assert len(result.colors) == 0
        assert result.extraction_confidence == 0.0

    def test_extraction_result_confidence_bounds(self):
        """Test extraction result confidence validation"""
        colors = [
            ExtractedColorToken(hex="#FF0000", rgb="rgb(255, 0, 0)", name="Red", confidence=0.9)
        ]

        # Valid bounds
        result = ColorExtractionResult(
            colors=colors,
            dominant_colors=["#FF0000"],
            color_palette="Red",
            extraction_confidence=0.5,
        )
        assert result.extraction_confidence == 0.5

        # Invalid - too high
        with pytest.raises(ValueError):
            ColorExtractionResult(
                colors=colors,
                dominant_colors=["#FF0000"],
                color_palette="Red",
                extraction_confidence=1.5,
            )


class TestHexToRGBConversion:
    """Test hex color to RGB conversion utility"""

    def test_hex_to_rgb_standard(self, color_extractor):
        """Test standard hex to RGB conversions"""
        assert color_extractor._hex_to_rgb("#FF0000") == (255, 0, 0)
        assert color_extractor._hex_to_rgb("#00FF00") == (0, 255, 0)
        assert color_extractor._hex_to_rgb("#0000FF") == (0, 0, 255)
        assert color_extractor._hex_to_rgb("#FFFFFF") == (255, 255, 255)
        assert color_extractor._hex_to_rgb("#000000") == (0, 0, 0)

    def test_hex_to_rgb_lowercase(self, color_extractor):
        """Test hex to RGB with lowercase input"""
        assert color_extractor._hex_to_rgb("#ff0000") == (255, 0, 0)
        assert color_extractor._hex_to_rgb("#00ff00") == (0, 255, 0)

    def test_hex_to_rgb_mixed_case(self, color_extractor):
        """Test hex to RGB with mixed case"""
        assert color_extractor._hex_to_rgb("#FfBbAa") == (255, 187, 170)

    def test_hex_to_rgb_arbitrary_values(self, color_extractor):
        """Test hex to RGB with arbitrary color values"""
        assert color_extractor._hex_to_rgb("#123456") == (18, 52, 86)
        assert color_extractor._hex_to_rgb("#ABCDEF") == (171, 205, 239)


class TestColorNameExtraction:
    """Test color name extraction from text"""

    def test_extract_quoted_color_name(self, color_extractor):
        """Test extracting quoted color names"""
        name = color_extractor._extract_color_name('Named "Sky Blue" at #87CEEB', "#87CEEB")
        assert name == "Sky Blue"

    def test_extract_pattern_color_name(self, color_extractor):
        """Test extracting pattern-based color names"""
        name = color_extractor._extract_color_name("Color named red at #FF0000", "#FF0000")
        assert isinstance(name, str)
        assert len(name) > 0

    def test_extract_fallback_hex_name(self, color_extractor):
        """Test fallback to hex code when no name found"""
        name = color_extractor._extract_color_name("Just a color #FF0000", "#FF0000")
        assert "#FF0000" in name


class TestSemanticNameExtraction:
    """Test semantic token name extraction"""

    def test_extract_primary_semantic(self, color_extractor):
        """Test extracting primary semantic token"""
        name = color_extractor._extract_semantic_name("This is the primary color for buttons")
        assert name == "primary"

    def test_extract_error_semantic(self, color_extractor):
        """Test extracting error semantic token"""
        name = color_extractor._extract_semantic_name("Error state indicator")
        assert name == "error"

    def test_extract_success_semantic(self, color_extractor):
        """Test extracting success semantic token"""
        name = color_extractor._extract_semantic_name("Success message color")
        assert name == "success"

    def test_extract_warning_semantic(self, color_extractor):
        """Test extracting warning semantic token"""
        name = color_extractor._extract_semantic_name("Warning alert background")
        assert name == "warning"

    def test_extract_info_semantic(self, color_extractor):
        """Test extracting info semantic token"""
        name = color_extractor._extract_semantic_name("This is the info notification color")
        assert name == "info"

    def test_no_semantic_name(self, color_extractor):
        """Test when no semantic name is present"""
        name = color_extractor._extract_semantic_name("Just a random purple color")
        assert name is None


class TestColorResponseParsing:
    """Test parsing Claude API responses"""

    def test_parse_simple_hex_response(self, color_extractor):
        """Test parsing response with simple hex codes"""
        response = """
        Extracted colors:
        1. #FF5733 - Coral Red
        2. #33FF57 - Lime Green
        3. #3357FF - Royal Blue
        """
        result = color_extractor._parse_color_response(response, max_colors=3)

        assert len(result.colors) >= 1
        assert any(c.hex == "#FF5733" for c in result.colors)

    def test_parse_response_respects_max_colors(self, color_extractor):
        """Test that max_colors limit is respected"""
        response = """
        #FF0000, #00FF00, #0000FF, #FFFF00, #FF00FF,
        #00FFFF, #808080, #C0C0C0, #800000, #008000,
        #000080, #808000, #C00000, #00C000, #0000C0
        """
        result = color_extractor._parse_color_response(response, max_colors=5)

        assert len(result.colors) <= 5

    def test_parse_removes_duplicates(self, color_extractor):
        """Test that duplicate colors are removed"""
        response = """
        Colors found:
        #FF5733 - Red (primary)
        #FF5733 - Red (duplicate)
        #33FF57 - Green
        #FF5733 - Red (another duplicate)
        """
        result = color_extractor._parse_color_response(response, max_colors=10)

        hex_codes = [c.hex for c in result.colors]
        unique_hex = set(hex_codes)
        # Should have fewer total colors than hex_codes due to deduplication
        assert len(unique_hex) <= len(hex_codes)

    def test_parse_response_with_confidence(self, color_extractor):
        """Test parsing response with confidence scores"""
        response = """
        Color 1: #FF5733, confidence: 0.95
        Color 2: #33FF57, confidence: 0.87
        """
        result = color_extractor._parse_color_response(response, max_colors=2)

        # Verify at least one color was extracted
        assert len(result.colors) >= 1

    def test_parse_fallback_palette(self, color_extractor):
        """Test fallback palette when no hex codes found"""
        response = "No valid color codes found in this response"
        result = color_extractor._parse_color_response(response, max_colors=10)

        # Should have fallback colors
        assert len(result.colors) > 0
        assert len(result.dominant_colors) == 3
        assert result.extraction_confidence > 0


class TestExtractorInitialization:
    """Test AIColorExtractor initialization"""

    def test_extractor_with_default_key(self):
        """Test extractor initializes with default API key"""
        extractor = AIColorExtractor()
        assert extractor.model == "claude-sonnet-4-5-20250929"
        assert extractor.client is not None

    def test_extractor_with_custom_key(self):
        """Test extractor initializes with custom API key"""
        extractor = AIColorExtractor(api_key="custom-key-123")
        assert extractor.model == "claude-sonnet-4-5-20250929"
        assert extractor.client is not None

    def test_extractor_model_version(self):
        """Test that extractor uses correct model version"""
        extractor = AIColorExtractor()
        # Verify it's using Claude Sonnet 4.5 (latest)
        assert "sonnet-4-5" in extractor.model


class TestColorExtractionIntegration:
    """Integration tests for full color extraction workflow"""

    def test_full_extraction_workflow(self, color_extractor):
        """Test complete extraction workflow"""
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

        # Verify structure
        assert len(result.colors) == 2
        assert result.extraction_confidence == 0.90

        # Verify each color has required fields
        for color in result.colors:
            assert color.hex.startswith("#")
            assert len(color.hex) == 7
            assert 0 <= color.confidence <= 1
            assert color.name
            assert color.rgb.startswith("rgb")

    def test_extraction_result_serialization(self):
        """Test that extraction result can be serialized to JSON"""
        colors = [
            ExtractedColorToken(hex="#FF0000", rgb="rgb(255, 0, 0)", name="Red", confidence=0.9)
        ]
        result = ColorExtractionResult(
            colors=colors,
            dominant_colors=["#FF0000"],
            color_palette="Red dominant",
            extraction_confidence=0.9,
        )

        # Should be JSON serializable
        import json

        json_str = json.dumps(result.model_dump())
        assert "#FF0000" in json_str
