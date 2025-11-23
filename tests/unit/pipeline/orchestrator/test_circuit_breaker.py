"""Tests for CircuitBreaker pattern implementation.

Tests written FIRST following TDD principles.
"""

import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest

from copy_that.pipeline.orchestrator.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitState,
)


class TestCircuitState:
    """Tests for CircuitState enum."""

    def test_states_exist(self):
        """Test all required states exist."""
        assert CircuitState.CLOSED is not None
        assert CircuitState.OPEN is not None
        assert CircuitState.HALF_OPEN is not None

    def test_state_values(self):
        """Test state string values."""
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"


class TestCircuitBreaker:
    """Tests for CircuitBreaker pattern."""

    @pytest.fixture
    def breaker(self):
        """Create a circuit breaker for testing."""
        return CircuitBreaker(
            name="test-breaker",
            failure_threshold=3,
            recovery_timeout=1.0,
        )

    def test_init_default_values(self):
        """Test default initialization."""
        breaker = CircuitBreaker(name="test")
        assert breaker.name == "test"
        assert breaker.failure_threshold == 5
        assert breaker.recovery_timeout == 30.0
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_init_custom_values(self):
        """Test custom initialization."""
        breaker = CircuitBreaker(
            name="custom",
            failure_threshold=10,
            recovery_timeout=60.0,
        )
        assert breaker.failure_threshold == 10
        assert breaker.recovery_timeout == 60.0

    def test_init_invalid_threshold(self):
        """Test invalid threshold raises error."""
        with pytest.raises(ValueError, match="must be positive"):
            CircuitBreaker(name="test", failure_threshold=0)

    def test_init_invalid_timeout(self):
        """Test invalid timeout raises error."""
        with pytest.raises(ValueError, match="must be positive"):
            CircuitBreaker(name="test", recovery_timeout=0)

    def test_initial_state_closed(self, breaker):
        """Test initial state is closed."""
        assert breaker.state == CircuitState.CLOSED
        assert breaker.is_closed
        assert not breaker.is_open
        assert not breaker.is_half_open

    @pytest.mark.asyncio
    async def test_successful_call(self, breaker):
        """Test successful call through closed breaker."""
        async def success():
            return "ok"

        result = await breaker.call(success)

        assert result == "ok"
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_single_failure(self, breaker):
        """Test single failure increments counter."""
        async def fail():
            raise ValueError("test error")

        with pytest.raises(ValueError):
            await breaker.call(fail)

        assert breaker.failure_count == 1
        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_failure_threshold_opens_circuit(self, breaker):
        """Test reaching threshold opens circuit."""
        async def fail():
            raise ValueError("test error")

        # Fail up to threshold
        for i in range(3):
            with pytest.raises(ValueError):
                await breaker.call(fail)

        assert breaker.failure_count == 3
        assert breaker.state == CircuitState.OPEN
        assert breaker.is_open

    @pytest.mark.asyncio
    async def test_open_circuit_rejects_calls(self, breaker):
        """Test open circuit rejects new calls."""
        async def fail():
            raise ValueError("test error")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await breaker.call(fail)

        # Next call should be rejected
        async def should_not_run():
            return "never"

        with pytest.raises(CircuitBreakerError, match="Circuit is open"):
            await breaker.call(should_not_run)

    @pytest.mark.asyncio
    async def test_recovery_timeout_to_half_open(self, breaker):
        """Test circuit transitions to half-open after timeout."""
        async def fail():
            raise ValueError("test error")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await breaker.call(fail)

        assert breaker.state == CircuitState.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(1.1)

        # Next call should be allowed (half-open)
        async def success():
            return "recovered"

        result = await breaker.call(success)

        assert result == "recovered"
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_half_open_failure_reopens(self, breaker):
        """Test failure in half-open state reopens circuit."""
        async def fail():
            raise ValueError("test error")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await breaker.call(fail)

        # Wait for recovery
        await asyncio.sleep(1.1)

        # Fail in half-open state
        with pytest.raises(ValueError):
            await breaker.call(fail)

        # Should be open again
        assert breaker.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_half_open_allows_single_probe(self, breaker):
        """Test half-open state allows only one probe call."""
        async def fail():
            raise ValueError("test error")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await breaker.call(fail)

        # Wait for recovery
        await asyncio.sleep(1.1)

        # Start a slow call
        slow_started = asyncio.Event()

        async def slow_success():
            slow_started.set()
            await asyncio.sleep(0.5)
            return "ok"

        # Start slow call
        task = asyncio.create_task(breaker.call(slow_success))

        # Wait for it to start
        await slow_started.wait()

        # Second call should be rejected while probe is in progress
        async def should_not_run():
            return "never"

        with pytest.raises(CircuitBreakerError, match="Circuit is half-open"):
            await breaker.call(should_not_run)

        # Wait for slow call to complete
        result = await task
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_success_resets_failure_count(self, breaker):
        """Test successful call resets failure count."""
        async def fail():
            raise ValueError("test error")

        async def success():
            return "ok"

        # Accumulate some failures
        for _ in range(2):
            with pytest.raises(ValueError):
                await breaker.call(fail)

        assert breaker.failure_count == 2

        # Success should reset
        await breaker.call(success)

        assert breaker.failure_count == 0

    def test_reset(self, breaker):
        """Test manual reset of circuit breaker."""
        # Manually set state
        breaker._state = CircuitState.OPEN
        breaker._failure_count = 5

        breaker.reset()

        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_trip(self, breaker):
        """Test manual trip of circuit breaker."""
        assert breaker.state == CircuitState.CLOSED

        breaker.trip()

        assert breaker.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test circuit breaker as context manager."""
        breaker = CircuitBreaker(name="ctx-test", failure_threshold=2)

        async with breaker:
            # Should work
            pass

        assert breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_context_manager_failure(self):
        """Test context manager records failures."""
        breaker = CircuitBreaker(name="ctx-test", failure_threshold=2)

        with pytest.raises(ValueError):
            async with breaker:
                raise ValueError("test error")

        assert breaker.failure_count == 1

    @pytest.mark.asyncio
    async def test_get_stats(self, breaker):
        """Test getting breaker statistics."""
        async def fail():
            raise ValueError("test error")

        async def success():
            return "ok"

        await breaker.call(success)

        for _ in range(2):
            with pytest.raises(ValueError):
                await breaker.call(fail)

        stats = breaker.get_stats()

        assert stats["name"] == "test-breaker"
        assert stats["state"] == "closed"
        assert stats["failure_count"] == 2
        assert stats["failure_threshold"] == 3
        assert stats["success_count"] >= 1
        assert stats["total_calls"] >= 3

    @pytest.mark.asyncio
    async def test_on_state_change_callback(self):
        """Test callback is called on state change."""
        state_changes = []

        def on_change(name, old_state, new_state):
            state_changes.append((name, old_state, new_state))

        breaker = CircuitBreaker(
            name="callback-test",
            failure_threshold=2,
            on_state_change=on_change,
        )

        async def fail():
            raise ValueError("test error")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                await breaker.call(fail)

        assert len(state_changes) == 1
        assert state_changes[0] == (
            "callback-test",
            CircuitState.CLOSED,
            CircuitState.OPEN,
        )

    @pytest.mark.asyncio
    async def test_excluded_exceptions(self):
        """Test excluded exceptions don't count as failures."""
        breaker = CircuitBreaker(
            name="exclude-test",
            failure_threshold=2,
            excluded_exceptions=(KeyError,),
        )

        async def key_error():
            raise KeyError("not found")

        async def value_error():
            raise ValueError("bad value")

        # KeyError should not count
        with pytest.raises(KeyError):
            await breaker.call(key_error)

        assert breaker.failure_count == 0

        # ValueError should count
        with pytest.raises(ValueError):
            await breaker.call(value_error)

        assert breaker.failure_count == 1

    @pytest.mark.asyncio
    async def test_concurrent_calls_in_closed_state(self, breaker):
        """Test concurrent calls work in closed state."""
        results = []

        async def slow_success(n):
            await asyncio.sleep(0.05)
            return f"result-{n}"

        tasks = [breaker.call(lambda n=i: slow_success(n)) for i in range(5)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 5
        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_time_in_state(self, breaker):
        """Test tracking time in current state."""
        await asyncio.sleep(0.1)

        time_in_state = breaker.time_in_state
        assert time_in_state >= 0.1

    @pytest.mark.asyncio
    async def test_last_failure_time(self, breaker):
        """Test last failure time is recorded."""
        assert breaker.last_failure_time is None

        async def fail():
            raise ValueError("test error")

        with pytest.raises(ValueError):
            await breaker.call(fail)

        assert breaker.last_failure_time is not None
        assert time.time() - breaker.last_failure_time < 1.0
