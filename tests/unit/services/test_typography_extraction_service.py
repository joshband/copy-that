"""Regression coverage for typography orchestration without HTTP or paid clients."""

from unittest.mock import AsyncMock, Mock

import pytest

from copy_that.application.typography_extractor import (
    ExtractedTypographyToken,
    TypographyExtractionResult,
)
from copy_that.services.typography_extraction_service import (
    TypographyExtractionInput,
    extract_typography,
    extract_typography_batch,
)


def result(source: str = "ai") -> TypographyExtractionResult:
    return TypographyExtractionResult(
        tokens=[
            ExtractedTypographyToken(
                font_family="Inter",
                font_size=16,
                font_weight=400,
                line_height=1.5,
                semantic_role="body",
                confidence=0.8,
                extraction_metadata={"source": source},
            )
        ],
        typography_palette="Measured",
        extraction_confidence=0.8,
        extractor_used=source,
    )


@pytest.mark.asyncio
async def test_auto_ai_failure_uses_cv_and_preserves_measured_metadata() -> None:
    repo = AsyncMock()
    colors = AsyncMock()
    cv = Mock()
    cv.extract = AsyncMock(return_value=result("cv_ocr_extractor").tokens)
    outcome = await extract_typography(
        TypographyExtractionInput(project_id=7, image_base64="aGVsbG8="),
        repo,
        colors,
        ai_factory=Mock(side_effect=ValueError("unavailable")),
        cv_factory=Mock(return_value=cv),
    )
    assert outcome.result.extractor_used == "cv_ocr_extractor"
    persisted = repo.record_extraction.call_args.kwargs
    assert persisted["source_url"] == "base64_upload"
    assert persisted["tokens"][0].extraction_metadata == '{"source": "cv_ocr_extractor"}'
    colors.list_by_project.assert_not_called()


@pytest.mark.asyncio
async def test_explicit_ai_failure_does_not_run_cv_or_persist() -> None:
    repo, colors, cv_factory = AsyncMock(), AsyncMock(), Mock()
    with pytest.raises(ValueError, match="unavailable"):
        await extract_typography(
            TypographyExtractionInput(project_id=7, image_base64="aGVsbG8=", extractor="ai"),
            repo,
            colors,
            ai_factory=Mock(side_effect=ValueError("unavailable")),
            cv_factory=cv_factory,
        )
    cv_factory.assert_not_called()
    repo.record_extraction.assert_not_called()


@pytest.mark.asyncio
async def test_batch_skips_failures_and_validates_each_item() -> None:
    ai = Mock()
    ai.extract_typography_from_image_url.side_effect = [ValueError("bad"), result(), result()]
    convert = Mock(side_effect=[ValueError("invalid response"), "success"])
    repo = AsyncMock()
    responses = await extract_typography_batch(
        ["bad", "invalid", "good"],
        None,
        15,
        repo,
        ai_factory=Mock(return_value=ai),
        response_factory=convert,
    )
    assert responses == ["success"]
    assert convert.call_count == 2
    repo.record_extraction.assert_not_called()


@pytest.mark.asyncio
async def test_only_fallback_ai_tokens_trigger_recommendation() -> None:
    repo, colors = AsyncMock(), AsyncMock()
    ai = Mock()
    ai.extract_typography_from_base64.return_value = result("fallback")
    style = {
        "primary_style": "minimalist",
        "color_temperature": "warm",
        "visual_weight": "balanced",
    }
    infer = Mock(return_value=style)
    recommend = Mock(return_value=(result("recommendation").tokens, 0.7))
    outcome = await extract_typography(
        TypographyExtractionInput(project_id=7, image_base64="aGVsbG8="),
        repo,
        colors,
        ai_factory=Mock(return_value=ai),
        infer_style=infer,
        recommend_tokens=recommend,
    )
    assert outcome.result.extractor_used == "typography_recommender"
    assert repo.record_extraction.call_args.kwargs["result_data"]["style_attributes"] == style
    colors.list_by_project.assert_awaited_once_with(project_id=7)


@pytest.mark.asyncio
async def test_route_injects_legacy_ai_patch_point(monkeypatch: pytest.MonkeyPatch) -> None:
    from copy_that.interfaces.api import typography
    from copy_that.interfaces.api.schemas import ExtractTypographyRequest

    ai = Mock()
    ai.extract_typography_from_base64.return_value = result()
    monkeypatch.setattr(typography, "AITypographyExtractor", Mock(return_value=ai))
    projects = AsyncMock()
    projects.get.return_value = object()
    repo = AsyncMock()
    response = await typography.extract_typography_from_image(
        ExtractTypographyRequest(project_id=7, image_base64="aGVsbG8=", extractor="ai"),
        projects,
        repo,
        AsyncMock(),
        None,
    )
    assert response.typography_tokens[0].font_family == "Inter"
    assert response.extractor_used == "ai"
    repo.record_extraction.assert_awaited_once()


