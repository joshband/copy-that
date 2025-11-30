"""Contract tests for W3C export endpoints and design_tokens payloads."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.application.color_extractor import ColorExtractionResult, ExtractedColorToken
from copy_that.domain.models import Base, ColorToken, Project, SpacingToken
from copy_that.infrastructure.database import get_db
from copy_that.interfaces.api.main import app
from copy_that.services.colors_service import result_to_response


@pytest_asyncio.fixture
async def async_db():
    """Create an in-memory SQLite database for API contract tests."""
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
    """ASGI test client backed by the in-memory DB."""

    async def override_get_db():
        yield async_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def project(async_db):
    """Seed a project for token association."""
    p = Project(name="W3C Export Project", description="For W3C export contract tests")
    async_db.add(p)
    await async_db.commit()
    await async_db.refresh(p)
    return p


@pytest.mark.asyncio
async def test_export_colors_w3c_shape(client, async_db, project):
    """Ensure /colors/export/w3c returns W3C-shaped color tokens."""
    color = ColorToken(
        project_id=project.id,
        hex="#112233",
        rgb="rgb(17, 34, 51)",
        name="Primary",
        confidence=0.9,
    )
    async_db.add(color)
    await async_db.commit()

    resp = await client.get("/api/v1/colors/export/w3c", params={"project_id": project.id})
    assert resp.status_code == 200
    data = resp.json()
    assert "color" in data
    entry = next(iter(data["color"].values()))
    assert entry["$type"] == "color"
    assert entry["value"]["space"] == "oklch"
    assert {"l", "c", "h"} <= set(entry["value"].keys())


@pytest.mark.asyncio
async def test_export_spacing_w3c_shape(client, async_db, project):
    """Ensure /spacing/export/w3c returns W3C-shaped spacing tokens."""
    spacing = SpacingToken(
        project_id=project.id,
        value_px=8,
        name="spacing-xxs",
        semantic_role="layout",
        category="cv",
        confidence=0.8,
    )
    async_db.add(spacing)
    await async_db.commit()

    resp = await client.get("/api/v1/spacing/export/w3c", params={"project_id": project.id})
    assert resp.status_code == 200
    data = resp.json()
    assert "spacing" in data
    entry = next(iter(data["spacing"].values()))
    assert entry["$type"] == "dimension"
    assert isinstance(entry["value"], dict)
    assert entry["value"]["unit"] == "px"
    assert entry["value"]["value"] == 8
    assert entry.get("rem") == pytest.approx(0.5)


@pytest.mark.asyncio
async def test_design_tokens_export_combines_sections(client, async_db, project):
    """Combined design token export should return color, spacing, and typography sections."""
    color = ColorToken(
        project_id=project.id,
        hex="#112233",
        rgb="rgb(17, 34, 51)",
        name="Primary",
        confidence=0.9,
        temperature="warm",
        saturation_level="high",
    )
    spacing = SpacingToken(
        project_id=project.id,
        value_px=8,
        name="spacing-xxs",
        semantic_role="layout",
        category="cv",
        confidence=0.8,
    )
    async_db.add_all([color, spacing])
    await async_db.commit()

    resp = await client.get(
        "/api/v1/design-tokens/export/w3c",
        params={"project_id": project.id, "style_hint": "minimalist"},
    )
    assert resp.status_code == 200
    data = resp.json()

    assert "color" in data and "spacing" in data and "typography" in data
    assert "color.text.primary" in data["color"]
    spacing_entry = next(iter(data["spacing"].values()))
    assert spacing_entry["$type"] == "dimension"
    typo_entry = data["typography"]["typography.body"]
    assert typo_entry["$type"] == "typography"
    assert typo_entry["$value"]["fontFamily"][0].startswith("{font.family.")
    assert data.get("meta", {}).get("typography_recommendation", {}).get("confidence") is not None


def test_design_tokens_present_in_color_response():
    """Ensure service response carries design_tokens derived from repo."""
    token = ExtractedColorToken(
        hex="#445566",
        rgb="rgb(68, 85, 102)",
        name="Accent",
        confidence=0.7,
        usage=[],
    )
    result = ColorExtractionResult(
        colors=[token],
        dominant_colors=["#445566"],
        color_palette="test",
        extraction_confidence=0.7,
        extractor_used="test",
    )

    payload = result_to_response(result, namespace="token/color/test")
    assert "design_tokens" in payload
    dt = payload["design_tokens"]
    assert "color" in dt
    entry = next(iter(dt["color"].values()))
    assert entry["$type"] == "color"
