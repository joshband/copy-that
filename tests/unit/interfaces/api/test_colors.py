"""Comprehensive unit tests for colors API endpoints

This module provides extensive test coverage for:
- serialize_color_token function
- get_extractor function
- extract_colors_from_image endpoint
- extract_colors_streaming endpoint
- get_project_colors endpoint
- create_color_token endpoint
- get_color_token endpoint
"""

import json
import os
from unittest.mock import MagicMock, patch

import anthropic
import pytest
import pytest_asyncio
import requests
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.application.color_extractor import AIColorExtractor, ExtractedColorToken
from copy_that.application.openai_color_extractor import OpenAIColorExtractor
from copy_that.domain.models import ColorToken, ExtractionJob, Project
from copy_that.infrastructure.database import Base, get_db
from copy_that.interfaces.api.colors import (
    get_extractor,
    serialize_color_token,
)
from copy_that.interfaces.api.main import app


@pytest_asyncio.fixture
async def async_db():
    """Create an in-memory SQLite database for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(async_db):
    """Create a test client with mocked database"""

    async def override_get_db():
        yield async_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_project(async_db):
    """Create a test project"""
    project = Project(name="Test Project", description="For testing colors API")
    async_db.add(project)
    await async_db.commit()
    await async_db.refresh(project)
    return project


@pytest_asyncio.fixture
async def test_color_token(async_db, test_project):
    """Create a test color token with all fields populated"""
    color = ColorToken(
        project_id=test_project.id,
        hex="#FF5733",
        rgb="rgb(255, 87, 51)",
        hsl="hsl(10, 100%, 60%)",
        hsv="hsv(10, 80%, 100%)",
        name="Coral Red",
        design_intent="error",
        semantic_names=json.dumps({"simple": "red", "descriptive": "coral red"}),
        extraction_metadata=json.dumps({"source": "test"}),
        category="accent",
        confidence=0.95,
        harmony="complementary",
        temperature="warm",
        saturation_level="vibrant",
        lightness_level="medium",
        usage=json.dumps(["alerts", "buttons"]),
        count=5,
        prominence_percentage=15.5,
        wcag_contrast_on_white=4.5,
        wcag_contrast_on_black=12.5,
        wcag_aa_compliant_text=True,
        wcag_aaa_compliant_text=True,
        wcag_aa_compliant_normal=True,
        wcag_aaa_compliant_normal=False,
        colorblind_safe=True,
        tint_color="#FF8A73",
        shade_color="#B33D24",
        tone_color="#CC6E57",
        closest_web_safe="#FF6633",
        closest_css_named="tomato",
        delta_e_to_dominant=5.2,
        is_neutral=False,
    )
    async_db.add(color)
    await async_db.commit()
    await async_db.refresh(color)
    return color


class TestSerializeColorToken:
    """Test serialize_color_token function"""

    def test_serialize_color_token_full(self, test_color_token):
        """Test serialization of color token with all fields"""
        result = serialize_color_token(test_color_token)

        assert result["id"] == test_color_token.id
        assert result["hex"] == "#FF5733"
        assert result["rgb"] == "rgb(255, 87, 51)"
        assert result["hsl"] == "hsl(10, 100%, 60%)"
        assert result["hsv"] == "hsv(10, 80%, 100%)"
        assert result["name"] == "Coral Red"
        assert result["design_intent"] == "error"
        assert result["semantic_names"] == {"simple": "red", "descriptive": "coral red"}
        assert result["extraction_metadata"] == {"source": "test"}
        assert result["category"] == "accent"
        assert result["confidence"] == 0.95
        assert result["harmony"] == "complementary"
        assert result["temperature"] == "warm"
        assert result["saturation_level"] == "vibrant"
        assert result["lightness_level"] == "medium"
        assert result["usage"] == ["alerts", "buttons"]
        assert result["count"] == 5
        assert result["prominence_percentage"] == 15.5
        assert result["wcag_contrast_on_white"] == 4.5
        assert result["wcag_contrast_on_black"] == 12.5
        assert result["wcag_aa_compliant_text"] is True
        assert result["wcag_aaa_compliant_text"] is True
        assert result["wcag_aa_compliant_normal"] is True
        assert result["wcag_aaa_compliant_normal"] is False
        assert result["colorblind_safe"] is True
        assert result["tint_color"] == "#FF8A73"
        assert result["shade_color"] == "#B33D24"
        assert result["tone_color"] == "#CC6E57"
        assert result["closest_web_safe"] == "#FF6633"
        assert result["closest_css_named"] == "tomato"
        assert result["delta_e_to_dominant"] == 5.2
        assert result["is_neutral"] is False

    @pytest.mark.asyncio
    async def test_serialize_color_token_minimal(self, async_db, test_project):
        """Test serialization of color token with minimal fields"""
        color = ColorToken(
            project_id=test_project.id,
            hex="#000000",
            rgb="rgb(0, 0, 0)",
            name="Black",
            confidence=1.0,
        )
        async_db.add(color)
        await async_db.commit()
        await async_db.refresh(color)

        result = serialize_color_token(color)

        assert result["hex"] == "#000000"
        assert result["rgb"] == "rgb(0, 0, 0)"
        assert result["name"] == "Black"
        assert result["confidence"] == 1.0
        assert result["semantic_names"] is None
        assert result["extraction_metadata"] is None
        assert result["usage"] is None


class TestGetExtractor:
    """Test get_extractor function"""

    def test_get_extractor_openai_with_key(self):
        """Test getting OpenAI extractor when key is available"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "ANTHROPIC_API_KEY": ""}):
            extractor, model_name = get_extractor("openai")
            assert isinstance(extractor, OpenAIColorExtractor)
            assert model_name == "gpt-4o"

    def test_get_extractor_openai_without_key(self):
        """Test getting OpenAI extractor when key is missing"""
        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": ""}, clear=True),
            pytest.raises(ValueError, match="OPENAI_API_KEY not set"),
        ):
            get_extractor("openai")

    def test_get_extractor_claude_with_key(self):
        """Test getting Claude extractor when key is available"""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key", "OPENAI_API_KEY": ""}):
            extractor, model_name = get_extractor("claude")
            assert isinstance(extractor, AIColorExtractor)
            assert model_name == "claude-sonnet-4-5"

    def test_get_extractor_claude_without_key(self):
        """Test getting Claude extractor when key is missing"""
        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": ""}, clear=True),
            pytest.raises(ValueError, match="ANTHROPIC_API_KEY not set"),
        ):
            get_extractor("claude")

    def test_get_extractor_auto_prefers_openai(self):
        """Test auto mode prefers OpenAI when available"""
        with patch.dict(
            os.environ, {"OPENAI_API_KEY": "openai-key", "ANTHROPIC_API_KEY": "anthropic-key"}
        ):
            extractor, model_name = get_extractor("auto")
            assert isinstance(extractor, OpenAIColorExtractor)
            assert model_name == "gpt-4o"

    def test_get_extractor_auto_fallback_to_claude(self):
        """Test auto mode falls back to Claude when OpenAI not available"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": "anthropic-key"}):
            extractor, model_name = get_extractor("auto")
            assert isinstance(extractor, AIColorExtractor)
            assert model_name == "claude-sonnet-4-5"

    def test_get_extractor_auto_no_keys(self):
        """Test auto mode raises error when no keys available"""
        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": ""}, clear=True),
            pytest.raises(ValueError, match="No API key available"),
        ):
            get_extractor("auto")


class TestExtractColorsFromImageEndpoint:
    """Test extract_colors_from_image endpoint"""

    @pytest.mark.asyncio
    async def test_extract_colors_project_not_found(self, client):
        """Test extraction fails when project not found"""
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "image_url": "https://example.com/image.jpg",
                "project_id": 999,
                "max_colors": 5,
            },
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_extract_colors_no_image_source(self, client, test_project):
        """Test extraction fails when no image source provided"""
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "project_id": test_project.id,
                "max_colors": 5,
            },
        )
        assert response.status_code == 400
        assert "image_url or image_base64" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_extract_colors_from_url_success(self, client, async_db, test_project):
        """Test successful color extraction from URL"""
        mock_result = MagicMock()
        mock_result.colors = [
            ExtractedColorToken(
                hex="#FF5733",
                rgb="rgb(255, 87, 51)",
                name="Coral",
                confidence=0.9,
                design_intent="accent",
                semantic_names={"simple": "red"},
                extraction_metadata={"source": "url"},
                harmony="complementary",
                usage=["alerts"],
            )
        ]
        mock_result.color_palette = "Warm palette"
        mock_result.dominant_colors = ["#FF5733"]
        mock_result.extraction_confidence = 0.9
        mock_result.extractor_used = None

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_image_url",
                return_value=mock_result,
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract",
                json={
                    "image_url": "https://example.com/image.jpg",
                    "project_id": test_project.id,
                    "max_colors": 5,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["colors"]) == 1
        assert data["colors"][0]["hex"] == "#FF5733"
        assert data["extractor_used"] == "gpt-4o"

    @pytest.mark.asyncio
    async def test_extract_colors_from_base64_success(self, client, async_db, test_project):
        """Test successful color extraction from base64"""
        mock_result = MagicMock()
        mock_result.colors = [
            ExtractedColorToken(
                hex="#00FF00",
                rgb="rgb(0, 255, 0)",
                name="Green",
                confidence=0.85,
                design_intent="success",
                semantic_names=None,
                extraction_metadata=None,
                harmony="monochromatic",
                usage=["buttons"],
            )
        ]
        mock_result.color_palette = "Green palette"
        mock_result.dominant_colors = ["#00FF00"]
        mock_result.extraction_confidence = 0.85
        mock_result.extractor_used = None

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_base64",
                return_value=mock_result,
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract",
                json={
                    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                    "project_id": test_project.id,
                    "max_colors": 5,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["colors"]) == 1
        assert data["colors"][0]["hex"] == "#00FF00"

    @pytest.mark.asyncio
    async def test_extract_colors_with_claude_extractor(self, client, async_db, test_project):
        """Test color extraction with Claude extractor"""
        mock_result = MagicMock()
        mock_result.colors = [
            ExtractedColorToken(
                hex="#0000FF",
                rgb="rgb(0, 0, 255)",
                name="Blue",
                confidence=0.92,
                design_intent="primary",
                semantic_names=None,
                extraction_metadata=None,
                harmony="analogous",
                usage=["backgrounds"],
            )
        ]
        mock_result.color_palette = "Blue palette"
        mock_result.dominant_colors = ["#0000FF"]
        mock_result.extraction_confidence = 0.92
        mock_result.extractor_used = None

        with (
            patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key", "OPENAI_API_KEY": ""}),
            patch.object(
                AIColorExtractor,
                "extract_colors_from_image_url",
                return_value=mock_result,
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract",
                json={
                    "image_url": "https://example.com/image.jpg",
                    "project_id": test_project.id,
                    "max_colors": 5,
                    "extractor": "claude",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["extractor_used"] == "claude-sonnet-4-5"

    @pytest.mark.asyncio
    async def test_extract_colors_value_error(self, client, test_project):
        """Test extraction handles ValueError properly"""
        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_image_url",
                side_effect=ValueError("Invalid image format"),
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract",
                json={
                    "image_url": "https://example.com/image.jpg",
                    "project_id": test_project.id,
                    "max_colors": 5,
                },
            )

        assert response.status_code == 400
        assert "Invalid input" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_extract_colors_request_exception(self, client, test_project):
        """Test extraction handles requests.RequestException properly"""
        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_image_url",
                side_effect=requests.RequestException("Failed to fetch"),
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract",
                json={
                    "image_url": "https://example.com/image.jpg",
                    "project_id": test_project.id,
                    "max_colors": 5,
                },
            )

        assert response.status_code == 502
        assert "Failed to fetch image" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_extract_colors_anthropic_api_error(self, client, test_project):
        """Test extraction handles anthropic.APIError properly"""
        with (
            patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key", "OPENAI_API_KEY": ""}),
            patch.object(
                AIColorExtractor,
                "extract_colors_from_image_url",
                side_effect=anthropic.APIError(
                    message="API error",
                    request=MagicMock(),
                    body=None,
                ),
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract",
                json={
                    "image_url": "https://example.com/image.jpg",
                    "project_id": test_project.id,
                    "max_colors": 5,
                    "extractor": "claude",
                },
            )

        assert response.status_code == 502
        assert "AI service error" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_extract_colors_unexpected_exception(self, client, test_project):
        """Test extraction handles unexpected exceptions properly"""
        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_image_url",
                side_effect=Exception("Unexpected error"),
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract",
                json={
                    "image_url": "https://example.com/image.jpg",
                    "project_id": test_project.id,
                    "max_colors": 5,
                },
            )

        assert response.status_code == 500
        assert "unexpected error" in response.json()["detail"].lower()


class TestExtractColorsStreamingEndpoint:
    """Test extract_colors_streaming endpoint"""

    @pytest.mark.asyncio
    async def test_streaming_project_not_found(self, client):
        """Test streaming fails when project not found"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            response = await client.post(
                "/api/v1/colors/extract-streaming",
                json={
                    "image_url": "https://example.com/image.jpg",
                    "project_id": 999,
                    "max_colors": 5,
                },
            )

        assert response.status_code == 200  # SSE returns 200
        assert "text/event-stream" in response.headers.get("content-type", "")
        # The error is in the stream
        assert "not found" in response.text.lower()

    @pytest.mark.asyncio
    async def test_streaming_success_with_url(self, client, async_db, test_project):
        """Test successful streaming extraction from URL"""
        mock_result = MagicMock()
        mock_result.colors = [
            ExtractedColorToken(
                hex="#FF5733",
                rgb="rgb(255, 87, 51)",
                hsl="hsl(10, 100%, 60%)",
                hsv="hsv(10, 80%, 100%)",
                name="Coral",
                confidence=0.9,
                design_intent="accent",
                semantic_names={"simple": "red"},
                harmony="complementary",
                temperature="warm",
                saturation_level="vibrant",
                lightness_level="medium",
                usage=["alerts"],
                count=3,
                wcag_contrast_on_white=4.5,
                wcag_contrast_on_black=12.5,
                wcag_aa_compliant_text=True,
                wcag_aaa_compliant_text=True,
                wcag_aa_compliant_normal=True,
                wcag_aaa_compliant_normal=False,
                colorblind_safe=True,
                tint_color="#FF8A73",
                shade_color="#B33D24",
                tone_color="#CC6E57",
                closest_web_safe="#FF6633",
                closest_css_named="tomato",
                delta_e_to_dominant=5.2,
                is_neutral=False,
            )
        ]
        mock_result.color_palette = "Warm palette"
        mock_result.dominant_colors = ["#FF5733"]
        mock_result.extraction_confidence = 0.9

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_image_url",
                return_value=mock_result,
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract-streaming",
                json={
                    "image_url": "https://example.com/image.jpg",
                    "project_id": test_project.id,
                    "max_colors": 5,
                },
            )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        # Parse SSE response
        content = response.text
        assert "colors_extracted" in content
        assert "extraction_complete" in content
        assert "#FF5733" in content

    @pytest.mark.asyncio
    async def test_streaming_success_with_base64(self, client, async_db, test_project):
        """Test successful streaming extraction from base64"""
        mock_result = MagicMock()
        mock_result.colors = [
            ExtractedColorToken(
                hex="#00FF00",
                rgb="rgb(0, 255, 0)",
                hsl="hsl(120, 100%, 50%)",
                hsv="hsv(120, 100%, 100%)",
                name="Green",
                confidence=0.85,
                design_intent="success",
                semantic_names=None,
                harmony="monochromatic",
                temperature="cool",
                saturation_level="vibrant",
                lightness_level="medium",
                usage=["buttons"],
                count=1,
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
                is_neutral=False,
            )
        ]
        mock_result.color_palette = "Green palette"
        mock_result.dominant_colors = ["#00FF00"]
        mock_result.extraction_confidence = 0.85

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_base64",
                return_value=mock_result,
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract-streaming",
                json={
                    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                    "project_id": test_project.id,
                    "max_colors": 5,
                },
            )

        assert response.status_code == 200
        content = response.text
        assert "colors_extracted" in content
        assert "#00FF00" in content

    @pytest.mark.asyncio
    async def test_streaming_multiple_colors_progress(self, client, async_db, test_project):
        """Test streaming with multiple colors shows progress"""
        # Create 10 colors to test progress streaming
        colors = []
        for i in range(10):
            colors.append(
                ExtractedColorToken(
                    hex=f"#FF{i:02d}00",
                    rgb=f"rgb(255, {i}, 0)",
                    hsl=f"hsl({i}, 100%, 50%)",
                    hsv=f"hsv({i}, 100%, 100%)",
                    name=f"Color{i}",
                    confidence=0.9,
                    design_intent="accent",
                    semantic_names=None,
                    harmony="complementary",
                    temperature="warm",
                    saturation_level="vibrant",
                    lightness_level="medium",
                    usage=[],
                    count=1,
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
                    is_neutral=False,
                )
            )

        mock_result = MagicMock()
        mock_result.colors = colors
        mock_result.color_palette = "Multi-color palette"
        mock_result.dominant_colors = ["#FF0000"]
        mock_result.extraction_confidence = 0.9

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_image_url",
                return_value=mock_result,
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract-streaming",
                json={
                    "image_url": "https://example.com/image.jpg",
                    "project_id": test_project.id,
                    "max_colors": 10,
                },
            )

        assert response.status_code == 200
        content = response.text
        # Should contain progress updates
        assert "colors_streaming" in content
        assert "progress" in content

    @pytest.mark.asyncio
    async def test_streaming_exception_handling(self, client, test_project):
        """Test streaming handles exceptions in the stream"""
        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_image_url",
                side_effect=Exception("Stream error"),
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract-streaming",
                json={
                    "image_url": "https://example.com/image.jpg",
                    "project_id": test_project.id,
                    "max_colors": 5,
                },
            )

        assert response.status_code == 200  # SSE returns 200
        content = response.text
        assert "error" in content.lower()
        assert "Stream error" in content or "extraction failed" in content.lower()


