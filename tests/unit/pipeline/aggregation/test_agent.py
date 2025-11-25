import pytest

from copy_that.pipeline import AggregationError, PipelineTask, TokenResult, TokenType
from copy_that.pipeline.aggregation.agent import AggregationAgent


def _token(name: str, value: str, confidence: float = 0.5) -> TokenResult:
    return TokenResult(
        token_type=TokenType.COLOR,
        name=name,
        value=value,
        confidence=confidence,
    )


def _task(context: dict | None = None) -> PipelineTask:
    return PipelineTask(
        task_id="agg-task",
        image_url="http://example.com/image.png",
        token_types=[TokenType.COLOR],
        context=context,
    )


@pytest.mark.asyncio
async def test_process_returns_empty_when_no_tokens():
    agent = AggregationAgent()
    result = await agent.process(_task(context={"input_tokens": []}))
    assert result == []


@pytest.mark.asyncio
async def test_deduplicates_similar_colors_and_adds_provenance():
    token_a = _token("primary", "#FF0000", confidence=0.8)
    token_b = _token("secondary", "#FF0000", confidence=0.6)
    context = {"input_tokens": [token_a, token_b], "provenance": {"source_id": "src1"}}

    agent = AggregationAgent()
    result = await agent.process(_task(context=context))

    assert len(result) == 1
    merged = result[0]
    assert merged.confidence == pytest.approx(0.8)
    assert "com.copythat.provenance" in merged.extensions
    assert merged.extensions["com.copythat.provenance"]["sources"] == ["src1"]


@pytest.mark.asyncio
async def test_process_raises_for_invalid_input_type():
    agent = AggregationAgent()
    with pytest.raises(AggregationError) as excinfo:
        await agent.process(_task(context={"input_tokens": 123}))
    assert "Invalid input_tokens type" in str(excinfo.value)


@pytest.mark.asyncio
async def test_process_handles_dict_tokens():
    agent = AggregationAgent()
    context = {
        "input_tokens": [
            {
                "token_type": TokenType.COLOR,
                "name": "dict-token",
                "value": "#00ff00",
                "confidence": 0.9,
            }
        ],
        "provenance": {"source_id": "dict-src"},
    }
    result = await agent.process(_task(context=context))
    assert result[0].name == "dict-token"
    assert result[0].extensions["com.copythat.provenance"]["sources"] == ["dict-src"]


@pytest.mark.asyncio
async def test_cluster_invalid_n_clusters_raises_error():
    agent = AggregationAgent()
    context = {
        "input_tokens": [
            _token("one", "#000000"),
            _token("two", "#000001"),
            _token("three", "#000002"),
        ],
        "enable_clustering": True,
        "n_clusters": 0,
    }

    with pytest.raises(AggregationError) as excinfo:
        await agent.process(_task(context=context))
    assert "Invalid n_clusters value" in str(excinfo.value)


@pytest.mark.asyncio
async def test_force_error_context_triggers_aggregation_error():
    agent = AggregationAgent()
    context = {"input_tokens": [_token("ok", "#123456")], "force_error": True}

    with pytest.raises(AggregationError) as excinfo:
        await agent.process(_task(context=context))
    assert "Forced error for testing" in str(excinfo.value)
