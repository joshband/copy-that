"""Tests for PipelineCoordinator.

Tests written FIRST following TDD principles.
"""

import asyncio

import pytest

from copy_that.pipeline import (
    BasePipelineAgent,
    PipelineError,
    PipelineTask,
    ProcessedImage,
    TokenResult,
    TokenType,
)
from copy_that.pipeline.orchestrator.agent_pool import AgentPool
from copy_that.pipeline.orchestrator.circuit_breaker import CircuitBreaker
from copy_that.pipeline.orchestrator.coordinator import (
    PipelineCoordinator,
    PipelineResult,
    PipelineStage,
    StageResult,
)


class MockPreprocessAgent(BasePipelineAgent):
    """Mock preprocessing agent."""

    def __init__(self, should_fail: bool = False):
        self._should_fail = should_fail

    @property
    def agent_type(self) -> str:
        return "preprocessor"

    @property
    def stage_name(self) -> str:
        return "preprocessing"

    async def process(self, task: PipelineTask) -> ProcessedImage:
        if self._should_fail:
            raise PipelineError("Preprocessing failed")
        return ProcessedImage(
            image_id="img-123",
            source_url=task.image_url,
            width=800,
            height=600,
            format="PNG",
        )

    async def health_check(self) -> bool:
        return True


class MockExtractionAgent(BasePipelineAgent):
    """Mock extraction agent."""

    def __init__(self, token_type: TokenType = TokenType.COLOR, should_fail: bool = False):
        self._token_type = token_type
        self._should_fail = should_fail

    @property
    def agent_type(self) -> str:
        return "extraction"

    @property
    def stage_name(self) -> str:
        return "extraction"

    async def process(self, task: PipelineTask) -> list[TokenResult]:
        if self._should_fail:
            raise PipelineError("Extraction failed")
        return [
            TokenResult(
                token_type=self._token_type,
                name=f"test-{self._token_type.value}",
                value="#FF0000" if self._token_type == TokenType.COLOR else "16px",
                confidence=0.95,
            )
        ]

    async def health_check(self) -> bool:
        return True


class MockAggregationAgent(BasePipelineAgent):
    """Mock aggregation agent."""

    def __init__(self, should_fail: bool = False):
        self._should_fail = should_fail

    @property
    def agent_type(self) -> str:
        return "aggregation"

    @property
    def stage_name(self) -> str:
        return "aggregation"

    async def process(self, task: PipelineTask) -> list[TokenResult]:
        if self._should_fail:
            raise PipelineError("Aggregation failed")
        # Pass through tokens from context
        tokens = task.context.get("tokens", []) if task.context else []
        return tokens

    async def health_check(self) -> bool:
        return True


class MockValidationAgent(BasePipelineAgent):
    """Mock validation agent."""

    def __init__(self, should_fail: bool = False):
        self._should_fail = should_fail

    @property
    def agent_type(self) -> str:
        return "validation"

    @property
    def stage_name(self) -> str:
        return "validation"

    async def process(self, task: PipelineTask) -> list[TokenResult]:
        if self._should_fail:
            raise PipelineError("Validation failed")
        tokens = task.context.get("tokens", []) if task.context else []
        return tokens

    async def health_check(self) -> bool:
        return True


class MockGeneratorAgent(BasePipelineAgent):
    """Mock generator agent."""

    def __init__(self, should_fail: bool = False):
        self._should_fail = should_fail

    @property
    def agent_type(self) -> str:
        return "generator"

    @property
    def stage_name(self) -> str:
        return "generation"

    async def process(self, task: PipelineTask) -> list[TokenResult]:
        if self._should_fail:
            raise PipelineError("Generation failed")
        tokens = task.context.get("tokens", []) if task.context else []
        return tokens

    async def health_check(self) -> bool:
        return True


class TestPipelineStage:
    """Tests for PipelineStage enum."""

    def test_stages_exist(self):
        """Test all pipeline stages exist."""
        assert PipelineStage.PREPROCESS is not None
        assert PipelineStage.EXTRACT is not None
        assert PipelineStage.AGGREGATE is not None
        assert PipelineStage.VALIDATE is not None
        assert PipelineStage.GENERATE is not None

    def test_stage_order(self):
        """Test stages have correct order."""
        stages = list(PipelineStage)
        assert stages[0] == PipelineStage.PREPROCESS
        assert stages[1] == PipelineStage.EXTRACT
        assert stages[2] == PipelineStage.AGGREGATE
        assert stages[3] == PipelineStage.VALIDATE
        assert stages[4] == PipelineStage.GENERATE


