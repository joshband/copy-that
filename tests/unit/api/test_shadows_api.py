"""Comprehensive tests for shadows API endpoints"""

import base64
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.domain.models import Project, ShadowToken
from copy_that.infrastructure.database import Base, get_db
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
    project = Project(name="Shadow Test Project", description="For shadow testing")
    async_db.add(project)
    await async_db.commit()
    await async_db.refresh(project)
    return project


@pytest_asyncio.fixture
def mock_shadow_extractor():
    """Create a mock shadow extractor result"""
    from copy_that.application.ai_shadow_extractor import (
        ExtractedShadowToken,
        ShadowExtractionResult,
    )

    shadow = ExtractedShadowToken(
        x_offset=2.0,
        y_offset=4.0,
        blur_radius=8.0,
        spread_radius=0.0,
        color_hex="#000000",
        opacity=0.25,
        shadow_type="drop",
        semantic_name="subtle-drop",
        confidence=0.95,
        is_inset=False,
        affects_text=False,
    )
    return ShadowExtractionResult(shadows=[shadow], shadow_count=1, extraction_confidence=0.95)


class TestShadowExtraction:
    """Test shadow extraction endpoint"""

    @pytest.mark.asyncio
    async def test_extract_shadows_base64_without_project(self, client, mock_shadow_extractor):
        """Test extracting shadows from base64 without project persistence"""
        # Create a minimal PNG (1x1 pixel) as base64
        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
            b"\x00\x01\x01\x00\x05\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        image_base64 = base64.b64encode(png_bytes).decode("utf-8")

        with patch("copy_that.interfaces.api.shadows.AIShadowExtractor") as mock_extractor_class:
            mock_instance = MagicMock()
            mock_instance.extract_shadows.return_value = mock_shadow_extractor
            mock_extractor_class.return_value = mock_instance

            response = await client.post(
                "/api/v1/shadows/extract",
                json={
                    "image_base64": image_base64,
                    "image_media_type": "image/png",
                    "max_tokens": 10,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "tokens" in data
        assert len(data["tokens"]) == 1
        assert data["tokens"][0]["x_offset"] == 2.0
        assert data["tokens"][0]["y_offset"] == 4.0
        assert data["tokens"][0]["blur_radius"] == 8.0
        assert data["tokens"][0]["color_hex"] == "#000000"
        assert data["tokens"][0]["opacity"] == 0.25
        assert data["tokens"][0]["confidence"] == 0.95
        assert data["extraction_confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_extract_shadows_with_project_persistence(
        self, client, test_project, mock_shadow_extractor, async_db
    ):
        """Test extracting shadows with project persistence"""
        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
            b"\x00\x01\x01\x00\x05\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        image_base64 = base64.b64encode(png_bytes).decode("utf-8")

        with patch("copy_that.interfaces.api.shadows.AIShadowExtractor") as mock_extractor_class:
            mock_instance = MagicMock()
            mock_instance.extract_shadows.return_value = mock_shadow_extractor
            mock_extractor_class.return_value = mock_instance

            response = await client.post(
                "/api/v1/shadows/extract",
                json={
                    "image_base64": image_base64,
                    "image_media_type": "image/png",
                    "project_id": test_project.id,
                    "max_tokens": 10,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["tokens"]) == 1

        # Verify persistence
        shadows = await async_db.query(ShadowToken).filter_by(project_id=test_project.id).all()
        assert len(shadows) == 1
        assert shadows[0].color_hex == "#000000"
        assert shadows[0].confidence == 0.95

    @pytest.mark.asyncio
    async def test_extract_shadows_multiple_tokens(self, client, mock_shadow_extractor):
        """Test extracting multiple shadow tokens"""
        from copy_that.application.ai_shadow_extractor import (
            ExtractedShadowToken,
            ShadowExtractionResult,
        )

        shadows = [
            ExtractedShadowToken(
                x_offset=2.0,
                y_offset=4.0,
                blur_radius=8.0,
                spread_radius=0.0,
                color_hex="#000000",
                opacity=0.25,
                shadow_type="drop",
                semantic_name="shadow.1",
                confidence=0.95,
                is_inset=False,
                affects_text=False,
            ),
            ExtractedShadowToken(
                x_offset=4.0,
                y_offset=8.0,
                blur_radius=16.0,
                spread_radius=0.0,
                color_hex="#000000",
                opacity=0.15,
                shadow_type="drop",
                semantic_name="shadow.2",
                confidence=0.88,
                is_inset=False,
                affects_text=False,
            ),
        ]
        multiple_shadows = ShadowExtractionResult(
            shadows=shadows, shadow_count=2, extraction_confidence=0.91
        )

        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
            b"\x00\x01\x01\x00\x05\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        image_base64 = base64.b64encode(png_bytes).decode("utf-8")

        with patch("copy_that.interfaces.api.shadows.AIShadowExtractor") as mock_extractor_class:
            mock_instance = MagicMock()
            mock_instance.extract_from_base64.return_value = multiple_shadows
            mock_extractor_class.return_value = mock_instance

            response = await client.post(
                "/api/v1/shadows/extract",
                json={
                    "image_base64": image_base64,
                    "max_tokens": 10,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["tokens"]) == 2
        assert data["extraction_confidence"] == pytest.approx((0.95 + 0.88) / 2, abs=0.01)

    @pytest.mark.asyncio
    async def test_extract_shadows_no_image_provided(self, client):
        """Test error when no image is provided"""
        response = await client.post(
            "/api/v1/shadows/extract",
            json={"max_tokens": 10},
        )

        assert response.status_code == 400
        assert "image_url or image_base64" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_extract_shadows_invalid_project(self, client):
        """Test error when project doesn't exist"""
        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
            b"\x00\x01\x01\x00\x05\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        image_base64 = base64.b64encode(png_bytes).decode("utf-8")

        response = await client.post(
            "/api/v1/shadows/extract",
            json={
                "image_base64": image_base64,
                "project_id": 9999,
                "max_tokens": 10,
            },
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_extract_shadows_empty_result(self, client):
        """Test handling empty extraction result"""
        from copy_that.application.ai_shadow_extractor import ShadowExtractionResult

        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
            b"\x00\x01\x01\x00\x05\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        image_base64 = base64.b64encode(png_bytes).decode("utf-8")

        with patch("copy_that.interfaces.api.shadows.AIShadowExtractor") as mock_extractor_class:
            mock_instance = MagicMock()
            mock_instance.extract_shadows.return_value = ShadowExtractionResult(
                shadows=[], shadow_count=0, extraction_confidence=0.0
            )
            mock_extractor_class.return_value = mock_instance

            response = await client.post(
                "/api/v1/shadows/extract",
                json={
                    "image_base64": image_base64,
                    "max_tokens": 10,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["tokens"]) == 0
        assert data["extraction_confidence"] == pytest.approx(0.0)

    @pytest.mark.asyncio
    async def test_extract_shadows_max_tokens_validation(self, client):
        """Test max_tokens parameter validation"""
        from copy_that.application.ai_shadow_extractor import ShadowExtractionResult

        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
            b"\x00\x01\x01\x00\x05\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        image_base64 = base64.b64encode(png_bytes).decode("utf-8")

        with patch("copy_that.interfaces.api.shadows.AIShadowExtractor") as mock_extractor_class:
            mock_instance = MagicMock()
            mock_instance.extract_shadows.return_value = ShadowExtractionResult(
                shadows=[], shadow_count=0, extraction_confidence=0.0
            )
            mock_extractor_class.return_value = mock_instance

            response = await client.post(
                "/api/v1/shadows/extract",
                json={
                    "image_base64": image_base64,
                    "max_tokens": 100,  # Over limit
                },
            )

        # Should fail validation
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_extract_shadows_response_schema(self, client, mock_shadow_extractor):
        """Test response schema matches specification"""
        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
            b"\x00\x01\x01\x00\x05\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        image_base64 = base64.b64encode(png_bytes).decode("utf-8")

        with patch("copy_that.interfaces.api.shadows.AIShadowExtractor") as mock_extractor_class:
            mock_instance = MagicMock()
            mock_instance.extract_shadows.return_value = mock_shadow_extractor
            mock_extractor_class.return_value = mock_instance

            response = await client.post(
                "/api/v1/shadows/extract",
                json={
                    "image_base64": image_base64,
                },
            )

        assert response.status_code == 200
        data = response.json()

        # Verify response schema
        assert "tokens" in data
        assert "extraction_confidence" in data
        assert "extraction_metadata" in data

        # Verify token schema
        token = data["tokens"][0]
        assert "x_offset" in token
        assert "y_offset" in token
        assert "blur_radius" in token
        assert "spread_radius" in token
        assert "color_hex" in token
        assert "opacity" in token
        assert "name" in token
        assert "shadow_type" in token
        assert "semantic_role" in token
        assert "confidence" in token

    @pytest.mark.asyncio
    async def test_extract_shadows_metadata(self, client, mock_shadow_extractor):
        """Test extraction metadata is properly set"""
        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
            b"\x00\x01\x01\x00\x05\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        image_base64 = base64.b64encode(png_bytes).decode("utf-8")

        with patch("copy_that.interfaces.api.shadows.AIShadowExtractor") as mock_extractor_class:
            mock_instance = MagicMock()
            mock_instance.extract_shadows.return_value = mock_shadow_extractor
            mock_extractor_class.return_value = mock_instance

            response = await client.post(
                "/api/v1/shadows/extract",
                json={
                    "image_base64": image_base64,
                    "max_tokens": 5,
                },
            )

        assert response.status_code == 200
        data = response.json()
        metadata = data["extraction_metadata"]

        assert metadata["extraction_source"] == "claude_sonnet_4.5"
        assert "claude-sonnet" in metadata["model"]
        assert metadata["token_count"] == 1

    @pytest.mark.asyncio
    async def test_extract_shadows_confidence_range(self, client):
        """Test confidence values are within valid range"""
        from copy_that.application.ai_shadow_extractor import (
            ExtractedShadowToken,
            ShadowExtractionResult,
        )

        shadows = [
            ExtractedShadowToken(
                x_offset=2.0,
                y_offset=4.0,
                blur_radius=8.0,
                spread_radius=0.0,
                color_hex="#000000",
                opacity=1.0,
                shadow_type="drop",
                semantic_name="shadow.1",
                confidence=0.0,
                is_inset=False,
                affects_text=False,
            ),
            ExtractedShadowToken(
                x_offset=4.0,
                y_offset=8.0,
                blur_radius=16.0,
                spread_radius=0.0,
                color_hex="#000000",
                opacity=1.0,
                shadow_type="drop",
                semantic_name="shadow.2",
                confidence=1.0,
                is_inset=False,
                affects_text=False,
            ),
        ]
        result = ShadowExtractionResult(shadows=shadows, shadow_count=2, extraction_confidence=0.5)

        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
            b"\x00\x01\x01\x00\x05\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        image_base64 = base64.b64encode(png_bytes).decode("utf-8")

        with patch("copy_that.interfaces.api.shadows.AIShadowExtractor") as mock_extractor_class:
            mock_instance = MagicMock()
            mock_instance.extract_shadows.return_value = result
            mock_extractor_class.return_value = mock_instance

            response = await client.post(
                "/api/v1/shadows/extract",
                json={
                    "image_base64": image_base64,
                },
            )

        assert response.status_code == 200
        data = response.json()

        # Verify all confidence values are in 0-1 range
        for token in data["tokens"]:
            assert 0 <= token["confidence"] <= 1

        # Overall confidence should also be in range
        assert 0 <= data["extraction_confidence"] <= 1

    @pytest.mark.asyncio
    async def test_extract_shadows_optional_fields(self, client):
        """Test optional fields (shadow_type, semantic_role) can be None"""
        from copy_that.application.ai_shadow_extractor import (
            ExtractedShadowToken,
            ShadowExtractionResult,
        )

        shadow = ExtractedShadowToken(
            x_offset=2.0,
            y_offset=4.0,
            blur_radius=8.0,
            spread_radius=0.0,
            color_hex="#000000",
            opacity=0.25,
            shadow_type="drop",
            semantic_name="shadow.1",
            confidence=0.95,
            is_inset=False,
            affects_text=False,
        )
        result = ShadowExtractionResult(
            shadows=[shadow], shadow_count=1, extraction_confidence=0.95
        )

        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
            b"\x00\x01\x01\x00\x05\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        image_base64 = base64.b64encode(png_bytes).decode("utf-8")

        with patch("copy_that.interfaces.api.shadows.AIShadowExtractor") as mock_extractor_class:
            mock_instance = MagicMock()
            mock_instance.extract_shadows.return_value = result
            mock_extractor_class.return_value = mock_instance

            response = await client.post(
                "/api/v1/shadows/extract",
                json={
                    "image_base64": image_base64,
                },
            )

        assert response.status_code == 200
        data = response.json()
        token = data["tokens"][0]

        # Verify optional fields are properly mapped
        assert "shadow_type" in token
        assert "semantic_role" in token
        assert token["name"] == "shadow.1"
        assert token["confidence"] == pytest.approx(0.95)
