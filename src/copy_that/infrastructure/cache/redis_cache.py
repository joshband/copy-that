"""Redis caching layer"""

import json
import os
from datetime import timedelta
from typing import Any, Optional

from redis.asyncio import Redis

# Global Redis client
_redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    """Get or create Redis client"""
    global _redis_client

    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = Redis.from_url(redis_url, decode_responses=True)

    return _redis_client


class RedisCache:
    """Application-level Redis caching"""

    def __init__(self, redis: Redis):
        self.redis = redis
        self.default_ttl = timedelta(hours=1)
        self.prefix = "copythat:"

    def _make_key(self, namespace: str, identifier: str) -> str:
        """Generate cache key with prefix and namespace"""
        return f"{self.prefix}{namespace}:{identifier}"

    async def get(self, namespace: str, identifier: str) -> Optional[Any]:
        """Get cached value"""
        key = self._make_key(namespace, identifier)
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(
        self,
        namespace: str,
        identifier: str,
        value: Any,
        ttl: Optional[timedelta] = None
    ):
        """Set cached value with TTL"""
        key = self._make_key(namespace, identifier)
        ttl = ttl or self.default_ttl
        await self.redis.setex(
            key,
            int(ttl.total_seconds()),
            json.dumps(value, default=str)
        )

    async def delete(self, namespace: str, identifier: str):
        """Delete cached value"""
        key = self._make_key(namespace, identifier)
        await self.redis.delete(key)

    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        full_pattern = f"{self.prefix}{pattern}"
        keys = await self.redis.keys(full_pattern)
        if keys:
            await self.redis.delete(*keys)

    async def get_or_set(
        self,
        namespace: str,
        identifier: str,
        factory,
        ttl: Optional[timedelta] = None
    ) -> Any:
        """Get from cache or compute and cache"""
        cached = await self.get(namespace, identifier)
        if cached is not None:
            return cached

        value = await factory()
        await self.set(namespace, identifier, value, ttl)
        return value
