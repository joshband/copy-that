import pytest

from copy_that.pipeline import PipelineTask, TokenResult, TokenType
from copy_that.pipeline.interfaces import BasePipelineAgent
from copy_that.pipeline.orchestrator.circuit_breaker import CircuitBreaker
from copy_that.pipeline.orchestrator.coordinator import PipelineCoordinator, PipelineStage


def _token(name: str) -> TokenResult:
    return TokenResult(
        token_type=TokenType.COLOR,
        name=name,
        value="#ff0000",
        confidence=0.9,
    )


def _task(task_id: str) -> PipelineTask:
    return PipelineTask(
        task_id=task_id,
        image_url="http://example.com/art.png",
        token_types=[TokenType.COLOR],
    )


class _SimpleAgent(BasePipelineAgent):
    def __init__(
        self,
        stage_name: str,
        tokens: list[TokenResult],
        fail: bool = False,
        health: bool = True,
    ) -> None:
        self._stage_name = stage_name
        self._tokens = tokens
        self._fail = fail
        self._health = health

    @property
    def agent_type(self) -> str:
        return f"{self._stage_name}_agent"

    @property
    def stage_name(self) -> str:
        return self._stage_name

    async def process(self, task: PipelineTask) -> list[TokenResult]:
        if self._fail:
            raise RuntimeError(f"{self._stage_name} failed")
        return self._tokens

    async def health_check(self) -> bool:
        return self._health


@pytest.mark.asyncio
async def test_execute_successful_pipeline():
    preprocess = _SimpleAgent("preprocess", [_token("pre")])
    extractor = _SimpleAgent("extract", [_token("extract")])
    aggregator = _SimpleAgent("aggregate", [_token("aggregate")])
    validator = _SimpleAgent("validate", [_token("validate")])
    generator = _SimpleAgent("generate", [_token("generate")])

    coordinator = PipelineCoordinator(
        preprocess_agent=preprocess,
        extraction_agents=[extractor],
        aggregation_agent=aggregator,
        validation_agent=validator,
        generator_agent=generator,
    )

    result = await coordinator.execute(_task("pipeline-success"))

    assert result.success
    assert result.tokens[0].name == "generate"
    assert PipelineStage.GENERATE in result.stage_results
    assert coordinator.get_stats()["successful"] == 1


@pytest.mark.asyncio
async def test_partial_extraction_allowed_when_disabled():
    extractor_ok = _SimpleAgent("extract", [_token("extract")])
    extractor_fail = _SimpleAgent("extract", [], fail=True)
    aggregator = _SimpleAgent("aggregate", [_token("aggregate")])
    validator = _SimpleAgent("validate", [_token("validate")])
    generator = _SimpleAgent("generate", [_token("generate")])

    coordinator = PipelineCoordinator(
        preprocess_agent=_SimpleAgent("preprocess", [_token("pre")]),
        extraction_agents=[extractor_ok, extractor_fail],
        aggregation_agent=aggregator,
        validation_agent=validator,
        generator_agent=generator,
        fail_on_partial_extraction=False,
    )

    result = await coordinator.execute(_task("partial-allowed"))

    assert result.success
    extract_stage = result.stage_results[PipelineStage.EXTRACT]
    assert extract_stage.error == "extract failed"
    assert coordinator.get_stats()["successful"] == 1


@pytest.mark.asyncio
async def test_partial_extraction_fails_when_enabled():
    extractor_ok = _SimpleAgent("extract", [_token("extract")])
    extractor_fail = _SimpleAgent("extract", [], fail=True)
    coordinator = PipelineCoordinator(
        preprocess_agent=_SimpleAgent("preprocess", [_token("pre")]),
        extraction_agents=[extractor_ok, extractor_fail],
        aggregation_agent=_SimpleAgent("aggregate", [_token("aggregate")]),
        validation_agent=_SimpleAgent("validate", [_token("validate")]),
        generator_agent=_SimpleAgent("generate", [_token("generate")]),
        fail_on_partial_extraction=True,
    )

    result = await coordinator.execute(_task("partial-fail"))

    assert not result.success
    assert PipelineStage.EXTRACT in result.stage_results
    assert result.stage_results[PipelineStage.EXTRACT].success is False
    assert coordinator.get_stats()["failed"] == 1


@pytest.mark.asyncio
async def test_execute_batch_runs_all_tasks():
    agent = _SimpleAgent("preprocess", [_token("pre")])
    coordinator = PipelineCoordinator(
        preprocess_agent=agent,
        extraction_agents=[_SimpleAgent("extract", [_token("extract")])],
        aggregation_agent=_SimpleAgent("aggregate", [_token("aggregate")]),
        validation_agent=_SimpleAgent("validate", [_token("validate")]),
        generator_agent=_SimpleAgent("generate", [_token("generate")]),
    )

    tasks = [_task(f"batch-{i}") for i in range(3)]
    results = await coordinator.execute_batch(tasks, max_parallel=2)

    assert len(results) == 3
    assert all(result.success for result in results)


@pytest.mark.asyncio
async def test_circuit_breaker_blocks_execution():
    breaker = CircuitBreaker("test-cb", failure_threshold=1, recovery_timeout=60.0)
    breaker.trip()

    coordinator = PipelineCoordinator(
        preprocess_agent=_SimpleAgent("preprocess", [_token("pre")]),
        extraction_agents=[_SimpleAgent("extract", [_token("extract")])],
        aggregation_agent=_SimpleAgent("aggregate", [_token("aggregate")]),
        validation_agent=_SimpleAgent("validate", [_token("validate")]),
        generator_agent=_SimpleAgent("generate", [_token("generate")]),
        circuit_breaker=breaker,
    )

    result = await coordinator.execute(_task("breaker"))

    assert not result.success
    assert "Circuit is open" in result.errors[0]


@pytest.mark.asyncio
async def test_health_check_reports_agent_status():
    healthy = _SimpleAgent("preprocess", [_token("pre")], health=True)
    unhealthy = _SimpleAgent("aggregate", [_token("agg")], health=False)

    coordinator = PipelineCoordinator(
        preprocess_agent=healthy,
        extraction_agents=[_SimpleAgent("extract", [_token("extract")])],
        aggregation_agent=unhealthy,
        validation_agent=_SimpleAgent("validate", [_token("validate")]),
        generator_agent=_SimpleAgent("generate", [_token("generate")]),
    )

    status = await coordinator.health_check()

    assert status["healthy"] is False
    assert status["agents"]["aggregation"] is False


@pytest.mark.asyncio
async def test_parallel_extraction_handles_exceptions():
    good = _SimpleAgent("extract", [_token("extract")])
    bad = _SimpleAgent("extract", [], fail=True)

    coordinator = PipelineCoordinator(
        preprocess_agent=_SimpleAgent("preprocess", [_token("pre")]),
        extraction_agents=[good, bad],
        aggregation_agent=_SimpleAgent("aggregate", [_token("aggregate")]),
        validation_agent=_SimpleAgent("validate", [_token("validate")]),
        generator_agent=_SimpleAgent("generate", [_token("generate")]),
        fail_on_partial_extraction=False,
    )

    results = await coordinator._execute_parallel_extraction(_task("parallel"))
    assert len(results) == 2
    assert any(not res.success for res in results)
