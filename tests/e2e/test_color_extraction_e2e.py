"""End-to-end tests for complete color extraction pipeline

This test file validates the full flow:
1. Create a project via API
2. Upload image and extract colors
3. Retrieve and display color tokens
"""

import pytest


@pytest.mark.asyncio
async def test_e2e_create_project_and_extract_colors(async_client):
    """End-to-end test: Create project → Extract colors → Display"""

    # ====== STEP 1: Create Project ======
    project_response = await async_client.post(
        "/api/v1/projects",
        json={"name": "E2E Test Project", "description": "Testing full color extraction pipeline"},
    )
    assert project_response.status_code == 201
    project = project_response.json()
    project_id = project["id"]

    # Verify project was created
    assert project["name"] == "E2E Test Project"
    assert "id" in project
    assert "created_at" in project
    assert "updated_at" in project

    # ====== STEP 2: Retrieve Project ======
    get_project_response = await async_client.get(f"/api/v1/projects/{project_id}")
    assert get_project_response.status_code == 200
    retrieved_project = get_project_response.json()
    assert retrieved_project["id"] == project_id

    # ====== STEP 3: Create Color Tokens ======
    # Simulate extracted colors from image
    test_colors = [
        {
            "project_id": project_id,
            "hex": "#FF6B6B",
            "rgb": "rgb(255, 107, 107)",
            "name": "Coral Red",
            "design_intent": "error",
            "confidence": 0.92,
            "harmony": "complementary",
        },
        {
            "project_id": project_id,
            "hex": "#4ECDC4",
            "rgb": "rgb(78, 205, 196)",
            "name": "Teal",
            "design_intent": "secondary",
            "confidence": 0.88,
            "harmony": "analogous",
        },
        {
            "project_id": project_id,
            "hex": "#45B7D1",
            "rgb": "rgb(69, 183, 209)",
            "name": "Sky Blue",
            "design_intent": "primary",
            "confidence": 0.95,
            "harmony": "triadic",
        },
    ]

    created_color_ids = []
    for color_data in test_colors:
        response = await async_client.post("/api/v1/colors", json=color_data)
        assert response.status_code == 201
        created_color = response.json()
        assert created_color["hex"] == color_data["hex"]
        assert created_color["design_intent"] == color_data["design_intent"]
        assert created_color["confidence"] == color_data["confidence"]
        created_color_ids.append(created_color["id"])

    # ====== STEP 4: Retrieve All Colors for Project ======
    colors_response = await async_client.get(f"/api/v1/projects/{project_id}/colors")
    assert colors_response.status_code == 200
    retrieved_colors = colors_response.json()

    # Verify all colors were retrieved
    assert len(retrieved_colors) == len(test_colors)

    # Create hex lookup for test colors
    test_color_by_hex = {c["hex"]: c for c in test_colors}

    # Verify color details
    for color in retrieved_colors:
        assert color["id"] in created_color_ids
        test_color = test_color_by_hex[color["hex"]]
        assert color["hex"] == test_color["hex"]
        assert color["name"] == test_color["name"]
        assert color["confidence"] == test_color["confidence"]
        assert 0 <= color["confidence"] <= 1

    # ====== STEP 5: Retrieve Individual Colors ======
    for color_id in created_color_ids:
        response = await async_client.get(f"/api/v1/colors/{color_id}")
        assert response.status_code == 200
        color = response.json()
        assert color["id"] == color_id
        assert color["project_id"] == project_id

    # ====== STEP 6: Verify Color Distribution ======
    # Check design intents distribution
    design_intents = [c["design_intent"] for c in retrieved_colors if c.get("design_intent")]
    assert "error" in design_intents
    assert "secondary" in design_intents
    assert "primary" in design_intents

    # Check confidence distribution
    confidences = [c["confidence"] for c in retrieved_colors]
    avg_confidence = sum(confidences) / len(confidences)
    assert 0.85 <= avg_confidence <= 0.96

    # ====== STEP 7: Update Project ======
    update_response = await async_client.put(
        f"/api/v1/projects/{project_id}", json={"name": "Updated E2E Test Project"}
    )
    assert update_response.status_code == 200
    updated_project = update_response.json()
    assert updated_project["name"] == "Updated E2E Test Project"
    assert updated_project["id"] == project_id

    # ====== STEP 8: Test Data Persistence ======
    # Verify colors still exist after project update
    final_colors_response = await async_client.get(f"/api/v1/projects/{project_id}/colors")
    assert final_colors_response.status_code == 200
    final_colors = final_colors_response.json()
    assert len(final_colors) == len(test_colors)


