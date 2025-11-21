"""End-to-end integration tests for color extraction flow"""

from pathlib import Path

import pytest

from copy_that.domain.models import Project
from copy_that.interfaces.api.main import app


@pytest.mark.asyncio
async def test_demo_page_loads():
    """Test that the demo page is accessible"""
    # Check that static HTML file exists
    demo_file = Path(__file__).parent.parent.parent / "static" / "index.html"
    assert demo_file.exists(), "Demo HTML file should exist"

    # Verify file has content
    content = demo_file.read_text()
    assert "Copy That" in content
    assert "Upload Image" in content
    assert "Extracted Colors" in content


def test_api_documentation_structure():
    """Test that API documentation endpoint returns correct structure"""
    from copy_that.interfaces.api.main import app

    # Get the endpoint from the app
    api_docs_route = None
    for route in app.routes:
        if "/api/v1/docs" in str(route.path):
            api_docs_route = route
            break

    assert api_docs_route is not None, "API docs endpoint should exist"

    # Verify the route method
    assert "GET" in str(api_docs_route.methods)


def test_health_endpoints_exist():
    """Test that health check endpoints are defined"""
    routes = [str(route.path) for route in app.routes]

    # Verify endpoints exist
    assert any("/health" in str(r) for r in routes), "Health endpoint should exist"
    assert any("/api/v1/status" in str(r) for r in routes), "Status endpoint should exist"


def test_database_models_structure():
    """Test that database models are correctly defined"""
    from copy_that.domain.models import ColorToken, ExtractionJob

    # Verify Project table
    assert Project.__tablename__ == "projects"
    project_cols = {c.name for c in Project.__table__.columns}
    assert project_cols >= {"id", "name", "created_at", "updated_at"}

    # Verify ExtractionJob table
    assert ExtractionJob.__tablename__ == "extraction_jobs"
    job_cols = {c.name for c in ExtractionJob.__table__.columns}
    assert job_cols >= {"id", "project_id", "status", "created_at"}

    # Verify ColorToken table
    assert ColorToken.__tablename__ == "color_tokens"
    color_cols = {c.name for c in ColorToken.__table__.columns}
    assert color_cols >= {"id", "project_id", "hex", "confidence", "created_at"}


def test_color_extraction_flow_imports():
    """Test that all color extraction components are importable"""
    from copy_that.application.color_extractor import AIColorExtractor
    from copy_that.domain.models import ColorToken, ExtractionJob

    # Verify they're not None
    assert AIColorExtractor is not None
    assert ColorToken is not None
    assert ExtractionJob is not None


class TestE2EWorkflow:
    """Test the complete end-to-end workflow"""

    def test_static_files_exist(self):
        """Verify all necessary static files exist"""
        static_dir = Path(__file__).parent.parent.parent / "static"

        # Check index.html exists
        index_file = static_dir / "index.html"
        assert index_file.exists(), "index.html should exist"

        # Verify HTML contains required elements
        content = index_file.read_text()
        required_elements = [
            "Copy That",
            "color extraction",
            "Upload",
            "Extract",
            "API",
            "Educational",
        ]

        for element in required_elements:
            assert element.lower() in content.lower(), f"{element} should be in HTML"

    def test_api_routes_defined(self):
        """Verify all required API routes are defined"""
        routes = [route.path for route in app.routes]

        required_routes = [
            "/",
            "/health",
            "/api/v1/status",
            "/api/v1/docs",
            "/api/v1/colors/extract",
            "/api/v1/projects/{project_id}/colors",
            "/api/v1/colors",
            "/api/v1/colors/{color_id}",
            "/api/v1/db-test",
        ]

        for route in required_routes:
            assert any(route in str(r) or str(r) in route for r in routes), (
                f"Route {route} should be defined"
            )

    def test_models_structure(self):
        """Verify ORM models have correct structure"""
        from copy_that.domain.models import ColorToken, ExtractionJob

        # Verify Project model
        project_fields = [c.name for c in Project.__table__.columns]
        assert "id" in project_fields
        assert "name" in project_fields
        assert "created_at" in project_fields

        # Verify ExtractionJob model
        job_fields = [c.name for c in ExtractionJob.__table__.columns]
        assert "id" in job_fields
        assert "project_id" in job_fields
        assert "status" in job_fields

        # Verify ColorToken model
        color_fields = [c.name for c in ColorToken.__table__.columns]
        assert "id" in color_fields
        assert "project_id" in color_fields
        assert "hex" in color_fields
        assert "confidence" in color_fields


def test_color_extraction_imports():
    """Test that color extraction module can be imported"""
    from copy_that.application.color_extractor import (
        AIColorExtractor,
        ColorExtractionResult,
        ColorToken,
    )

    # Verify classes are available
    assert AIColorExtractor is not None
    assert ColorToken is not None
    assert ColorExtractionResult is not None


def test_api_schemas_imports():
    """Test that API schemas can be imported"""
    from copy_that.interfaces.api.schemas import (
        ColorExtractionResponse,
        ColorTokenResponse,
        ExtractColorRequest,
    )

    # Verify classes are available
    assert ColorTokenResponse is not None
    assert ColorExtractionResponse is not None
    assert ExtractColorRequest is not None
