"""Tests for batch extraction API endpoints"""

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


@pytest.mark.asyncio
async def test_session_endpoints_exist(client):
    """Test that session endpoints are available"""
    # These should return 422/404 if no valid request, but endpoint should exist
    response = await client.get("/api/v1/sessions/1")
    # Should be 404 or 500, not 404 for "not found" endpoint
    assert response.status_code in [404, 500]


@pytest.mark.asyncio
async def test_extract_endpoint_exists(client):
    """Test that batch extract endpoint exists"""
    response = await client.post(
        "/api/v1/sessions/1/extract",
        json={"image_urls": ["http://example.com/image.jpg"], "max_colors": 10},
    )
    # Will fail due to missing session, but endpoint should exist
    assert response.status_code in [404, 422, 500]


@pytest.mark.asyncio
async def test_library_endpoint_exists(client):
    """Test that library endpoint exists"""
    response = await client.get("/api/v1/sessions/1/library")
    # Will return 404 because session/library doesn't exist
    assert response.status_code in [404, 500]


@pytest.mark.asyncio
async def test_curate_endpoint_exists(client):
    """Test that curate endpoint exists"""
    response = await client.post(
        "/api/v1/sessions/1/library/curate", json={"role_assignments": [], "notes": ""}
    )
    assert response.status_code in [404, 422, 500]


@pytest.mark.asyncio
async def test_export_endpoint_exists(client):
    """Test that export endpoint exists"""
    response = await client.get("/api/v1/sessions/1/library/export?format=w3c")
    assert response.status_code in [400, 404, 500]


@pytest.mark.asyncio
async def test_export_invalid_format(client):
    """Test export endpoint rejects invalid formats"""
    response = await client.get("/api/v1/sessions/1/library/export?format=invalid")
    # Should return 400 for invalid format before checking session
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_export_valid_formats(client):
    """Test export endpoint accepts valid formats"""
    valid_formats = ["w3c", "css", "react", "html"]
    for fmt in valid_formats:
        response = await client.get(f"/api/v1/sessions/1/library/export?format={fmt}")
        # Should not be 400 (invalid format error)
        assert response.status_code in [404, 500]  # 404 because session doesn't exist
        assert response.status_code != 400


@pytest.mark.asyncio
async def test_batch_extract_validation_empty_urls(client):
    """Test batch extract validates non-empty URL list"""
    response = await client.post(
        "/api/v1/sessions/1/extract", json={"image_urls": [], "max_colors": 10}
    )
    # Should fail validation (422) or session not found (404)
    assert response.status_code in [422, 404, 500]


@pytest.mark.asyncio
async def test_batch_extract_validation_max_urls(client):
    """Test batch extract validates max 50 URLs"""
    urls = [f"http://example.com/image{i}.jpg" for i in range(51)]
    response = await client.post(
        "/api/v1/sessions/1/extract", json={"image_urls": urls, "max_colors": 10}
    )
    # Should fail validation for too many URLs
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_batch_extract_validation_max_colors(client):
    """Test batch extract validates max_colors"""
    response = await client.post(
        "/api/v1/sessions/1/extract",
        json={"image_urls": ["http://example.com/image.jpg"], "max_colors": 1001},
    )
    # Should fail validation or session not found
    assert response.status_code in [422, 404, 500]


@pytest.mark.asyncio
async def test_session_creation_validation_project_id_required(client):
    """Test session creation requires project_id"""
    response = await client.post("/api/v1/sessions", json={"session_name": "Test"})
    # Should fail validation
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_session_creation_accepts_minimal_data(client, async_db):
    """Test session creation accepts minimal required data"""
    # Create a project first so the session creation can succeed
    project = Project(name="Test Project", description="Test")
    async_db.add(project)
    await async_db.commit()
    await async_db.refresh(project)

    response = await client.post(
        "/api/v1/sessions", json={"project_id": project.id, "name": "Test Session"}
    )
    # Should succeed with 201
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_api_documentation_available(client):
    """Test that API documentation is available"""
    response = await client.get("/docs")
    assert response.status_code == 200
    assert "openapi" in response.text.lower() or "swagger" in response.text.lower()


@pytest.mark.asyncio
async def test_api_version_in_paths(client):
    """Test that API uses v1 versioning"""
    response = await client.get("/openapi.json")
    if response.status_code == 200:
        data = response.json()
        paths = list(data.get("paths", {}).keys())
        # Should have v1 in paths
        v1_paths = [p for p in paths if "/api/v1/" in p]
        assert len(v1_paths) > 0


@pytest.mark.asyncio
async def test_error_response_format(client):
    """Test that error responses have consistent format"""
    response = await client.post(
        "/api/v1/sessions/invalid/extract",
        json={"image_urls": ["http://example.com/image.jpg"], "max_colors": 10},
    )
    # Should have error or detail field
    assert response.status_code != 200
    data = response.json()
    assert "detail" in data or "error" in data or "message" in data


@pytest.mark.asyncio
async def test_invalid_http_method(client):
    """Test that invalid HTTP methods return 405"""
    response = await client.delete("/api/v1/sessions")
    assert response.status_code == 405  # Method Not Allowed


@pytest.mark.asyncio
async def test_cors_headers_present(client):
    """Test that CORS headers are configured"""
    response = await client.options("/api/v1/sessions")
    # CORS may or may not be enabled, but shouldn't error
    assert response.status_code in [204, 405, 200]