class TestGetProjectColorsEndpoint:
    """Test get_project_colors endpoint"""

    @pytest.mark.asyncio
    async def test_get_project_colors_not_found(self, client):
        """Test getting colors for non-existent project"""
        response = await client.get("/api/v1/projects/999/colors")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_project_colors_empty(self, client, test_project):
        """Test getting colors for project with no colors"""
        response = await client.get(f"/api/v1/projects/{test_project.id}/colors")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_project_colors_with_colors(self, client, async_db, test_project):
        """Test getting colors for project with multiple colors"""
        # Create multiple colors
        colors_data = [
            {"hex": "#FF0000", "name": "Red", "confidence": 0.9},
            {"hex": "#00FF00", "name": "Green", "confidence": 0.85},
            {"hex": "#0000FF", "name": "Blue", "confidence": 0.8},
        ]

        for data in colors_data:
            color = ColorToken(
                project_id=test_project.id,
                hex=data["hex"],
                rgb=f"rgb({data['hex']})",
                name=data["name"],
                confidence=data["confidence"],
            )
            async_db.add(color)
        await async_db.commit()

        response = await client.get(f"/api/v1/projects/{test_project.id}/colors")
        assert response.status_code == 200
        colors = response.json()
        assert len(colors) == 3

    @pytest.mark.asyncio
    async def test_get_project_colors_with_json_fields(self, client, async_db, test_project):
        """Test getting colors with JSON fields properly deserialized"""
        color = ColorToken(
            project_id=test_project.id,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral",
            confidence=0.9,
            semantic_names=json.dumps({"simple": "red", "descriptive": "coral"}),
            extraction_metadata=json.dumps({"source": "test", "version": 1}),
            usage=json.dumps(["backgrounds", "alerts"]),
        )
        async_db.add(color)
        await async_db.commit()

        response = await client.get(f"/api/v1/projects/{test_project.id}/colors")
        assert response.status_code == 200
        colors = response.json()
        assert len(colors) == 1
        assert colors[0]["semantic_names"] == {"simple": "red", "descriptive": "coral"}
        assert colors[0]["extraction_metadata"] == {"source": "test", "version": 1}
        assert colors[0]["usage"] == ["backgrounds", "alerts"]

    @pytest.mark.asyncio
    async def test_get_project_colors_ordered_by_created_at(self, client, async_db, test_project):
        """Test colors are ordered by created_at descending"""
        # Create colors - they should be returned newest first
        for i in range(3):
            color = ColorToken(
                project_id=test_project.id,
                hex=f"#FF000{i}",
                rgb=f"rgb({i}, 0, 0)",
                name=f"Color{i}",
                confidence=0.9,
            )
            async_db.add(color)
            await async_db.commit()

        response = await client.get(f"/api/v1/projects/{test_project.id}/colors")
        assert response.status_code == 200
        colors = response.json()
        # Most recent should be first
        assert colors[0]["name"] == "Color2"


