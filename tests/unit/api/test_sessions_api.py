"""Comprehensive tests for sessions API endpoints to achieve 80%+ coverage"""

import json
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.domain.models import (
    ColorToken,
    ExtractionSession,
    Project,
    TokenLibrary,
)
from copy_that.infrastructure.database import Base, get_db
from copy_that.interfaces.api.main import app
from copy_that.interfaces.api.sessions import safe_json_loads


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
    project = Project(name="Test Project", description="For session testing")
    async_db.add(project)
    await async_db.commit()
    await async_db.refresh(project)
    return project


@pytest_asyncio.fixture
async def test_session(async_db, test_project):
    """Create a test session"""
    session = ExtractionSession(
        project_id=test_project.id,
        name="Test Session",
        description="For testing",
    )
    async_db.add(session)
    await async_db.commit()
    await async_db.refresh(session)
    return session


class TestSafeJsonLoads:
    """Test safe_json_loads helper function"""

    def test_valid_json_object(self):
        """Test parsing valid JSON object"""
        result = safe_json_loads('{"key": "value"}')
        assert result == {"key": "value"}

    def test_valid_json_array(self):
        """Test parsing valid JSON array"""
        result = safe_json_loads('["a", "b", "c"]', default=[])
        assert result == ["a", "b", "c"]

    def test_empty_string(self):
        """Test empty string returns default"""
        result = safe_json_loads("")
        assert result == {}

    def test_none_input(self):
        """Test None input returns default"""
        result = safe_json_loads(None)
        assert result == {}

    def test_invalid_json(self):
        """Test invalid JSON returns default"""
        result = safe_json_loads("not valid json")
        assert result == {}

    def test_custom_default(self):
        """Test custom default value"""
        result = safe_json_loads(None, default={"custom": True})
        assert result == {"custom": True}

    def test_custom_list_default(self):
        """Test custom list default value"""
        result = safe_json_loads("", default=["default"])
        assert result == ["default"]


