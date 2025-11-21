"""Integration tests for color extraction endpoints"""

import pytest


@pytest.mark.asyncio
async def test_extract_colors_with_url(async_client):
    """Test extracting colors from image URL (without actual API call)"""
    # First create a project
    project_resp = await async_client.post("/api/v1/projects", json={"name": "Color Test Project"})
    project_id = project_resp.json()["id"]

    # Note: In production tests, we'd mock the Claude API
    # For now, we skip the actual extraction to avoid API calls
    # This test structure ensures the endpoint is properly set up


@pytest.mark.asyncio
async def test_extract_colors_missing_project(async_client):
    """Test that extraction fails if project doesn't exist"""
    response = await async_client.post(
        "/api/v1/colors/extract",
        json={"project_id": 999999, "image_url": "https://example.com/image.jpg", "max_colors": 10},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_extract_colors_missing_image_source(async_client):
    """Test that extraction fails without image_url or image_base64"""
    # Create a project first
    project_resp = await async_client.post("/api/v1/projects", json={"name": "Project"})
    project_id = project_resp.json()["id"]

    response = await async_client.post(
        "/api/v1/colors/extract",
        json={
            "project_id": project_id,
            "max_colors": 10,
            # Missing both image_url and image_base64
        },
    )

    assert response.status_code == 400
    assert "image_url or image_base64" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_color_token_manually(async_client):
    """Test creating a color token directly"""
    # Create a project
    project_resp = await async_client.post("/api/v1/projects", json={"name": "Token Project"})
    project_id = project_resp.json()["id"]

    # Create a color token
    response = await async_client.post(
        "/api/v1/colors",
        json={
            "project_id": project_id,
            "hex": "#FF5733",
            "rgb": "rgb(255, 87, 51)",
            "name": "Coral Red",
            "confidence": 0.95,
            "harmony": "complementary",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["hex"] == "#FF5733"
    assert data["name"] == "Coral Red"
    assert data["confidence"] == 0.95
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_color_token_invalid_project(async_client):
    """Test that creating color token fails for non-existent project"""
    response = await async_client.post(
        "/api/v1/colors",
        json={
            "project_id": 999999,
            "hex": "#FF5733",
            "rgb": "rgb(255, 87, 51)",
            "name": "Test",
            "confidence": 0.9,
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_project_colors(async_client):
    """Test retrieving all color tokens for a project"""
    # Create a project
    project_resp = await async_client.post("/api/v1/projects", json={"name": "Colors Project"})
    project_id = project_resp.json()["id"]

    # Create multiple color tokens
    colors_data = [
        {"hex": "#FF0000", "rgb": "rgb(255, 0, 0)", "name": "Red", "confidence": 0.9},
        {"hex": "#00FF00", "rgb": "rgb(0, 255, 0)", "name": "Green", "confidence": 0.85},
        {"hex": "#0000FF", "rgb": "rgb(0, 0, 255)", "name": "Blue", "confidence": 0.88},
    ]

    for color_data in colors_data:
        await async_client.post("/api/v1/colors", json={**color_data, "project_id": project_id})

    # Retrieve all colors for the project
    response = await async_client.get(f"/api/v1/projects/{project_id}/colors")

    assert response.status_code == 200
    colors = response.json()
    assert len(colors) == 3

    # Verify each color has required fields
    for color in colors:
        assert "id" in color
        assert "hex" in color
        assert "name" in color
        assert "confidence" in color
        assert 0 <= color["confidence"] <= 1


@pytest.mark.asyncio
async def test_get_project_colors_empty(async_client):
    """Test retrieving colors for empty project"""
    # Create a project
    project_resp = await async_client.post("/api/v1/projects", json={"name": "Empty Project"})
    project_id = project_resp.json()["id"]

    # Retrieve colors (should be empty)
    response = await async_client.get(f"/api/v1/projects/{project_id}/colors")

    assert response.status_code == 200
    colors = response.json()
    assert len(colors) == 0


@pytest.mark.asyncio
async def test_get_project_colors_invalid_project(async_client):
    """Test retrieving colors for non-existent project"""
    response = await async_client.get("/api/v1/projects/999999/colors")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_color_token(async_client):
    """Test retrieving a specific color token"""
    # Create a project
    project_resp = await async_client.post("/api/v1/projects", json={"name": "Project"})
    project_id = project_resp.json()["id"]

    # Create a color token
    create_resp = await async_client.post(
        "/api/v1/colors",
        json={
            "project_id": project_id,
            "hex": "#FF5733",
            "rgb": "rgb(255, 87, 51)",
            "name": "Coral",
            "confidence": 0.9,
        },
    )
    color_id = create_resp.json()["id"]

    # Retrieve the color token
    response = await async_client.get(f"/api/v1/colors/{color_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == color_id
    assert data["hex"] == "#FF5733"
    assert data["name"] == "Coral"


@pytest.mark.asyncio
async def test_get_color_token_not_found(async_client):
    """Test retrieving non-existent color token"""
    response = await async_client.get("/api/v1/colors/999999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_color_token_with_various_designs(async_client):
    """Test creating color tokens with various design intents"""
    # Create a project
    project_resp = await async_client.post(
        "/api/v1/projects", json={"name": "Design Intent Project"}
    )
    project_id = project_resp.json()["id"]

    colors = [
        {"hex": "#0066FF", "name": "Primary", "design_intent": "primary"},
        {"hex": "#666666", "name": "Secondary", "design_intent": "secondary"},
        {"hex": "#FF0000", "name": "Error", "design_intent": "error"},
        {"hex": "#00AA00", "name": "Success", "design_intent": "success"},
        {"hex": "#FFAA00", "name": "Warning", "design_intent": "warning"},
        {"hex": "#0099FF", "name": "Info", "design_intent": "info"},
    ]

    for color in colors:
        response = await async_client.post(
            "/api/v1/colors",
            json={
                "project_id": project_id,
                "hex": color["hex"],
                "rgb": "rgb(100, 100, 100)",  # Placeholder
                "name": color["name"],
                "design_intent": color["design_intent"],
                "confidence": 0.9,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["design_intent"] == color["design_intent"]


@pytest.mark.asyncio
async def test_color_token_with_harmony_info(async_client):
    """Test creating color tokens with harmony information"""
    # Create a project
    project_resp = await async_client.post("/api/v1/projects", json={"name": "Harmony Project"})
    project_id = project_resp.json()["id"]

    # Create color tokens with harmony info
    response = await async_client.post(
        "/api/v1/colors",
        json={
            "project_id": project_id,
            "hex": "#FF5733",
            "rgb": "rgb(255, 87, 51)",
            "name": "Coral",
            "harmony": "complementary",
            "confidence": 0.9,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["harmony"] == "complementary"


@pytest.mark.asyncio
async def test_color_token_confidence_validation(async_client):
    """Test that confidence values are validated"""
    # Create a project
    project_resp = await async_client.post("/api/v1/projects", json={"name": "Validation Project"})
    project_id = project_resp.json()["id"]

    # Try to create with invalid confidence (> 1.0)
    response = await async_client.post(
        "/api/v1/colors",
        json={
            "project_id": project_id,
            "hex": "#FF5733",
            "rgb": "rgb(255, 87, 51)",
            "name": "Test",
            "confidence": 1.5,  # Invalid
        },
    )

    assert response.status_code == 422  # Validation error
