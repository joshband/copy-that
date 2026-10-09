"""Spacing service acceptance using real token models/cache and offline boundaries."""

from contextlib import asynccontextmanager, nullcontext
from types import SimpleNamespace
from unittest.mock import AsyncMock

import requests

from copy_that.application.spacing_models import SpacingExtractionResult, SpacingScale, SpacingToken
from copy_that.infrastructure.cache.extraction_cache import ExtractionCache, InMemoryBackend
from copy_that.services.spacing_models import SpacingExtractionRequest
from copy_that.services.spacing_pipeline import (
    SpacingPipelineDependencies,
    extract_single,
    stream_events,
)


class RecordingRepository:
    def __init__(self):
        self.extractions = []

    async def record_extraction(self, **values):
        self.extractions.append(values)
        return 7


class InlineExecutor:
    async def run(self, operation):
        return operation()


@asynccontextmanager
async def slot():
    yield


def measured_result():
    return SpacingExtractionResult(
        tokens=[SpacingToken(value_px=8, name="spacing-8", confidence=0.6)],
        scale_system=SpacingScale.EIGHT_POINT,
        base_unit=8,
        grid_compliance=1.0,
        extraction_confidence=0.6,
        unique_values=[8],
        min_spacing=8,
        max_spacing=8,
        warnings=["Measured spacing"],
        spacing_confidence_breakdown={"overall": 0.6, "fallback": 0.0},
    )


def dependencies(result, cache=None, *, block_cost=False):
    def fail_ai(*args):
        raise requests.RequestException("provider unavailable")

    cv = SimpleNamespace(
        extract_from_base64=lambda data: result, extract_from_bytes=lambda data: result
    )
    ai = SimpleNamespace(extract_spacing_from_base64=fail_ai)
    cost = SimpleNamespace(
        record=lambda **kwargs: SimpleNamespace(
            blocked=block_cost, warned=False, total=0.02, hard_limit=1, window="day"
        ),
        persist=AsyncMock(),
    )
    return SpacingPipelineDependencies(
        get_extractor=lambda quality="standard": ai,
        cv_extractor=lambda **kwargs: cv,
        download_image=lambda url: (b"offline-image", "image/png"),
        validate_image_url=lambda url: url,
        enforce_payload_size=lambda data: None,
        extract_slot=slot,
        cache=lambda: cache or ExtractionCache(InMemoryBackend()),
        input_hash=lambda *args: "known-hash",
        track_perf=lambda *args, **kwargs: nullcontext(),
        cost_tracker=cost,
    )


async def test_single_ai_failure_preserves_measured_cv_and_persists_tokens():
    result = measured_result()
    spacing_repo, layout_repo = RecordingRepository(), RecordingRepository()
    response = await extract_single(
        SpacingExtractionRequest(image_base64="aW1hZ2U=", project_id=3),
        spacing_repo,
        layout_repo,
        InlineExecutor(),
        dependencies(result),
    )
    assert response.tokens[0].value_px == 8
    assert response.extraction_confidence == 0.6
    assert response.warnings == ["Measured spacing"]
    assert response.spacing_confidence_breakdown == {"overall": 0.6, "fallback": 0.0}
    assert spacing_repo.extractions[0]["project_id"] == 3
    assert spacing_repo.extractions[0]["tokens"][0].value_px == 8
    assert "token/spacing/project/3/job/7/01" in response.design_tokens["spacing"]


async def test_cached_stream_preserves_event_sequence_and_completion_identity():
    result = measured_result()
    cache = ExtractionCache(InMemoryBackend())
    cache.set("spacing.full", "known-hash", "project:3", result.model_dump())
    deps = dependencies(result, cache)

    # A cache hit must not fetch the image or invoke CV/AI.
    def unexpected_download(url):
        raise AssertionError("cached extraction fetched input")

    deps = SpacingPipelineDependencies(**{**vars(deps), "download_image": unexpected_download})
    events = [
        item
        async for item in stream_events(
            SpacingExtractionRequest(image_url="https://example.com/image.png", project_id=3),
            "https://example.com/image.png",
            RecordingRepository(),
            RecordingRepository(),
            InlineExecutor(),
            None,
            {},
            deps,
        )
    ]
    assert [name for name, _ in events] == [
        "progress",
        "progress",
        "progress",
        "progress",
        "token",
        "complete",
    ]
    completed = events[-1][1]
    assert completed["job_id"] == 7
    assert completed["project_id"] == 3
    assert completed["warnings"] == ["Measured spacing"]


async def test_stream_cost_block_emits_error_without_persistence():
    spacing_repo = RecordingRepository()
    events = [
        item
        async for item in stream_events(
            SpacingExtractionRequest(image_url="https://example.com/image.png", project_id=3),
            "https://example.com/image.png",
            spacing_repo,
            RecordingRepository(),
            InlineExecutor(),
            None,
            {},
            dependencies(measured_result(), block_cost=True),
        )
    ]
    assert len(events) == 1
    assert events[0][0] == "error"
    assert "Cost quota exceeded" in events[0][1]["message"]
    assert events[0][1]["type"] == "HTTPException"
    assert not spacing_repo.extractions


async def test_spacing_http_adapter_uses_injected_extraction_boundaries(monkeypatch):
    from fastapi import FastAPI
    from httpx import ASGITransport, AsyncClient

    from copy_that.interfaces.api import dependencies as api_dependencies
    from copy_that.interfaces.api import spacing as spacing_router

    result = measured_result()
    offline = dependencies(result)
    monkeypatch.setattr(spacing_router, "get_extractor", offline.get_extractor)
    monkeypatch.setattr(spacing_router, "CVSpacingExtractor", offline.cv_extractor)
    spacing_repo, layout_repo = RecordingRepository(), RecordingRepository()
    app = FastAPI()
    app.include_router(spacing_router.router)
    app.dependency_overrides[api_dependencies.get_spacing_repo] = lambda: spacing_repo
    app.dependency_overrides[api_dependencies.get_layout_repo] = lambda: layout_repo
    app.dependency_overrides[api_dependencies.get_async_executor] = InlineExecutor
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/spacing/extract", json={"image_base64": "aW1hZ2U=", "project_id": 3}
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["tokens"][0]["value_px"] == 8
    assert payload["extraction_confidence"] == 0.6
    assert spacing_repo.extractions[0]["source_url"] == "base64_upload"
