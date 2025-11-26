"""Unit tests for API schemas"""

import pytest

from copy_that.interfaces.api.schemas import (
    ColorExtractionResponse,
    ColorTokenDetailResponse,
    ColorTokenResponse,
    ExtractColorRequest,
)


class TestColorTokenResponse:
    """Test ColorTokenResponse schema"""

    def test_color_token_response_creation(self):
        """Test creating a ColorTokenResponse"""
        response = ColorTokenResponse(
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            design_intent="error",
            confidence=0.95,
            harmony="complementary",
            usage=["backgrounds"],
        )

        assert response.hex == "#FF5733"
        assert response.name == "Coral Red"
        assert response.confidence == 0.95


class TestColorExtractionResponse:
    """Test ColorExtractionResponse schema"""

    def test_color_extraction_response_creation(self):
        """Test creating a ColorExtractionResponse"""
        colors = [
            ColorTokenResponse(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red", confidence=0.95)
        ]

        response = ColorExtractionResponse(
            colors=colors,
            dominant_colors=["#FF5733"],
            color_palette="Warm palette",
            extraction_confidence=0.95,
            extractor_used="gpt-4o",
            design_tokens={"color": {"token/test": {"value": {"hex": "#FF5733"}}}},
        )

        assert len(response.colors) == 1
        assert response.extraction_confidence == 0.95
        assert "color" in response.design_tokens


class TestExtractColorRequest:
    """Test ExtractColorRequest schema"""

    def test_extract_color_request_creation(self):
        """Test creating an ExtractColorRequest"""
        request = ExtractColorRequest(
            image_url="https://example.com/image.jpg", project_id=1, max_colors=10
        )

        assert request.image_url == "https://example.com/image.jpg"
        assert request.project_id == 1
        assert request.max_colors == 10

    def test_extract_color_request_default_max_colors(self):
        """Test ExtractColorRequest with default max_colors"""
        request = ExtractColorRequest(image_url="https://example.com/image.jpg", project_id=1)

        assert request.max_colors == 10

    def test_extract_color_request_validation(self):
        """Test ExtractColorRequest validation"""
        # Max colors should not exceed 50
        with pytest.raises(ValueError):
            ExtractColorRequest(
                image_url="https://example.com/image.jpg", project_id=1, max_colors=100
            )

        # Max colors should be at least 1
        with pytest.raises(ValueError):
            ExtractColorRequest(
                image_url="https://example.com/image.jpg", project_id=1, max_colors=0
            )


class TestColorTokenDetailResponse:
    """Test ColorTokenDetailResponse schema"""

    def test_color_token_detail_response_creation(self):
        """Test creating a ColorTokenDetailResponse"""
        response = ColorTokenDetailResponse(
            id=1,
            project_id=1,
            extraction_job_id=1,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            design_intent="error",
            confidence=0.95,
            harmony="complementary",
            usage=["backgrounds"],
            created_at="2025-11-19T12:00:00",
        )

        assert response.id == 1
        assert response.hex == "#FF5733"
        assert response.created_at == "2025-11-19T12:00:00"