class TestCreateColorTokenEndpoint:
    """Test create_color_token endpoint"""

    @pytest.mark.asyncio
    async def test_create_color_token_project_not_found(self, client):
        """Test creating color token with non-existent project"""
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": 999,
                "hex": "#FF5733",
                "rgb": "rgb(255, 87, 51)",
                "name": "Coral",
                "confidence": 0.9,
            },
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_color_token_success(self, client, test_project):
        """Test successful color token creation"""
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "hex": "#FF5733",
                "rgb": "rgb(255, 87, 51)",
                "name": "Coral Red",
                "design_intent": "error",
                "confidence": 0.95,
                "harmony": "complementary",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["hex"] == "#FF5733"
        assert data["rgb"] == "rgb(255, 87, 51)"
        assert data["name"] == "Coral Red"
        assert data["design_intent"] == "error"
        assert data["confidence"] == 0.95
        assert data["harmony"] == "complementary"
        assert data["project_id"] == test_project.id
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_color_token_with_extraction_job(self, client, async_db, test_project):
        """Test creating color token with extraction job reference"""
        # Create an extraction job
        job = ExtractionJob(
            project_id=test_project.id,
            source_url="https://example.com/image.jpg",
            extraction_type="color",
            status="completed",
        )
        async_db.add(job)
        await async_db.commit()
        await async_db.refresh(job)

        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "extraction_job_id": job.id,
                "hex": "#00FF00",
                "rgb": "rgb(0, 255, 0)",
                "name": "Green",
                "confidence": 0.85,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["extraction_job_id"] == job.id

    @pytest.mark.asyncio
    async def test_create_color_token_with_usage(self, client, test_project):
        """Test creating color token with usage field"""
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "hex": "#0000FF",
                "rgb": "rgb(0, 0, 255)",
                "name": "Blue",
                "confidence": 0.9,
                "usage": '["backgrounds", "links"]',
            },
        )
        assert response.status_code == 201
        data = response.json()
        # Usage is stored as JSON string
        assert data["usage"] == ["backgrounds", "links"]

    @pytest.mark.asyncio
    async def test_create_color_token_minimal(self, client, test_project):
        """Test creating color token with minimal required fields"""
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "hex": "#000000",
                "rgb": "rgb(0, 0, 0)",
                "name": "Black",
                "confidence": 1.0,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["hex"] == "#000000"
        assert data["design_intent"] is None
        assert data["harmony"] is None


