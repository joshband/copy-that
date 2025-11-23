"""AgentPool for managing concurrent pipeline agent execution.

Provides semaphore-based concurrency control with task tracking.
"""

import asyncio
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from copy_that.pipeline import BasePipelineAgent, PipelineTask, TokenResult


class TaskStatus(str, Enum):
    """Status of a task in the pool."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskTracker:
    """Tracks the status and metadata of a task."""

    task_id: str
    stage: str
    status: TaskStatus
    started_at: float | None = None
    completed_at: float | None = None
    error: str | None = None
    result: list[TokenResult] | None = None


class AgentPool:
    """Pool for managing concurrent agent task execution.

    Uses semaphores to enforce concurrency limits globally and per-stage.
    Tracks task status for monitoring and debugging.

    Example:
        pool = AgentPool(max_concurrency=5)
        result = await pool.submit(agent, task)
    """

    def __init__(
        self,
        max_concurrency: int = 5,
        stage_limits: dict[str, int] | None = None,
        task_timeout: float | None = None,
    ):
        """Initialize the agent pool.

        Args:
            max_concurrency: Maximum concurrent tasks globally
            stage_limits: Per-stage concurrency limits
            task_timeout: Optional timeout for task execution in seconds

        Raises:
            ValueError: If max_concurrency is not positive
        """
        if max_concurrency <= 0:
            raise ValueError("max_concurrency must be positive")

        self._max_concurrency = max_concurrency
        self._stage_limits = stage_limits or {}
        self._task_timeout = task_timeout

        # Global semaphore
        self._global_semaphore = asyncio.Semaphore(max_concurrency)

        # Per-stage semaphores
        self._stage_semaphores: dict[str, asyncio.Semaphore] = {}
        for stage, limit in self._stage_limits.items():
            self._stage_semaphores[stage] = asyncio.Semaphore(limit)

        # Task tracking
        self._tasks: dict[str, TaskTracker] = {}
        self._lock = asyncio.Lock()

        # Counters
        self._active_count = 0
        self._completed_count = 0
        self._failed_count = 0

        # Shutdown flag
        self._shutting_down = False

    @property
    def max_concurrency(self) -> int:
        """Get maximum global concurrency."""
        return self._max_concurrency

    @property
    def active_count(self) -> int:
        """Get number of currently active tasks."""
        return self._active_count

    @property
    def completed_count(self) -> int:
        """Get number of completed tasks."""
        return self._completed_count

    @property
    def failed_count(self) -> int:
        """Get number of failed tasks."""
        return self._failed_count

    def get_stage_limit(self, stage: str) -> int:
        """Get concurrency limit for a stage.

        Args:
            stage: Stage name

        Returns:
            Stage-specific limit or global max_concurrency
        """
        return self._stage_limits.get(stage, self._max_concurrency)

    async def submit(
        self,
        agent: BasePipelineAgent,
        task: PipelineTask,
    ) -> list[TokenResult]:
        """Submit a task for execution.

        Args:
            agent: The agent to execute the task
            task: The pipeline task to execute

        Returns:
            List of TokenResults from the agent

        Raises:
            Exception: Any exception raised by the agent
            asyncio.TimeoutError: If task exceeds timeout
        """
        stage = agent.stage_name

        # Get or create stage semaphore
        if stage not in self._stage_semaphores:
            async with self._lock:
                if stage not in self._stage_semaphores:
                    limit = self._stage_limits.get(stage, self._max_concurrency)
                    self._stage_semaphores[stage] = asyncio.Semaphore(limit)

        stage_semaphore = self._stage_semaphores[stage]

        # Create tracker
        tracker = TaskTracker(
            task_id=task.task_id,
            stage=stage,
            status=TaskStatus.PENDING,
        )

        async with self._lock:
            self._tasks[task.task_id] = tracker

        try:
            # Acquire both semaphores
            async with self._global_semaphore, stage_semaphore:
                # Update status to running
                async with self._lock:
                    tracker.status = TaskStatus.RUNNING
                    tracker.started_at = time.time()
                    self._active_count += 1

                try:
                    # Execute with optional timeout
                    if self._task_timeout:
                        result = await asyncio.wait_for(
                            agent.process(task),
                            timeout=self._task_timeout,
                        )
                    else:
                        result = await agent.process(task)

                    # Handle non-list results (e.g., ProcessedImage)
                    if not isinstance(result, list):
                        # Wrap in list for consistency
                        result = [result]  # type: ignore[list-item]

                    # Update tracker
                    async with self._lock:
                        tracker.status = TaskStatus.COMPLETED
                        tracker.completed_at = time.time()
                        tracker.result = result
                        self._active_count -= 1
                        self._completed_count += 1

                    return result

                except TimeoutError:
                    async with self._lock:
                        tracker.status = TaskStatus.FAILED
                        tracker.completed_at = time.time()
                        tracker.error = f"Task timed out after {self._task_timeout}s"
                        self._active_count -= 1
                        self._failed_count += 1
                    raise

                except Exception as e:
                    async with self._lock:
                        tracker.status = TaskStatus.FAILED
                        tracker.completed_at = time.time()
                        tracker.error = str(e)
                        self._active_count -= 1
                        self._failed_count += 1
                    raise

        except Exception:
            # Ensure counters are updated even if semaphore acquisition fails
            if tracker.status == TaskStatus.PENDING:
                async with self._lock:
                    tracker.status = TaskStatus.FAILED
                    tracker.completed_at = time.time()
                    self._failed_count += 1
            raise

    def get_task_status(self, task_id: str) -> TaskTracker | None:
        """Get the status tracker for a task.

        Args:
            task_id: The task identifier

        Returns:
            TaskTracker if found, None otherwise
        """
        return self._tasks.get(task_id)

    def clear_completed(self) -> None:
        """Clear all completed tasks from tracking."""
        completed_ids = [
            task_id
            for task_id, tracker in self._tasks.items()
            if tracker.status == TaskStatus.COMPLETED
        ]

        for task_id in completed_ids:
            del self._tasks[task_id]

        self._completed_count = 0

    def get_stats(self) -> dict[str, Any]:
        """Get pool statistics.

        Returns:
            Dictionary with pool statistics
        """
        return {
            "active": self._active_count,
            "completed": self._completed_count,
            "failed": self._failed_count,
            "total": self._completed_count + self._failed_count,
            "max_concurrency": self._max_concurrency,
            "stage_limits": self._stage_limits.copy(),
        }

    def reset(self) -> None:
        """Reset the pool state and counters."""
        self._tasks.clear()
        self._active_count = 0
        self._completed_count = 0
        self._failed_count = 0

    async def shutdown(self, wait: bool = True) -> None:
        """Shutdown the pool.

        Args:
            wait: If True, wait for active tasks to complete
        """
        self._shutting_down = True

        if wait and self._active_count > 0:
            # Wait for active tasks
            while self._active_count > 0:
                await asyncio.sleep(0.1)
