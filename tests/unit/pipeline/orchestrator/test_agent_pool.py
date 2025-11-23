"""Tests for AgentPool with semaphore-based concurrency control.

Tests written FIRST following TDD principles.
"""

import asyncio

import pytest

from copy_that.pipeline import BasePipelineAgent, PipelineTask, TokenResult, TokenType
from copy_that.pipeline.orchestrator.agent_pool import AgentPool, TaskStatus, TaskTracker


class MockAgent(BasePipelineAgent):
    """Mock agent for testing."""

    def __init__(
        self,
        agent_type: str = "mock",
        stage: str = "test",
        delay: float = 0.0,
        should_fail: bool = False,
    ):
        self._agent_type = agent_type
        self._stage = stage
        self._delay = delay
        self._should_fail = should_fail
        self.process_count = 0

    @property
    def agent_type(self) -> str:
        return self._agent_type

    @property
    def stage_name(self) -> str:
        return self._stage

    async def process(self, task: PipelineTask) -> list[TokenResult]:
        self.process_count += 1
        if self._delay > 0:
            await asyncio.sleep(self._delay)
        if self._should_fail:
            raise Exception("Mock agent failure")
        return [
            TokenResult(
                token_type=TokenType.COLOR,
                name="test",
                value="#000000",
                confidence=0.9,
            )
        ]

    async def health_check(self) -> bool:
        return True


class TestTaskTracker:
    """Tests for TaskTracker dataclass."""

    def test_create_tracker(self):
        """Test creating a task tracker."""
        tracker = TaskTracker(
            task_id="task-1",
            stage="extraction",
            status=TaskStatus.PENDING,
        )
        assert tracker.task_id == "task-1"
        assert tracker.stage == "extraction"
        assert tracker.status == TaskStatus.PENDING
        assert tracker.started_at is None
        assert tracker.completed_at is None
        assert tracker.error is None

    def test_tracker_status_transitions(self):
        """Test tracker status can be updated."""
        tracker = TaskTracker(
            task_id="task-1",
            stage="extraction",
            status=TaskStatus.PENDING,
        )
        tracker.status = TaskStatus.RUNNING
        assert tracker.status == TaskStatus.RUNNING

        tracker.status = TaskStatus.COMPLETED
        assert tracker.status == TaskStatus.COMPLETED


