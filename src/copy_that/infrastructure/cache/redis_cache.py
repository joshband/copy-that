"""Redis caching layer with connectivity checks and fallback handling"""

import json
import logging
import os
from datetime import timedelta
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import ConnectionError, TimeoutError

logger = logging.getLogger(__name__)

# Global Redis client
_redis_client: Redis | None = None
_redis_available: bool = True


async def get_redis() -> Redis | None:
    """Get or create Redis client with connectivity check"""
    global _redis_client, _redis_available

    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL")

        if not redis_url:
            logger.warning(
                "REDIS_URL not configured. Caching and rate limiting will be disabled. "
                "Set REDIS_URL environment variable to enable these features."
            )
            _redis_available = False
            return None

        try:
            _redis_client = Redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            await _redis_client.ping()
            logger.info("Redis connection established successfully")
            _redis_available = True
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.error(
                f"Failed to connect to Redis: {e}. "
                "Caching and rate limiting will be disabled."
            )
            _redis_available = False
            _redis_client = None
            return None

    return _redis_client


async def check_redis_health() -> dict:
    """Check Redis connectivity and return health status"""
    global _redis_available

    if not os.getenv("REDIS_URL"):
        return {
            "status": "not_configured",
            "message": "REDIS_URL environment variable not set"
        }

    try:
        redis = await get_redis()
        if redis:
            await redis.ping()
            info = await redis.info("server")
            return {
                "status": "healthy",
                "version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", "unknown")
            }
        else:
            return {
                "status": "unavailable",
                "message": "Could not establish connection"
            }
    except Exception as e:
        _redis_available = False
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def is_redis_available() -> bool:
    """Check if Redis is available"""
    return _redis_available


class RedisCache:
    """Application-level Redis caching"""

    def __init__(self, redis: Redis):
        self.redis = redis
        self.default_ttl = timedelta(hours=1)
        self.prefix = "copythat:"

    def _make_key(self, namespace: str, identifier: str) -> str:
        """Generate cache key with prefix and namespace"""
        return f"{self.prefix}{namespace}:{identifier}"

    async def get(self, namespace: str, identifier: str) -> Any | None:
        """Get cached value with error handling"""
        try:
            key = self._make_key(namespace, identifier)
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Redis get failed for {namespace}:{identifier}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode cached value: {e}")
            return None

    async def set(
        self,
        namespace: str,
        identifier: str,
        value: Any,
        ttl: timedelta | None = None
    ):
        """Set cached value with TTL and error handling"""
        try:
            key = self._make_key(namespace, identifier)
            ttl = ttl or self.default_ttl
            await self.redis.setex(
                key,
                int(ttl.total_seconds()),
                json.dumps(value, default=str)
            )
        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Redis set failed for {namespace}:{identifier}: {e}")
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize value for cache: {e}")

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
        ttl: timedelta | None = None
    ) -> Any:
        """Get from cache or compute and cache"""
        cached = await self.get(namespace, identifier)
        if cached is not None:
            return cached

        value = await factory()
        await self.set(namespace, identifier, value, ttl)
        return value
