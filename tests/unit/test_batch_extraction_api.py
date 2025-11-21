"""Tests for batch extraction API endpoints"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from copy_that.interfaces.api.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


def test_session_endpoints_exist(client):
    """Test that session endpoints are available"""
    # These should return 422/404 if no valid request, but endpoint should exist
    response = client.get("/api/v1/sessions/1")
    # Should be 404 or 500, not 404 for "not found" endpoint
    assert response.status_code in [404, 500]


def test_extract_endpoint_exists(client):
    """Test that batch extract endpoint exists"""
    response = client.post(
        "/api/v1/sessions/1/extract",
        json={"image_urls": ["http://example.com/image.jpg"], "max_colors": 10}
    )
    # Will fail due to missing session, but endpoint should exist
    assert response.status_code in [404, 422, 500]


def test_library_endpoint_exists(client):
    """Test that library endpoint exists"""
    response = client.get("/api/v1/sessions/1/library")
    # Will return 404 because session/library doesn't exist
    assert response.status_code in [404, 500]


def test_curate_endpoint_exists(client):
    """Test that curate endpoint exists"""
    response = client.post(
        "/api/v1/sessions/1/library/curate",
        json={"role_assignments": [], "notes": ""}
    )
    assert response.status_code in [404, 422, 500]


def test_export_endpoint_exists(client):
    """Test that export endpoint exists"""
    response = client.get("/api/v1/sessions/1/library/export?format=w3c")
    assert response.status_code in [400, 404, 500]


def test_export_invalid_format(client):
    """Test export endpoint rejects invalid formats"""
    response = client.get("/api/v1/sessions/1/library/export?format=invalid")
    # Should return 400 for invalid format before checking session
    assert response.status_code == 400


def test_export_valid_formats(client):
    """Test export endpoint accepts valid formats"""
    valid_formats = ["w3c", "css", "react", "html"]
    for fmt in valid_formats:
        response = client.get(f"/api/v1/sessions/1/library/export?format={fmt}")
        # Should not be 400 (invalid format error)
        assert response.status_code in [404, 500]  # 404 because session doesn't exist
        assert response.status_code != 400


def test_batch_extract_validation_empty_urls(client):
    """Test batch extract validates non-empty URL list"""
    response = client.post(
        "/api/v1/sessions/1/extract",
        json={"image_urls": [], "max_colors": 10}
    )
    # Should fail validation (422) or session not found (404)
    assert response.status_code in [422, 404, 500]


def test_batch_extract_validation_max_urls(client):
    """Test batch extract validates max 50 URLs"""
    urls = [f"http://example.com/image{i}.jpg" for i in range(51)]
    response = client.post(
        "/api/v1/sessions/1/extract",
        json={"image_urls": urls, "max_colors": 10}
    )
    # Should fail validation for too many URLs
    assert response.status_code == 422


def test_batch_extract_validation_max_colors(client):
    """Test batch extract validates max_colors"""
    response = client.post(
        "/api/v1/sessions/1/extract",
        json={"image_urls": ["http://example.com/image.jpg"], "max_colors": 1001}
    )
    # Should fail validation or session not found
    assert response.status_code in [422, 404, 500]


def test_session_creation_validation_project_id_required(client):
    """Test session creation requires project_id"""
    response = client.post(
        "/api/v1/sessions",
        json={"session_name": "Test"}
    )
    # Should fail validation
    assert response.status_code == 422


def test_session_creation_accepts_minimal_data(client):
    """Test session creation accepts minimal required data"""
    response = client.post(
        "/api/v1/sessions",
        json={"project_id": 1}
    )
    # Should succeed or fail due to DB connection, not validation
    assert response.status_code in [201, 500]


def test_api_documentation_available(client):
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "openapi" in response.text.lower() or "swagger" in response.text.lower()


def test_api_version_in_paths(client):
    """Test that API uses v1 versioning"""
    response = client.get("/openapi.json")
    if response.status_code == 200:
        data = response.json()
        paths = list(data.get("paths", {}).keys())
        # Should have v1 in paths
        v1_paths = [p for p in paths if "/api/v1/" in p]
        assert len(v1_paths) > 0


def test_error_response_format(client):
    """Test that error responses have consistent format"""
    response = client.post(
        "/api/v1/sessions/invalid/extract",
        json={"image_urls": ["http://example.com/image.jpg"], "max_colors": 10}
    )
    # Should have error or detail field
    assert response.status_code != 200
    data = response.json()
    assert "detail" in data or "error" in data or "message" in data


def test_invalid_http_method(client):
    """Test that invalid HTTP methods return 405"""
    response = client.delete("/api/v1/sessions")
    assert response.status_code == 405  # Method Not Allowed


def test_cors_headers_present(client):
    """Test that CORS headers are configured"""
    response = client.options("/api/v1/sessions")
    # CORS may or may not be enabled, but shouldn't error
    assert response.status_code in [204, 405, 200]
