import asyncio

import pytest

from copy_that.pipeline import PipelineTask, TokenResult, TokenType
from copy_that.pipeline.interfaces import BasePipelineAgent
from copy_that.pipeline.orchestrator.agent_pool import AgentPool, TaskStatus


class _SimpleAgent(BasePipelineAgent):
    def __init__(
        self,
        stage_name: str,
        tokens: list[TokenResult],
        delay: float = 0.0,
        fail: bool = False,
    ) -> None:
        self._stage_name = stage_name
        self._tokens = tokens
        self._delay = delay
        self._fail = fail

    @property
    def agent_type(self) -> str:
        return f"{self._stage_name}_agent"

    @property
    def stage_name(self) -> str:
        return self._stage_name

    async def process(self, task: PipelineTask) -> list[TokenResult]:
        if self._delay:
            await asyncio.sleep(self._delay)
        if self._fail:
            raise RuntimeError("simulated failure")
        return self._tokens

    async def health_check(self) -> bool:
        return True


def _create_task(task_id: str) -> PipelineTask:
    return PipelineTask(
        task_id=task_id,
        image_url="http://example.com/image.png",
        token_types=[TokenType.COLOR],
    )


def _create_token(name: str) -> TokenResult:
    return TokenResult(
        token_type=TokenType.COLOR,
        name=name,
        value="#000000",
        confidence=0.5,
    )


@pytest.mark.asyncio
async def test_submit_success_tracks_stats():
    pool = AgentPool(max_concurrency=2, stage_limits={"extract": 1})
    agent = _SimpleAgent("extract", [_create_token("color")])
    task = _create_task("task-1")

    result = await pool.submit(agent, task)

    assert isinstance(result, list)
    assert len(result) == 1
    assert pool.completed_count == 1
    assert pool.failed_count == 0
    assert pool.active_count == 0

    tracker = pool.get_task_status(task.task_id)
    assert tracker is not None
    assert tracker.status == TaskStatus.COMPLETED
    assert tracker.result == result

    stats = pool.get_stats()
    assert stats["running"] == 0
    assert stats["completed"] == 1
    assert stats["stage_limits"]["extract"] == 1

    pool.clear_completed()
    assert pool.completed_count == 0
    assert pool.get_task_status(task.task_id) is None


@pytest.mark.asyncio
async def test_submit_timeout_marks_failed():
    pool = AgentPool(max_concurrency=1, task_timeout=0.01)
    agent = _SimpleAgent("extract", [_create_token("color")], delay=0.05)
    task = _create_task("timeout-task")

    with pytest.raises(asyncio.TimeoutError):
        await pool.submit(agent, task)

    assert pool.failed_count == 1
    tracker = pool.get_task_status(task.task_id)
    assert tracker is not None
    assert tracker.status == TaskStatus.FAILED


@pytest.mark.asyncio
async def test_submit_failure_updates_failed_count():
    pool = AgentPool(max_concurrency=1)
    agent = _SimpleAgent("extract", [_create_token("color")], fail=True)
    task = _create_task("failure-task")

    with pytest.raises(RuntimeError):
        await pool.submit(agent, task)

    assert pool.failed_count == 1
