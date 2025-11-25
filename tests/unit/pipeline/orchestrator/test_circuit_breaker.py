import asyncio

import pytest

from copy_that.pipeline.orchestrator.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitState,
)


async def _failing_call():
    raise RuntimeError("boom")


async def _successful_call():
    return "ok"


@pytest.mark.asyncio
async def test_breaker_opens_after_threshold(monkeypatch):
    breaker = CircuitBreaker("test", failure_threshold=2, recovery_timeout=0.01)

    with pytest.raises(RuntimeError):
        await breaker.call(_failing_call)
    assert breaker.state == CircuitState.CLOSED

    with pytest.raises(RuntimeError):
        await breaker.call(_failing_call)
    assert breaker.is_open

    with pytest.raises(CircuitBreakerError):
        await breaker.call(_successful_call)

    # Wait for recovery timeout and allow probe
    await asyncio.sleep(0.02)
    result = await breaker.call(_successful_call)
    assert result == "ok"
    assert breaker.is_closed


@pytest.mark.asyncio
async def test_breaker_context_manager_handles_success_and_failure():
    breaker = CircuitBreaker("ctx", failure_threshold=1, recovery_timeout=0.1)

    async with breaker:
        pass
    assert breaker.is_closed

    with pytest.raises(RuntimeError):
        async with breaker:
            raise RuntimeError("ctx failure")

    assert breaker.is_open