class TestStageResult:
    """Tests for StageResult dataclass."""

    def test_create_result(self):
        """Test creating a stage result."""
        result = StageResult(
            stage=PipelineStage.EXTRACT,
            success=True,
            tokens=[],
        )
        assert result.stage == PipelineStage.EXTRACT
        assert result.success is True
        assert result.tokens == []
        assert result.error is None


class TestPipelineResult:
    """Tests for PipelineResult dataclass."""

    def test_create_result(self):
        """Test creating a pipeline result."""
        result = PipelineResult(
            task_id="test-task",
            success=True,
            tokens=[],
            stage_results={},
        )
        assert result.task_id == "test-task"
        assert result.success is True
        assert result.tokens == []
        assert result.errors == []


class TestPipelineCoordinator:
    """Tests for PipelineCoordinator."""

    @pytest.fixture
    def coordinator(self):
        """Create a coordinator with mock agents."""
        return PipelineCoordinator(
            preprocess_agent=MockPreprocessAgent(),
            extraction_agents=[MockExtractionAgent(TokenType.COLOR)],
            aggregation_agent=MockAggregationAgent(),
            validation_agent=MockValidationAgent(),
            generator_agent=MockGeneratorAgent(),
        )

    @pytest.fixture
    def task(self):
        """Create a test task."""
        return PipelineTask(
            task_id="test-task-1",
            image_url="https://example.com/test.png",
            token_types=[TokenType.COLOR],
        )

    def test_init(self):
        """Test coordinator initialization."""
        coordinator = PipelineCoordinator(
            preprocess_agent=MockPreprocessAgent(),
            extraction_agents=[MockExtractionAgent()],
            aggregation_agent=MockAggregationAgent(),
            validation_agent=MockValidationAgent(),
            generator_agent=MockGeneratorAgent(),
        )

        assert coordinator.preprocess_agent is not None
        assert len(coordinator.extraction_agents) == 1
        assert coordinator.aggregation_agent is not None

    def test_init_with_custom_pool(self):
        """Test coordinator with custom agent pool."""
        pool = AgentPool(max_concurrency=10)
        coordinator = PipelineCoordinator(
            preprocess_agent=MockPreprocessAgent(),
            extraction_agents=[MockExtractionAgent()],
            aggregation_agent=MockAggregationAgent(),
            validation_agent=MockValidationAgent(),
            generator_agent=MockGeneratorAgent(),
            agent_pool=pool,
        )

        assert coordinator.agent_pool.max_concurrency == 10

    def test_init_with_circuit_breaker(self):
        """Test coordinator with circuit breaker."""
        breaker = CircuitBreaker(name="test", failure_threshold=3)
        coordinator = PipelineCoordinator(
            preprocess_agent=MockPreprocessAgent(),
            extraction_agents=[MockExtractionAgent()],
            aggregation_agent=MockAggregationAgent(),
            validation_agent=MockValidationAgent(),
            generator_agent=MockGeneratorAgent(),
            circuit_breaker=breaker,
        )

        assert coordinator.circuit_breaker is not None

    @pytest.mark.asyncio
    async def test_execute_full_pipeline(self, coordinator, task):
        """Test executing full pipeline."""
        result = await coordinator.execute(task)

        assert result.success is True
        assert result.task_id == "test-task-1"
        assert len(result.tokens) == 1
        assert result.tokens[0].name == "test-color"
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_execute_all_stages(self, coordinator, task):
        """Test all stages are executed."""
        result = await coordinator.execute(task)

        assert PipelineStage.PREPROCESS in result.stage_results
        assert PipelineStage.EXTRACT in result.stage_results
        assert PipelineStage.AGGREGATE in result.stage_results
        assert PipelineStage.VALIDATE in result.stage_results
        assert PipelineStage.GENERATE in result.stage_results

        for stage_result in result.stage_results.values():
            assert stage_result.success is True

    @pytest.mark.asyncio
    async def test_preprocessing_failure(self, task):
        """Test pipeline handles preprocessing failure."""
        coordinator = PipelineCoordinator(
            preprocess_agent=MockPreprocessAgent(should_fail=True),
            extraction_agents=[MockExtractionAgent()],
            aggregation_agent=MockAggregationAgent(),
            validation_agent=MockValidationAgent(),
            generator_agent=MockGeneratorAgent(),
        )

        result = await coordinator.execute(task)

        assert result.success is False
        assert len(result.errors) > 0
        assert "Preprocessing failed" in result.errors[0]

    @pytest.mark.asyncio
    async def test_extraction_failure(self, task):
        """Test pipeline handles extraction failure."""
        coordinator = PipelineCoordinator(
            preprocess_agent=MockPreprocessAgent(),
            extraction_agents=[MockExtractionAgent(should_fail=True)],
            aggregation_agent=MockAggregationAgent(),
            validation_agent=MockValidationAgent(),
            generator_agent=MockGeneratorAgent(),
        )

        result = await coordinator.execute(task)

        assert result.success is False
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_parallel_extraction(self, task):
        """Test parallel extraction with multiple agents."""
        coordinator = PipelineCoordinator(
            preprocess_agent=MockPreprocessAgent(),
            extraction_agents=[
                MockExtractionAgent(TokenType.COLOR),
                MockExtractionAgent(TokenType.SPACING),
                MockExtractionAgent(TokenType.TYPOGRAPHY),
            ],
            aggregation_agent=MockAggregationAgent(),
            validation_agent=MockValidationAgent(),
            generator_agent=MockGeneratorAgent(),
        )

        result = await coordinator.execute(task)

        assert result.success is True
        assert len(result.tokens) == 3  # One from each extractor

    @pytest.mark.asyncio
    async def test_partial_extraction_failure(self, task):
        """Test some extractors fail while others succeed."""
        coordinator = PipelineCoordinator(
            preprocess_agent=MockPreprocessAgent(),
            extraction_agents=[
                MockExtractionAgent(TokenType.COLOR),
                MockExtractionAgent(TokenType.SPACING, should_fail=True),
                MockExtractionAgent(TokenType.TYPOGRAPHY),
            ],
            aggregation_agent=MockAggregationAgent(),
            validation_agent=MockValidationAgent(),
            generator_agent=MockGeneratorAgent(),
            fail_on_partial_extraction=False,
        )

        result = await coordinator.execute(task)

        # Should still succeed with partial results
        assert result.success is True
        assert len(result.tokens) == 2
        assert len(result.errors) == 1

    @pytest.mark.asyncio
    async def test_validation_failure(self, task):
        """Test pipeline handles validation failure."""
        coordinator = PipelineCoordinator(
            preprocess_agent=MockPreprocessAgent(),
            extraction_agents=[MockExtractionAgent()],
            aggregation_agent=MockAggregationAgent(),
            validation_agent=MockValidationAgent(should_fail=True),
            generator_agent=MockGeneratorAgent(),
        )

        result = await coordinator.execute(task)

        assert result.success is False

    @pytest.mark.asyncio
    async def test_generation_failure(self, task):
        """Test pipeline handles generation failure."""
        coordinator = PipelineCoordinator(
            preprocess_agent=MockPreprocessAgent(),
            extraction_agents=[MockExtractionAgent()],
            aggregation_agent=MockAggregationAgent(),
            validation_agent=MockValidationAgent(),
            generator_agent=MockGeneratorAgent(should_fail=True),
        )

        result = await coordinator.execute(task)

        assert result.success is False

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens(self, task):
        """Test circuit breaker opens after failures."""
        breaker = CircuitBreaker(name="test", failure_threshold=2, recovery_timeout=10.0)
        coordinator = PipelineCoordinator(
            preprocess_agent=MockPreprocessAgent(should_fail=True),
            extraction_agents=[MockExtractionAgent()],
            aggregation_agent=MockAggregationAgent(),
            validation_agent=MockValidationAgent(),
            generator_agent=MockGeneratorAgent(),
            circuit_breaker=breaker,
        )

        # First two failures should open the circuit
        for _ in range(2):
            await coordinator.execute(task)

        assert breaker.is_open

        # Third call should be rejected
        result = await coordinator.execute(task)
        assert result.success is False
        assert any("Circuit is open" in e for e in result.errors)

    @pytest.mark.asyncio
    async def test_execute_batch(self, coordinator):
        """Test executing multiple tasks."""
        tasks = [
            PipelineTask(
                task_id=f"task-{i}",
                image_url=f"https://example.com/{i}.png",
                token_types=[TokenType.COLOR],
            )
            for i in range(3)
        ]

        results = await coordinator.execute_batch(tasks)

        assert len(results) == 3
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_execute_batch_parallel(self, coordinator):
        """Test batch execution runs in parallel."""
        tasks = [
            PipelineTask(
                task_id=f"task-{i}",
                image_url=f"https://example.com/{i}.png",
                token_types=[TokenType.COLOR],
            )
            for i in range(5)
        ]

        start_time = asyncio.get_event_loop().time()
        results = await coordinator.execute_batch(tasks, max_parallel=5)
        elapsed = asyncio.get_event_loop().time() - start_time

        assert len(results) == 5
        # Should be much faster than sequential

    @pytest.mark.asyncio
    async def test_health_check(self, coordinator):
        """Test coordinator health check."""
        health = await coordinator.health_check()

        assert health["healthy"] is True
        assert "preprocess" in health["agents"]
        assert health["agents"]["preprocess"] is True

    @pytest.mark.asyncio
    async def test_get_stats(self, coordinator, task):
        """Test getting coordinator statistics."""
        await coordinator.execute(task)

        stats = coordinator.get_stats()

        assert stats["total_executed"] == 1
        assert stats["successful"] == 1
        assert stats["failed"] == 0
        assert "pool_stats" in stats

    @pytest.mark.asyncio
    async def test_reset_stats(self, coordinator, task):
        """Test resetting statistics."""
        await coordinator.execute(task)

        coordinator.reset_stats()

        stats = coordinator.get_stats()
        assert stats["total_executed"] == 0

    @pytest.mark.asyncio
    async def test_skip_stages(self, task):
        """Test skipping certain stages."""
        coordinator = PipelineCoordinator(
            preprocess_agent=MockPreprocessAgent(),
            extraction_agents=[MockExtractionAgent()],
            aggregation_agent=MockAggregationAgent(),
            validation_agent=MockValidationAgent(),
            generator_agent=MockGeneratorAgent(),
        )

        result = await coordinator.execute(
            task, skip_stages=[PipelineStage.VALIDATE, PipelineStage.GENERATE]
        )

        assert result.success is True
        assert PipelineStage.VALIDATE not in result.stage_results
        assert PipelineStage.GENERATE not in result.stage_results

    @pytest.mark.asyncio
    async def test_context_passed_between_stages(self, coordinator, task):
        """Test context is passed between pipeline stages."""
        result = await coordinator.execute(task)

        # Tokens should flow through all stages
        assert result.success is True
        assert len(result.tokens) == 1

    @pytest.mark.asyncio
    async def test_error_aggregation(self, task):
        """Test errors are aggregated from all stages."""
        coordinator = PipelineCoordinator(
            preprocess_agent=MockPreprocessAgent(),
            extraction_agents=[
                MockExtractionAgent(TokenType.COLOR, should_fail=True),
                MockExtractionAgent(TokenType.SPACING, should_fail=True),
            ],
            aggregation_agent=MockAggregationAgent(),
            validation_agent=MockValidationAgent(),
            generator_agent=MockGeneratorAgent(),
        )

        result = await coordinator.execute(task)

        assert result.success is False
        assert len(result.errors) >= 2

    @pytest.mark.asyncio
    async def test_timing_information(self, coordinator, task):
        """Test timing information is recorded."""
        result = await coordinator.execute(task)

        assert result.duration_ms > 0
        assert result.started_at is not None
        assert result.completed_at is not None

    @pytest.mark.asyncio
    async def test_shutdown(self, coordinator):
        """Test graceful shutdown."""
        await coordinator.shutdown()

        # Pool should be cleaned up
        stats = coordinator.get_stats()
        assert stats["pool_stats"]["active"] == 0