class TestGetColorTokenEndpoint:
    """Test get_color_token endpoint"""

    @pytest.mark.asyncio
    async def test_get_color_token_not_found(self, client):
        """Test getting non-existent color token"""
        response = await client.get("/api/v1/colors/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_color_token_success(self, client, test_color_token):
        """Test successful retrieval of color token"""
        response = await client.get(f"/api/v1/colors/{test_color_token.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_color_token.id
        assert data["hex"] == "#FF5733"
        assert data["rgb"] == "rgb(255, 87, 51)"
        assert data["name"] == "Coral Red"
        assert data["confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_get_color_token_with_json_fields(self, client, test_color_token):
        """Test color token retrieval with JSON fields deserialized"""
        response = await client.get(f"/api/v1/colors/{test_color_token.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["semantic_names"] == {"simple": "red", "descriptive": "coral red"}
        assert data["extraction_metadata"] == {"source": "test"}
        assert data["usage"] == ["alerts", "buttons"]

    @pytest.mark.asyncio
    async def test_get_color_token_minimal(self, client, async_db, test_project):
        """Test getting color token with minimal fields"""
        color = ColorToken(
            project_id=test_project.id,
            hex="#FFFFFF",
            rgb="rgb(255, 255, 255)",
            name="White",
            confidence=1.0,
        )
        async_db.add(color)
        await async_db.commit()
        await async_db.refresh(color)

        response = await client.get(f"/api/v1/colors/{color.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["hex"] == "#FFFFFF"
        assert data["semantic_names"] is None
        assert data["extraction_metadata"] is None
        assert data["usage"] is None


class TestDirectFunctionCalls:
    """Test router functions directly for better coverage"""

    @pytest.mark.asyncio
    async def test_extract_colors_direct_call_success(self, async_db, test_project):
        """Test extract_colors_from_image function directly"""
        from copy_that.interfaces.api.colors import extract_colors_from_image
        from copy_that.interfaces.api.schemas import ExtractColorRequest

        mock_result = MagicMock()
        mock_result.colors = [
            ExtractedColorToken(
                hex="#FF5733",
                rgb="rgb(255, 87, 51)",
                name="Coral",
                confidence=0.95,
                design_intent="primary",
                semantic_names={"simple": "red"},
                extraction_metadata={"tool": "test"},
                harmony="complementary",
                usage=["buttons"],
            )
        ]
        mock_result.color_palette = "Warm palette"
        mock_result.dominant_colors = ["#FF5733"]
        mock_result.extraction_confidence = 0.95
        mock_result.extractor_used = None

        request = ExtractColorRequest(
            image_url="https://example.com/image.jpg",
            project_id=test_project.id,
            max_colors=5,
        )

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_image_url",
                return_value=mock_result,
            ),
        ):
            result = await extract_colors_from_image(request, async_db)

        assert result.colors[0].hex == "#FF5733"
        assert result.extractor_used == "gpt-4o"

    @pytest.mark.asyncio
    async def test_extract_colors_direct_call_base64(self, async_db, test_project):
        """Test extract_colors_from_image function with base64"""
        from copy_that.interfaces.api.colors import extract_colors_from_image
        from copy_that.interfaces.api.schemas import ExtractColorRequest

        mock_result = MagicMock()
        mock_result.colors = [
            ExtractedColorToken(
                hex="#00FF00",
                rgb="rgb(0, 255, 0)",
                name="Green",
                confidence=0.9,
                design_intent="success",
                semantic_names=None,
                extraction_metadata=None,
                harmony="monochromatic",
                usage=[],
            )
        ]
        mock_result.color_palette = "Green palette"
        mock_result.dominant_colors = ["#00FF00"]
        mock_result.extraction_confidence = 0.9
        mock_result.extractor_used = None

        request = ExtractColorRequest(
            image_base64="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            project_id=test_project.id,
            max_colors=5,
        )

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_base64",
                return_value=mock_result,
            ),
        ):
            result = await extract_colors_from_image(request, async_db)

        assert result.colors[0].hex == "#00FF00"

    @pytest.mark.asyncio
    async def test_extract_colors_direct_project_not_found(self, async_db):
        """Test extract_colors_from_image raises 404 for missing project"""
        from fastapi import HTTPException

        from copy_that.interfaces.api.colors import extract_colors_from_image
        from copy_that.interfaces.api.schemas import ExtractColorRequest

        request = ExtractColorRequest(
            image_url="https://example.com/image.jpg",
            project_id=9999,
            max_colors=5,
        )

        with pytest.raises(HTTPException) as exc_info:
            await extract_colors_from_image(request, async_db)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_extract_colors_direct_no_image(self, async_db, test_project):
        """Test extract_colors_from_image raises 400 for no image"""
        from fastapi import HTTPException

        from copy_that.interfaces.api.colors import extract_colors_from_image
        from copy_that.interfaces.api.schemas import ExtractColorRequest

        request = ExtractColorRequest(
            project_id=test_project.id,
            max_colors=5,
        )

        with pytest.raises(HTTPException) as exc_info:
            await extract_colors_from_image(request, async_db)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_get_project_colors_direct_call(self, async_db, test_project):
        """Test get_project_colors function directly"""
        from copy_that.interfaces.api.colors import get_project_colors

        # Add a color first
        color = ColorToken(
            project_id=test_project.id,
            hex="#FF0000",
            rgb="rgb(255, 0, 0)",
            name="Red",
            confidence=0.9,
        )
        async_db.add(color)
        await async_db.commit()

        result = await get_project_colors(test_project.id, async_db)

        assert len(result) == 1
        assert result[0].hex == "#FF0000"

    @pytest.mark.asyncio
    async def test_get_project_colors_direct_not_found(self, async_db):
        """Test get_project_colors raises 404 for missing project"""
        from fastapi import HTTPException

        from copy_that.interfaces.api.colors import get_project_colors

        with pytest.raises(HTTPException) as exc_info:
            await get_project_colors(9999, async_db)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_create_color_token_direct_call(self, async_db, test_project):
        """Test create_color_token function directly"""
        from copy_that.interfaces.api.colors import create_color_token
        from copy_that.interfaces.api.schemas import ColorTokenCreateRequest

        request = ColorTokenCreateRequest(
            project_id=test_project.id,
            hex="#0000FF",
            rgb="rgb(0, 0, 255)",
            name="Blue",
            confidence=0.85,
            design_intent="primary",
            harmony="analogous",
        )

        result = await create_color_token(request, async_db)

        assert result.hex == "#0000FF"
        assert result.name == "Blue"
        assert result.project_id == test_project.id

    @pytest.mark.asyncio
    async def test_create_color_token_direct_not_found(self, async_db):
        """Test create_color_token raises 404 for missing project"""
        from fastapi import HTTPException

        from copy_that.interfaces.api.colors import create_color_token
        from copy_that.interfaces.api.schemas import ColorTokenCreateRequest

        request = ColorTokenCreateRequest(
            project_id=9999,
            hex="#FF0000",
            rgb="rgb(255, 0, 0)",
            name="Red",
            confidence=0.9,
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_color_token(request, async_db)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_color_token_direct_call(self, async_db, test_project):
        """Test get_color_token function directly"""
        from copy_that.interfaces.api.colors import get_color_token

        # Create a color
        color = ColorToken(
            project_id=test_project.id,
            hex="#FFFF00",
            rgb="rgb(255, 255, 0)",
            name="Yellow",
            confidence=0.92,
        )
        async_db.add(color)
        await async_db.commit()
        await async_db.refresh(color)

        result = await get_color_token(color.id, async_db)

        assert result.hex == "#FFFF00"
        assert result.name == "Yellow"

    @pytest.mark.asyncio
    async def test_get_color_token_direct_not_found(self, async_db):
        """Test get_color_token raises 404 for missing color"""
        from fastapi import HTTPException

        from copy_that.interfaces.api.colors import get_color_token

        with pytest.raises(HTTPException) as exc_info:
            await get_color_token(9999, async_db)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_extract_colors_direct_value_error(self, async_db, test_project):
        """Test extract_colors_from_image handles ValueError"""
        from fastapi import HTTPException

        from copy_that.interfaces.api.colors import extract_colors_from_image
        from copy_that.interfaces.api.schemas import ExtractColorRequest

        request = ExtractColorRequest(
            image_url="https://example.com/image.jpg",
            project_id=test_project.id,
            max_colors=5,
        )

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_image_url",
                side_effect=ValueError("Invalid image format"),
            ),
            pytest.raises(HTTPException) as exc_info,
        ):
            await extract_colors_from_image(request, async_db)

        assert exc_info.value.status_code == 400
        assert "Invalid input" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_extract_colors_direct_request_exception(self, async_db, test_project):
        """Test extract_colors_from_image handles requests.RequestException"""
        from fastapi import HTTPException

        from copy_that.interfaces.api.colors import extract_colors_from_image
        from copy_that.interfaces.api.schemas import ExtractColorRequest

        request = ExtractColorRequest(
            image_url="https://example.com/image.jpg",
            project_id=test_project.id,
            max_colors=5,
        )

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_image_url",
                side_effect=requests.RequestException("Network error"),
            ),
            pytest.raises(HTTPException) as exc_info,
        ):
            await extract_colors_from_image(request, async_db)

        assert exc_info.value.status_code == 502
        assert "Failed to fetch image" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_extract_colors_direct_anthropic_error(self, async_db, test_project):
        """Test extract_colors_from_image handles anthropic.APIError"""
        from fastapi import HTTPException

        from copy_that.interfaces.api.colors import extract_colors_from_image
        from copy_that.interfaces.api.schemas import ExtractColorRequest

        request = ExtractColorRequest(
            image_url="https://example.com/image.jpg",
            project_id=test_project.id,
            max_colors=5,
            extractor="claude",
        )

        with (
            patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key", "OPENAI_API_KEY": ""}),
            patch.object(
                AIColorExtractor,
                "extract_colors_from_image_url",
                side_effect=anthropic.APIError(
                    message="API quota exceeded",
                    request=MagicMock(),
                    body=None,
                ),
            ),
            pytest.raises(HTTPException) as exc_info,
        ):
            await extract_colors_from_image(request, async_db)

        assert exc_info.value.status_code == 502
        assert "AI service error" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_extract_colors_direct_unexpected_error(self, async_db, test_project):
        """Test extract_colors_from_image handles unexpected exceptions"""
        from fastapi import HTTPException

        from copy_that.interfaces.api.colors import extract_colors_from_image
        from copy_that.interfaces.api.schemas import ExtractColorRequest

        request = ExtractColorRequest(
            image_url="https://example.com/image.jpg",
            project_id=test_project.id,
            max_colors=5,
        )

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_image_url",
                side_effect=RuntimeError("Unexpected system error"),
            ),
            pytest.raises(HTTPException) as exc_info,
        ):
            await extract_colors_from_image(request, async_db)

        assert exc_info.value.status_code == 500
        assert "unexpected error" in exc_info.value.detail.lower()


