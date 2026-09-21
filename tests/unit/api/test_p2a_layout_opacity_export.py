"""P2a: layout/shape persist + W3C/CSS export + opacity synthesis."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.core_tokens.adapters.w3c import tokens_to_w3c_flat
from copy_that.core_tokens.model import Token, TokenType
from copy_that.domain.layout_tokens import LayoutTokenCreate
from copy_that.generators.plugins.css import CSSGenerator
from copy_that.infrastructure.database import Base, get_db
from copy_that.infrastructure.persistence.models import LayoutToken, Project, ShadowToken
from copy_that.infrastructure.persistence.repositories.layout_tokens import (
    SQLAlchemyLayoutTokenRepository,
)
from copy_that.interfaces.api.main import app
from copy_that.services.layout_service import (
    db_layout_to_repo,
    synthesize_opacity_tokens_from_shadows,
    tokens_to_creates,
)


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

    previous_overrides = dict(app.dependency_overrides)
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous_overrides)


@pytest_asyncio.fixture
async def project(async_db):
    p = Project(name="P2a Layout Project", description="layout + opacity")
    async_db.add(p)
    await async_db.commit()
    await async_db.refresh(p)
    return p


def test_tokens_to_creates_from_shape_tokens():
    tokens = [
        Token(
            id="token/layout/radius/1",
            type=TokenType.LAYOUT,
            value={"radius": 8},
            attributes={"role": "corner_radius"},
        ),
        Token(
            id="token/layout/border/1",
            type=TokenType.LAYOUT,
            value={"border": {"width": 2}},
            attributes={"role": "border_width"},
        ),
    ]
    creates = tokens_to_creates(tokens)
    assert len(creates) == 2
    roles = {c.role for c in creates}
    assert roles == {"corner_radius", "border_width"}
    by_role = {c.role: c for c in creates}
    assert by_role["corner_radius"].value_px == 8
    assert by_role["border_width"].value_px == 2


def test_db_layout_to_repo_round_trips_w3c_layout():
    class Row:
        name = "radius-1"
        role = "corner_radius"
        value_px = 12.0
        value_json = '{"radius": 12}'
        confidence = 0.9

    class BorderRow:
        name = "border-1"
        role = "border_width"
        value_px = 1.0
        value_json = '{"border": {"width": 1}}'
        confidence = 0.85

    repo = db_layout_to_repo([Row(), BorderRow()], namespace="token/layout/test")
    exported = tokens_to_w3c_flat(repo)
    assert "layout" in exported
    radius_entry = next(v for k, v in exported["layout"].items() if "radius" in k)
    assert radius_entry["$type"] == "layout"
    assert radius_entry["$value"]["radius"]["value"] == 12
    border_entry = next(v for k, v in exported["layout"].items() if "border" in k)
    assert border_entry["$value"]["border"]["width"]["value"] == 1


def test_synthesize_opacity_from_shadows():
    class Shadow:
        opacity = 0.25
        semantic_role = "soft"
        name = "shadow.1"

    class Shadow2:
        opacity = 0.25  # duplicate
        semantic_role = "soft"
        name = "shadow.2"

    class Shadow3:
        opacity = 0.6
        semantic_role = "medium"
        name = "shadow.3"

    tokens = synthesize_opacity_tokens_from_shadows([Shadow(), Shadow2(), Shadow3()])
    assert len(tokens) == 2
    values = sorted(float(t.value) for t in tokens)
    assert values == [0.25, 0.6]
    assert all(t.attributes.get("$type") == "number" for t in tokens)
    assert all(str(t.id).startswith("opacity.") for t in tokens)


def test_css_emits_layout_radius_border_and_opacity():
    tokens = {
        "layout": {
            "token/layout/radius/1": {
                "$type": "layout",
                "$value": {"radius": {"value": 8, "unit": "px"}},
                "role": "corner_radius",
            },
            "token/layout/border/1": {
                "$type": "layout",
                "$value": {"border": {"width": {"value": 2, "unit": "px"}}},
                "role": "border_width",
            },
        },
        "opacity": {
            "opacity.shadow-soft": {"$type": "number", "$value": 0.25},
        },
    }
    css = CSSGenerator(tokens=tokens).generate()
    assert "/* Layout / shape */" in css
    assert "8px" in css
    assert "2px" in css
    assert "radius" in css
    assert "border-width" in css
    assert "/* Opacity */" in css
    assert "--opacity-shadow-soft: 0.25;" in css


@pytest.mark.asyncio
async def test_layout_tokens_persist_and_appear_in_w3c_export(client, async_db, project):
    repo = SQLAlchemyLayoutTokenRepository(async_db)
    await repo.record_extraction(
        project_id=project.id,
        extraction_job_id=None,
        tokens=[
            LayoutTokenCreate(
                name="radius-1",
                role="corner_radius",
                value_px=10,
                value_json='{"radius": 10}',
                confidence=0.9,
            ),
            LayoutTokenCreate(
                name="border-1",
                role="border_width",
                value_px=2,
                value_json='{"border": {"width": 2}}',
                confidence=0.85,
            ),
        ],
    )

    shadow = ShadowToken(
        project_id=project.id,
        x_offset=0,
        y_offset=4,
        blur_radius=8,
        spread_radius=0,
        color_hex="#000000",
        opacity=0.35,
        name="shadow.card",
        shadow_type="drop",
        semantic_role="soft",
        confidence=0.9,
    )
    async_db.add(shadow)
    await async_db.commit()

    resp = await client.get(
        "/api/v1/design-tokens/export/w3c",
        params={"project_id": project.id},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "layout" in data
    layout_values = list(data["layout"].values())
    assert any(
        e.get("$value", {}).get("radius", {}).get("value") == 10
        or e.get("value", {}).get("radius", {}).get("value") == 10
        for e in layout_values
    )
    assert "opacity" in data
    opacity_entry = next(iter(data["opacity"].values()))
    assert opacity_entry["$type"] == "number"
    assert opacity_entry.get("$value", opacity_entry.get("value")) == pytest.approx(0.35)

    css_resp = await client.get(
        "/api/v1/design-tokens/export/css",
        params={"project_id": project.id},
    )
    assert css_resp.status_code == 200
    css = css_resp.json()["content"]
    assert "10px" in css
    assert "2px" in css
    assert "0.35" in css


@pytest.mark.asyncio
async def test_layout_token_model_create_all(async_db, project):
    row = LayoutToken(
        project_id=project.id,
        name="radius-x",
        role="corner_radius",
        value_px=6,
        value_json='{"radius": 6}',
        confidence=0.8,
    )
    async_db.add(row)
    await async_db.commit()
    await async_db.refresh(row)
    assert row.id is not None
