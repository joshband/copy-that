"""Comprehensive tests for typography extraction API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.models import Project, TypographyToken
from copy_that.interfaces.api.main import app

client = TestClient(app)

# Fixtures


@pytest.fixture
async def project_with_typography(async_session: AsyncSession):
    """Create a project with typography tokens."""
    project = Project(name="Typography Test Project", description="Test typography extraction")
    async_session.add(project)
    await async_session.flush()

    # Add sample typography tokens
    tokens = [
        TypographyToken(
            project_id=project.id,
            font_family="Inter",
            font_weight=700,
            font_size=32,
            line_height=1.2,
            semantic_role="heading",
            category="display",
            name="Heading Large",
            confidence=0.95,
        ),
        TypographyToken(
            project_id=project.id,
            font_family="Inter",
            font_weight=400,
            font_size=16,
            line_height=1.5,
            semantic_role="body",
            category="text",
            name="Body Regular",
            confidence=0.92,
        ),
    ]
    for token in tokens:
        async_session.add(token)

    await async_session.commit()
    return project


# Extraction Tests


class TestTypographyExtraction:
    """Test typography extraction endpoint."""

    async def test_extract_typography_with_url(self):
        """Extract typography from image URL."""
        project_id = await self._create_project()
        with patch("copy_that.interfaces.api.typography.AITypographyExtractor") as mock_extractor:
            mock_ai = AsyncMock()
            mock_ai.extract_typography_from_image_url.return_value = self._mock_extraction_result()
            mock_extractor.return_value = mock_ai

            response = client.post(
                "/api/v1/typography/extract",
                json={
                    "image_url": "https://example.com/image.png",
                    "project_id": project_id,
                    "max_tokens": 10,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "typography_tokens" in data
            assert data["extractor_used"] is not None
            assert 0 <= data["extraction_confidence"] <= 1

    async def test_extract_typography_with_base64(self):
        """Extract typography from base64 image data."""
        project_id = await self._create_project()
        base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        with patch("copy_that.interfaces.api.typography.AITypographyExtractor") as mock_extractor:
            mock_ai = AsyncMock()
            mock_ai.extract_typography_from_base64.return_value = self._mock_extraction_result()
            mock_extractor.return_value = mock_ai

            response = client.post(
                "/api/v1/typography/extract",
                json={
                    "image_base64": base64_image,
                    "project_id": project_id,
                    "max_tokens": 15,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "typography_tokens" in data

    async def test_extract_typography_invalid_project(self):
        """Extract typography with non-existent project."""
        response = client.post(
            "/api/v1/typography/extract",
            json={
                "image_url": "https://example.com/image.png",
                "project_id": 99999,
                "max_tokens": 10,
            },
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_extract_typography_missing_image(self):
        """Extract typography without image URL or base64."""
        project_id = await self._create_project()
        response = client.post(
            "/api/v1/typography/extract",
            json={
                "project_id": project_id,
                "max_tokens": 10,
            },
        )

        assert response.status_code == 400
        assert "image" in response.json()["detail"].lower()

    # List/Get Tests

    async def test_get_project_typography_list(self, project_with_typography):
        """Get all typography tokens for a project."""
        response = client.get(f"/api/v1/projects/{project_with_typography.id}/typography")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        assert data[0]["font_family"] is not None
        assert data[0]["font_weight"] is not None

    async def test_get_project_typography_empty(self):
        """Get typography tokens for project with none."""
        project = await self._create_project()
        response = client.get(f"/api/v1/projects/{project.id}/typography")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_get_project_typography_invalid_project(self):
        """Get typography tokens for non-existent project."""
        response = client.get("/api/v1/projects/99999/typography")

        assert response.status_code == 404

    # Create Tests

    async def test_create_typography_token(self):
        """Create a new typography token."""
        project_id = await self._create_project()
        response = client.post(
            "/api/v1/typography",
            json={
                "project_id": project_id,
                "font_family": "Roboto",
                "font_weight": 500,
                "font_size": 18,
                "line_height": 1.6,
                "semantic_role": "body",
                "category": "text",
                "name": "Body Medium",
                "confidence": 0.88,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["font_family"] == "Roboto"
        assert data["font_weight"] == 500
        assert data["confidence"] == 0.88

    async def test_create_typography_invalid_font_weight(self):
        """Create typography with invalid font weight."""
        project_id = await self._create_project()
        response = client.post(
            "/api/v1/typography",
            json={
                "project_id": project_id,
                "font_family": "Arial",
                "font_weight": 1000,  # Invalid
                "font_size": 16,
                "line_height": 1.5,
                "semantic_role": "body",
                "confidence": 0.9,
            },
        )

        assert response.status_code == 422

    async def test_create_typography_missing_required_field(self):
        """Create typography missing required field."""
        project_id = await self._create_project()
        response = client.post(
            "/api/v1/typography",
            json={
                "project_id": project_id,
                "font_family": "Arial",
                # Missing font_weight
                "font_size": 16,
                "line_height": 1.5,
                "semantic_role": "body",
                "confidence": 0.9,
            },
        )

        assert response.status_code == 422

    # Get Single Token Tests

    async def test_get_typography_token(self, project_with_typography):
        """Get a specific typography token."""
        # Get first token
        list_response = client.get(f"/api/v1/projects/{project_with_typography.id}/typography")
        token_id = list_response.json()[0]["id"]

        response = client.get(f"/api/v1/typography/{token_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == token_id
        assert data["font_family"] == "Inter"

    async def test_get_typography_token_not_found(self):
        """Get non-existent typography token."""
        response = client.get("/api/v1/typography/99999")

        assert response.status_code == 404

    # Update Tests

    async def test_update_typography_token(self, project_with_typography):
        """Update an existing typography token."""
        list_response = client.get(f"/api/v1/projects/{project_with_typography.id}/typography")
        token_id = list_response.json()[0]["id"]

        response = client.put(
            f"/api/v1/typography/{token_id}",
            json={
                "project_id": project_with_typography.id,
                "font_family": "Inter",
                "font_weight": 600,  # Updated
                "font_size": 32,
                "line_height": 1.2,
                "semantic_role": "heading",
                "category": "display",
                "name": "Heading Updated",
                "confidence": 0.98,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["font_weight"] == 600
        assert data["name"] == "Heading Updated"

    async def test_update_typography_not_found(self):
        """Update non-existent typography token."""
        response = client.put(
            "/api/v1/typography/99999",
            json={
                "project_id": 1,
                "font_family": "Arial",
                "font_weight": 400,
                "font_size": 16,
                "line_height": 1.5,
                "semantic_role": "body",
                "confidence": 0.9,
            },
        )

        assert response.status_code == 404

    # Delete Tests

    async def test_delete_typography_token(self, project_with_typography):
        """Delete a typography token."""
        list_response = client.get(f"/api/v1/projects/{project_with_typography.id}/typography")
        initial_count = len(list_response.json())
        token_id = list_response.json()[0]["id"]

        response = client.delete(f"/api/v1/typography/{token_id}")

        assert response.status_code == 204

        # Verify deletion
        list_after = client.get(f"/api/v1/projects/{project_with_typography.id}/typography")
        assert len(list_after.json()) == initial_count - 1

    async def test_delete_typography_not_found(self):
        """Delete non-existent typography token."""
        response = client.delete("/api/v1/typography/99999")

        assert response.status_code == 404

    # Batch Tests

    async def test_batch_extract_typography(self):
        """Batch extract typography from multiple URLs."""
        project = await self._create_project()

        with patch("copy_that.interfaces.api.typography.AITypographyExtractor") as mock_extractor:
            mock_ai = AsyncMock()
            mock_ai.extract_typography_from_image_url.return_value = self._mock_extraction_result()
            mock_extractor.return_value = mock_ai

            response = client.post(
                "/api/v1/typography/batch",
                json={
                    "image_urls": [
                        "https://example.com/image1.png",
                        "https://example.com/image2.png",
                    ],
                    "project_id": project.id,
                    "max_tokens": 10,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2

    # W3C Export Tests

    async def test_export_typography_w3c(self, project_with_typography):
        """Export typography tokens as W3C JSON."""
        response = client.get(
            f"/api/v1/typography/export/w3c?project_id={project_with_typography.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    async def test_export_typography_w3c_all(self):
        """Export all typography tokens as W3C JSON."""
        response = client.get("/api/v1/typography/export/w3c")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    # Helper Methods

    def _mock_extraction_result(self):
        """Create mock extraction result."""
        from copy_that.application.ai_typography_extractor import (
            ExtractedTypographyToken,
            TypographyExtractionResult,
        )

        tokens = [
            ExtractedTypographyToken(
                font_family="Inter",
                font_weight=700,
                font_size=32,
                line_height=1.2,
                semantic_role="heading",
                category="display",
                name="Heading",
                confidence=0.95,
            ),
            ExtractedTypographyToken(
                font_family="Inter",
                font_weight=400,
                font_size=16,
                line_height=1.5,
                semantic_role="body",
                category="text",
                name="Body",
                confidence=0.92,
            ),
        ]

        return TypographyExtractionResult(
            tokens=tokens,
            typography_palette="Inter family with 2 weights",
            extraction_confidence=0.93,
            extractor_used="AITypographyExtractor",
            color_associations=None,
        )

    async def _create_project(self):
        """Helper to create a project."""
        response = client.post(
            "/api/v1/projects",
            json={"name": "Typography Test Project", "description": "For testing"},
        )
        assert response.status_code in [200, 201]
        return response.json()["id"]
