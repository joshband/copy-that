"""API contract tests for shadow multi-extractor endpoint."""

from __future__ import annotations

import base64
from io import BytesIO

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.infrastructure.database import Base, get_db
from copy_that.infrastructure.persistence.models import Project
from copy_that.interfaces.api.main import app


@pytest_asyncio.fixture
async def async_db():
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
    async def override_get_db():
        yield async_db

    previous = dict(app.dependency_overrides)
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


@pytest_asyncio.fixture
async def test_project(async_db):
    project = Project(name="Shadow Multi", description="multi extract")
    async_db.add(project)
    await async_db.commit()
    await async_db.refresh(project)
    return project


@pytest.fixture
def tiny_png_b64():
    img = Image.new("RGB", (16, 16), color="black")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


@pytest.mark.asyncio
async def test_shadows_extract_multi_endpoint_exists(client, test_project, tiny_png_b64):
    resp = await client.post(
        "/api/v1/shadows/extract/multi",
        json={"image_base64": tiny_png_b64, "project_id": test_project.id, "max_tokens": 10},
    )
    assert resp.status_code != 404
    assert resp.status_code in (200, 401, 422, 500)
    if resp.status_code == 200:
        body = resp.json()
        assert "tokens" in body
        assert body.get("extractor_used") == "multi-extractor-orchestrator"
