"""PipelineCoordinator for orchestrating the full extraction pipeline.

Coordinates: Preprocess → Extract → Aggregate → Validate → Generate
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from copy_that.pipeline import BasePipelineAgent, PipelineTask, TokenResult
from copy_that.pipeline.orchestrator.agent_pool import AgentPool
from copy_that.pipeline.orchestrator.circuit_breaker import CircuitBreaker, CircuitBreakerError


class PipelineStage(str, Enum):
    """Stages in the extraction pipeline."""

    PREPROCESS = "preprocess"
    EXTRACT = "extract"
    AGGREGATE = "aggregate"
    VALIDATE = "validate"
    GENERATE = "generate"


@dataclass
class StageResult:
    """Result of a single pipeline stage."""

    stage: PipelineStage
    success: bool
    tokens: list[TokenResult] = field(default_factory=list)
    error: str | None = None
    duration_ms: float = 0.0


@dataclass
class PipelineResult:
    """Result of full pipeline execution."""

    task_id: str
    success: bool
    tokens: list[TokenResult]
    stage_results: dict[PipelineStage, StageResult]
    errors: list[str] = field(default_factory=list)
    duration_ms: float = 0.0
    started_at: datetime | None = None
    completed_at: datetime | None = None


class PipelineCoordinator:
    """Orchestrator for the full token extraction pipeline.

    Coordinates all pipeline stages with concurrency control and fault tolerance.

    Pipeline flow:
    PREPROCESS → EXTRACT → AGGREGATE → VALIDATE → GENERATE

    Example:
        coordinator = PipelineCoordinator(
            preprocess_agent=PreprocessingAgent(),
            extraction_agents=[ColorAgent(), SpacingAgent()],
            aggregation_agent=AggregationAgent(),
            validation_agent=ValidationAgent(),
            generator_agent=GeneratorAgent(),
        )
        result = await coordinator.execute(task)
    """

    def __init__(
        self,
        preprocess_agent: BasePipelineAgent,
        extraction_agents: list[BasePipelineAgent],
        aggregation_agent: BasePipelineAgent,
        validation_agent: BasePipelineAgent,
        generator_agent: BasePipelineAgent,
        agent_pool: AgentPool | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        fail_on_partial_extraction: bool = True,
    ):
        """Initialize the coordinator.

        Args:
            preprocess_agent: Agent for preprocessing images
            extraction_agents: List of extraction agents
            aggregation_agent: Agent for aggregating tokens
            validation_agent: Agent for validating tokens
            generator_agent: Agent for generating output
            agent_pool: Optional custom agent pool
            circuit_breaker: Optional circuit breaker for fault tolerance
            fail_on_partial_extraction: If False, continue with partial extraction results
        """
        self._preprocess_agent = preprocess_agent
        self._extraction_agents = extraction_agents
        self._aggregation_agent = aggregation_agent
        self._validation_agent = validation_agent
        self._generator_agent = generator_agent
        self._fail_on_partial_extraction = fail_on_partial_extraction

        # Pool and breaker
        self._agent_pool = agent_pool or AgentPool(max_concurrency=10)
        self._circuit_breaker = circuit_breaker

        # Statistics
        self._total_executed = 0
        self._successful = 0
        self._failed = 0

    @property
    def preprocess_agent(self) -> BasePipelineAgent:
        """Get preprocessing agent."""
        return self._preprocess_agent

    @property
    def extraction_agents(self) -> list[BasePipelineAgent]:
        """Get extraction agents."""
        return self._extraction_agents

    @property
    def aggregation_agent(self) -> BasePipelineAgent:
        """Get aggregation agent."""
        return self._aggregation_agent

    @property
    def agent_pool(self) -> AgentPool:
        """Get agent pool."""
        return self._agent_pool

    @property
    def circuit_breaker(self) -> CircuitBreaker | None:
        """Get circuit breaker."""
        return self._circuit_breaker

    async def execute(
        self,
        task: PipelineTask,
        skip_stages: list[PipelineStage] | None = None,
    ) -> PipelineResult:
        """Execute the full pipeline for a task.

        Args:
            task: The pipeline task to execute
            skip_stages: Optional list of stages to skip

        Returns:
            PipelineResult with tokens and stage results
        """
        skip_stages = skip_stages or []
        started_at = datetime.now()
        start_time = time.time()

        stage_results: dict[PipelineStage, StageResult] = {}
        errors: list[str] = []
        tokens: list[TokenResult] = []
        success = True

        # Check circuit breaker
        if (
            self._circuit_breaker
            and self._circuit_breaker.is_open
            and self._circuit_breaker.last_failure_time
            and time.time() - self._circuit_breaker.last_failure_time
            < self._circuit_breaker.recovery_timeout
        ):
            self._total_executed += 1
            self._failed += 1
            return PipelineResult(
                task_id=task.task_id,
                success=False,
                tokens=[],
                stage_results={},
                errors=[f"Circuit is open: {self._circuit_breaker.name}"],
                duration_ms=(time.time() - start_time) * 1000,
                started_at=started_at,
                completed_at=datetime.now(),
            )

        try:
            # Stage 1: Preprocess
            if PipelineStage.PREPROCESS not in skip_stages:
                result = await self._execute_stage(
                    PipelineStage.PREPROCESS,
                    self._preprocess_agent,
                    task,
                )
                stage_results[PipelineStage.PREPROCESS] = result

                if not result.success:
                    success = False
                    errors.append(result.error or "Preprocessing failed")
                    self._record_failure()
                    return self._create_result(
                        task.task_id,
                        success,
                        tokens,
                        stage_results,
                        errors,
                        start_time,
                        started_at,
                    )

                # Store preprocessed image in context
                if result.tokens:
                    task = self._update_task_context(
                        task, {"preprocessed_image": result.tokens[0]}
                    )

            # Stage 2: Extract (parallel)
            if PipelineStage.EXTRACT not in skip_stages:
                extraction_results = await self._execute_parallel_extraction(task)
                all_tokens: list[TokenResult] = []
                extraction_errors: list[str] = []

                for agent_result in extraction_results:
                    if agent_result.success:
                        all_tokens.extend(agent_result.tokens)
                    else:
                        extraction_errors.append(agent_result.error or "Extraction failed")

                # Create combined stage result
                stage_results[PipelineStage.EXTRACT] = StageResult(
                    stage=PipelineStage.EXTRACT,
                    success=len(extraction_errors) == 0 or not self._fail_on_partial_extraction,
                    tokens=all_tokens,
                    error="; ".join(extraction_errors) if extraction_errors else None,
                )

                errors.extend(extraction_errors)

                if extraction_errors and self._fail_on_partial_extraction:
                    success = False
                    self._record_failure()
                    return self._create_result(
                        task.task_id,
                        success,
                        all_tokens,
                        stage_results,
                        errors,
                        start_time,
                        started_at,
                    )

                # Update context with extracted tokens
                task = self._update_task_context(task, {"tokens": all_tokens})
                tokens = all_tokens

            # Stage 3: Aggregate
            if PipelineStage.AGGREGATE not in skip_stages:
                result = await self._execute_stage(
                    PipelineStage.AGGREGATE,
                    self._aggregation_agent,
                    task,
                )
                stage_results[PipelineStage.AGGREGATE] = result

                if not result.success:
                    success = False
                    errors.append(result.error or "Aggregation failed")
                    self._record_failure()
                    return self._create_result(
                        task.task_id,
                        success,
                        tokens,
                        stage_results,
                        errors,
                        start_time,
                        started_at,
                    )

                # Update tokens
                tokens = result.tokens
                task = self._update_task_context(task, {"tokens": tokens})

            # Stage 4: Validate
            if PipelineStage.VALIDATE not in skip_stages:
                result = await self._execute_stage(
                    PipelineStage.VALIDATE,
                    self._validation_agent,
                    task,
                )
                stage_results[PipelineStage.VALIDATE] = result

                if not result.success:
                    success = False
                    errors.append(result.error or "Validation failed")
                    self._record_failure()
                    return self._create_result(
                        task.task_id,
                        success,
                        tokens,
                        stage_results,
                        errors,
                        start_time,
                        started_at,
                    )

                tokens = result.tokens
                task = self._update_task_context(task, {"tokens": tokens})

            # Stage 5: Generate
            if PipelineStage.GENERATE not in skip_stages:
                result = await self._execute_stage(
                    PipelineStage.GENERATE,
                    self._generator_agent,
                    task,
                )
                stage_results[PipelineStage.GENERATE] = result

                if not result.success:
                    success = False
                    errors.append(result.error or "Generation failed")
                    self._record_failure()
                    return self._create_result(
                        task.task_id,
                        success,
                        tokens,
                        stage_results,
                        errors,
                        start_time,
                        started_at,
                    )

                tokens = result.tokens

            # Success
            self._record_success()
            return self._create_result(
                task.task_id,
                True,
                tokens,
                stage_results,
                errors,
                start_time,
                started_at,
            )

        except CircuitBreakerError as e:
            self._record_failure()
            return PipelineResult(
                task_id=task.task_id,
                success=False,
                tokens=[],
                stage_results=stage_results,
                errors=[str(e)],
                duration_ms=(time.time() - start_time) * 1000,
                started_at=started_at,
                completed_at=datetime.now(),
            )

        except Exception as e:
            self._record_failure()
            return PipelineResult(
                task_id=task.task_id,
                success=False,
                tokens=[],
                stage_results=stage_results,
                errors=[f"Pipeline error: {str(e)}"],
                duration_ms=(time.time() - start_time) * 1000,
                started_at=started_at,
                completed_at=datetime.now(),
            )

    async def _execute_stage(
        self,
        stage: PipelineStage,
        agent: BasePipelineAgent,
        task: PipelineTask,
    ) -> StageResult:
        """Execute a single pipeline stage.

        Args:
            stage: The pipeline stage
            agent: The agent to execute
            task: The task to process

        Returns:
            StageResult with tokens and status
        """
        start_time = time.time()

        try:
            # Execute through circuit breaker if available
            if self._circuit_breaker:
                result = await self._circuit_breaker.call(
                    lambda: self._agent_pool.submit(agent, task)
                )
            else:
                result = await self._agent_pool.submit(agent, task)

            # Convert to list if needed
            tokens = result if isinstance(result, list) else []

            return StageResult(
                stage=stage,
                success=True,
                tokens=tokens,
                duration_ms=(time.time() - start_time) * 1000,
            )

        except Exception as e:
            return StageResult(
                stage=stage,
                success=False,
                tokens=[],
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000,
            )

    async def _execute_parallel_extraction(
        self,
        task: PipelineTask,
    ) -> list[StageResult]:
        """Execute extraction agents in parallel.

        Args:
            task: The task to process

        Returns:
            List of StageResults from each extractor
        """
        tasks = []
        for agent in self._extraction_agents:
            tasks.append(
                self._execute_stage(PipelineStage.EXTRACT, agent, task)
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        stage_results: list[StageResult] = []
        for result in results:
            if isinstance(result, BaseException):
                stage_results.append(
                    StageResult(
                        stage=PipelineStage.EXTRACT,
                        success=False,
                        tokens=[],
                        error=str(result),
                    )
                )
            else:
                stage_results.append(result)

        return stage_results

    def _update_task_context(
        self,
        task: PipelineTask,
        updates: dict[str, Any],
    ) -> PipelineTask:
        """Update task context with new data.

        Args:
            task: The original task
            updates: Context updates to apply

        Returns:
            New task with updated context
        """
        new_context = dict(task.context) if task.context else {}
        new_context.update(updates)

        return PipelineTask(
            task_id=task.task_id,
            image_url=task.image_url,
            token_types=task.token_types,
            priority=task.priority,
            context=new_context,
            created_at=task.created_at,
        )

    def _create_result(
        self,
        task_id: str,
        success: bool,
        tokens: list[TokenResult],
        stage_results: dict[PipelineStage, StageResult],
        errors: list[str],
        start_time: float,
        started_at: datetime,
    ) -> PipelineResult:
        """Create a PipelineResult.

        Args:
            task_id: The task identifier
            success: Whether pipeline succeeded
            tokens: Extracted tokens
            stage_results: Results from each stage
            errors: Accumulated errors
            start_time: Pipeline start timestamp
            started_at: Pipeline start datetime

        Returns:
            PipelineResult instance
        """
        return PipelineResult(
            task_id=task_id,
            success=success,
            tokens=tokens,
            stage_results=stage_results,
            errors=errors,
            duration_ms=(time.time() - start_time) * 1000,
            started_at=started_at,
            completed_at=datetime.now(),
        )

    def _record_success(self) -> None:
        """Record successful execution."""
        self._total_executed += 1
        self._successful += 1

    def _record_failure(self) -> None:
        """Record failed execution."""
        self._total_executed += 1
        self._failed += 1

    async def execute_batch(
        self,
        tasks: list[PipelineTask],
        max_parallel: int = 5,
    ) -> list[PipelineResult]:
        """Execute multiple tasks in parallel.

        Args:
            tasks: List of tasks to execute
            max_parallel: Maximum parallel executions

        Returns:
            List of PipelineResults
        """
        semaphore = asyncio.Semaphore(max_parallel)

        async def execute_with_limit(task: PipelineTask) -> PipelineResult:
            async with semaphore:
                return await self.execute(task)

        return await asyncio.gather(*[execute_with_limit(task) for task in tasks])

    async def health_check(self) -> dict[str, Any]:
        """Check health of all agents.

        Returns:
            Dictionary with health status
        """
        agents = {
            "preprocess": self._preprocess_agent,
            "aggregation": self._aggregation_agent,
            "validation": self._validation_agent,
            "generator": self._generator_agent,
        }

        # Add extraction agents
        for i, agent in enumerate(self._extraction_agents):
            agents[f"extraction_{i}"] = agent

        health_checks = await asyncio.gather(
            *[agent.health_check() for agent in agents.values()]
        )

        agent_health = dict(zip(agents.keys(), health_checks, strict=True))
        all_healthy = all(health_checks)

        return {
            "healthy": all_healthy,
            "agents": agent_health,
        }

    def get_stats(self) -> dict[str, Any]:
        """Get coordinator statistics.

        Returns:
            Dictionary with execution statistics
        """
        return {
            "total_executed": self._total_executed,
            "successful": self._successful,
            "failed": self._failed,
            "success_rate": (
                self._successful / self._total_executed
                if self._total_executed > 0
                else 0.0
            ),
            "pool_stats": self._agent_pool.get_stats(),
            "circuit_breaker": (
                self._circuit_breaker.get_stats()
                if self._circuit_breaker
                else None
            ),
        }

    def reset_stats(self) -> None:
        """Reset execution statistics."""
        self._total_executed = 0
        self._successful = 0
        self._failed = 0
        self._agent_pool.reset()

    async def shutdown(self) -> None:
        """Shutdown the coordinator and pool."""
        await self._agent_pool.shutdown(wait=True)
