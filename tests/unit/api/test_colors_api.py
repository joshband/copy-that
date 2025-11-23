"""Comprehensive tests for colors API endpoints to achieve 80%+ coverage"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.domain.models import ColorToken, ExtractionJob, Project
from copy_that.infrastructure.database import Base, get_db
from copy_that.interfaces.api.colors import get_extractor, serialize_color_token
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
    project = Project(name="Test Project", description="For color testing")
    async_db.add(project)
    await async_db.commit()
    await async_db.refresh(project)
    return project


class TestSerializeColorToken:
    """Test serialize_color_token helper function"""

    def test_serialize_full_color_token(self):
        """Test serializing a color token with all fields"""
        color = MagicMock()
        color.id = 1
        color.hex = "#FF5733"
        color.rgb = "rgb(255, 87, 51)"
        color.hsl = "hsl(9, 100%, 60%)"
        color.hsv = "hsv(9, 80%, 100%)"
        color.name = "Coral Red"
        color.design_intent = "accent"
        color.semantic_names = '["coral", "warm-red"]'
        color.extraction_metadata = '{"source": "test"}'
        color.category = "warm"
        color.confidence = 0.95
        color.harmony = "complementary"
        color.temperature = "warm"
        color.saturation_level = "high"
        color.lightness_level = "medium"
        color.usage = '["buttons", "accents"]'
        color.count = 150
        color.prominence_percentage = 25.5
        color.wcag_contrast_on_white = 3.5
        color.wcag_contrast_on_black = 8.2
        color.wcag_aa_compliant_text = True
        color.wcag_aaa_compliant_text = False
        color.wcag_aa_compliant_normal = True
        color.wcag_aaa_compliant_normal = False
        color.colorblind_safe = True
        color.tint_color = "#FF8866"
        color.shade_color = "#CC4422"
        color.tone_color = "#DD6644"
        color.closest_web_safe = "#FF6633"
        color.closest_css_named = "coral"
        color.delta_e_to_dominant = 5.2
        color.is_neutral = False

        result = serialize_color_token(color)

        assert result["id"] == 1
        assert result["hex"] == "#FF5733"
        assert result["rgb"] == "rgb(255, 87, 51)"
        assert result["name"] == "Coral Red"
        assert result["semantic_names"] == ["coral", "warm-red"]
        assert result["extraction_metadata"] == {"source": "test"}
        assert result["usage"] == ["buttons", "accents"]
        assert result["confidence"] == 0.95

    def test_serialize_minimal_color_token(self):
        """Test serializing a color token with minimal fields"""
        color = MagicMock()
        color.id = 1
        color.hex = "#000000"
        color.rgb = "rgb(0, 0, 0)"
        color.hsl = None
        color.hsv = None
        color.name = "Black"
        color.design_intent = None
        color.semantic_names = None
        color.extraction_metadata = None
        color.category = None
        color.confidence = 0.5
        color.harmony = None
        color.temperature = None
        color.saturation_level = None
        color.lightness_level = None
        color.usage = None
        color.count = 0
        color.prominence_percentage = None
        color.wcag_contrast_on_white = None
        color.wcag_contrast_on_black = None
        color.wcag_aa_compliant_text = None
        color.wcag_aaa_compliant_text = None
        color.wcag_aa_compliant_normal = None
        color.wcag_aaa_compliant_normal = None
        color.colorblind_safe = None
        color.tint_color = None
        color.shade_color = None
        color.tone_color = None
        color.closest_web_safe = None
        color.closest_css_named = None
        color.delta_e_to_dominant = None
        color.is_neutral = None

        result = serialize_color_token(color)

        assert result["id"] == 1
        assert result["hex"] == "#000000"
        assert result["semantic_names"] is None
        assert result["extraction_metadata"] is None
        assert result["usage"] is None


class TestGetExtractor:
    """Test get_extractor helper function"""

    def test_get_extractor_openai(self):
        """Test getting OpenAI extractor"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            extractor, model = get_extractor("openai")
            assert model == "gpt-4o"

    def test_get_extractor_openai_no_key(self):
        """Test OpenAI extractor without API key raises error"""
        with patch.dict(os.environ, {}, clear=True):
            # Remove keys
            os.environ.pop("OPENAI_API_KEY", None)
            os.environ.pop("ANTHROPIC_API_KEY", None)
            with pytest.raises(ValueError, match="OPENAI_API_KEY not set"):
                get_extractor("openai")

    def test_get_extractor_claude(self):
        """Test getting Claude extractor"""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=False):
            extractor, model = get_extractor("claude")
            assert model == "claude-sonnet-4-5"

    def test_get_extractor_claude_no_key(self):
        """Test Claude extractor without API key raises error"""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENAI_API_KEY", None)
            os.environ.pop("ANTHROPIC_API_KEY", None)
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY not set"):
                get_extractor("claude")

    def test_get_extractor_auto_prefers_openai(self):
        """Test auto mode prefers OpenAI when available"""
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "openai-key", "ANTHROPIC_API_KEY": "anthropic-key"},
            clear=False,
        ):
            extractor, model = get_extractor("auto")
            assert model == "gpt-4o"

    def test_get_extractor_auto_falls_back_to_claude(self):
        """Test auto mode falls back to Claude when OpenAI unavailable"""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "anthropic-key"}, clear=False):
            os.environ.pop("OPENAI_API_KEY", None)
            extractor, model = get_extractor("auto")
            assert model == "claude-sonnet-4-5"

    def test_get_extractor_auto_no_keys(self):
        """Test auto mode raises error when no keys available"""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENAI_API_KEY", None)
            os.environ.pop("ANTHROPIC_API_KEY", None)
            with pytest.raises(ValueError, match="No API key available"):
                get_extractor("auto")


