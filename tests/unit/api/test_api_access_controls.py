"""API access policy tests using in-memory users; no broker or provider calls."""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.infrastructure.database import Base, get_db
from copy_that.infrastructure.persistence.models import User
from copy_that.infrastructure.security import rate_limiter
from copy_that.infrastructure.security.authentication import (
    create_access_token,
    create_refresh_token,
)
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.app_factory import config, create_app

BODY = {"colors": [{"hex": "#2171B5"}], "include_images": False}
PARKED_PATHS = ("/api/v1/sessions", "/api/v1/batch/enqueue", "/api/v1/extract/stream")


@pytest.fixture
async def policy_app(monkeypatch: pytest.MonkeyPatch):
    # Configuration validation is orthogonal to route access; DB stays in memory.
    monkeypatch.setattr(config, "validate_required", lambda: None)
    monkeypatch.setenv("ENVIRONMENT", "local")
    monkeypatch.delenv("ENABLE_PARKED_ROUTERS", raising=False)
    monkeypatch.delenv("CELERY_BROKER_URL", raising=False)
    app = create_app()
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine, expire_on_commit=False) as db:
        db.add_all(
            [
                User(
                    id="active",
                    email="active@example.com",
                    hashed_password="unused",
                    is_active=True,
                ),
                User(
                    id="disabled",
                    email="disabled@example.com",
                    hashed_password="unused",
                    is_active=False,
                ),
                User(
                    id="other",
                    email="other@example.com",
                    hashed_password="unused",
                    is_active=True,
                ),
            ]
        )
        await db.commit()

        async def override_db():
            yield db

        app.dependency_overrides[get_db] = override_db
        yield app
    await engine.dispose()


@pytest.mark.parametrize("enabled", ["true", "false"])
async def test_parked_routes_configurable(
    policy_app: FastAPI, monkeypatch: pytest.MonkeyPatch, enabled: str
) -> None:
    monkeypatch.setenv("ENABLE_PARKED_ROUTERS", enabled)
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        schema = (await client.get("/openapi.json")).json()["paths"]
        catalog = (await client.get("/api/v1/docs")).json()["endpoints"]
        for path in PARKED_PATHS:
            assert (path in schema) == (enabled == "true")
            if enabled == "false":
                response = await client.post(path, json={})
                assert response.status_code == 404
        for area in ("sessions", "multi_extract"):
            assert (area in catalog) == (enabled == "true")
        # Mood depends on jobs even when other parked surfaces are unmounted.
        assert "/api/v1/jobs/{job_id}" in schema
        assert "/api/v1/mood-board/generate" in schema
        assert "/api/v1/colors/extract" in schema


@pytest.mark.parametrize(
    "environment,enabled", [("local", True), ("staging", False), ("production", False)]
)
async def test_parked_defaults_follow_deployment_environment(
    policy_app: FastAPI, monkeypatch: pytest.MonkeyPatch, environment: str, enabled: bool
) -> None:
    monkeypatch.setenv("ENVIRONMENT", environment)
    async with AsyncClient(
        transport=ASGITransport(app=create_app()), base_url="http://test"
    ) as client:
        schema = (await client.get("/openapi.json")).json()["paths"]
        assert ("/api/v1/sessions" in schema) == enabled


async def test_local_mood_remains_anonymous(policy_app: FastAPI) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=policy_app), base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/mood-board/generate", json=BODY)
    # Reaches broker preflight without authentication, but never calls a broker.
    assert response.status_code == 503
    assert "CELERY_BROKER_URL" in response.json()["detail"]


@pytest.mark.parametrize("environment", ["staging", "production"])
@pytest.mark.parametrize(
    "credential", ["missing", "invalid", "expired", "refresh", "unknown", "disabled"]
)
async def test_hosted_mood_rejects_unauthorized_requests(
    policy_app: FastAPI, monkeypatch: pytest.MonkeyPatch, environment: str, credential: str
) -> None:
    monkeypatch.setenv("ENVIRONMENT", environment)
    data = {"sub": "active", "email": "active@example.com"}
    tokens = {
        "invalid": "invalid",
        "expired": create_access_token(data, expires_delta=timedelta(seconds=-1)),
        "refresh": create_refresh_token(data),
        "unknown": create_access_token({**data, "sub": "unknown"}),
        "disabled": create_access_token({**data, "sub": "disabled"}),
    }
    headers = {} if credential == "missing" else {"Authorization": f"Bearer {tokens[credential]}"}
    async with AsyncClient(
        transport=ASGITransport(app=policy_app), base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/mood-board/generate", json=BODY, headers=headers)
        assert response.status_code == (403 if credential == "disabled" else 401)
        assert (await client.get("/api/v1/mood-board/health")).status_code == 200


async def test_hosted_mood_accepts_access_token_and_enforces_user_limit(
    policy_app: FastAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setattr(rate_limiter, "ENVIRONMENT", "production")
    monkeypatch.setattr(rate_limiter, "MOCK_MODE", False)
    token = create_access_token({"sub": "active", "email": "active@example.com"})
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(
        transport=ASGITransport(app=policy_app), base_url="http://test"
    ) as client:
        unauthorized = await client.post("/api/v1/mood-board/generate", json=BODY)
        assert unauthorized.status_code == 401
        for i in range(5):
            response = await client.post(
                "/api/v1/mood-board/generate",
                json=BODY,
                headers={**headers, "X-Forwarded-For": f"192.0.2.{i}"},
            )
            assert response.status_code == 503  # Authorized, no broker configured.
        response = await client.post("/api/v1/mood-board/generate", json=BODY, headers=headers)
        assert response.status_code == 429
        assert int(response.headers["Retry-After"]) > 0
        assert response.headers["X-RateLimit-Remaining"] == "0"
        other_token = create_access_token({"sub": "other", "email": "other@example.com"})
        other_response = await client.post(
            "/api/v1/mood-board/generate",
            json=BODY,
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert other_response.status_code == 503


async def test_hosted_mood_enqueues_durable_job_for_active_user(
    policy_app: FastAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://unused:6379/0")
    celery = MagicMock()
    celery.control.inspect.return_value.ping.return_value = {"worker": {"ok": "pong"}}
    monkeypatch.setattr("copy_that.interfaces.api.mood_board.celery_app", celery)
    policy_app.dependency_overrides[deps.get_job_executor] = lambda: AsyncMock()
    token = create_access_token({"sub": "active", "email": "active@example.com"})
    async with AsyncClient(
        transport=ASGITransport(app=policy_app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/mood-board/generate",
            json=BODY,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 202
        handle = response.json()
        job = (await client.get(f"/api/v1/jobs/{handle['job_id']}")).json()
        assert job["job_id"] == handle["job_id"]
        assert job["status"] == "queued"
