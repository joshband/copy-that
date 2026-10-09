"""Shadow service contracts independent of HTTP routing."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from copy_that.application.execution.async_executor import AsyncExecutor
from copy_that.services.shadow_extraction_models import ShadowExtractionRequest
from copy_that.services.shadow_extraction_service import extract_shadows


@pytest.mark.asyncio
async def test_empty_cv_fallback_preserves_message_and_persistence():
    cv_result = SimpleNamespace(
        shadows=[],
        shadow_count=0,
        extractor_used="cv_classical_empty",
        product_message="No elevation detected",
        warnings=["No elevation detected"],
    )
    cv = Mock()
    cv.extract_shadows.return_value = cv_result
    ai = Mock(side_effect=RuntimeError("offline"))
    shadow_repo = AsyncMock()
    result = await extract_shadows(
        ShadowExtractionRequest(image_base64="aW1hZ2U=", project_id=3),
        AsyncMock(),
        shadow_repo,
        AsyncExecutor(),
        cv_factory=lambda: cv,
        ai_factory=ai,
        shadowlab_enabled=lambda: False,
        pipeline_runner=Mock(),
        payload_guard=Mock(),
    )
    assert result.tokens == []
    assert result.extraction_confidence == 0.0
    assert result.extraction_metadata["extraction_source"] == "cv_classical_empty_fallback"
    assert result.extraction_metadata["empty_reason"] == "no_elevation"
    assert result.warnings == ["No elevation detected"]
    shadow_repo.record_extraction.assert_awaited_once_with(
        project_id=3,
        source_url="base64_upload",
        shadows=[],
    )


def test_upload_preview_never_runs_geometry_or_ml(tmp_path, monkeypatch):
    import base64
    from io import BytesIO

    from PIL import Image

    from copy_that.services.shadow_extraction_service import _run_shadowlab_pipeline
    from copy_that.shadowlab import stages, tokens

    forbidden = Mock(side_effect=AssertionError("heavy model executed on upload"))
    monkeypatch.setattr(stages, "stage_04_ml_mask", forbidden)
    monkeypatch.setattr(stages, "stage_06_geometry", forbidden)
    monkeypatch.setattr(tokens, "_extract_real_geometry", forbidden)
    image = BytesIO()
    Image.new("RGB", (32, 32), "white").save(image, format="PNG")
    result = _run_shadowlab_pipeline(base64.b64encode(image.getvalue()).decode(), "image/png")
    forbidden.assert_not_called()
    assert result["pipeline"]["mode"] == "classical_upload"
    assert "depth_map" not in result["artifacts"]
    assert "ml_shadow_mask" not in result["artifacts"]


@pytest.mark.asyncio
async def test_payload_rejection_is_not_converted_to_empty_fallback():
    from copy_that.services.shadow_extraction_service import ShadowServiceError

    factory = Mock()
    with pytest.raises(ShadowServiceError) as caught:
        await extract_shadows(
            ShadowExtractionRequest(image_base64="aW1hZ2U="),
            AsyncMock(),
            AsyncMock(),
            AsyncExecutor(),
            cv_factory=factory,
            ai_factory=factory,
            shadowlab_enabled=lambda: False,
            pipeline_runner=Mock(),
            payload_guard=Mock(side_effect=ShadowServiceError(status_code=413, detail="oversize")),
        )
    assert caught.value.status_code == 413
    factory.assert_not_called()


@pytest.mark.asyncio
async def test_multi_limits_persisted_tokens_and_retains_failure_provenance(monkeypatch):
    from copy_that.extractors.shadow import adapters, orchestrator
    from copy_that.extractors.shadow.extractor import ShadowStyle
    from copy_that.services.shadow_extraction_service import extract_shadows_multi

    styles = [
        ShadowStyle(color="#000000", opacity=0.3, x=0, y=4, blur=8, spread=0, confidence=0.8),
        ShadowStyle(color="#000000", opacity=0.4, x=0, y=12, blur=20, spread=0, confidence=0.9),
    ]
    extraction = SimpleNamespace(
        aggregated_tokens=styles,
        overall_confidence=0.85,
        failed_extractors=[("AI", "offline")],
        total_time_ms=7.0,
    )
    runner = AsyncMock()
    runner.extract_all_safe.return_value = extraction
    monkeypatch.setattr(adapters, "CVShadowExtractorAdapter", Mock())
    monkeypatch.setattr(adapters, "AIShadowExtractorAdapter", Mock())
    monkeypatch.setattr(orchestrator, "ShadowExtractionOrchestrator", Mock(return_value=runner))
    repo = AsyncMock()
    result = await extract_shadows_multi(
        ShadowExtractionRequest(
            image_base64="data:image/png;base64,aW1hZ2U=", project_id=4, max_tokens=1
        ),
        AsyncMock(),
        repo,
        payload_guard=Mock(),
    )
    assert len(result.tokens) == 1
    assert result.failed_extractors == [{"name": "AI", "error": "offline"}]
    assert result.extraction_metadata["total_time_ms"] == 7.0
    runner.extract_all_safe.assert_awaited_once()
    assert runner.extract_all_safe.await_args.args[0] == b"image"
    assert len(repo.record_extraction.await_args.kwargs["shadows"]) == 1


@pytest.mark.asyncio
async def test_batch_keeps_per_image_error_and_empty_cv_warning(monkeypatch):
    import requests

    from copy_that.services.shadow_extraction_models import ShadowBatchRequest
    from copy_that.services.shadow_extraction_service import extract_shadows_batch

    response = Mock(content=b"image", headers={"Content-Type": "image/png"})
    monkeypatch.setattr(
        requests, "get", Mock(side_effect=[response, RuntimeError("download failed")])
    )
    cv = Mock()
    cv.extract_shadows.return_value = SimpleNamespace(
        shadows=[],
        shadow_count=0,
        extractor_used="cv_classical_empty",
        product_message="Flat image",
    )
    result = await extract_shadows_batch(
        ShadowBatchRequest(
            image_urls=["https://example.com/flat.png", "https://example.com/bad.png"]
        ),
        AsyncExecutor(),
        cv_factory=lambda: cv,
        ai_factory=Mock(side_effect=RuntimeError("offline")),
        shadowlab_enabled=lambda: False,
        pipeline_runner=Mock(),
    )
    assert result.results[0].extractor_used == "cv_classical_empty_fallback"
    assert result.results[0].warnings == ["AI extraction unavailable: offline", "Flat image"]
    assert result.results[1].extractor_used == "error"
    assert result.results[1].warnings == ["Failed to process: download failed"]
