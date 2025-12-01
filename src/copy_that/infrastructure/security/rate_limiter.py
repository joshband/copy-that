"""Redis-based rate limiting"""

import os
import time
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class RateLimiter:
    """Redis-based rate limiting"""

    def __init__(self, redis_client: Any) -> None:
        self.redis = redis_client

    async def check_rate_limit(
        self, key: str, limit: int, window_seconds: int
    ) -> tuple[bool, int, int]:
        """
        Check if request is within rate limit

        Returns:
            (allowed, remaining, reset_at)
        """
        current_time = int(time.time())
        window_start = current_time - window_seconds

        # Redis sorted set key
        rate_key = f"ratelimit:{key}"

        pipe = self.redis.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(rate_key, 0, window_start)

        # Count requests in window
        pipe.zcard(rate_key)

        # Add current request
        pipe.zadd(rate_key, {str(current_time): current_time})

        # Set expiry on key
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

    def check_rate_limit(
        self, key: str, limit: int, window_seconds: int
    ) -> tuple[bool, int, int]:
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

        # Use in-memory limiter (could be extended to use Redis if available)
        allowed, remaining, reset_at = _memory_limiter.check_rate_limit(
            rate_key, requests, seconds
        )

        if not allowed:
            retry_after = max(1, reset_at - int(time.time()))
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

    return Depends(dependency)


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
