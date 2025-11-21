"""Tests for OpenAI color extractor module"""

from unittest.mock import MagicMock, patch

import pytest

from copy_that.application.openai_color_extractor import (
    ColorExtractionResult,
    ColorToken,
    OpenAIColorExtractor,
)


class TestColorTokenModel:
    """Test ColorToken Pydantic model"""

    def test_color_token_creation(self):
        """Test basic color token creation"""
        token = ColorToken(
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            confidence=0.95,
        )
        assert token.hex == "#FF5733"
        assert token.rgb == "rgb(255, 87, 51)"
        assert token.name == "Coral Red"
        assert token.confidence == 0.95

    def test_color_token_with_all_fields(self):
        """Test color token with all optional fields"""
        token = ColorToken(
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            hsl="hsl(11, 100%, 60%)",
            hsv="hsv(11, 80%, 100%)",
            name="Coral Red",
            design_intent="primary",
            semantic_names={"simple": "red", "emotional": "energetic-red"},
            category="warm",
            confidence=0.95,
            harmony="complementary",
            temperature="warm",
            saturation_level="high",
            lightness_level="medium",
            usage=["backgrounds", "buttons"],
            count=3,
            prominence_percentage=25.5,
            wcag_contrast_on_white=3.5,
            wcag_contrast_on_black=8.2,
            wcag_aa_compliant_text=True,
            wcag_aaa_compliant_text=False,
            wcag_aa_compliant_normal=False,
            wcag_aaa_compliant_normal=False,
            colorblind_safe=True,
            tint_color="#FF8A6C",
            shade_color="#CC4529",
            tone_color="#D96B52",
            closest_web_safe="#FF6633",
            closest_css_named="tomato",
            delta_e_to_dominant=5.2,
            is_neutral=False,
            extraction_metadata={"extractor": "openai"},
            histogram_significance=0.85,
        )
        assert token.hsl == "hsl(11, 100%, 60%)"
        assert token.hsv == "hsv(11, 80%, 100%)"
        assert token.design_intent == "primary"
        assert token.semantic_names["simple"] == "red"
        assert token.usage == ["backgrounds", "buttons"]
        assert token.tint_color == "#FF8A6C"

    def test_color_token_default_values(self):
        """Test color token default values"""
        token = ColorToken(
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Red",
            confidence=0.9,
        )
        assert token.usage == []
        assert token.count == 1
        assert token.hsl is None
        assert token.design_intent is None

    def test_color_token_usage_list(self):
        """Test color token with usage list"""
        token = ColorToken(
            hex="#0000FF",
            rgb="rgb(0, 0, 255)",
            name="Blue",
            confidence=0.8,
            usage=["headers", "links", "icons"],
        )
        assert len(token.usage) == 3
        assert "headers" in token.usage


class TestColorExtractionResultModel:
    """Test ColorExtractionResult Pydantic model"""

    def test_extraction_result_creation(self):
        """Test basic extraction result creation"""
        color = ColorToken(
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            confidence=0.95,
        )
        result = ColorExtractionResult(
            colors=[color],
            dominant_colors=["#FF5733"],
            color_palette="Warm monochromatic palette",
            extraction_confidence=0.85,
        )
        assert len(result.colors) == 1
        assert result.colors[0].hex == "#FF5733"
        assert result.dominant_colors == ["#FF5733"]
        assert result.color_palette == "Warm monochromatic palette"
        assert result.extraction_confidence == 0.85

    def test_extraction_result_multiple_colors(self):
        """Test extraction result with multiple colors"""
        colors = [
            ColorToken(hex="#FF0000", rgb="rgb(255, 0, 0)", name="Red", confidence=0.9),
            ColorToken(hex="#00FF00", rgb="rgb(0, 255, 0)", name="Green", confidence=0.85),
            ColorToken(hex="#0000FF", rgb="rgb(0, 0, 255)", name="Blue", confidence=0.8),
        ]
        result = ColorExtractionResult(
            colors=colors,
            dominant_colors=["#FF0000", "#00FF00", "#0000FF"],
            color_palette="Primary colors palette",
            extraction_confidence=0.88,
        )
        assert len(result.colors) == 3
        assert len(result.dominant_colors) == 3

    def test_extraction_result_empty_colors(self):
        """Test extraction result with empty colors"""
        result = ColorExtractionResult(
            colors=[],
            dominant_colors=[],
            color_palette="No colors found",
            extraction_confidence=0.0,
        )
        assert len(result.colors) == 0
        assert result.extraction_confidence == 0.0


