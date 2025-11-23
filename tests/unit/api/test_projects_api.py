"""Comprehensive tests for projects API endpoints to achieve 80%+ coverage"""

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


class TestCreateProject:
    """Test project creation endpoint"""

    @pytest.mark.asyncio
    async def test_create_project_full(self, client):
        """Test creating a project with all fields"""
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Test Project", "description": "A test project description"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["description"] == "A test project description"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

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
    async def test_create_project_empty_name(self, client):
        """Test that empty name fails validation"""
        response = await client.post(
            "/api/v1/projects",
            json={"name": "", "description": "Test"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_project_missing_name(self, client):
        """Test that missing name fails validation"""
        response = await client.post(
            "/api/v1/projects",
            json={"description": "Test"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_project_long_name(self, client):
        """Test creating project with long name"""
        response = await client.post(
            "/api/v1/projects",
            json={"name": "A" * 200, "description": "Long name project"},
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_project_special_characters(self, client):
        """Test creating project with special characters in name"""
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Project @#$% 123!", "description": "Special chars"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Project @#$% 123!"


class TestListProjects:
    """Test project listing endpoint"""

    @pytest.mark.asyncio
    async def test_list_projects_empty(self, client):
        """Test listing projects when none exist"""
        response = await client.get("/api/v1/projects")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_projects_multiple(self, client, async_db):
        """Test listing multiple projects"""
        for i in range(5):
            project = Project(name=f"Project {i}", description=f"Description {i}")
            async_db.add(project)
        await async_db.commit()

        response = await client.get("/api/v1/projects")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    @pytest.mark.asyncio
    async def test_list_projects_with_limit(self, client, async_db):
        """Test listing projects with limit parameter"""
        for i in range(10):
            project = Project(name=f"Project {i}")
            async_db.add(project)
        await async_db.commit()

        response = await client.get("/api/v1/projects?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    @pytest.mark.asyncio
    async def test_list_projects_with_offset(self, client, async_db):
        """Test listing projects with offset parameter"""
        for i in range(10):
            project = Project(name=f"Project {i}")
            async_db.add(project)
        await async_db.commit()

        response = await client.get("/api/v1/projects?offset=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    @pytest.mark.asyncio
    async def test_list_projects_with_limit_and_offset(self, client, async_db):
        """Test listing projects with both limit and offset"""
        for i in range(20):
            project = Project(name=f"Project {i}")
            async_db.add(project)
        await async_db.commit()

        response = await client.get("/api/v1/projects?limit=5&offset=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    @pytest.mark.asyncio
    async def test_list_projects_invalid_limit(self, client):
        """Test listing projects with invalid limit (too high)"""
        response = await client.get("/api/v1/projects?limit=10000")

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_projects_invalid_offset(self, client):
        """Test listing projects with negative offset"""
        response = await client.get("/api/v1/projects?offset=-1")

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_projects_zero_limit(self, client):
        """Test listing projects with zero limit"""
        response = await client.get("/api/v1/projects?limit=0")

        assert response.status_code == 422


class TestGetProject:
    """Test get project by ID endpoint"""

    @pytest.mark.asyncio
    async def test_get_project_success(self, client, async_db):
        """Test getting a specific project"""
        project = Project(name="Test Project", description="Test Description")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        response = await client.get(f"/api/v1/projects/{project.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["description"] == "Test Description"
        assert data["id"] == project.id

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, client):
        """Test getting non-existent project"""
        response = await client.get("/api/v1/projects/999")

        assert response.status_code == 404
        assert "not found" in response.text.lower()

    @pytest.mark.asyncio
    async def test_get_project_with_null_description(self, client, async_db):
        """Test getting project with null description"""
        project = Project(name="No Description", description=None)
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        response = await client.get(f"/api/v1/projects/{project.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["description"] is None


class TestUpdateProject:
    """Test project update endpoint"""

    @pytest.mark.asyncio
    async def test_update_project_full(self, client, async_db):
        """Test updating all project fields"""
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
    async def test_update_project_name_only(self, client, async_db):
        """Test updating only project name"""
        project = Project(name="Original", description="Keep this")
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
        # Description should remain unchanged (partial update)

    @pytest.mark.asyncio
    async def test_update_project_description_only(self, client, async_db):
        """Test updating only project description"""
        project = Project(name="Keep this", description="Original")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        response = await client.put(
            f"/api/v1/projects/{project.id}",
            json={"description": "New Description"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "New Description"
        # Name should remain unchanged

    @pytest.mark.asyncio
    async def test_update_project_set_empty_description(self, client, async_db):
        """Test setting description to empty string"""
        project = Project(name="Test", description="Has description")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        response = await client.put(
            f"/api/v1/projects/{project.id}",
            json={"description": ""},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == ""

    @pytest.mark.asyncio
    async def test_update_project_not_found(self, client):
        """Test updating non-existent project"""
        response = await client.put(
            "/api/v1/projects/999",
            json={"name": "Updated"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_project_empty_body(self, client, async_db):
        """Test updating project with empty body"""
        project = Project(name="Original", description="Original")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        response = await client.put(
            f"/api/v1/projects/{project.id}",
            json={},
        )

        # Should succeed but not change anything
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_project_verifies_updated_at(self, client, async_db):
        """Test that updated_at changes on update"""
        project = Project(name="Original", description="Original")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        original_updated = project.updated_at

        response = await client.put(
            f"/api/v1/projects/{project.id}",
            json={"name": "Updated"},
        )

        assert response.status_code == 200
        data = response.json()
        # updated_at should be different (newer)
        assert data["updated_at"] != original_updated.isoformat()


class TestDeleteProject:
    """Test project deletion endpoint"""

    @pytest.mark.asyncio
    async def test_delete_project_success(self, client, async_db):
        """Test deleting a project"""
        project = Project(name="To Delete", description="Will be deleted")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)

        response = await client.delete(f"/api/v1/projects/{project.id}")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(f"/api/v1/projects/{project.id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, client):
        """Test deleting non-existent project"""
        response = await client.delete("/api/v1/projects/999")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_project_twice(self, client, async_db):
        """Test deleting same project twice fails second time"""
        project = Project(name="Delete Twice", description="Test")
        async_db.add(project)
        await async_db.commit()
        await async_db.refresh(project)
        project_id = project.id

        # First delete
        response1 = await client.delete(f"/api/v1/projects/{project_id}")
        assert response1.status_code == 204

        # Second delete should fail
        response2 = await client.delete(f"/api/v1/projects/{project_id}")
        assert response2.status_code == 404
