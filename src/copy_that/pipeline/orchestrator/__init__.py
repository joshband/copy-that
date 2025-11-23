"""Pipeline orchestrator module.

Provides coordination, concurrency control, and fault tolerance for the
token extraction pipeline.

Components:
- AgentPool: Semaphore-based concurrency control for agents
- CircuitBreaker: Fault tolerance with fail-fast behavior
- PipelineCoordinator: Full pipeline orchestration

Example:
    from copy_that.pipeline.orchestrator import (
        PipelineCoordinator,
        AgentPool,
        CircuitBreaker,
    )

    coordinator = PipelineCoordinator(
        preprocess_agent=PreprocessingAgent(),
        extraction_agents=[ColorAgent(), SpacingAgent()],
        aggregation_agent=AggregationAgent(),
        validation_agent=ValidationAgent(),
        generator_agent=GeneratorAgent(),
        agent_pool=AgentPool(max_concurrency=10),
        circuit_breaker=CircuitBreaker("pipeline", failure_threshold=5),
    )

    result = await coordinator.execute(task)
"""

from copy_that.pipeline.orchestrator.agent_pool import (
    AgentPool,
    TaskStatus,
    TaskTracker,
)
from copy_that.pipeline.orchestrator.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitState,
)
from copy_that.pipeline.orchestrator.coordinator import (
    PipelineCoordinator,
    PipelineResult,
    PipelineStage,
    StageResult,
)

__all__ = [
    # Agent Pool
    "AgentPool",
    "TaskStatus",
    "TaskTracker",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerError",
    "CircuitState",
    # Coordinator
    "PipelineCoordinator",
    "PipelineResult",
    "PipelineStage",
    "StageResult",
]