class TestOpenAIColorExtractor:
    """Test OpenAIColorExtractor class"""

    def test_extractor_initialization(self):
        """Test extractor initialization with API key"""
        with patch("copy_that.application.openai_color_extractor.OpenAI"):
            extractor = OpenAIColorExtractor(api_key="test-key")
            assert extractor.model == "gpt-4o"

    def test_extractor_initialization_env_var(self):
        """Test extractor initialization with environment variable"""
        with (
            patch("copy_that.application.openai_color_extractor.OpenAI"),
            patch.dict("os.environ", {"OPENAI_API_KEY": "env-key"}),
        ):
            extractor = OpenAIColorExtractor()
            assert extractor.model == "gpt-4o"

    @patch("copy_that.application.openai_color_extractor.OpenAI")
    def test_extract_colors_from_image_url(self, mock_openai_class):
        """Test extracting colors from image URL"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='''{
                    "colors": [
                        {
                            "hex": "#FF5733",
                            "name": "Coral",
                            "design_intent": "accent",
                            "confidence": 0.95,
                            "usage": ["buttons"],
                            "prominence_percentage": 30.0
                        }
                    ],
                    "dominant_colors": ["#FF5733"],
                    "color_palette": "Warm accent palette"
                }'''
                )
            )
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        extractor = OpenAIColorExtractor(api_key="test-key")
        result = extractor.extract_colors_from_image_url(
            "http://example.com/image.jpg", max_colors=5
        )

        assert isinstance(result, ColorExtractionResult)
        assert len(result.colors) == 1
        assert result.colors[0].hex == "#FF5733"
        assert result.colors[0].name == "Coral"
        assert result.dominant_colors == ["#FF5733"]

    @patch("copy_that.application.openai_color_extractor.OpenAI")
    def test_extract_colors_from_base64(self, mock_openai_class):
        """Test extracting colors from base64 image"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='''{
                    "colors": [
                        {
                            "hex": "#0000FF",
                            "name": "Blue",
                            "confidence": 0.9
                        }
                    ],
                    "dominant_colors": ["#0000FF"],
                    "color_palette": "Blue palette"
                }'''
                )
            )
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        extractor = OpenAIColorExtractor(api_key="test-key")
        result = extractor.extract_colors_from_base64(
            "base64encodeddata", media_type="image/png", max_colors=3
        )

        assert isinstance(result, ColorExtractionResult)
        assert result.colors[0].hex == "#0000FF"

    @patch("copy_that.application.openai_color_extractor.OpenAI")
    def test_extract_colors_enrichment(self, mock_openai_class):
        """Test that extracted colors are enriched with calculated properties"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='''{
                    "colors": [
                        {
                            "hex": "#FF0000",
                            "name": "Red",
                            "confidence": 0.95
                        }
                    ],
                    "dominant_colors": ["#FF0000"],
                    "color_palette": "Red palette"
                }'''
                )
            )
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        extractor = OpenAIColorExtractor(api_key="test-key")
        result = extractor.extract_colors_from_image_url("http://example.com/image.jpg")

        color = result.colors[0]
        # Check enriched properties
        assert color.rgb == "rgb(255, 0, 0)"
        assert color.hsl is not None
        assert color.hsv is not None
        assert color.wcag_contrast_on_white is not None
        assert color.wcag_contrast_on_black is not None
        assert color.tint_color is not None
        assert color.shade_color is not None
        assert color.tone_color is not None
        assert color.extraction_metadata is not None
        assert color.extraction_metadata["extractor"] == "openai_gpt4v"

    @patch("copy_that.application.openai_color_extractor.OpenAI")
    def test_extract_colors_multiple(self, mock_openai_class):
        """Test extracting multiple colors"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='''{
                    "colors": [
                        {"hex": "#FF0000", "name": "Red", "confidence": 0.9},
                        {"hex": "#00FF00", "name": "Green", "confidence": 0.85},
                        {"hex": "#0000FF", "name": "Blue", "confidence": 0.8}
                    ],
                    "dominant_colors": ["#FF0000", "#00FF00", "#0000FF"],
                    "color_palette": "Primary colors"
                }'''
                )
            )
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        extractor = OpenAIColorExtractor(api_key="test-key")
        result = extractor.extract_colors_from_image_url("http://example.com/image.jpg")

        assert len(result.colors) == 3
        assert result.colors[0].hex == "#FF0000"
        assert result.colors[1].hex == "#00FF00"
        assert result.colors[2].hex == "#0000FF"

    @patch("copy_that.application.openai_color_extractor.OpenAI")
    def test_extract_colors_invalid_json_error(self, mock_openai_class):
        """Test error handling when invalid JSON in response"""
        import json

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="This is not JSON"))
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        extractor = OpenAIColorExtractor(api_key="test-key")

        # With JSON mode, invalid JSON raises JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            extractor.extract_colors_from_image_url("http://example.com/image.jpg")

    @patch("copy_that.application.openai_color_extractor.OpenAI")
    def test_extract_colors_api_error(self, mock_openai_class):
        """Test error handling for API errors"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client

        extractor = OpenAIColorExtractor(api_key="test-key")

        with pytest.raises(Exception, match="API Error"):
            extractor.extract_colors_from_image_url("http://example.com/image.jpg")

    @patch("copy_that.application.openai_color_extractor.OpenAI")
    def test_extract_colors_default_values(self, mock_openai_class):
        """Test default values when response is missing fields"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='''{
                    "colors": [
                        {"hex": "#808080"}
                    ],
                    "dominant_colors": [],
                    "color_palette": ""
                }'''
                )
            )
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        extractor = OpenAIColorExtractor(api_key="test-key")
        result = extractor.extract_colors_from_image_url("http://example.com/image.jpg")

        color = result.colors[0]
        assert color.hex == "#808080"
        assert color.name == "Unknown"
        assert color.confidence == 0.8
        assert color.usage == []

    @patch("copy_that.application.openai_color_extractor.OpenAI")
    def test_extract_colors_with_usage(self, mock_openai_class):
        """Test colors with usage array"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='''{
                    "colors": [
                        {
                            "hex": "#FF5733",
                            "name": "Coral",
                            "confidence": 0.9,
                            "usage": ["buttons", "links", "icons"]
                        }
                    ],
                    "dominant_colors": ["#FF5733"],
                    "color_palette": "Accent palette"
                }'''
                )
            )
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        extractor = OpenAIColorExtractor(api_key="test-key")
        result = extractor.extract_colors_from_image_url("http://example.com/image.jpg")

        assert result.colors[0].usage == ["buttons", "links", "icons"]

    @patch("copy_that.application.openai_color_extractor.OpenAI")
    def test_extract_colors_accessibility_calculation(self, mock_openai_class):
        """Test WCAG compliance calculations"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='''{
                    "colors": [
                        {"hex": "#000000", "name": "Black", "confidence": 1.0}
                    ],
                    "dominant_colors": ["#000000"],
                    "color_palette": "Black"
                }'''
                )
            )
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        extractor = OpenAIColorExtractor(api_key="test-key")
        result = extractor.extract_colors_from_image_url("http://example.com/image.jpg")

        color = result.colors[0]
        # Black on white should have high contrast
        assert color.wcag_contrast_on_white > 10
        # Black on black should have low contrast
        assert color.wcag_contrast_on_black == 1.0
        # Black should pass AAA on white
        assert color.wcag_aaa_compliant_normal is True

    @patch("copy_that.application.openai_color_extractor.OpenAI")
    def test_extract_colors_response_format_used(self, mock_openai_class):
        """Test that response_format is passed to OpenAI API"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='''{
                        "colors": [{"hex": "#FF5733", "name": "Coral", "confidence": 0.9}],
                        "dominant_colors": ["#FF5733"],
                        "color_palette": "Warm"
                    }'''
                )
            )
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        extractor = OpenAIColorExtractor(api_key="test-key")
        extractor.extract_colors_from_image_url("http://example.com/image.jpg")

        # Verify response_format was passed for JSON mode
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["response_format"] == {"type": "json_object"}


class TestColorVariants:
    """Test color variant calculations in extractor"""

    @patch("copy_that.application.openai_color_extractor.OpenAI")
    def test_tint_shade_tone_calculated(self, mock_openai_class):
        """Test that tint, shade, and tone are calculated"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='''{
                    "colors": [{"hex": "#FF0000", "name": "Red", "confidence": 0.9}],
                    "dominant_colors": ["#FF0000"],
                    "color_palette": "Red"
                }'''
                )
            )
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        extractor = OpenAIColorExtractor(api_key="test-key")
        result = extractor.extract_colors_from_image_url("http://example.com/image.jpg")

        color = result.colors[0]
        # Tint should be lighter (more white)
        assert color.tint_color is not None
        assert color.tint_color.startswith("#")
        # Shade should be darker (more black)
        assert color.shade_color is not None
        assert color.shade_color.startswith("#")
        # Tone should be grayer
        assert color.tone_color is not None
        assert color.tone_color.startswith("#")


class TestSemanticNames:
    """Test semantic name enrichment"""

    @patch("copy_that.application.openai_color_extractor.OpenAI")
    def test_semantic_names_added(self, mock_openai_class):
        """Test that semantic names are added to colors"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='''{
                    "colors": [{"hex": "#FF0000", "name": "Red", "confidence": 0.9}],
                    "dominant_colors": ["#FF0000"],
                    "color_palette": "Red"
                }'''
                )
            )
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        extractor = OpenAIColorExtractor(api_key="test-key")
        result = extractor.extract_colors_from_image_url("http://example.com/image.jpg")

        color = result.colors[0]
        assert color.semantic_names is not None
        assert isinstance(color.semantic_names, dict)
