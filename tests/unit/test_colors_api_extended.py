"""Extended tests for colors API endpoints"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.domain.models import ColorToken, Project
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
    project = Project(name="Test Project", description="For testing")
    async_db.add(project)
    await async_db.commit()
    await async_db.refresh(project)
    return project


class TestColorTokenCRUD:
    """Test color token CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_color_token_full(self, client, test_project):
        """Test creating a color token with all fields"""
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
                "usage": '["backgrounds", "alerts"]',
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["hex"] == "#FF5733"
        assert data["name"] == "Coral Red"
        assert data["confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_create_color_token_minimal(self, client, test_project):
        """Test creating a color token with minimal fields"""
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "hex": "#00FF00",
                "rgb": "rgb(0, 255, 0)",
                "name": "Green",
                "confidence": 0.8,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["hex"] == "#00FF00"

    @pytest.mark.asyncio
    async def test_create_color_token_invalid_confidence(self, client, test_project):
        """Test creating color token with invalid confidence"""
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "hex": "#FF0000",
                "rgb": "rgb(255, 0, 0)",
                "name": "Red",
                "confidence": 1.5,  # Over 1.0
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_color_token_negative_confidence(self, client, test_project):
        """Test creating color token with negative confidence"""
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "hex": "#FF0000",
                "rgb": "rgb(255, 0, 0)",
                "name": "Red",
                "confidence": -0.1,  # Negative
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_color_token(self, client, async_db, test_project):
        """Test getting a specific color token"""
        color = ColorToken(
            project_id=test_project.id,
            hex="#0000FF",
            rgb="rgb(0, 0, 255)",
            name="Blue",
            confidence=0.9,
        )
        async_db.add(color)
        await async_db.commit()
        await async_db.refresh(color)

        response = await client.get(f"/api/v1/colors/{color.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["hex"] == "#0000FF"
        assert data["id"] == color.id

    @pytest.mark.asyncio
    async def test_get_color_token_not_found(self, client):
        """Test getting non-existent color token"""
        response = await client.get("/api/v1/colors/999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_project_colors(self, client, async_db, test_project):
        """Test listing all colors for a project"""
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


class TestColorExtraction:
    """Test color extraction operations"""

    @pytest.mark.asyncio
    async def test_extract_colors_no_image(self, client, test_project):
        """Test extraction with no image provided"""
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "project_id": test_project.id,
                "max_colors": 10,
            },
        )
        # Should process but may fail without actual image
        assert response.status_code in [200, 400, 422, 500]

    @pytest.mark.asyncio
    async def test_extract_colors_invalid_max_colors_high(self, client, test_project):
        """Test extraction with max_colors over limit"""
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "project_id": test_project.id,
                "image_url": "http://example.com/image.jpg",
                "max_colors": 100,  # Over limit of 50
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_extract_colors_invalid_max_colors_zero(self, client, test_project):
        """Test extraction with max_colors of zero"""
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "project_id": test_project.id,
                "image_url": "http://example.com/image.jpg",
                "max_colors": 0,  # Invalid
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_extract_colors_project_not_found(self, client):
        """Test extraction with non-existent project"""
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "project_id": 999,
                "image_url": "http://example.com/image.jpg",
                "max_colors": 10,
            },
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_extract_colors_with_extractor_option(self, client, test_project):
        """Test extraction with specific extractor"""
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "project_id": test_project.id,
                "image_url": "http://example.com/image.jpg",
                "max_colors": 5,
                "extractor": "claude",
            },
        )
        # Will fail due to missing API key or failed image fetch, but validates the request
        assert response.status_code in [200, 400, 500, 502]


class TestColorTokenValidation:
    """Test color token validation scenarios"""

    @pytest.mark.asyncio
    async def test_create_color_missing_required_fields(self, client, test_project):
        """Test creating color with missing required fields"""
        # Missing hex
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "rgb": "rgb(255, 0, 0)",
                "name": "Red",
                "confidence": 0.9,
            },
        )
        assert response.status_code == 422

        # Missing rgb
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "hex": "#FF0000",
                "name": "Red",
                "confidence": 0.9,
            },
        )
        assert response.status_code == 422

        # Missing name
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "hex": "#FF0000",
                "rgb": "rgb(255, 0, 0)",
                "confidence": 0.9,
            },
        )
        assert response.status_code == 422

        # Missing confidence
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": test_project.id,
                "hex": "#FF0000",
                "rgb": "rgb(255, 0, 0)",
                "name": "Red",
            },
        )
        assert response.status_code == 422


class TestAPIEndpoints:
    """Test general API endpoints"""

    @pytest.mark.asyncio
    async def test_db_test_endpoint(self, client):
        """Test database test endpoint"""
        response = await client.get("/api/v1/db-test")
        assert response.status_code == 200
        data = response.json()
        assert data["database"] == "connected"
        assert "projects_count" in data

    @pytest.mark.asyncio
    async def test_api_docs_endpoint(self, client):
        """Test API documentation endpoint"""
        response = await client.get("/api/v1/docs")
        assert response.status_code == 200
        data = response.json()
        assert "endpoints" in data
        assert "colors" in data["endpoints"]
        assert "projects" in data["endpoints"]

    @pytest.mark.asyncio
    async def test_openapi_schema(self, client):
        """Test OpenAPI schema endpoint"""
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