class TestCreateSession:
    """Test session creation endpoint"""

    @pytest.mark.asyncio
    async def test_create_session_full(self, client, test_project):
        """Test creating a session with all fields"""
        response = await client.post(
            "/api/v1/sessions",
            json={
                "project_id": test_project.id,
                "name": "Test Session",
                "description": "A test session",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Session"
        assert data["description"] == "A test session"
        assert data["project_id"] == test_project.id
        assert data["image_count"] == 0
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_session_minimal(self, client, test_project):
        """Test creating a session with only required fields"""
        response = await client.post(
            "/api/v1/sessions",
            json={
                "project_id": test_project.id,
                "name": "Minimal Session",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Session"
        assert data["description"] is None

    @pytest.mark.asyncio
    async def test_create_session_project_not_found(self, client):
        """Test creating session with non-existent project"""
        response = await client.post(
            "/api/v1/sessions",
            json={
                "project_id": 999,
                "name": "Test Session",
            },
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_session_missing_name(self, client, test_project):
        """Test that missing name fails validation"""
        response = await client.post(
            "/api/v1/sessions",
            json={"project_id": test_project.id},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_session_missing_project_id(self, client):
        """Test that missing project_id fails validation"""
        response = await client.post(
            "/api/v1/sessions",
            json={"name": "Test Session"},
        )

        assert response.status_code == 422


class TestGetSession:
    """Test get session endpoint"""

    @pytest.mark.asyncio
    async def test_get_session_success(self, client, test_session):
        """Test getting a specific session"""
        response = await client.get(f"/api/v1/sessions/{test_session.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Session"
        assert data["id"] == test_session.id

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, client):
        """Test getting non-existent session"""
        response = await client.get("/api/v1/sessions/999")

        assert response.status_code == 404


class TestGetLibrary:
    """Test get library endpoint"""

    @pytest.mark.asyncio
    async def test_get_library_creates_new(self, client, test_session):
        """Test getting library creates empty library if none exists"""
        response = await client.get(f"/api/v1/sessions/{test_session.id}/library")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == test_session.id
        assert data["token_type"] == "color"
        assert data["is_curated"] is False
        assert data["tokens"] == []
        assert "statistics" in data

    @pytest.mark.asyncio
    async def test_get_library_existing(self, client, async_db, test_session):
        """Test getting existing library"""
        # Create library
        library = TokenLibrary(
            session_id=test_session.id,
            token_type="color",
            statistics=json.dumps({
                "color_count": 5,
                "image_count": 2,
                "avg_confidence": 0.85,
                "min_confidence": 0.7,
                "max_confidence": 0.95,
                "dominant_colors": ["#FF0000", "#00FF00"],
                "multi_image_colors": 3,
            }),
            is_curated=True,
        )
        async_db.add(library)
        await async_db.commit()

        response = await client.get(f"/api/v1/sessions/{test_session.id}/library")

        assert response.status_code == 200
        data = response.json()
        assert data["is_curated"] is True
        assert data["statistics"]["color_count"] == 5
        assert data["statistics"]["image_count"] == 2

    @pytest.mark.asyncio
    async def test_get_library_session_not_found(self, client):
        """Test getting library for non-existent session"""
        response = await client.get("/api/v1/sessions/999/library")

        assert response.status_code == 404


class TestCurateLibrary:
    """Test library curation endpoint"""

    @pytest.mark.asyncio
    async def test_curate_library_success(self, client, async_db, test_session):
        """Test successful library curation"""
        # Create library with tokens
        library = TokenLibrary(
            session_id=test_session.id,
            token_type="color",
            statistics="{}",
        )
        async_db.add(library)
        await async_db.commit()
        await async_db.refresh(library)

        # Create color tokens
        token1 = ColorToken(
            project_id=test_session.project_id,
            library_id=library.id,
            hex="#FF0000",
            rgb="rgb(255, 0, 0)",
            name="Red",
            confidence=0.9,
        )
        token2 = ColorToken(
            project_id=test_session.project_id,
            library_id=library.id,
            hex="#00FF00",
            rgb="rgb(0, 255, 0)",
            name="Green",
            confidence=0.85,
        )
        async_db.add(token1)
        async_db.add(token2)
        await async_db.commit()
        await async_db.refresh(token1)
        await async_db.refresh(token2)

        # Curate
        response = await client.post(
            f"/api/v1/sessions/{test_session.id}/library/curate",
            json={
                "role_assignments": [
                    {"token_id": token1.id, "role": "primary"},
                    {"token_id": token2.id, "role": "secondary"},
                ],
                "notes": "Initial curation",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "2 tokens" in data["message"]

    @pytest.mark.asyncio
    async def test_curate_library_invalid_role(self, client, async_db, test_session):
        """Test curation with invalid role fails"""
        # Create library
        library = TokenLibrary(
            session_id=test_session.id,
            token_type="color",
            statistics="{}",
        )
        async_db.add(library)
        await async_db.commit()

        response = await client.post(
            f"/api/v1/sessions/{test_session.id}/library/curate",
            json={
                "role_assignments": [{"token_id": 1, "role": "invalid_role"}],
                "notes": "Test",
            },
        )

        assert response.status_code == 400
        assert "Invalid role" in response.text

    @pytest.mark.asyncio
    async def test_curate_library_empty_assignments(self, client, async_db, test_session):
        """Test curation with empty assignments"""
        # Create library
        library = TokenLibrary(
            session_id=test_session.id,
            token_type="color",
            statistics="{}",
        )
        async_db.add(library)
        await async_db.commit()

        response = await client.post(
            f"/api/v1/sessions/{test_session.id}/library/curate",
            json={"role_assignments": [], "notes": "Empty"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "0 tokens" in data["message"]

    @pytest.mark.asyncio
    async def test_curate_library_not_found(self, client, test_session):
        """Test curating non-existent library"""
        response = await client.post(
            f"/api/v1/sessions/{test_session.id}/library/curate",
            json={"role_assignments": [], "notes": "Test"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_curate_library_all_valid_roles(self, client, async_db, test_session):
        """Test all valid role types are accepted"""
        # Create library
        library = TokenLibrary(
            session_id=test_session.id,
            token_type="color",
            statistics="{}",
        )
        async_db.add(library)
        await async_db.commit()
        await async_db.refresh(library)

        # Create tokens for each role
        valid_roles = ["primary", "secondary", "accent", "neutral", "success", "warning", "danger", "info"]
        tokens = []
        for i, role in enumerate(valid_roles):
            token = ColorToken(
                project_id=test_session.project_id,
                library_id=library.id,
                hex=f"#00000{i}",
                rgb=f"rgb({i}, {i}, {i})",
                name=f"Color {i}",
                confidence=0.9,
            )
            async_db.add(token)
            tokens.append(token)
        await async_db.commit()
        for token in tokens:
            await async_db.refresh(token)

        # Curate with all valid roles
        response = await client.post(
            f"/api/v1/sessions/{test_session.id}/library/curate",
            json={
                "role_assignments": [
                    {"token_id": tokens[i].id, "role": role}
                    for i, role in enumerate(valid_roles)
                ],
                "notes": "All roles",
            },
        )

        assert response.status_code == 200


class TestBatchExtract:
    """Test batch extraction endpoint"""

    @pytest.mark.asyncio
    async def test_batch_extract_session_not_found(self, client):
        """Test batch extraction for non-existent session"""
        response = await client.post(
            "/api/v1/sessions/999/extract",
            json={
                "image_urls": ["https://example.com/image.jpg"],
                "max_colors": 10,
            },
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_batch_extract_empty_urls(self, client, test_session):
        """Test batch extraction with empty URL list"""
        response = await client.post(
            f"/api/v1/sessions/{test_session.id}/extract",
            json={"image_urls": [], "max_colors": 10},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_batch_extract_invalid_max_colors(self, client, test_session):
        """Test batch extraction with invalid max_colors"""
        response = await client.post(
            f"/api/v1/sessions/{test_session.id}/extract",
            json={
                "image_urls": ["https://example.com/image.jpg"],
                "max_colors": 100,  # Over limit of 50
            },
        )

        assert response.status_code == 422


class TestExportLibrary:
    """Test library export endpoint"""

    @pytest.mark.asyncio
    async def test_export_library_w3c(self, client, async_db, test_session):
        """Test exporting library in W3C format"""
        # Create library with tokens
        library = TokenLibrary(
            session_id=test_session.id,
            token_type="color",
            statistics=json.dumps({"color_count": 1}),
        )
        async_db.add(library)
        await async_db.commit()
        await async_db.refresh(library)

        token = ColorToken(
            project_id=test_session.project_id,
            library_id=library.id,
            hex="#FF0000",
            rgb="rgb(255, 0, 0)",
            name="Red",
            confidence=0.9,
        )
        async_db.add(token)
        await async_db.commit()

        response = await client.get(f"/api/v1/sessions/{test_session.id}/library/export?format=w3c")

        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "w3c"
        assert data["mime_type"] == "application/json"

    @pytest.mark.asyncio
    async def test_export_library_css(self, client, async_db, test_session):
        """Test exporting library in CSS format"""
        library = TokenLibrary(
            session_id=test_session.id,
            token_type="color",
            statistics=json.dumps({"color_count": 1}),
        )
        async_db.add(library)
        await async_db.commit()
        await async_db.refresh(library)

        token = ColorToken(
            project_id=test_session.project_id,
            library_id=library.id,
            hex="#FF0000",
            rgb="rgb(255, 0, 0)",
            name="Red",
            confidence=0.9,
        )
        async_db.add(token)
        await async_db.commit()

        response = await client.get(f"/api/v1/sessions/{test_session.id}/library/export?format=css")

        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "css"
        assert data["mime_type"] == "text/css"

    @pytest.mark.asyncio
    async def test_export_library_react(self, client, async_db, test_session):
        """Test exporting library in React format"""
        library = TokenLibrary(
            session_id=test_session.id,
            token_type="color",
            statistics=json.dumps({"color_count": 1}),
        )
        async_db.add(library)
        await async_db.commit()
        await async_db.refresh(library)

        token = ColorToken(
            project_id=test_session.project_id,
            library_id=library.id,
            hex="#00FF00",
            rgb="rgb(0, 255, 0)",
            name="Green",
            confidence=0.85,
        )
        async_db.add(token)
        await async_db.commit()

        response = await client.get(f"/api/v1/sessions/{test_session.id}/library/export?format=react")

        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "react"
        assert data["mime_type"] == "text/plain"

    @pytest.mark.asyncio
    async def test_export_library_html(self, client, async_db, test_session):
        """Test exporting library in HTML format"""
        library = TokenLibrary(
            session_id=test_session.id,
            token_type="color",
            statistics=json.dumps({"color_count": 1}),
        )
        async_db.add(library)
        await async_db.commit()
        await async_db.refresh(library)

        token = ColorToken(
            project_id=test_session.project_id,
            library_id=library.id,
            hex="#0000FF",
            rgb="rgb(0, 0, 255)",
            name="Blue",
            confidence=0.95,
        )
        async_db.add(token)
        await async_db.commit()

        response = await client.get(f"/api/v1/sessions/{test_session.id}/library/export?format=html")

        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "html"
        assert data["mime_type"] == "text/html"

    @pytest.mark.asyncio
    async def test_export_library_invalid_format(self, client, test_session):
        """Test export with invalid format"""
        response = await client.get(f"/api/v1/sessions/{test_session.id}/library/export?format=invalid")

        assert response.status_code == 400
        assert "Invalid format" in response.text

    @pytest.mark.asyncio
    async def test_export_library_not_found(self, client, test_session):
        """Test export for session without library"""
        response = await client.get(f"/api/v1/sessions/{test_session.id}/library/export?format=css")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_export_library_default_format(self, client, async_db, test_session):
        """Test export with default format (w3c)"""
        library = TokenLibrary(
            session_id=test_session.id,
            token_type="color",
            statistics=json.dumps({"color_count": 0}),
        )
        async_db.add(library)
        await async_db.commit()

        response = await client.get(f"/api/v1/sessions/{test_session.id}/library/export")

        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "w3c"

    @pytest.mark.asyncio
    async def test_export_library_empty(self, client, async_db, test_session):
        """Test exporting empty library"""
        library = TokenLibrary(
            session_id=test_session.id,
            token_type="color",
            statistics=json.dumps({"color_count": 0}),
        )
        async_db.add(library)
        await async_db.commit()

        response = await client.get(f"/api/v1/sessions/{test_session.id}/library/export?format=css")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_export_library_with_provenance(self, client, async_db, test_session):
        """Test exporting library with token provenance data"""
        library = TokenLibrary(
            session_id=test_session.id,
            token_type="color",
            statistics=json.dumps({"color_count": 1}),
        )
        async_db.add(library)
        await async_db.commit()
        await async_db.refresh(library)

        token = ColorToken(
            project_id=test_session.project_id,
            library_id=library.id,
            hex="#FF00FF",
            rgb="rgb(255, 0, 255)",
            name="Magenta",
            confidence=0.9,
            role="accent",
            provenance=json.dumps({"source": "test", "images": ["img1.jpg"]}),
        )
        async_db.add(token)
        await async_db.commit()

        response = await client.get(f"/api/v1/sessions/{test_session.id}/library/export?format=w3c")

        assert response.status_code == 200
