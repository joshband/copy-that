"""Color pipeline contracts independent of HTTP transport."""

from copy_that.extractors.color.extractor import ColorExtractionResult, ExtractedColorToken
from copy_that.services.color_pipeline import color_result_payload


def test_color_payload_preserves_debug_artifacts_and_role_tokens():
    result = ColorExtractionResult(
        colors=[
            ExtractedColorToken(hex="#336699", rgb="rgb(51, 102, 153)", name="Blue", confidence=0.9)
        ],
        dominant_colors=["#336699"],
        color_palette="Blue palette",
        extraction_confidence=0.9,
        extractor_used="test",
        background_colors=["#FFFFFF"],
        debug={"normalized_rgb_base64": "preview"},
    )

    payload = color_result_payload(result, namespace="token/color/test")

    assert payload["colors"][0]["hex"] == "#336699"
    assert payload["artifacts"]["images"][0]["base64"] == "preview"
    assert payload["artifacts"]["images"][0]["stage"] == "ingest"
    assert payload["artifacts"]["json"] == []
    assert payload["design_tokens"]


async def test_cached_stream_yields_structured_events_and_persists_records():
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, Mock

    from copy_that.services.color_pipeline import ColorPipelineDependencies, stream_color_events

    color = ExtractedColorToken(hex="#336699", rgb="rgb(51, 102, 153)", name="Blue", confidence=0.9)
    result = ColorExtractionResult(
        colors=[color],
        dominant_colors=[color.hex],
        color_palette="Cached palette",
        extraction_confidence=0.9,
        extractor_used="cached",
    )
    cache = Mock()
    cache.get.side_effect = [
        result.model_dump(),
        {"phase": 3, "status": "ai_enhancement_complete", "colors": []},
    ]
    extractor = Mock()
    tracker = Mock()
    tracker.record.return_value = SimpleNamespace(blocked=False, warned=False, total=0.02)
    tracker.persist = AsyncMock()
    repo = Mock()
    repo.record_extraction = AsyncMock(return_value=7)
    repo.list_by_job = AsyncMock(return_value=[])
    request = SimpleNamespace(
        project_id=1,
        image_base64="cached-image",
        image_url=None,
        max_colors=10,
        extractor="auto",
        include_science_artifacts=False,
    )
    dependencies = ColorPipelineDependencies(
        get_extractor=lambda _: (extractor, "cached"),
        get_cache=lambda: cache,
        cost_tracker=tracker,
    )
    headers: dict[str, str] = {}

    events = [
        event async for event in stream_color_events(request, repo, None, headers, dependencies)
    ]

    assert [event["status"] for event in events] == [
        "colors_extracted",
        "colors_streaming",
        "extraction_complete",
        "ai_enhancement_complete",
    ]
    assert events[1]["progress"] == 1.0
    assert events[2]["colors"][0]["hex"] == color.hex
    assert headers["X-Cost-Usage"] == "0.02"
    assert repo.record_extraction.await_args.kwargs["tokens"][0].hex == color.hex
    extractor.extract_colors_from_base64.assert_not_called()
    tracker.persist.assert_awaited_once()


async def test_multi_pipeline_aggregates_decoded_input_with_provenance():
    import base64
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, Mock

    from copy_that.services.color_pipeline import ColorPipelineDependencies, multi_color_payload

    color = ExtractedColorToken(
        hex="#336699",
        rgb="rgb(51, 102, 153)",
        name="Blue",
        confidence=0.9,
        extraction_metadata={"extractor_sources": ["cv", "kmeans"]},
    )
    orchestrator = Mock()
    orchestrator.extract_all = AsyncMock(
        return_value=SimpleNamespace(aggregated_colors=[color], overall_confidence=0.9)
    )
    factory = Mock(return_value=orchestrator)
    dependencies = ColorPipelineDependencies(
        kmeans_adapter=Mock(),
        cv_adapter=Mock(),
        aggregator=Mock(),
        orchestrator=factory,
    )
    request = SimpleNamespace(project_id=9, max_colors=10, include_science_artifacts=False)
    encoded = base64.b64encode(b"image-input").decode()

    payload = await multi_color_payload(request, encoded, dependencies)

    assert orchestrator.extract_all.await_args.args[0] == b"image-input"
    assert orchestrator.extract_all.await_args.args[1].startswith("project_9_")
    assert payload["colors"][0]["provenance"] == ["cv", "kmeans"]
    assert payload["dominant_colors"] == [color.hex]
    assert payload["artifacts"] == {"images": [], "json": []}
    assert len(factory.call_args.kwargs["extractors"]) == 2
