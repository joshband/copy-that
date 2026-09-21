"""
Rate limiting and quota tracking for expensive API endpoints.

This module provides environment-aware rate limiting:
- Production: Enforces strict rate limits to protect against abuse
- Development: Tracks usage without enforcement (doesn't block development)
- Testing: Uses mock implementation for fast tests
"""

import asyncio
import functools
import logging
import os
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from fastapi import HTTPException, Request

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


def get_client_identifier(request: Request) -> str:
    """Extract client identifier from request (API key or IP)."""
    # Priority: API key > X-Forwarded-For > remote address
    if hasattr(request, "headers"):
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"

        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"

    if hasattr(request, "client") and request.client:
        return f"ip:{request.client.host}"

    return "unknown"


def rate_limit(
    max_requests: int = 10,
    window_seconds: int = 60,
    cost: float = 0.0,
    endpoint_name: str = "unknown",
) -> Callable[..., Any]:
    """
    Decorator for rate limiting endpoints.

    Args:
        max_requests: Max requests per window
        window_seconds: Time window in seconds
        cost: Estimated API cost per request (for tracking)
        endpoint_name: Name of endpoint (for logging)

    In production: Enforces limits and returns 429 if exceeded
    In development: Only tracks usage
    In testing: Skips limiting entirely
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, request: Request, **kwargs: Any) -> Any:
            client_id = get_client_identifier(request)

            # Mock mode: skip rate limiting (for tests)
            if MOCK_MODE:
                return await func(*args, request=request, **kwargs)

            # Check rate limit
            is_limited, quota = await quota_store.check_limit(
                client_id, max_requests, window_seconds
            )

            # Development mode: only track usage
            if ENVIRONMENT in ("local", "development"):
                if is_limited:
                    logger.warning(
                        "Rate limit exceeded in development (tracking only): "
                        "%s - %d requests in %ds window",
                        client_id,
                        quota.requests_count,
                        window_seconds,
                    )
                # Record the request regardless
                await quota_store.record_request(client_id, cost)
                return await func(*args, request=request, **kwargs)

            # Production mode: enforce limits
            if is_limited:
                logger.error(
                    "Rate limit exceeded: %s - %d requests in %ds window",
                    client_id,
                    quota.requests_count,
                    window_seconds,
                )
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Too many requests",
                        "endpoint": endpoint_name,
                        "limit": max_requests,
                        "window_seconds": window_seconds,
                        "retry_after": window_seconds,
                    },
                )

            # Record the request
            updated_quota = await quota_store.record_request(client_id, cost)

            logger.info(
                "Request recorded for %s: %d/%d in window",
                client_id,
                updated_quota.requests_count,
                max_requests,
            )

            return await func(*args, request=request, **kwargs)

        return wrapper

    return decorator


# Endpoint-specific rate limit configurations
RATE_LIMIT_CONFIG = {
    "colors_extract": {
        "max_requests": 10,
        "window_seconds": 60,
        "cost": 0.01,  # ~$0.01 per color extraction
    },
    "spacing_extract": {
        "max_requests": 10,
        "window_seconds": 60,
        "cost": 0.005,  # ~$0.005 per spacing extraction
    },
    "extract_stream": {
        "max_requests": 5,
        "window_seconds": 60,
        "cost": 0.015,  # ~$0.015 per multi-extraction
    },
    "batch_extract": {
        "max_requests": 3,
        "window_seconds": 60,
        "cost": 0.05,  # ~$0.05 per batch (multiple items)
    },
}


async def get_quota_stats(client_id: str) -> dict[str, Any]:
    """Get quota stats for a client (for monitoring endpoints)."""
    return await quota_store.get_stats(client_id)


async def reset_quota(client_id: str | None = None) -> None:
    """Reset quota for a client (admin endpoint)."""
    await quota_store.reset(client_id)
