"""CircuitBreaker pattern for fault tolerance.

Prevents cascading failures by failing fast when a service is unhealthy.
"""

import asyncio
import time
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Any, TypeVar

T = TypeVar("T")


class CircuitState(str, Enum):
    """States of a circuit breaker."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker prevents execution."""

    pass


class CircuitBreaker:
    """Circuit breaker for preventing cascading failures.

    States:
    - CLOSED: Normal operation, failures are counted
    - OPEN: Circuit is tripped, calls fail immediately
    - HALF_OPEN: Testing if service has recovered

    Example:
        breaker = CircuitBreaker("api", failure_threshold=5)
        result = await breaker.call(some_async_function)
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        on_state_change: Callable[[str, CircuitState, CircuitState], None] | None = None,
        excluded_exceptions: tuple[type[Exception], ...] = (),
    ):
        """Initialize the circuit breaker.

        Args:
            name: Identifier for this breaker
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds to wait before attempting recovery
            on_state_change: Callback when state changes
            excluded_exceptions: Exception types that don't count as failures

        Raises:
            ValueError: If threshold or timeout is not positive
        """
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")
        if recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be positive")

        self._name = name
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._on_state_change = on_state_change
        self._excluded_exceptions = excluded_exceptions

        # State
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._total_calls = 0
        self._last_failure_time: float | None = None
        self._last_state_change_time = time.time()

        # Lock for thread safety
        self._lock = asyncio.Lock()

        # Half-open probe lock
        self._probe_lock = asyncio.Lock()
        self._probe_in_progress = False

    @property
    def name(self) -> str:
        """Get breaker name."""
        return self._name

    @property
    def state(self) -> CircuitState:
        """Get current state."""
        return self._state

    @property
    def failure_threshold(self) -> int:
        """Get failure threshold."""
        return self._failure_threshold

    @property
    def recovery_timeout(self) -> float:
        """Get recovery timeout."""
        return self._recovery_timeout

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed."""
        return self._state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if circuit is open."""
        return self._state == CircuitState.OPEN

    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open."""
        return self._state == CircuitState.HALF_OPEN

    @property
    def last_failure_time(self) -> float | None:
        """Get timestamp of last failure."""
        return self._last_failure_time

    @property
    def time_in_state(self) -> float:
        """Get time in current state in seconds."""
        return time.time() - self._last_state_change_time

    async def call(self, func: Callable[[], Awaitable[T]]) -> T:
        """Execute a function through the circuit breaker.

        Args:
            func: Async callable to execute

        Returns:
            Result from the function

        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Any exception from the function
        """
        async with self._lock:
            await self._check_state()

            if self._state == CircuitState.OPEN:
                raise CircuitBreakerError(f"Circuit is open: {self._name}")

            if self._state == CircuitState.HALF_OPEN:
                # Only allow one probe at a time
                if self._probe_in_progress:
                    raise CircuitBreakerError(f"Circuit is half-open, probe in progress: {self._name}")
                self._probe_in_progress = True

        try:
            self._total_calls += 1
            result = await func()

            # Success
            async with self._lock:
                await self._on_success()

            return result

        except Exception as e:
            # Check if exception should be excluded
            if isinstance(e, self._excluded_exceptions):
                async with self._lock:
                    if self._state == CircuitState.HALF_OPEN:
                        self._probe_in_progress = False
                raise

            # Record failure
            async with self._lock:
                await self._on_failure()

            raise

    async def _check_state(self) -> None:
        """Check if state should transition based on time."""
        if (
            self._state == CircuitState.OPEN
            and self._last_failure_time
            and time.time() - self._last_failure_time >= self._recovery_timeout
        ):
            await self._transition_to(CircuitState.HALF_OPEN)

    async def _on_success(self) -> None:
        """Handle successful call."""
        self._success_count += 1

        if self._state == CircuitState.HALF_OPEN:
            # Recovery successful
            self._probe_in_progress = False
            self._failure_count = 0
            await self._transition_to(CircuitState.CLOSED)
        elif self._state == CircuitState.CLOSED:
            # Reset failure count on success
            self._failure_count = 0

    async def _on_failure(self) -> None:
        """Handle failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            # Recovery failed
            self._probe_in_progress = False
            await self._transition_to(CircuitState.OPEN)
        elif self._state == CircuitState.CLOSED:
            # Check threshold
            if self._failure_count >= self._failure_threshold:
                await self._transition_to(CircuitState.OPEN)

    async def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state.

        Args:
            new_state: The state to transition to
        """
        old_state = self._state
        self._state = new_state
        self._last_state_change_time = time.time()

        if self._on_state_change and old_state != new_state:
            self._on_state_change(self._name, old_state, new_state)

    def reset(self) -> None:
        """Reset the circuit breaker to closed state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._last_state_change_time = time.time()
        self._probe_in_progress = False

    def trip(self) -> None:
        """Manually trip the circuit breaker to open state."""
        self._state = CircuitState.OPEN
        self._last_failure_time = time.time()
        self._last_state_change_time = time.time()

    def get_stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics.

        Returns:
            Dictionary with breaker statistics
        """
        return {
            "name": self._name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self._failure_threshold,
            "recovery_timeout": self._recovery_timeout,
            "success_count": self._success_count,
            "total_calls": self._total_calls,
            "last_failure_time": self._last_failure_time,
            "time_in_state": self.time_in_state,
        }

    async def __aenter__(self) -> "CircuitBreaker":
        """Async context manager entry."""
        async with self._lock:
            await self._check_state()

            if self._state == CircuitState.OPEN:
                raise CircuitBreakerError(f"Circuit is open: {self._name}")

            if self._state == CircuitState.HALF_OPEN:
                if self._probe_in_progress:
                    raise CircuitBreakerError(f"Circuit is half-open, probe in progress: {self._name}")
                self._probe_in_progress = True

        self._total_calls += 1
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Async context manager exit."""
        if exc_type is None:
            async with self._lock:
                await self._on_success()
        else:
            # Check if exception should be excluded
            if exc_type and issubclass(exc_type, self._excluded_exceptions):
                async with self._lock:
                    if self._state == CircuitState.HALF_OPEN:
                        self._probe_in_progress = False
                return

            async with self._lock:
                await self._on_failure()