class TestAgentPool:
    """Tests for AgentPool concurrency management."""

    @pytest.fixture
    def agent_pool(self):
        """Create an agent pool for testing."""
        return AgentPool(max_concurrency=3)

    @pytest.fixture
    def mock_task(self):
        """Create a mock pipeline task."""
        return PipelineTask(
            task_id="test-task-1",
            image_url="https://example.com/test.png",
            token_types=[TokenType.COLOR],
        )

    def test_init_default_concurrency(self):
        """Test default concurrency limit."""
        pool = AgentPool()
        assert pool.max_concurrency == 5
        assert pool.active_count == 0
        assert pool.completed_count == 0
        assert pool.failed_count == 0

    def test_init_custom_concurrency(self):
        """Test custom concurrency limit."""
        pool = AgentPool(max_concurrency=10)
        assert pool.max_concurrency == 10

    def test_init_invalid_concurrency(self):
        """Test invalid concurrency raises error."""
        with pytest.raises(ValueError, match="must be positive"):
            AgentPool(max_concurrency=0)
        with pytest.raises(ValueError, match="must be positive"):
            AgentPool(max_concurrency=-1)

    @pytest.mark.asyncio
    async def test_submit_task(self, agent_pool, mock_task):
        """Test submitting a task to the pool."""
        agent = MockAgent()
        result = await agent_pool.submit(agent, mock_task)

        assert len(result) == 1
        assert result[0].name == "test"
        assert agent_pool.completed_count == 1
        assert agent_pool.active_count == 0

    @pytest.mark.asyncio
    async def test_submit_with_delay(self, mock_task):
        """Test submitting tasks with processing delay."""
        pool = AgentPool(max_concurrency=2)
        agent = MockAgent(delay=0.1)

        result = await pool.submit(agent, mock_task)

        assert len(result) == 1
        assert pool.completed_count == 1

    @pytest.mark.asyncio
    async def test_concurrent_task_limit(self):
        """Test that concurrency limit is enforced."""
        pool = AgentPool(max_concurrency=2)
        agent = MockAgent(delay=0.1)

        tasks = [
            PipelineTask(
                task_id=f"task-{i}",
                image_url=f"https://example.com/{i}.png",
                token_types=[TokenType.COLOR],
            )
            for i in range(5)
        ]

        # Track max concurrent executions
        max_concurrent = 0
        concurrent_count = 0
        lock = asyncio.Lock()

        original_process = agent.process

        async def tracking_process(task):
            nonlocal max_concurrent, concurrent_count
            async with lock:
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)
            try:
                return await original_process(task)
            finally:
                async with lock:
                    concurrent_count -= 1

        agent.process = tracking_process

        # Submit all tasks concurrently
        results = await asyncio.gather(*[pool.submit(agent, task) for task in tasks])

        assert len(results) == 5
        assert max_concurrent <= 2
        assert pool.completed_count == 5

    @pytest.mark.asyncio
    async def test_failed_task_tracking(self, agent_pool, mock_task):
        """Test that failed tasks are tracked correctly."""
        agent = MockAgent(should_fail=True)

        with pytest.raises(Exception, match="Mock agent failure"):
            await agent_pool.submit(agent, mock_task)

        assert agent_pool.failed_count == 1
        assert agent_pool.completed_count == 0
        assert agent_pool.active_count == 0

    @pytest.mark.asyncio
    async def test_get_task_status(self, agent_pool, mock_task):
        """Test retrieving task status."""
        agent = MockAgent()
        await agent_pool.submit(agent, mock_task)

        status = agent_pool.get_task_status(mock_task.task_id)
        assert status is not None
        assert status.status == TaskStatus.COMPLETED
        assert status.started_at is not None
        assert status.completed_at is not None

    @pytest.mark.asyncio
    async def test_get_task_status_not_found(self, agent_pool):
        """Test retrieving status for unknown task."""
        status = agent_pool.get_task_status("unknown-task")
        assert status is None

    @pytest.mark.asyncio
    async def test_clear_completed_tasks(self, agent_pool, mock_task):
        """Test clearing completed tasks from tracking."""
        agent = MockAgent()
        await agent_pool.submit(agent, mock_task)

        assert agent_pool.completed_count == 1

        agent_pool.clear_completed()

        assert agent_pool.completed_count == 0
        assert agent_pool.get_task_status(mock_task.task_id) is None

    @pytest.mark.asyncio
    async def test_stage_specific_concurrency(self):
        """Test per-stage concurrency limits."""
        pool = AgentPool(
            max_concurrency=5,
            stage_limits={"extraction": 2, "validation": 3},
        )

        assert pool.get_stage_limit("extraction") == 2
        assert pool.get_stage_limit("validation") == 3
        assert pool.get_stage_limit("preprocessing") == 5  # Default

    @pytest.mark.asyncio
    async def test_stage_concurrency_enforcement(self):
        """Test that stage-specific limits are enforced."""
        pool = AgentPool(
            max_concurrency=10,
            stage_limits={"test": 2},
        )
        agent = MockAgent(delay=0.1)

        tasks = [
            PipelineTask(
                task_id=f"task-{i}",
                image_url=f"https://example.com/{i}.png",
                token_types=[TokenType.COLOR],
            )
            for i in range(5)
        ]

        # Track max concurrent for the stage
        max_concurrent = 0
        concurrent_count = 0
        lock = asyncio.Lock()

        original_process = agent.process

        async def tracking_process(task):
            nonlocal max_concurrent, concurrent_count
            async with lock:
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)
            try:
                return await original_process(task)
            finally:
                async with lock:
                    concurrent_count -= 1

        agent.process = tracking_process

        results = await asyncio.gather(*[pool.submit(agent, task) for task in tasks])

        assert len(results) == 5
        assert max_concurrent <= 2  # Stage limit

    @pytest.mark.asyncio
    async def test_get_stats(self, agent_pool, mock_task):
        """Test getting pool statistics."""
        agent = MockAgent()
        await agent_pool.submit(agent, mock_task)

        stats = agent_pool.get_stats()

        assert stats["active"] == 0
        assert stats["completed"] == 1
        assert stats["failed"] == 0
        assert stats["total"] == 1
        assert stats["max_concurrency"] == 3

    @pytest.mark.asyncio
    async def test_reset_pool(self, agent_pool, mock_task):
        """Test resetting the pool."""
        agent = MockAgent()
        await agent_pool.submit(agent, mock_task)

        assert agent_pool.completed_count == 1

        agent_pool.reset()

        assert agent_pool.active_count == 0
        assert agent_pool.completed_count == 0
        assert agent_pool.failed_count == 0

    @pytest.mark.asyncio
    async def test_parallel_different_agents(self, agent_pool):
        """Test running different agents in parallel."""
        agent1 = MockAgent(agent_type="agent1", delay=0.05)
        agent2 = MockAgent(agent_type="agent2", delay=0.05)

        task1 = PipelineTask(
            task_id="task-1",
            image_url="https://example.com/1.png",
            token_types=[TokenType.COLOR],
        )
        task2 = PipelineTask(
            task_id="task-2",
            image_url="https://example.com/2.png",
            token_types=[TokenType.COLOR],
        )

        results = await asyncio.gather(
            agent_pool.submit(agent1, task1),
            agent_pool.submit(agent2, task2),
        )

        assert len(results) == 2
        assert agent1.process_count == 1
        assert agent2.process_count == 1
        assert agent_pool.completed_count == 2

    @pytest.mark.asyncio
    async def test_task_timeout(self):
        """Test task timeout handling."""
        pool = AgentPool(max_concurrency=3, task_timeout=0.1)
        agent = MockAgent(delay=1.0)  # Will timeout

        task = PipelineTask(
            task_id="timeout-task",
            image_url="https://example.com/timeout.png",
            token_types=[TokenType.COLOR],
        )

        with pytest.raises(asyncio.TimeoutError):
            await pool.submit(agent, task)

        assert pool.failed_count == 1

    @pytest.mark.asyncio
    async def test_shutdown(self, agent_pool):
        """Test graceful shutdown."""
        agent = MockAgent(delay=0.5)

        task = PipelineTask(
            task_id="shutdown-task",
            image_url="https://example.com/shutdown.png",
            token_types=[TokenType.COLOR],
        )

        # Start a task
        task_future = asyncio.create_task(agent_pool.submit(agent, task))

        # Give it time to start
        await asyncio.sleep(0.1)

        # Shutdown should wait for completion
        await agent_pool.shutdown(wait=True)

        # Task should complete
        result = await task_future
        assert len(result) == 1
