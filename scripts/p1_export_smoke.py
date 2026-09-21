"""P1 smoke: project → (seed or extract) → export w3c + css files."""

from __future__ import annotations

import asyncio
import base64
import io
import os
import sys
from pathlib import Path

# Ensure src on path
ROOT = Path(os.environ.get("COPY_THAT_ROOT", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT / "src"))

os.environ.setdefault("ENVIRONMENT", "local")
os.environ.setdefault("SECRET_KEY", "dev-smoke-secret-key-not-for-prod")
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{ROOT / 'copy_that_smoke.db'}")

from httpx import ASGITransport, AsyncClient
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.infrastructure.database import Base, get_db
from copy_that.infrastructure.persistence.models import ColorToken, SpacingToken
from copy_that.interfaces.api.main import app


async def main() -> int:
    out_dir = ROOT / "tmp_smoke_exports"
    out_dir.mkdir(exist_ok=True)
    db_path = ROOT / "copy_that_smoke.db"
    if db_path.exists():
        db_path.unlink()

    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with AsyncSession(engine, expire_on_commit=False) as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1) Create project
        resp = await client.post(
            "/api/v1/projects", json={"name": "P1 Smoke", "description": "export smoke"}
        )
        print("create project", resp.status_code, resp.text[:200])
        resp.raise_for_status()
        project_id = resp.json()["id"]

        used_extract = False
        openai = os.getenv("OPENAI_API_KEY")
        anthropic = os.getenv("ANTHROPIC_API_KEY")

        if openai or anthropic:
            # Real-ish extract with a tiny PNG
            img = Image.new("RGB", (64, 64), color=(220, 40, 40))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            # streaming extract
            async with client.stream(
                "POST",
                "/api/v1/colors/extract-streaming",
                json={"project_id": project_id, "image_base64": b64, "max_colors": 5},
                timeout=120.0,
            ) as stream:
                print("extract stream", stream.status_code)
                body = ""
                async for chunk in stream.aiter_text():
                    body += chunk
                print("extract bytes", len(body))
                print(body[:500])
            used_extract = stream.status_code == 200
            # also fire spacing (may fail without CV deps — ok)
            spacing = await client.post(
                "/api/v1/spacing/extract",
                json={
                    "image_base64": b64,
                    "image_media_type": "image/png",
                    "project_id": project_id,
                    "max_tokens": 5,
                },
                timeout=60.0,
            )
            print("spacing", spacing.status_code, spacing.text[:200])
        else:
            print("NO_API_KEYS — seeding tokens to validate export downloads")
            async with AsyncSession(engine, expire_on_commit=False) as session:
                session.add_all(
                    [
                        ColorToken(
                            project_id=project_id,
                            hex="#DC2828",
                            rgb="rgb(220, 40, 40)",
                            name="Smoke Red",
                            confidence=0.9,
                        ),
                        SpacingToken(
                            project_id=project_id,
                            value_px=8,
                            name="spacing-sm",
                            semantic_role="layout",
                            category="cv",
                            confidence=0.8,
                        ),
                    ]
                )
                await session.commit()

        # 2) Export W3C + CSS
        w3c = await client.get(
            "/api/v1/design-tokens/export/w3c", params={"project_id": project_id}
        )
        css = await client.get(
            "/api/v1/design-tokens/export/css", params={"project_id": project_id}
        )
        print("w3c", w3c.status_code)
        print("css", css.status_code)
        w3c.raise_for_status()
        css.raise_for_status()
        w3c_path = out_dir / f"project-{project_id}.tokens.json"
        css_path = out_dir / f"project-{project_id}.tokens.css"
        w3c_path.write_text(w3c.text if False else __import__("json").dumps(w3c.json(), indent=2))
        css_json = css.json()
        css_path.write_text(css_json["content"])
        print("WROTE", w3c_path, "bytes", w3c_path.stat().st_size)
        print("WROTE", css_path, "bytes", css_path.stat().st_size)
        print("CSS_HAS_ROOT", ":root" in css_json["content"])
        print("USED_EXTRACT", used_extract)
        print("SMOKE_OK")
        return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