class TestColorExtraction:
    """Test color extraction endpoints"""

    @pytest.mark.asyncio
    async def test_extract_colors_project_not_found(self, client):
        """Test extraction with non-existent project"""
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "image_url": "https://example.com/image.jpg",
                "project_id": 999,
                "max_colors": 10,
            },
        )

        assert response.status_code == 404
        assert "not found" in response.text.lower()

    @pytest.mark.asyncio
    async def test_extract_colors_no_image_source(self, client, test_project):
        """Test extraction without image_url or image_base64"""
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "project_id": test_project.id,
                "max_colors": 10,
            },
        )

        assert response.status_code == 400
        assert "image_url or image_base64" in response.text.lower()

    @pytest.mark.asyncio
    async def test_extract_colors_invalid_max_colors(self, client, test_project):
        """Test extraction with invalid max_colors"""
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "image_url": "https://example.com/image.jpg",
                "project_id": test_project.id,
                "max_colors": 100,  # Exceeds max of 50
            },
        )

        assert response.status_code == 422


class TestColorStreamingExtraction:
    """Test streaming color extraction endpoint"""

    @pytest.mark.asyncio
    async def test_extract_streaming_project_not_found(self, client):
        """Test streaming extraction with non-existent project"""
        response = await client.post(
            "/api/v1/colors/extract-streaming",
            json={
                "image_url": "https://example.com/image.jpg",
                "project_id": 999,
                "max_colors": 10,
            },
        )

        # Streaming endpoint returns 200 but streams error in data
        assert response.status_code == 200


class TestProjectColors:
    """Test project colors endpoints"""

    @pytest.mark.asyncio
    async def test_get_project_colors_empty(self, client, test_project):
        """Test getting colors for project with no colors"""
        response = await client.get(f"/api/v1/projects/{test_project.id}/colors")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_project_colors_not_found(self, client):
        """Test getting colors for non-existent project"""
        response = await client.get("/api/v1/projects/999/colors")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_project_colors_with_colors(self, client, async_db, test_project):
        """Test getting colors for project with existing colors"""
        # Create color tokens
        for i, hex_color in enumerate(["#FF0000", "#00FF00", "#0000FF"]):
            color = ColorToken(
                project_id=test_project.id,
                hex=hex_color,
                rgb=f"rgb({i}, {i}, {i})",
                name=f"Color {i}",
                confidence=0.9,
            )
            async_db.add(color)
        await async_db.commit()

        response = await client.get(f"/api/v1/projects/{test_project.id}/colors")

        assert response.status_code == 200
        colors = response.json()
        assert len(colors) == 3

    @pytest.mark.asyncio
    async def test_get_project_colors_with_json_fields(self, client, async_db, test_project):
        """Test getting colors with JSON serialized fields"""
        color = ColorToken(
            project_id=test_project.id,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral",
            confidence=0.95,
            semantic_names='["coral", "warm"]',
            extraction_metadata='{"source": "test"}',
            usage='["accent"]',
        )
        async_db.add(color)
        await async_db.commit()

        response = await client.get(f"/api/v1/projects/{test_project.id}/colors")

        assert response.status_code == 200
        colors = response.json()
        assert len(colors) == 1
        assert colors[0]["semantic_names"] == ["coral", "warm"]