class TestDirectFunctionCoverage:
    """Direct function tests for improved coverage"""

    @pytest.mark.asyncio
    async def test_extract_colors_full_flow_url(self, client, async_db, test_project):
        """Test the full extraction flow with URL to ensure all code paths"""
        # Create a comprehensive mock result
        mock_result = MagicMock()
        mock_result.colors = [
            ExtractedColorToken(
                hex="#FF5733",
                rgb="rgb(255, 87, 51)",
                hsl="hsl(10, 100%, 60%)",
                hsv="hsv(10, 80%, 100%)",
                name="Coral",
                confidence=0.95,
                design_intent="primary",
                semantic_names={"simple": "red", "emotional": "energetic"},
                extraction_metadata={"tool": "openai"},
                category="accent",
                harmony="complementary",
                temperature="warm",
                saturation_level="vibrant",
                lightness_level="medium",
                usage=["buttons", "alerts"],
                count=5,
                prominence_percentage=25.5,
                wcag_contrast_on_white=4.5,
                wcag_contrast_on_black=12.5,
                wcag_aa_compliant_text=True,
                wcag_aaa_compliant_text=True,
                wcag_aa_compliant_normal=True,
                wcag_aaa_compliant_normal=False,
                colorblind_safe=True,
                tint_color="#FF8A73",
                shade_color="#B33D24",
                tone_color="#CC6E57",
                closest_web_safe="#FF6633",
                closest_css_named="tomato",
                delta_e_to_dominant=3.5,
                is_neutral=False,
            ),
            ExtractedColorToken(
                hex="#3498DB",
                rgb="rgb(52, 152, 219)",
                name="Blue",
                confidence=0.88,
                design_intent="secondary",
                semantic_names=None,
                extraction_metadata=None,
                harmony="analogous",
                usage=["links"],
            ),
        ]
        mock_result.color_palette = "Vibrant warm palette"
        mock_result.dominant_colors = ["#FF5733", "#3498DB"]
        mock_result.extraction_confidence = 0.92
        mock_result.extractor_used = None

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_image_url",
                return_value=mock_result,
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract",
                json={
                    "image_url": "https://example.com/test-image.jpg",
                    "project_id": test_project.id,
                    "max_colors": 10,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["colors"]) == 2
        assert data["extraction_confidence"] == 0.92
        assert data["extractor_used"] == "gpt-4o"

    @pytest.mark.asyncio
    async def test_extract_colors_full_flow_base64(self, client, async_db, test_project):
        """Test the full extraction flow with base64 to cover that branch"""
        mock_result = MagicMock()
        mock_result.colors = [
            ExtractedColorToken(
                hex="#2ECC71",
                rgb="rgb(46, 204, 113)",
                name="Emerald Green",
                confidence=0.91,
                design_intent="success",
                semantic_names={"simple": "green"},
                extraction_metadata={"source": "base64"},
                harmony="monochromatic",
                usage=["success-states"],
            ),
        ]
        mock_result.color_palette = "Green palette"
        mock_result.dominant_colors = ["#2ECC71"]
        mock_result.extraction_confidence = 0.91
        mock_result.extractor_used = None

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_base64",
                return_value=mock_result,
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract",
                json={
                    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                    "project_id": test_project.id,
                    "max_colors": 5,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["colors"][0]["hex"] == "#2ECC71"

    @pytest.mark.asyncio
    async def test_extract_colors_stores_in_database(self, client, async_db, test_project):
        """Verify extraction properly stores colors and job in database"""
        mock_result = MagicMock()
        mock_result.colors = [
            ExtractedColorToken(
                hex="#9B59B6",
                rgb="rgb(155, 89, 182)",
                name="Amethyst",
                confidence=0.89,
                design_intent="accent",
                semantic_names=None,
                extraction_metadata=None,
                harmony="triadic",
                usage=["accents"],
            ),
        ]
        mock_result.color_palette = "Purple palette"
        mock_result.dominant_colors = ["#9B59B6"]
        mock_result.extraction_confidence = 0.89
        mock_result.extractor_used = None

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_image_url",
                return_value=mock_result,
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract",
                json={
                    "image_url": "https://example.com/purple.jpg",
                    "project_id": test_project.id,
                    "max_colors": 5,
                },
            )

        assert response.status_code == 200

        # Verify data was stored in database
        colors_response = await client.get(f"/api/v1/projects/{test_project.id}/colors")
        assert colors_response.status_code == 200
        colors = colors_response.json()
        assert len(colors) >= 1
        # Find our color
        purple_colors = [c for c in colors if c["hex"] == "#9B59B6"]
        assert len(purple_colors) >= 1


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.mark.asyncio
    async def test_extract_colors_max_colors_boundary(self, client, test_project):
        """Test extraction with boundary max_colors values"""
        # Test minimum
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "image_url": "https://example.com/image.jpg",
                "project_id": test_project.id,
                "max_colors": 1,
            },
        )
        # Should not fail validation
        assert response.status_code in [200, 400, 502, 500]

        # Test maximum
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "image_url": "https://example.com/image.jpg",
                "project_id": test_project.id,
                "max_colors": 50,
            },
        )
        assert response.status_code in [200, 400, 502, 500]

    @pytest.mark.asyncio
    async def test_create_color_token_confidence_boundary(self, client, test_project):
        """Test color token creation with boundary confidence values"""
        # Test confidence = 0
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "hex": "#000000",
                "rgb": "rgb(0, 0, 0)",
                "name": "Black",
                "confidence": 0.0,
            },
        )
        assert response.status_code == 201

        # Test confidence = 1
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "hex": "#FFFFFF",
                "rgb": "rgb(255, 255, 255)",
                "name": "White",
                "confidence": 1.0,
            },
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_streaming_with_auto_extractor(self, client, async_db, test_project):
        """Test streaming with auto extractor selection"""
        mock_result = MagicMock()
        mock_result.colors = [
            ExtractedColorToken(
                hex="#123456",
                rgb="rgb(18, 52, 86)",
                hsl=None,
                hsv=None,
                name="Deep Blue",
                confidence=0.9,
                design_intent=None,
                semantic_names=None,
                harmony=None,
                temperature=None,
                saturation_level=None,
                lightness_level=None,
                usage=[],
                count=1,
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
            )
        ]
        mock_result.color_palette = "Blue palette"
        mock_result.dominant_colors = ["#123456"]
        mock_result.extraction_confidence = 0.9

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "ANTHROPIC_API_KEY": ""}),
            patch.object(
                OpenAIColorExtractor,
                "extract_colors_from_image_url",
                return_value=mock_result,
            ),
        ):
            response = await client.post(
                "/api/v1/colors/extract-streaming",
                json={
                    "image_url": "https://example.com/image.jpg",
                    "project_id": test_project.id,
                    "max_colors": 5,
                    "extractor": "auto",
                },
            )

        assert response.status_code == 200
        content = response.text
        assert "gpt-4o" in content  # Auto should select OpenAI

    @pytest.mark.asyncio
    async def test_multiple_projects_isolation(self, client, async_db):
        """Test that colors are properly isolated by project"""
        # Create two projects
        project1 = Project(name="Project 1", description="First")
        project2 = Project(name="Project 2", description="Second")
        async_db.add(project1)
        async_db.add(project2)
        await async_db.commit()
        await async_db.refresh(project1)
        await async_db.refresh(project2)

        # Add color to project 1
        color = ColorToken(
            project_id=project1.id,
            hex="#FF0000",
            rgb="rgb(255, 0, 0)",
            name="Red",
            confidence=0.9,
        )
        async_db.add(color)
        await async_db.commit()

        # Get colors for project 1
        response = await client.get(f"/api/v1/projects/{project1.id}/colors")
        assert response.status_code == 200
        assert len(response.json()) == 1

        # Get colors for project 2 should be empty
        response = await client.get(f"/api/v1/projects/{project2.id}/colors")
        assert response.status_code == 200
        assert len(response.json()) == 0