@pytest.mark.asyncio
async def test_route_invalid_choice_keeps_400() -> None:
    from fastapi import HTTPException

    from copy_that.interfaces.api import typography
    from copy_that.interfaces.api.schemas import ExtractTypographyRequest

    projects = AsyncMock()
    projects.get.return_value = object()
    with pytest.raises(HTTPException) as error:
        await typography.extract_typography_from_image(
            ExtractTypographyRequest(project_id=7, image_base64="aGVsbG8=", extractor="invalid"),
            projects,
            AsyncMock(),
            AsyncMock(),
            None,
        )
    assert error.value.status_code == 400
    assert error.value.detail.startswith("Invalid input:")


@pytest.mark.asyncio
async def test_multi_preserves_partial_failures_and_job_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace

    from copy_that.extractors.typography import adapters, orchestrator
    from copy_that.services.typography_extraction_service import extract_typography_multi

    monkeypatch.setattr(adapters, "AITypographyExtractorAdapter", Mock())
    monkeypatch.setattr(adapters, "CVTypographyExtractorAdapter", Mock())
    runner = Mock()
    runner.extract_all_safe = AsyncMock(
        return_value=SimpleNamespace(
            aggregated_tokens=result("cv").tokens,
            overall_confidence=0.8,
            failed_extractors=[("ai", "unavailable")],
        )
    )
    monkeypatch.setattr(orchestrator, "TypographyExtractionOrchestrator", Mock(return_value=runner))
    repo = AsyncMock()
    repo.record_extraction.return_value = 12
    outcome = await extract_typography_multi(
        TypographyExtractionInput(project_id=7, image_base64="data:image/png;base64,aGVsbG8="),
        repo,
    )
    assert outcome.failed_extractors == [{"name": "ai", "error": "unavailable"}]
    assert outcome.namespace == "token/typography/project/7/job/12"
    assert repo.record_extraction.call_args.kwargs["result_data"]["failed_extractors"] == [
        ("ai", "unavailable")
    ]
    assert runner.extract_all_safe.call_args.args[0] == b"hello"


@pytest.mark.asyncio
async def test_low_confidence_ai_merges_cv_without_relabeling_source() -> None:
    ai_result = result("ai")
    ai_result.extraction_confidence = 0.5
    ai = Mock()
    ai.extract_typography_from_base64.return_value = ai_result
    measured = result("cv_ocr_extractor").tokens[0]
    measured.font_size = 24
    cv = Mock()
    cv.extract = AsyncMock(return_value=[measured])
    repo = AsyncMock()
    outcome = await extract_typography(
        TypographyExtractionInput(project_id=7, image_base64="aGVsbG8="),
        repo,
        AsyncMock(),
        ai_factory=Mock(return_value=ai),
        cv_factory=Mock(return_value=cv),
    )
    assert [token.font_size for token in outcome.result.tokens] == [16, 24]
    assert outcome.result.extractor_used == "ai"
    assert outcome.result.extraction_confidence == 0.5
    assert outcome.result.tokens[1].extraction_metadata == {"source": "cv_ocr_extractor"}
    assert len(repo.record_extraction.call_args.kwargs["tokens"]) == 2


@pytest.mark.asyncio
async def test_batch_persists_each_success_with_original_job_payload() -> None:
    ai = Mock()
    ai.extract_typography_from_image_url.return_value = result()
    repo = AsyncMock()
    repo.record_extraction.return_value = 12
    outcomes = await extract_typography_batch(
        ["https://example.test/image"],
        7,
        9,
        repo,
        ai_factory=Mock(return_value=ai),
        response_factory=lambda outcome: outcome,
    )
    assert outcomes[0].namespace == "token/typography/project/7/job/12"
    assert repo.record_extraction.call_args.kwargs["result_data"] == {"typography_count": 1}
    ai.extract_typography_from_image_url.assert_called_once_with(
        "https://example.test/image",
        max_tokens=9,
    )


@pytest.mark.asyncio
async def test_route_ai_download_error_keeps_502(monkeypatch: pytest.MonkeyPatch) -> None:
    import requests
    from fastapi import HTTPException

    from copy_that.interfaces.api import typography
    from copy_that.interfaces.api.schemas import ExtractTypographyRequest

    ai = Mock()
    ai.extract_typography_from_image_url.side_effect = requests.RequestException("unreachable")
    monkeypatch.setattr(typography, "AITypographyExtractor", Mock(return_value=ai))
    projects = AsyncMock()
    projects.get.return_value = object()
    with pytest.raises(HTTPException) as error:
        await typography.extract_typography_from_image(
            ExtractTypographyRequest(
                project_id=7, image_url="https://example.test/image", extractor="ai"
            ),
            projects,
            AsyncMock(),
            AsyncMock(),
            None,
        )
    assert error.value.status_code == 502
    assert error.value.detail == "Failed to fetch image from URL: unreachable"