class TestCreateColorToken:
    """Test create color token endpoint"""

    @pytest.mark.asyncio
    async def test_create_color_token_success(self, client, test_project):
        """Test creating a color token"""
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "hex": "#FF5733",
                "rgb": "rgb(255, 87, 51)",
                "name": "Coral Red",
                "design_intent": "accent",
                "confidence": 0.95,
                "harmony": "complementary",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["hex"] == "#FF5733"
        assert data["name"] == "Coral Red"
        assert data["project_id"] == test_project.id

    @pytest.mark.asyncio
    async def test_create_color_token_minimal(self, client, test_project):
        """Test creating a color token with minimal fields"""
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "hex": "#000000",
                "rgb": "rgb(0, 0, 0)",
                "name": "Black",
                "confidence": 0.5,
            },
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_color_token_project_not_found(self, client):
        """Test creating color token with non-existent project"""
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": 999,
                "hex": "#FF5733",
                "rgb": "rgb(255, 87, 51)",
                "name": "Test",
                "confidence": 0.9,
            },
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_color_token_invalid_confidence(self, client, test_project):
        """Test creating color token with invalid confidence > 1"""
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "hex": "#FF5733",
                "rgb": "rgb(255, 87, 51)",
                "name": "Test",
                "confidence": 1.5,
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_color_token_with_extraction_job(self, client, async_db, test_project):
        """Test creating color token with extraction job ID"""
        # Create extraction job
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
                "hex": "#FF5733",
                "rgb": "rgb(255, 87, 51)",
                "name": "Test",
                "confidence": 0.9,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["extraction_job_id"] == job.id


class TestGetColorToken:
    """Test get color token by ID endpoint"""

    @pytest.mark.asyncio
    async def test_get_color_token_success(self, client, async_db, test_project):
        """Test getting a specific color token"""
        color = ColorToken(
            project_id=test_project.id,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            confidence=0.95,
        )
        async_db.add(color)
        await async_db.commit()
        await async_db.refresh(color)

        response = await client.get(f"/api/v1/colors/{color.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["hex"] == "#FF5733"
        assert data["id"] == color.id

    @pytest.mark.asyncio
    async def test_get_color_token_not_found(self, client):
        """Test getting non-existent color token"""
        response = await client.get("/api/v1/colors/999")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_color_token_with_all_json_fields(self, client, async_db, test_project):
        """Test getting color token with all JSON fields populated"""
        color = ColorToken(
            project_id=test_project.id,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral",
            confidence=0.95,
            semantic_names='["coral", "warm-red"]',
            extraction_metadata='{"confidence": 0.95, "method": "ai"}',
            usage='["buttons", "links"]',
        )
        async_db.add(color)
        await async_db.commit()
        await async_db.refresh(color)

        response = await client.get(f"/api/v1/colors/{color.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["semantic_names"] == ["coral", "warm-red"]
        assert data["extraction_metadata"]["method"] == "ai"
        assert "buttons" in data["usage"]

    @pytest.mark.asyncio
    async def test_get_color_token_with_null_json_fields(self, client, async_db, test_project):
        """Test getting color token with null JSON fields"""
        color = ColorToken(
            project_id=test_project.id,
            hex="#000000",
            rgb="rgb(0, 0, 0)",
            name="Black",
            confidence=0.5,
            semantic_names=None,
            extraction_metadata=None,
            usage=None,
        )
        async_db.add(color)
        await async_db.commit()
        await async_db.refresh(color)

        response = await client.get(f"/api/v1/colors/{color.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["semantic_names"] is None
        assert data["extraction_metadata"] is None
        assert data["usage"] is None
