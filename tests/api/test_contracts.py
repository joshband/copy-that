"""API contract tests using Schemathesis.

Run with:
    pytest tests/api -v

Or run schemathesis directly:
    schemathesis run http://localhost:8000/openapi.json --stateful=links
"""

import os

import pytest
import schemathesis

# Load schema from OpenAPI endpoint
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Skip all tests if API is not available
pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true" and not os.getenv("API_AVAILABLE"),
    reason="API not available in CI",
)


# Try to load schema, skip if not available
try:
    schema = schemathesis.from_uri(f"{API_URL}/openapi.json")
except Exception:
    schema = None


# Only define schemathesis tests if schema is available
if schema is not None:
    class TestAPIContracts:
        """API contract tests generated from OpenAPI schema."""

        @schema.parametrize()
        def test_api_contract(self, case):
            """Test that API responses match OpenAPI schema.

            This test is automatically generated for each endpoint
            defined in the OpenAPI schema.
            """
            response = case.call()
            case.validate_response(response)

        @schema.parametrize(endpoint="/health")
        def test_health_endpoint(self, case):
            """Test health endpoint specifically."""
            response = case.call()
            case.validate_response(response)
            assert response.status_code == 200

        @schema.parametrize(endpoint="/api/v1/projects")
        def test_projects_endpoint(self, case):
            """Test projects endpoint."""
            response = case.call()
            case.validate_response(response)
            # Allow 401 for unauthenticated requests
            assert response.status_code in [200, 401, 403]


class TestManualContracts:
    """Manual API contract tests for specific scenarios."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        import httpx

        return httpx.Client(base_url=API_URL, timeout=10)

    def test_health_returns_ok(self, client):
        """Test health endpoint returns expected format."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok", "up"]

    def test_openapi_schema_available(self, client):
        """Test OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema_data = response.json()
        assert "openapi" in schema_data
        assert "paths" in schema_data
        assert "info" in schema_data

    def test_api_versioning(self, client):
        """Test API versioning is consistent."""
        response = client.get("/openapi.json")
        schema_data = response.json()

        # Check all paths use v1
        for path in schema_data.get("paths", {}):
            if path.startswith("/api/"):
                assert "/v1/" in path, f"Path {path} should include version"

    def test_error_format(self, client):
        """Test error responses follow consistent format."""
        # Hit a non-existent endpoint
        response = client.get("/api/v1/nonexistent")

        assert response.status_code == 404
        data = response.json()

        # Errors should have detail field
        assert "detail" in data

    def test_content_type_json(self, client):
        """Test API returns JSON content type."""
        response = client.get("/health")

        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type

    @pytest.mark.skip(reason="Requires authentication")
    def test_authentication_required(self, client):
        """Test protected endpoints require authentication."""
        protected_endpoints = [
            "/api/v1/projects",
            "/api/v1/libraries",
            "/api/v1/sessions",
        ]

        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [401, 403], f"{endpoint} should require auth"


def test_contract_infrastructure():
    """Verify API contract testing is set up."""
    assert schemathesis is not None, "Schemathesis should be importable"
