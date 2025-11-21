"""Unit tests for color extraction API endpoints"""

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


class TestColorExtractionAPI:
    """Test color extraction API endpoints"""

    @pytest.mark.asyncio
    async def test_extract_colors_endpoint_not_found(self, client, async_db):
        """Test color extraction with non-existent project"""
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "image_url": "https://example.com/image.jpg",
                "project_id": 999,  # Non-existent project
                "max_colors": 10,
            },
        )

        assert response.status_code == 404
        assert "not found" in response.text.lower()

    @pytest.mark.asyncio
    async def test_get_project_colors_endpoint(self, client, async_db):
        """Test getting colors for a project"""
        # Create a test project
        project = Project(name="Test Project", description="Test")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        # Try to get colors (should be empty)
        response = await client.get(f"/api/v1/projects/{project.id}/colors")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_project_colors_not_found(self, client):
        """Test getting colors for non-existent project"""
        response = await client.get("/api/v1/projects/999/colors")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_color_token_endpoint(self, client, async_db):
        """Test creating a color token"""
        # Create a test project
        project = Project(name="Test Project", description="Test")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        # Create a color token
        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": project.id,
                "hex": "#FF5733",
                "rgb": "rgb(255, 87, 51)",
                "name": "Coral Red",
                "design_intent": "error",
                "confidence": 0.95,
                "harmony": "complementary",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["hex"] == "#FF5733"
        assert data["name"] == "Coral Red"
        assert data["design_intent"] == "error"
        assert data["project_id"] == project.id

    @pytest.mark.asyncio
    async def test_create_color_token_not_found(self, client):
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
    async def test_get_color_token_endpoint(self, client, async_db):
        """Test getting a specific color token"""
        # Create project and color token
        project = Project(name="Test Project", description="Test")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        color = ColorToken(
            project_id=project.id,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            design_intent="error",
            confidence=0.95,
        )
        async_db.add(color)
        await async_db.commit()
        await async_db.refresh(color)

        # Retrieve the color
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
    async def test_project_colors_list(self, client, async_db):
        """Test listing all colors for a project"""
        # Create project
        project = Project(name="Test Project", description="Test")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        # Add multiple colors
        colors_data = [
            {"hex": "#FF5733", "name": "Red", "confidence": 0.95},
            {"hex": "#33FF57", "name": "Green", "confidence": 0.87},
            {"hex": "#3357FF", "name": "Blue", "confidence": 0.90},
        ]

        for data in colors_data:
            color = ColorToken(
                project_id=project.id,
                hex=data["hex"],
                rgb=data["rgb"] if "rgb" in data else f"rgb({data['hex']})",
                name=data["name"],
                confidence=data["confidence"],
            )
            async_db.add(color)

        await async_db.commit()

        # Get all colors for project
        response = await client.get(f"/api/v1/projects/{project.id}/colors")

        assert response.status_code == 200
        colors = response.json()
        assert len(colors) == 3
        assert colors[0]["name"] in ["Red", "Green", "Blue"]


class TestAPIValidation:
    """Test API request validation"""

    @pytest.mark.asyncio
    async def test_extract_colors_missing_required_field(self, client):
        """Test extract endpoint with missing required field"""
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "project_id": 1  # Missing image_url
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_extract_colors_invalid_max_colors(self, client, async_db):
        """Test extract endpoint with invalid max_colors"""
        # Create a test project first
        project = Project(name="Test", description="Test")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        # Try with invalid max_colors
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "image_url": "https://example.com/image.jpg",
                "project_id": project.id,
                "max_colors": 100,  # Exceeds max of 50
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_color_invalid_confidence(self, client, async_db):
        """Test create color with invalid confidence"""
        # Create a test project
        project = Project(name="Test Project", description="Test")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        response = await client.post(
            "/api/v1/colors",
            json={
                "project_id": project.id,
                "hex": "#FF5733",
                "rgb": "rgb(255, 87, 51)",
                "name": "Test",
                "confidence": 1.5,  # Invalid confidence > 1
            },
        )

        assert response.status_code == 422  # Validation error


class TestHealthEndpoints:
    """Test API health and status endpoints"""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test health endpoint"""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_api_status_endpoint(self, client):
        """Test API status endpoint"""
        response = await client.get("/api/v1/status")

        assert response.status_code == 200
        data = response.json()
        assert "api" in data
        assert data["status"] == "operational"