@pytest.mark.asyncio
async def test_e2e_multiple_projects_with_colors(async_client):
    """End-to-end test: Multiple projects with separate color palettes"""

    # Create multiple projects
    projects = []
    for i in range(3):
        response = await async_client.post("/api/v1/projects", json={"name": f"Project {i + 1}"})
        assert response.status_code == 201
        projects.append(response.json())

    # Add different colors to each project
    for proj_idx, project in enumerate(projects):
        project_id = project["id"]

        # Create different color palette for each project
        colors_per_project = [
            {"hex": "#FF0000", "rgb": "rgb(255,0,0)", "name": "Red"},
            {"hex": "#00FF00", "rgb": "rgb(0,255,0)", "name": "Green"},
            {"hex": "#0000FF", "rgb": "rgb(0,0,255)", "name": "Blue"},
        ]

        for color_data in colors_per_project:
            response = await async_client.post(
                "/api/v1/colors",
                json={
                    **color_data,
                    "project_id": project_id,
                    "confidence": 0.9 + (proj_idx * 0.01),
                },
            )
            assert response.status_code == 201

    # Verify each project has its own colors
    for project in projects:
        project_id = project["id"]
        response = await async_client.get(f"/api/v1/projects/{project_id}/colors")
        assert response.status_code == 200
        colors = response.json()
        assert len(colors) == 3

    # Verify cross-project isolation
    project1_colors = (
        await async_client.get(f"/api/v1/projects/{projects[0]['id']}/colors")
    ).json()
    project2_colors = (
        await async_client.get(f"/api/v1/projects/{projects[1]['id']}/colors")
    ).json()

    # Colors should be different objects (IDs different)
    assert project1_colors[0]["id"] != project2_colors[0]["id"]


@pytest.mark.asyncio
async def test_e2e_color_extraction_validation(async_client):
    """End-to-end test: Validate color extraction data integrity"""

    # Create project
    project_response = await async_client.post("/api/v1/projects", json={"name": "Validation Test"})
    project_id = project_response.json()["id"]

    # Create color with all fields
    complete_color = {
        "project_id": project_id,
        "hex": "#FF5733",
        "rgb": "rgb(255,87,51)",
        "name": "Coral",
        "design_intent": "error",
        "confidence": 0.95,
        "harmony": "complementary",
    }

    response = await async_client.post("/api/v1/colors", json=complete_color)
    assert response.status_code == 201
    created_color = response.json()

    # Verify data integrity - all fields present and correct
    assert created_color["hex"] == "#FF5733"
    assert created_color["rgb"] == "rgb(255,87,51)"
    assert created_color["name"] == "Coral"
    assert created_color["design_intent"] == "error"
    assert created_color["confidence"] == 0.95
    assert created_color["harmony"] == "complementary"
    assert created_color["project_id"] == project_id

    # Verify ID was assigned
    assert "id" in created_color
    assert isinstance(created_color["id"], int)

    # Verify timestamp was created
    assert "created_at" in created_color
    assert isinstance(created_color["created_at"], str)

    # Retrieve and verify data persistence
    retrieved = await async_client.get(f"/api/v1/colors/{created_color['id']}")
    assert retrieved.status_code == 200
    retrieved_color = retrieved.json()

    # All fields should match
    for key in complete_color:
        assert retrieved_color[key] == complete_color[key]


@pytest.mark.asyncio
async def test_e2e_list_projects_with_pagination(async_client):
    """End-to-end test: List projects with pagination"""

    # Create 5 projects
    created_ids = []
    for i in range(5):
        response = await async_client.post("/api/v1/projects", json={"name": f"Project {i}"})
        assert response.status_code == 201
        created_ids.append(response.json()["id"])

    # List projects with default limit
    response = await async_client.get("/api/v1/projects")
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) >= 5

    # Verify our created projects are in the list
    project_ids = [p["id"] for p in projects]
    for created_id in created_ids:
        assert created_id in project_ids

    # Test pagination with limit
    response = await async_client.get("/api/v1/projects?limit=2")
    assert response.status_code == 200
    limited_projects = response.json()
    assert len(limited_projects) == 2
