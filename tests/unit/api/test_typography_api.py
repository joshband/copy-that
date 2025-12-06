"""Comprehensive tests for typography extraction API endpoints."""

import json
from unittest.mock import Mock, patch

import pytest

from copy_that.domain.models import Project, TypographyToken

# Fixtures


@pytest.fixture
async def project_with_typography(test_db):
    """Create a project with typography tokens."""
    project = Project(name="Typography Test Project", description="Test typography extraction")
    test_db.add(project)
    await test_db.flush()

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
        test_db.add(token)

    await test_db.commit()
    return project


@pytest.fixture
async def create_project(test_db):
    """Helper to create a project."""

    async def _create():
        project = Project(
            name="Typography Test Project", description=json.dumps({"text": "For testing"})
        )
        test_db.add(project)
        await test_db.flush()
        await test_db.refresh(project)
        return project

    return _create


# Extraction Tests


class TestTypographyExtraction:
    """Test typography extraction endpoint."""

    async def test_extract_typography_with_url(self, async_client, create_project):
        """Extract typography from image URL."""
        project = await create_project()

        with patch("copy_that.interfaces.api.typography.AITypographyExtractor") as mock_extractor:
            mock_ai = Mock()
            mock_ai.extract_typography_from_image_url.return_value = self._mock_extraction_result()
            mock_extractor.return_value = mock_ai

            response = await async_client.post(
                "/api/v1/typography/extract",
                json={
                    "image_url": "https://example.com/image.png",
                    "project_id": project.id,
                    "max_tokens": 10,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "typography_tokens" in data
            assert data["extractor_used"] is not None
            assert 0 <= data["extraction_confidence"] <= 1

    async def test_extract_typography_with_base64(self, async_client, create_project):
        """Extract typography from base64 image data."""
        project = await create_project()
        base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        with patch("copy_that.interfaces.api.typography.AITypographyExtractor") as mock_extractor:
            mock_ai = Mock()
            mock_ai.extract_typography_from_base64.return_value = self._mock_extraction_result()
            mock_extractor.return_value = mock_ai

            response = await async_client.post(
                "/api/v1/typography/extract",
                json={
                    "image_base64": base64_image,
                    "project_id": project.id,
                    "max_tokens": 15,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "typography_tokens" in data

    async def test_extract_typography_invalid_project(self, async_client):
        """Extract typography with non-existent project."""
        response = await async_client.post(
            "/api/v1/typography/extract",
            json={
                "image_url": "https://example.com/image.png",
                "project_id": 99999,
                "max_tokens": 10,
            },
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_extract_typography_missing_image(self, async_client, create_project):
        """Extract typography without image URL or base64."""
        project = await create_project()
        response = await async_client.post(
            "/api/v1/typography/extract",
            json={
                "project_id": project.id,
                "max_tokens": 10,
            },
        )

        assert response.status_code == 400
        assert "image" in response.json()["detail"].lower()

    # List/Get Tests

    async def test_get_project_typography_list(self, project_with_typography, async_client):
        """Get all typography tokens for a project."""
        response = await async_client.get(
            f"/api/v1/projects/{project_with_typography.id}/typography"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        assert data[0]["font_family"] is not None
        assert data[0]["font_weight"] is not None

    async def test_get_project_typography_empty(self, async_client, create_project):
        """Get typography tokens for project with none."""
        project = await create_project()
        response = await async_client.get(f"/api/v1/projects/{project.id}/typography")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_get_project_typography_invalid_project(self, async_client):
        """Get typography tokens for non-existent project."""
        response = await async_client.get("/api/v1/projects/99999/typography")

        assert response.status_code == 404

    # Create Tests

    async def test_create_typography_token(self, async_client, create_project):
        """Create a new typography token."""
        project = await create_project()
        response = await async_client.post(
            "/api/v1/typography",
            json={
                "project_id": project.id,
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

    async def test_create_typography_invalid_font_weight(self, async_client, create_project):
        """Create typography with invalid font weight."""
        project = await create_project()
        response = await async_client.post(
            "/api/v1/typography",
            json={
                "project_id": project.id,
                "font_family": "Arial",
                "font_weight": 1000,  # Invalid
                "font_size": 16,
                "line_height": 1.5,
                "semantic_role": "body",
                "confidence": 0.9,
            },
        )

        assert response.status_code == 422

    async def test_create_typography_missing_required_field(self, async_client, create_project):
        """Create typography missing required field."""
        project = await create_project()
        response = await async_client.post(
            "/api/v1/typography",
            json={
                "project_id": project.id,
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

    async def test_get_typography_token(self, project_with_typography, async_client):
        """Get a specific typography token."""
        # Get first token
        list_response = await async_client.get(
            f"/api/v1/projects/{project_with_typography.id}/typography"
        )
        token_id = list_response.json()[0]["id"]

        response = await async_client.get(f"/api/v1/typography/{token_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == token_id
        assert data["font_family"] == "Inter"

    async def test_get_typography_token_not_found(self, async_client):
        """Get non-existent typography token."""
        response = await async_client.get("/api/v1/typography/99999")

        assert response.status_code == 404

    # Update Tests

    async def test_update_typography_token(self, project_with_typography, async_client):
        """Update an existing typography token."""
        list_response = await async_client.get(
            f"/api/v1/projects/{project_with_typography.id}/typography"
        )
        token_id = list_response.json()[0]["id"]

        response = await async_client.put(
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

    async def test_update_typography_not_found(self, async_client):
        """Update non-existent typography token."""
        response = await async_client.put(
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

    async def test_delete_typography_token(self, project_with_typography, async_client):
        """Delete a typography token."""
        list_response = await async_client.get(
            f"/api/v1/projects/{project_with_typography.id}/typography"
        )
        initial_count = len(list_response.json())
        token_id = list_response.json()[0]["id"]

        response = await async_client.delete(f"/api/v1/typography/{token_id}")

        assert response.status_code == 204

        # Verify deletion
        list_after = await async_client.get(
            f"/api/v1/projects/{project_with_typography.id}/typography"
        )
        assert len(list_after.json()) == initial_count - 1

    async def test_delete_typography_not_found(self, async_client):
        """Delete non-existent typography token."""
        response = await async_client.delete("/api/v1/typography/99999")

        assert response.status_code == 404

    # Batch Tests

    async def test_batch_extract_typography(self, async_client, create_project):
        """Batch extract typography from multiple URLs."""
        project = await create_project()

        with patch("copy_that.interfaces.api.typography.AITypographyExtractor") as mock_extractor:
            mock_ai = Mock()
            mock_ai.extract_typography_from_image_url.return_value = self._mock_extraction_result()
            mock_extractor.return_value = mock_ai

            response = await async_client.post(
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

    async def test_export_typography_w3c(self, project_with_typography, async_client):
        """Export typography tokens as W3C JSON."""
        response = await async_client.get(
            f"/api/v1/typography/export/w3c?project_id={project_with_typography.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    async def test_export_typography_w3c_all(self, async_client):
        """Export all typography tokens as W3C JSON."""
        response = await async_client.get("/api/v1/typography/export/w3c")

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
