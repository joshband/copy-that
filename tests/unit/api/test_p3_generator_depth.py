"""P3: CSS depth, React theme, Tailwind generator + export endpoints."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.generators.plugins.css import CSSGenerator
from copy_that.generators.plugins.react import ReactGenerator
from copy_that.generators.plugins.tailwind import TailwindGenerator
from copy_that.infrastructure.database import Base, get_db
from copy_that.infrastructure.persistence.models import ColorToken, Project, SpacingToken
from copy_that.interfaces.api.main import app

SAMPLE_TOKENS = {
    "color": {
        "color.primary": {"$type": "color", "$value": "#112233", "hex": "#112233"},
    },
    "spacing": {
        "spacing.md": {
            "$type": "dimension",
            "$value": {"value": 16, "unit": "px"},
            "value_rem": 1.0,
        },
        "spacing.lg": {
            "$type": "dimension",
            "$value": {"value": 1.5, "unit": "rem"},
        },
    },
    "typography": {
        "typography.body": {
            "$type": "typography",
            "$value": {
                "fontFamily": "Inter",
                "fontSize": {"value": 16, "unit": "px"},
                "fontWeight": 500,
                "fontStyle": "normal",
                "lineHeight": {"value": 24, "unit": "px"},
                "letterSpacing": {"value": 0.01, "unit": "em"},
                "textAlign": "left",
            },
        },
        "typography.alias": {
            "$type": "typography",
            "$value": {
                "fontFamily": "{font.family.primary}",
                "fontSize": {"value": 14, "unit": "px"},
                "fontWeight": 400,
            },
        },
    },
    "shadow": {
        "shadow.card": {
            "$type": "shadow",
            "$value": [
                {
                    "color": "{color.shadow}",
                    "x": {"value": 0, "unit": "px"},
                    "y": {"value": 4, "unit": "px"},
                    "blur": {"value": 8, "unit": "px"},
                    "spread": {"value": 0, "unit": "px"},
                },
                {
                    "color": "#000000",
                    "x": 0,
                    "y": 2,
                    "blur": 4,
                    "spread": 0,
                    "inset": True,
                },
            ],
        },
    },
    "layout": {
        "token/layout/radius/1": {
            "$type": "layout",
            "$value": {"radius": {"value": 8, "unit": "px"}},
            "role": "corner_radius",
        },
    },
    "gradient": {
        "gradient.brand": {
            "$type": "gradient",
            "$value": {
                "angle": 90,
                "stops": [
                    {"color": "#112233", "position": 0},
                    {"color": "#445566", "position": 1},
                ],
            },
        },
    },
    "opacity": {
        "opacity.muted": {"$type": "number", "$value": 0.6},
    },
    "duration": {
        "duration.fast": {"$type": "duration", "$value": {"value": 150, "unit": "ms"}},
    },
    "cubicBezier": {
        "cubicBezier.ease": {"$type": "cubicBezier", "$value": [0.25, 0.1, 0.25, 1]},
    },
}


def test_css_emits_typography_depth_and_multi_layer_shadow():
    css = CSSGenerator(tokens=SAMPLE_TOKENS).generate()

    assert "--typography-body-font-weight: 500;" in css
    assert "--typography-body-line-height: 24px;" in css
    assert "--typography-body-font-style: normal;" in css
    assert "--typography-body-letter-spacing: 0.01em;" in css
    assert "--typography-body-text-align: left;" in css
    assert "--typography-body-font-family: Inter;" in css
    # Brace aliases skipped
    assert "{font.family.primary}" not in css
    assert "--typography-alias-font-family" not in css
    assert "--typography-alias-font-weight: 400;" in css

    # Spacing: px primary + rem companion; rem-preferring when unit is rem
    assert "--spacing-md: 16px;" in css
    assert "--spacing-md-rem: 1.0rem;" in css
    assert "--spacing-lg: 1.5rem;" in css

    # Multi-layer shadow with brace-ref color fallback
    assert "/* Shadows */" in css
    shadow_line = next(line for line in css.splitlines() if "--shadow-card:" in line)
    assert "," in shadow_line
    assert "rgba(0,0,0,0.2)" in shadow_line
    assert "inset" in shadow_line
    assert "#000000" in shadow_line


def test_react_theme_contains_keys_and_no_undefined():
    content = ReactGenerator(tokens=SAMPLE_TOKENS).generate()

    assert "export const theme = {" in content
    assert "export const tokens = theme;" in content
    assert "colors:" in content
    assert "spacing:" in content
    # Section prefixes stripped for theme object keys
    assert "'primary'" in content
    assert "'md'" in content
    assert "'card'" in content
    # CSS vars keep full slug names aligned with CSS export
    assert "export const cssVars" in content
    assert "'--color-primary'" in content
    assert "'--spacing-md'" in content
    assert "export function ThemeProvider" in content
    assert "export function useTheme" in content
    assert "createContext" in content
    assert "undefined" not in content
    assert "export async function loadTokens()" in content
    assert "designTokens = tokens" not in content


def test_tailwind_contains_theme_extend():
    content = TailwindGenerator(tokens=SAMPLE_TOKENS).generate()

    assert "theme: {" in content
    assert "extend: {" in content
    assert "colors:" in content
    assert "spacing:" in content
    assert "borderRadius:" in content
    assert "boxShadow:" in content
    assert "backgroundImage:" in content
    assert "fontSize:" in content
    assert "opacity:" in content
    assert "transitionDuration:" in content
    assert "transitionTimingFunction:" in content
    assert "cubic-bezier(" in content
    # Cleaner keys (no redundant section prefix)
    assert "'primary'" in content
    assert "'md'" in content
    assert "'card'" in content
    assert "'body'" in content
    assert "linear-gradient(" in content
    assert "'muted'" in content


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
    p = Project(name="P3 Generator Project", description="react + tailwind export")
    async_db.add(p)
    await async_db.commit()
    await async_db.refresh(p)
    return p


@pytest.mark.asyncio
async def test_export_react_and_tailwind_asgi(client, async_db, project):
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

    react_resp = await client.get(
        "/api/v1/design-tokens/export/react",
        params={"project_id": project.id},
    )
    assert react_resp.status_code == 200
    react_data = react_resp.json()
    assert react_data["format"] == "react"
    assert react_data["filename"] == "tokens.theme.ts"
    assert "export const theme" in react_data["content"]
    assert "ThemeProvider" in react_data["content"]
    assert "cssVars" in react_data["content"]
    assert "undefined" not in react_data["content"]

    tw_resp = await client.get(
        "/api/v1/design-tokens/export/tailwind",
        params={"project_id": project.id},
    )
    assert tw_resp.status_code == 200
    tw_data = tw_resp.json()
    assert tw_data["format"] == "tailwind"
    assert tw_data["filename"] == "tailwind.theme.js"
    assert "theme.extend" in tw_data["content"].replace("\n", " ").replace(" ", "") or (
        "extend: {" in tw_data["content"]
    )
    assert "boxShadow:" in tw_data["content"] or "colors:" in tw_data["content"]
