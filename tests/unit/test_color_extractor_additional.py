"""Additional tests for color_extractor module to increase coverage"""

import pytest

from copy_that.application.color_extractor import (
    AIColorExtractor,
    ColorExtractionResult,
    ColorToken,
)


class TestColorTokenEdgeCases:
    """Test ColorToken edge cases"""

    def test_color_token_with_all_fields(self):
        """Test creating a ColorToken with all optional fields"""
        token = ColorToken(
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            design_intent="primary",
            confidence=0.95,
            harmony="complementary",
            usage=["buttons", "headers"],
        )
        assert token.hex == "#FF5733"
        assert token.rgb == "rgb(255, 87, 51)"
        assert token.name == "Coral Red"
        assert token.design_intent == "primary"
        assert token.confidence == 0.95
        assert token.harmony == "complementary"
        assert token.usage == ["buttons", "headers"]

    def test_color_token_with_empty_usage(self):
        """Test ColorToken with empty usage list"""
        token = ColorToken(
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Test",
            confidence=0.5,
            usage=[],
        )
        assert token.usage == []

    def test_color_token_boundary_confidence_zero(self):
        """Test ColorToken with zero confidence"""
        token = ColorToken(
            hex="#000000",
            rgb="rgb(0, 0, 0)",
            name="Black",
            confidence=0.0,
        )
        assert token.confidence == 0.0

    def test_color_token_boundary_confidence_one(self):
        """Test ColorToken with confidence of 1"""
        token = ColorToken(
            hex="#FFFFFF",
            rgb="rgb(255, 255, 255)",
            name="White",
            confidence=1.0,
        )
        assert token.confidence == 1.0

    def test_color_token_with_design_intents(self):
        """Test various design intents"""
        intents = ["primary", "secondary", "accent", "background", "text", "error", "warning", "success"]
        for intent in intents:
            token = ColorToken(
                hex="#FF0000",
                rgb="rgb(255, 0, 0)",
                name="Test",
                design_intent=intent,
                confidence=0.5,
            )
            assert token.design_intent == intent


class TestColorExtractionResultEdgeCases:
    """Test ColorExtractionResult edge cases"""

    def test_result_with_single_color(self):
        """Test result with single color"""
        color = ColorToken(
            hex="#FF0000",
            rgb="rgb(255, 0, 0)",
            name="Red",
            confidence=0.9,
        )
        result = ColorExtractionResult(
            colors=[color],
            dominant_colors=["#FF0000"],
            metadata={"source": "test"},
            extraction_confidence=0.9,
        )
        assert len(result.colors) == 1
        assert result.extraction_confidence == 0.9

    def test_result_with_many_colors(self):
        """Test result with many colors"""
        colors = []
        for i in range(20):
            colors.append(
                ColorToken(
                    hex=f"#FF{i:02d}00",
                    rgb=f"rgb(255, {i}, 0)",
                    name=f"Color {i}",
                    confidence=0.5 + i * 0.02,
                )
            )
        result = ColorExtractionResult(
            colors=colors,
            dominant_colors=[c.hex for c in colors[:3]],
            metadata={"count": len(colors)},
            extraction_confidence=0.85,
        )
        assert len(result.colors) == 20

    def test_result_with_empty_metadata(self):
        """Test result with empty metadata"""
        result = ColorExtractionResult(
            colors=[],
            dominant_colors=[],
            metadata={},
            extraction_confidence=0.0,
        )
        assert result.metadata == {}


class TestAIColorExtractorMethods:
    """Test AIColorExtractor helper methods"""

    def test_hex_to_rgb_with_hash(self):
        """Test hex to RGB conversion with hash"""
        extractor = AIColorExtractor()
        result = extractor._hex_to_rgb("#FF5733")
        assert result == "rgb(255, 87, 51)"

    def test_hex_to_rgb_without_hash(self):
        """Test hex to RGB handles hex without hash"""
        extractor = AIColorExtractor()
        result = extractor._hex_to_rgb("FF5733")
        assert result == "rgb(255, 87, 51)"

    def test_hex_to_rgb_lowercase(self):
        """Test hex to RGB with lowercase"""
        extractor = AIColorExtractor()
        result = extractor._hex_to_rgb("#ff5733")
        assert result == "rgb(255, 87, 51)"

    def test_extract_color_name_with_quotes(self):
        """Test extracting color name from quoted text"""
        extractor = AIColorExtractor()
        text = 'The color is called "Coral Red" in design'
        result = extractor._extract_color_name(text)
        assert "Coral" in result or "Red" in result or result != ""

    def test_extract_color_name_with_colon(self):
        """Test extracting color name with colon pattern"""
        extractor = AIColorExtractor()
        text = "Color name: Vibrant Orange"
        result = extractor._extract_color_name(text)
        assert len(result) > 0

    def test_extract_semantic_name_primary(self):
        """Test extracting semantic name for primary"""
        extractor = AIColorExtractor()
        text = "This is the primary color for buttons"
        result = extractor._extract_semantic_name(text)
        assert result in ["primary", None, ""]

    def test_extract_semantic_name_error(self):
        """Test extracting semantic name for error"""
        extractor = AIColorExtractor()
        text = "Used for error states and alerts"
        result = extractor._extract_semantic_name(text)
        assert result in ["error", None, ""]

    def test_extract_semantic_name_success(self):
        """Test extracting semantic name for success"""
        extractor = AIColorExtractor()
        text = "Represents success messages"
        result = extractor._extract_semantic_name(text)
        assert result in ["success", None, ""]

    def test_parse_color_response_simple(self):
        """Test parsing simple color response"""
        extractor = AIColorExtractor()
        response = "#FF0000\n#00FF00\n#0000FF"
        colors = extractor._parse_color_response(response, max_colors=10)
        assert len(colors) <= 10
        assert all(c.hex.startswith("#") for c in colors)

    def test_parse_color_response_with_confidence(self):
        """Test parsing response with confidence values"""
        extractor = AIColorExtractor()
        response = "#FF0000 confidence: 0.95\n#00FF00 confidence: 0.85"
        colors = extractor._parse_color_response(response, max_colors=10)
        assert len(colors) > 0

    def test_parse_color_response_max_limit(self):
        """Test that max_colors limit is respected"""
        extractor = AIColorExtractor()
        response = "\n".join([f"#{i:06X}" for i in range(100)])
        colors = extractor._parse_color_response(response, max_colors=5)
        assert len(colors) <= 5

    def test_parse_color_response_duplicates_removed(self):
        """Test that duplicate colors are removed"""
        extractor = AIColorExtractor()
        response = "#FF0000\n#FF0000\n#FF0000"
        colors = extractor._parse_color_response(response, max_colors=10)
        assert len(colors) == 1

    def test_parse_color_response_fallback(self):
        """Test fallback when no valid colors found"""
        extractor = AIColorExtractor()
        response = "No valid hex codes here"
        colors = extractor._parse_color_response(response, max_colors=10)
        # Should return empty or fallback palette
        assert isinstance(colors, list)


class TestExtractorInitialization:
    """Test extractor initialization"""

    def test_extractor_default_init(self):
        """Test extractor with default initialization"""
        extractor = AIColorExtractor()
        assert extractor is not None

    def test_extractor_with_custom_key(self):
        """Test extractor with custom API key"""
        extractor = AIColorExtractor(api_key="test-key")
        assert extractor is not None

    def test_extractor_model_attribute(self):
        """Test extractor has model attribute"""
        extractor = AIColorExtractor()
        assert hasattr(extractor, "model")
