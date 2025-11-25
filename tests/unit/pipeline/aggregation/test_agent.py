import pytest

from copy_that.pipeline import AggregationError, PipelineTask, TokenResult, TokenType
from copy_that.pipeline.aggregation.agent import AggregationAgent


class DummyDeduplicator:
    def __init__(self, threshold=2.0):
        self.threshold = threshold
        self.called = False

    def deduplicate(self, tokens):
        self.called = True
        return tokens[:1]


class DummyProvenanceTracker:
    def __init__(self):
        self.records = {}

    def add_provenance(self, token_id, record):
        self.records[token_id] = record

    def apply_to_token(self, token_id, token):
        token.extensions = {"id": token_id}
        return token


@pytest.mark.asyncio
async def test_process_returns_empty_when_no_tokens(monkeypatch):
    agent = AggregationAgent()
    task = PipelineTask(
        task_id="task-empty",
        image_url="http://example.com/image",
        token_types=[TokenType.COLOR],
        context={"input_tokens": []},
    )
    result = await agent.process(task)
    assert result == []


@pytest.mark.asyncio
async def test_process_with_invalid_token_type(monkeypatch):
    agent = AggregationAgent()
    task = PipelineTask(
        task_id="task-invalid",
        image_url="http://example.com/image",
        token_types=[TokenType.COLOR],
        context={"input_tokens": [123]},
    )
    with pytest.raises(AggregationError) as exc:
        await agent.process(task)
    assert "Invalid token type" in str(exc.value)


@pytest.mark.asyncio
async def test_disable_deduplication(monkeypatch):
    agent = AggregationAgent()
    dedup = DummyDeduplicator()
    agent._deduplicator = dedup
    agent._provenance_tracker = DummyProvenanceTracker()

    payload = [
        TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            path=["color"],
            w3c_type=None,
            value="#ff0000",
            confidence=0.9,
        )
    ]

    task = PipelineTask(
        task_id="task-nodeup",
        image_url="http://example.com/img",
        token_types=[TokenType.COLOR],
        context={
            "input_tokens": payload,
            "enable_deduplication": False,
            "enable_provenance": False,
        },
    )

    result = await agent.process(task)
    assert result == payload
    assert dedup.called is False


@pytest.mark.asyncio
async def test_clustering_invalid_n_clusters(monkeypatch):
    agent = AggregationAgent()
    agent._deduplicator = DummyDeduplicator()
    agent._provenance_tracker = DummyProvenanceTracker()

    tokens = [
        TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            path=["color"],
            w3c_type=None,
            value="#ff0000",
            confidence=0.9,
        ),
        TokenResult(
            token_type=TokenType.COLOR,
            name="secondary",
            path=["color"],
            w3c_type=None,
            value="#00ff00",
            confidence=0.8,
        ),
    ]

    task = PipelineTask(
        task_id="task-cluster",
        image_url="http://example.com/img",
        token_types=[TokenType.COLOR],
        context={
            "input_tokens": tokens,
            "enable_clustering": True,
            "n_clusters": 0,
        },
    )

    with pytest.raises(AggregationError):
        await agent.process(task)


@pytest.mark.asyncio
async def test_force_error_context(monkeypatch):
    agent = AggregationAgent()
    task = PipelineTask(
        task_id="task-force",
        image_url="http://example.com/img",
        token_types=[TokenType.COLOR],
        context={"force_error": True},
    )
    with pytest.raises(AggregationError) as exc:
        await agent.process(task)
    assert "Forced error" in str(exc.value)


@pytest.mark.asyncio
async def test_output_provenance_applied(monkeypatch):
    agent = AggregationAgent()
    agent._deduplicator = DummyDeduplicator()
    tracker = DummyProvenanceTracker()
    agent._provenance_tracker = tracker
    monkeypatch.setattr(agent, "_kmeans_cluster", lambda tokens, values, clusters: tokens[:1])

    token = TokenResult(
        token_type=TokenType.COLOR,
        name="primary",
        path=["color"],
        w3c_type=None,
        value="#ff0000",
        confidence=0.9,
    )

    task = PipelineTask(
        task_id="task-prov",
        image_url="http://example.com/img",
        token_types=[TokenType.COLOR],
        context={
            "input_tokens": [token],
            "enable_clustering": True,
            "n_clusters": 2,
        },
    )

    result = await agent.process(task)
    assert result[0].extensions == {"id": "color.primary"}
