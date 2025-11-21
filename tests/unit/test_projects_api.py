"""Tests for projects API endpoints"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.domain.models import Project
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


class TestProjectCRUD:
    """Test project CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_project(self, client):
        """Test creating a new project"""
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Test Project", "description": "A test project"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["description"] == "A test project"
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_project_minimal(self, client):
        """Test creating a project with only required fields"""
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Minimal Project"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Project"
        assert data["description"] is None

    @pytest.mark.asyncio
    async def test_create_project_validation_empty_name(self, client):
        """Test that empty name fails validation"""
        response = await client.post(
            "/api/v1/projects",
            json={"name": "", "description": "Test"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_project_validation_missing_name(self, client):
        """Test that missing name fails validation"""
        response = await client.post(
            "/api/v1/projects",
            json={"description": "Test"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_projects(self, client, async_db):
        """Test listing all projects"""
        # Create test projects
        for i in range(3):
            project = Project(name=f"Project {i}", description=f"Description {i}")
            async_db.add(project)
        await async_db.commit()

        response = await client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_list_projects_empty(self, client):
        """Test listing projects when none exist"""
        response = await client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_get_project(self, client, async_db):
        """Test getting a specific project"""
        project = Project(name="Test Project", description="Test")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        response = await client.get(f"/api/v1/projects/{project.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["id"] == project.id

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, client):
        """Test getting non-existent project"""
        response = await client.get("/api/v1/projects/999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_project(self, client, async_db):
        """Test updating a project"""
        project = Project(name="Original", description="Original desc")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        response = await client.put(
            f"/api/v1/projects/{project.id}",
            json={"name": "Updated", "description": "Updated desc"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["description"] == "Updated desc"

    @pytest.mark.asyncio
    async def test_update_project_partial(self, client, async_db):
        """Test partial update of a project"""
        project = Project(name="Original", description="Original desc")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        response = await client.put(
            f"/api/v1/projects/{project.id}",
            json={"name": "New Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"

    @pytest.mark.asyncio
    async def test_update_project_not_found(self, client):
        """Test updating non-existent project"""
        response = await client.put(
            "/api/v1/projects/999",
            json={"name": "Updated"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_project(self, client, async_db):
        """Test deleting a project"""
        project = Project(name="To Delete", description="Will be deleted")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        response = await client.delete(f"/api/v1/projects/{project.id}")
        assert response.status_code == 204  # No Content

        # Verify it's deleted
        response = await client.get(f"/api/v1/projects/{project.id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, client):
        """Test deleting non-existent project"""
        response = await client.delete("/api/v1/projects/999")
        assert response.status_code == 404


class TestProjectColors:
    """Test project color relationships"""

    @pytest.mark.asyncio
    async def test_get_project_colors_empty(self, client, async_db):
        """Test getting colors for project with no colors"""
        project = Project(name="Empty Project", description="No colors")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        response = await client.get(f"/api/v1/projects/{project.id}/colors")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_project_colors_not_found(self, client):
        """Test getting colors for non-existent project"""
        response = await client.get("/api/v1/projects/999/colors")
        assert response.status_code == 404
