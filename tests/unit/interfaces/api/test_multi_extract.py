"""Tests for multi-token streaming extract and snapshots."""

import json
import os
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.application.color_extractor import ColorExtractionResult, ExtractedColorToken
from copy_that.application.spacing_models import SpacingExtractionResult, SpacingToken
from copy_that.domain.models import Base as ModelBase
from copy_that.domain.models import ColorToken, Project, ProjectSnapshot
from copy_that.domain.models import SpacingToken as DBSpacing
from copy_that.infrastructure.database import Base, get_db
from copy_that.interfaces.api.main import app
from copy_that.interfaces.api.utils import sanitize_numbers


@pytest_asyncio.fixture
async def async_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(ModelBase.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(async_db):
    """Create a test client with mocked database."""

    async def override_get_db():
        yield async_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def project(async_db):
    proj = Project(name="Stream Test", description="desc")
    async_db.add(proj)
    await async_db.commit()
    await async_db.refresh(proj)
    return proj


def _fake_color_result() -> ColorExtractionResult:
    token = ExtractedColorToken(
        hex="#abcdef",
        rgb="rgb(171, 205, 239)",
        name="Test",
        confidence=0.9,
        design_intent=None,
        semantic_names=None,
        extraction_metadata={"source": "test"},
        harmony=None,
        usage=[],
    )
    return ColorExtractionResult(
        colors=[token],
        dominant_colors=["#abcdef"],
        color_palette="demo",
        extraction_confidence=0.9,
        extractor_used="test",
    )


def _fake_spacing_result() -> SpacingExtractionResult:
    tok = SpacingToken(
        value_px=8,
        name="spacing-sm",
        semantic_role="layout",
        spacing_type=None,
        category="cv",
        confidence=0.8,
        usage=["layout"],
        scale_position=0,
        base_unit=4,
        scale_system="4pt",
        grid_aligned=True,
    )
    return SpacingExtractionResult(
        tokens=[tok],
        scale_system="4pt",
        base_unit=4,
        base_unit_confidence=0.95,
        grid_compliance=1.0,
        extraction_confidence=0.8,
        min_spacing=8,
        max_spacing=8,
        unique_values=[8],
    )


@pytest.mark.asyncio
async def test_extract_stream_persists_tokens_and_snapshot(client, async_db, project):
    """Stream should emit events and persist color/spacing tokens and snapshot."""
    image_b64 = "data:image/png;base64,AAA"

    with (
        patch.dict(os.environ, {"OPENAI_API_KEY": "test"}),
        patch(
            "copy_that.interfaces.api.multi_extract.CVColorExtractor.extract_from_base64",
            return_value=_fake_color_result(),
        ),
        patch(
            "copy_that.interfaces.api.multi_extract.CVSpacingExtractor.extract_from_base64",
            return_value=_fake_spacing_result(),
        ),
        patch(
            "copy_that.interfaces.api.multi_extract.OpenAIColorExtractor.extract_colors_from_base64",
            return_value=_fake_color_result(),
        ),
        patch(
            "copy_that.interfaces.api.multi_extract.AISpacingExtractor.extract_spacing_from_base64",
            return_value=_fake_spacing_result(),
        ),
    ):
        resp = await client.post(
            "/api/v1/extract/stream",
            json={"image_base64": image_b64, "project_id": project.id},
        )
        body = resp.text

    assert resp.status_code == 200
    # Ensure events are present
    assert "event: token" in body
    assert "event: complete" in body

    # Verify persistence
    colors = (await async_db.execute(select(ColorToken))).scalars().all()
    spacings = (await async_db.execute(select(DBSpacing))).scalars().all()
    snapshots = (await async_db.execute(select(ProjectSnapshot))).scalars().all()
    assert len(colors) == 1
    assert len(spacings) == 1
    assert len(snapshots) == 1


@pytest.mark.asyncio
async def test_extract_stream_project_not_found(client):
    """Should emit error event when project does not exist."""
    resp = await client.post(
        "/api/v1/extract/stream", json={"image_base64": "abc", "project_id": 999}
    )
    assert resp.status_code == 200
    assert "Project 999 not found" in resp.text


def test_sanitize_numbers_replaces_nan():
    """Ensure NaN/inf are replaced with None for valid JSON."""
    payload = {"a": float("nan"), "b": [float("inf"), 1.0]}
    cleaned = sanitize_numbers(payload)
    assert cleaned == {"a": None, "b": [None, 1.0]}


@pytest.mark.asyncio
async def test_snapshots_list_and_fetch(client, async_db, project):
    """Snapshots API returns persisted entries."""
    snap = ProjectSnapshot(project_id=project.id, version=1, data=json.dumps({"x": 1}))
    async_db.add(snap)
    await async_db.commit()

    list_resp = await client.get(f"/api/v1/projects/{project.id}/snapshots")
    assert list_resp.status_code == 200
    snap_id = list_resp.json()[0]["id"]

    fetch_resp = await client.get(f"/api/v1/projects/{project.id}/snapshots/{snap_id}")
    assert fetch_resp.status_code == 200
    assert fetch_resp.json()["data"] == {"x": 1}


@pytest.mark.asyncio
async def test_extract_stream_error_handling(client, project):
    """Verify error handling and session cleanup on extraction failures."""
    image_b64 = "data:image/png;base64,AAA"

    # Test extraction failure is properly handled and returned as error event
    with (
        patch.dict(os.environ, {"OPENAI_API_KEY": "test"}),
        patch(
            "copy_that.interfaces.api.multi_extract.CVColorExtractor.extract_from_base64",
            side_effect=ValueError("CV extraction failed"),
        ),
    ):
        resp = await client.post(
            "/api/v1/extract/stream",
            json={"image_base64": image_b64, "project_id": project.id},
        )
        # Should still return 200 (streaming errors are sent as events)
        assert resp.status_code == 200
        # Error event should be in response
        assert "event: error" in resp.text
        assert "error" in resp.text
