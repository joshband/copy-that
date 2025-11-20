"""Integration tests for project management endpoints"""

import pytest


@pytest.mark.asyncio
async def test_create_project(async_client):
    """Test creating a project"""
    response = await async_client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "description": "A test project"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A test project"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_projects(async_client):
    """Test listing projects"""
    # Create a project first
    create_resp = await async_client.post(
        "/api/v1/projects",
        json={"name": "Project 1"}
    )
    project_id = create_resp.json()["id"]

    # List projects
    response = await async_client.get("/api/v1/projects")

    assert response.status_code == 200
    projects = response.json()
    assert len(projects) >= 1
    assert any(p["id"] == project_id for p in projects)


@pytest.mark.asyncio
async def test_get_project(async_client):
    """Test getting a single project"""
    # Create a project first
    create_resp = await async_client.post(
        "/api/v1/projects",
        json={"name": "Get Test Project", "description": "For GET test"}
    )
    project_id = create_resp.json()["id"]

    # Get the project
    response = await async_client.get(f"/api/v1/projects/{project_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Get Test Project"
    assert data["description"] == "For GET test"


@pytest.mark.asyncio
async def test_get_project_not_found(async_client):
    """Test getting a non-existent project"""
    response = await async_client.get("/api/v1/projects/999999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_project(async_client):
    """Test updating a project"""
    # Create a project
    create_resp = await async_client.post(
        "/api/v1/projects",
        json={"name": "Original Name", "description": "Original description"}
    )
    project_id = create_resp.json()["id"]

    # Update it
    response = await async_client.put(
        f"/api/v1/projects/{project_id}",
        json={"name": "Updated Name"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["id"] == project_id
    # Description should remain unchanged
    assert data["description"] == "Original description"


@pytest.mark.asyncio
async def test_delete_project(async_client):
    """Test deleting a project"""
    # Create a project
    create_resp = await async_client.post(
        "/api/v1/projects",
        json={"name": "To Delete"}
    )
    project_id = create_resp.json()["id"]

    # Delete it
    response = await async_client.delete(f"/api/v1/projects/{project_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await async_client.get(f"/api/v1/projects/{project_id}")
    assert get_resp.status_code == 404
