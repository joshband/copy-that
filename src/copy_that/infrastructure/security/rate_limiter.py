"""
Rate limiting and quota tracking for expensive API endpoints.

This module provides environment-aware rate limiting:
- Production: Enforces strict rate limits to protect against abuse
- Development: Tracks usage without enforcement (doesn't block development)
- Testing: Uses mock implementation for fast tests
"""

import asyncio
import logging
import os
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from fastapi import HTTPException, Request, status
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger(__name__)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
MOCK_MODE = os.getenv("TESTING", "false").lower() == "true"


@dataclass
class QuotaUsage:
    """Tracks API quota usage for a single key/IP."""

    key: str
    requests_count: int = 0
    estimated_cost: float = 0.0
    last_request_time: float | None = None
    window_start: float = field(default_factory=time.time)

    def reset_window_if_needed(self, window_seconds: int = 60) -> None:
        """Reset the window if it's expired."""
        if time.time() - self.window_start > window_seconds:
            self.requests_count = 0
            self.estimated_cost = 0.0
            self.window_start = time.time()

    def is_rate_limited(self, max_requests: int, window_seconds: int = 60) -> bool:
        """Check if this key is rate limited."""
        self.reset_window_if_needed(window_seconds)
        return self.requests_count >= max_requests

    def record_request(self, cost: float = 0.0) -> None:
        """Record a new request."""
        self.requests_count += 1
        self.estimated_cost += cost
        self.last_request_time = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging/monitoring."""
        return {
            "key": self.key,
            "requests_count": self.requests_count,
            "estimated_cost": f"${self.estimated_cost:.4f}",
            "last_request_time": (
                datetime.fromtimestamp(self.last_request_time).isoformat()
                if self.last_request_time
                else None
            ),
            "window_start": datetime.fromtimestamp(self.window_start).isoformat(),
        }


class QuotaStore:
    """In-memory quota tracking store."""

    def __init__(self) -> None:
        self._quotas: dict[str, QuotaUsage] = defaultdict(lambda: QuotaUsage(key=""))
        self._lock = asyncio.Lock()

    async def get_or_create(self, key: str) -> QuotaUsage:
        """Get or create quota for a key."""
        async with self._lock:
            if key not in self._quotas:
                self._quotas[key] = QuotaUsage(key=key)
            return self._quotas[key]

    async def record_request(self, key: str, cost: float = 0.0) -> QuotaUsage:
        """Record a request and return updated quota."""
        quota = await self.get_or_create(key)
        quota.record_request(cost)
        return quota

    async def check_limit(
        self, key: str, max_requests: int, window_seconds: int = 60
    ) -> tuple[bool, QuotaUsage]:
        """Check if key is rate limited. Returns (is_limited, quota)."""
        quota = await self.get_or_create(key)
        is_limited = quota.is_rate_limited(max_requests, window_seconds)
        return is_limited, quota

    async def get_stats(self, key: str) -> dict[str, Any]:
        """Get quota stats for a key."""
        quota = await self.get_or_create(key)
        quota.reset_window_if_needed()
        return quota.to_dict()

    async def reset(self, key: str | None = None) -> None:
        """Reset quota for a key or all keys."""
        async with self._lock:
            if key:
                if key in self._quotas:
                    self._quotas[key] = QuotaUsage(key=key)
            else:
                self._quotas.clear()

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get stats for all keys (for monitoring)."""
        return {key: quota.to_dict() for key, quota in self._quotas.items()}


# Global quota store
quota_store = QuotaStore()


