"""API contract tests for mood board router (no live Celery / AI)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.main import app

VALID_BODY = {
    "colors": [{"hex": "#2171B5", "name": "Blue"}],
    "num_variants": 1,
    "include_images": False,
    "focus_type": "material",
}


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_mood_board_health(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("MOOD_BOARD_TEXT_BASE_URL", raising=False)
    monkeypatch.delenv("MOOD_BOARD_IMAGE_BASE_URL", raising=False)
    monkeypatch.delenv("MOOD_BOARD_FLUX_BASE_URL", raising=False)
    resp = await client.get("/api/v1/mood-board/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["anthropic_configured"] is False
    assert data["openai_configured"] is False
    assert data["text_provider"] == "anthropic"
    assert data["text_configured"] is False
    assert data["image_provider"] == "token_collage"
    assert data["image_configured"] is True
    assert data["recommended_policy"] == "cheap"
    assert any(b["id"] == "token_collage" for b in data["backends"])


@pytest.mark.asyncio
async def test_mood_board_health_local_providers(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MOOD_BOARD_TEXT_BASE_URL", "http://127.0.0.1:1234/v1")
    monkeypatch.setenv("MOOD_BOARD_TEXT_MODEL", "local-llama")
    monkeypatch.setenv("MOOD_BOARD_IMAGE_BASE_URL", "http://127.0.0.1:8765/v1")
    monkeypatch.setenv("MOOD_BOARD_IMAGE_MODEL", "local-sd")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("MOOD_BOARD_FLUX_BASE_URL", raising=False)

    resp = await client.get("/api/v1/mood-board/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["text_provider"] == "openai_compatible"
    assert data["text_configured"] is True
    assert data["text_model"] == "local-llama"
    assert data["image_provider"] == "local_mflux"
    assert data["image_configured"] is True
    assert data["image_model"] == "local-sd"
    assert data["recommended_policy"] == "private"


@pytest.mark.asyncio
async def test_generate_rejects_empty_colors(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/mood-board/generate", json={"colors": []})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_generate_503_without_broker(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CELERY_BROKER_URL", raising=False)
    resp = await client.post("/api/v1/mood-board/generate", json=VALID_BODY)
    assert resp.status_code == 503
    assert "CELERY_BROKER_URL" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_generate_503_when_broker_unreachable(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

    with (
        patch("copy_that.interfaces.api.mood_board.celery_app") as celery_app,
        patch("redis.from_url") as from_url,
    ):
        insp = MagicMock()
        insp.ping.return_value = None
        celery_app.control.inspect.return_value = insp
        from_url.side_effect = ConnectionError("broker down")
        resp = await client.post("/api/v1/mood-board/generate", json=VALID_BODY)

    assert resp.status_code == 503
    detail = resp.json()["detail"].lower()
    assert "celery" in detail or "broker" in detail or "worker" in detail


@pytest.mark.asyncio
async def test_generate_202_when_inspect_empty_but_broker_up(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Solo-pool workers may miss inspect.ping while busy; broker ping is enough."""
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

    job = MagicMock()
    job.id = 43
    job.queue = "mood-board"

    job_repo = AsyncMock()
    job_executor = AsyncMock()
    previous = dict(app.dependency_overrides)
    app.dependency_overrides[deps.get_job_repo] = lambda: job_repo
    app.dependency_overrides[deps.get_job_executor] = lambda: job_executor

    redis_client = MagicMock()
    redis_client.ping.return_value = True

    with (
        patch(
            "copy_that.interfaces.api.mood_board.job_use_cases.create_job",
            new=AsyncMock(return_value=job),
        ),
        patch(
            "copy_that.interfaces.api.mood_board.job_use_cases.mark_queued",
            new=AsyncMock(),
        ),
        patch("copy_that.interfaces.api.mood_board.celery_app") as celery_app,
        patch("redis.from_url", return_value=redis_client),
    ):
        insp = MagicMock()
        insp.ping.return_value = None
        celery_app.control.inspect.return_value = insp
        job_executor.enqueue = AsyncMock()
        try:
            resp = await client.post("/api/v1/mood-board/generate", json=VALID_BODY)
        finally:
            app.dependency_overrides.clear()
            app.dependency_overrides.update(previous)

    assert resp.status_code == 202
    assert resp.json()["job_id"] == 43


@pytest.mark.asyncio
async def test_generate_202_when_celery_and_jobs_ok(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

    job = MagicMock()
    job.id = 42
    job.queue = "mood-board"

    job_repo = AsyncMock()
    job_executor = AsyncMock()

    previous = dict(app.dependency_overrides)
    app.dependency_overrides[deps.get_job_repo] = lambda: job_repo
    app.dependency_overrides[deps.get_job_executor] = lambda: job_executor

    with (
        patch(
            "copy_that.interfaces.api.mood_board.job_use_cases.create_job",
            new=AsyncMock(return_value=job),
        ),
        patch(
            "copy_that.interfaces.api.mood_board.job_use_cases.mark_queued",
            new=AsyncMock(),
        ),
        patch("copy_that.interfaces.api.mood_board.celery_app") as celery_app,
    ):
        insp = MagicMock()
        insp.ping.return_value = {"worker@host": {"ok": "pong"}}
        celery_app.control.inspect.return_value = insp
        job_executor.enqueue = AsyncMock()

        try:
            resp = await client.post("/api/v1/mood-board/generate", json=VALID_BODY)
        finally:
            app.dependency_overrides.clear()
            app.dependency_overrides.update(previous)

    assert resp.status_code == 202
    data = resp.json()
    assert data["job_id"] == 42
    assert data["stream_url"] == "/api/v1/jobs/42/stream"
    assert "variants" not in data  # job handle, not sync payload