class RateLimiter:
    """Redis-based rate limiting (legacy support)"""

    def __init__(self, redis_client: Any) -> None:
        self.redis = redis_client

    async def check_rate_limit(
        self, key: str, limit: int, window_seconds: int
    ) -> tuple[bool, int, int]:
        """Check if request is within rate limit"""
        current_time = int(time.time())
        window_start = current_time - window_seconds
        rate_key = f"ratelimit:{key}"

        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(rate_key, 0, window_start)
        pipe.zcard(rate_key)
        pipe.zadd(rate_key, {str(current_time): current_time})
        pipe.expire(rate_key, window_seconds)

        results = await pipe.execute()
        request_count = results[1]

        remaining = max(0, limit - request_count - 1)
        reset_at = current_time + window_seconds

        if request_count >= limit:
            return False, 0, reset_at

        return True, remaining, reset_at


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting"""

    def __init__(
        self,
        app: Starlette,
        redis_client: Any,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ) -> None:
        super().__init__(app)
        self.limiter = RateLimiter(redis_client)
        self.per_minute = requests_per_minute
        self.per_hour = requests_per_hour
        self.enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip rate limiting if disabled or for health checks
        if not self.enabled or request.url.path in ["/health", "/health/ready", "/health/live"]:
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)

        try:
            # Check minute limit
            allowed, remaining, reset = await self.limiter.check_rate_limit(
                f"{client_id}:minute", self.per_minute, 60
            )

            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded (per minute)",
                    headers={
                        "X-RateLimit-Limit": str(self.per_minute),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset),
                        "Retry-After": str(reset - int(time.time())),
                    },
                )

            # Check hour limit
            allowed, remaining_hour, reset_hour = await self.limiter.check_rate_limit(
                f"{client_id}:hour", self.per_hour, 3600
            )

            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded (per hour)",
                    headers={
                        "X-RateLimit-Limit": str(self.per_hour),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset_hour),
                        "Retry-After": str(reset_hour - int(time.time())),
                    },
                )

            # Process request
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(self.per_minute)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset)

            return response

        except HTTPException:
            raise
        except Exception:
            # If Redis is unavailable, allow the request
            return await call_next(request)

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user ID from state (set by auth middleware)
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        if request.client:
            return f"ip:{request.client.host}"

        return "ip:unknown"


class InMemoryRateLimiter:
    """Simple in-memory rate limiter for when Redis is unavailable."""

    def __init__(self) -> None:
        self._requests: dict[str, list[float]] = {}

    def check_rate_limit(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int, int]:
        """Check if request is within rate limit (synchronous)."""
        current_time = time.time()
        window_start = current_time - window_seconds

        # Get or create request list for this key
        if key not in self._requests:
            self._requests[key] = []

        # Remove old entries
        self._requests[key] = [t for t in self._requests[key] if t > window_start]

        # Check limit
        request_count = len(self._requests[key])
        if request_count >= limit:
            reset_at = int(current_time + window_seconds)
            return False, 0, reset_at

        # Add current request
        self._requests[key].append(current_time)

        remaining = max(0, limit - request_count - 1)
        reset_at = int(current_time + window_seconds)
        return True, remaining, reset_at


# Global in-memory rate limiter instance (fallback when Redis unavailable)
_memory_limiter = InMemoryRateLimiter()


def reset_rate_limiter() -> None:
    """Reset the global rate limiter state. Useful for testing."""
    global _memory_limiter
    _memory_limiter = InMemoryRateLimiter()


def rate_limit(requests: int, seconds: int) -> Any:
    """
    Dependency for endpoint-specific rate limits.

    Usage:
        @router.post("/expensive-endpoint")
        async def expensive_endpoint(
            request: Request,
            _rate_limit: None = Depends(rate_limit(requests=10, seconds=60))
        ):
            ...

    Args:
        requests: Maximum number of requests allowed in the time window
        seconds: Time window in seconds

    Raises:
        HTTPException: 429 Too Many Requests if rate limit exceeded
    """

    async def dependency(request: Request) -> None:
        # Get client identifier
        client_id = _get_client_identifier(request)
        endpoint = request.url.path
        rate_key = f"{client_id}:{endpoint}"

        # Mock mode: skip rate limiting (for tests)
        if MOCK_MODE:
            return

        # Development mode: only track usage
        if ENVIRONMENT in ("local", "development"):
            allowed, remaining, reset_at = _memory_limiter.check_rate_limit(
                rate_key, requests, seconds
            )
            if not allowed:
                logger.warning(
                    "Rate limit would be exceeded in production: %s - %d requests",
                    client_id,
                    remaining,
                )
            return

        # Production mode: enforce limits
        allowed, remaining, reset_at = _memory_limiter.check_rate_limit(rate_key, requests, seconds)

        if not allowed:
            retry_after = max(1, reset_at - int(time.time()))
            logger.error("Rate limit exceeded: %s", client_id)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {requests} requests per {seconds} seconds.",
                headers={
                    "X-RateLimit-Limit": str(requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_at),
                    "Retry-After": str(retry_after),
                },
            )

    return dependency


def _get_client_identifier(request: Request) -> str:
    """Get client identifier for rate limiting."""
    # Try to get user ID from state (set by auth middleware)
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.id}"

    # Fall back to IP address
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return f"ip:{forwarded.split(',')[0].strip()}"

    if request.client:
        return f"ip:{request.client.host}"

    return "ip:unknown"
