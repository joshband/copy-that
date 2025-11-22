"""
Unit tests for Redis cache module
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from redis.exceptions import ConnectionError

from copy_that.infrastructure.cache.redis_cache import (
    RedisCache,
    check_redis_health,
    get_redis,
    is_redis_available,
)


class TestGetRedis:
    """Tests for get_redis function"""

    @pytest.mark.asyncio
    async def test_returns_none_when_redis_url_not_configured(self):
        """Test that None is returned when REDIS_URL is not set"""
        with (
            patch.dict("os.environ", {}, clear=True),
            patch("copy_that.infrastructure.cache.redis_cache._redis_client", None),
            patch("copy_that.infrastructure.cache.redis_cache._redis_available", True),
        ):
            result = await get_redis()
            assert result is None

    @pytest.mark.asyncio
    async def test_returns_existing_client_if_available(self):
        """Test that existing client is returned if already initialized"""
        mock_client = MagicMock()
        with patch("copy_that.infrastructure.cache.redis_cache._redis_client", mock_client):
            result = await get_redis()
            assert result == mock_client

    @pytest.mark.asyncio
    async def test_connection_error_returns_none(self):
        """Test that connection errors return None"""
        with (
            patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379"}),
            patch("copy_that.infrastructure.cache.redis_cache._redis_client", None),
            patch("copy_that.infrastructure.cache.redis_cache.Redis") as mock_redis,
        ):
            mock_instance = AsyncMock()
            mock_instance.ping.side_effect = ConnectionError("Connection failed")
            mock_redis.from_url.return_value = mock_instance

            result = await get_redis()
            assert result is None


class TestCheckRedisHealth:
    """Tests for check_redis_health function"""

    @pytest.mark.asyncio
    async def test_returns_not_configured_when_no_url(self):
        """Test health check when REDIS_URL is not set"""
        with patch.dict("os.environ", {}, clear=True):
            result = await check_redis_health()
            assert result["status"] == "not_configured"

    @pytest.mark.asyncio
    async def test_returns_unavailable_when_cannot_connect(self):
        """Test health check when Redis is unavailable"""
        with (
            patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379"}),
            patch(
                "copy_that.infrastructure.cache.redis_cache.get_redis",
                return_value=None,
            ),
        ):
            result = await check_redis_health()
            assert result["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_returns_healthy_when_connected(self):
        """Test health check when Redis is healthy"""
        mock_redis = AsyncMock()
        mock_redis.info.return_value = {
            "redis_version": "7.0.0",
            "connected_clients": 5,
        }

        with (
            patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379"}),
            patch(
                "copy_that.infrastructure.cache.redis_cache.get_redis",
                return_value=mock_redis,
            ),
        ):
            result = await check_redis_health()
            assert result["status"] == "healthy"
            assert result["version"] == "7.0.0"

    @pytest.mark.asyncio
    async def test_returns_unhealthy_on_exception(self):
        """Test health check when exception occurs"""
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = Exception("Connection lost")

        with (
            patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379"}),
            patch(
                "copy_that.infrastructure.cache.redis_cache.get_redis",
                return_value=mock_redis,
            ),
        ):
            result = await check_redis_health()
            assert result["status"] == "unhealthy"


class TestIsRedisAvailable:
    """Tests for is_redis_available function"""

    def test_returns_current_availability_status(self):
        """Test that is_redis_available returns the global status"""
        with patch("copy_that.infrastructure.cache.redis_cache._redis_available", True):
            assert is_redis_available() is True

        with patch("copy_that.infrastructure.cache.redis_cache._redis_available", False):
            assert is_redis_available() is False


class TestRedisCache:
    """Tests for RedisCache class"""

    def test_make_key(self):
        """Test cache key generation"""
        mock_redis = MagicMock()
        cache = RedisCache(mock_redis)

        key = cache._make_key("sessions", "123")
        assert key == "copythat:sessions:123"

    @pytest.mark.asyncio
    async def test_get_returns_cached_value(self):
        """Test getting cached value"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = json.dumps({"key": "value"})

        cache = RedisCache(mock_redis)
        result = await cache.get("test", "123")

        assert result == {"key": "value"}
        mock_redis.get.assert_called_once_with("copythat:test:123")

    @pytest.mark.asyncio
    async def test_get_returns_none_when_not_found(self):
        """Test get returns None when key doesn't exist"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        cache = RedisCache(mock_redis)
        result = await cache.get("test", "123")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_handles_connection_error(self):
        """Test get handles connection errors gracefully"""
        mock_redis = AsyncMock()
        mock_redis.get.side_effect = ConnectionError("Connection lost")

        cache = RedisCache(mock_redis)
        result = await cache.get("test", "123")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_handles_json_decode_error(self):
        """Test get handles invalid JSON gracefully"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = "invalid json"

        cache = RedisCache(mock_redis)
        result = await cache.get("test", "123")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_caches_value(self):
        """Test setting cached value"""
        mock_redis = AsyncMock()

        cache = RedisCache(mock_redis)
        await cache.set("test", "123", {"key": "value"})

        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "copythat:test:123"

    @pytest.mark.asyncio
    async def test_set_handles_connection_error(self):
        """Test set handles connection errors gracefully"""
        mock_redis = AsyncMock()
        mock_redis.setex.side_effect = ConnectionError("Connection lost")

        cache = RedisCache(mock_redis)
        # Should not raise
        await cache.set("test", "123", {"key": "value"})

    @pytest.mark.asyncio
    async def test_set_handles_serialization_error(self):
        """Test set handles non-serializable values"""
        mock_redis = AsyncMock()

        # Create an object that can't be JSON serialized
        class NonSerializable:
            pass

        cache = RedisCache(mock_redis)
        # Should not raise
        await cache.set("test", "123", NonSerializable())

    @pytest.mark.asyncio
    async def test_delete_removes_key(self):
        """Test deleting cached value"""
        mock_redis = AsyncMock()

        cache = RedisCache(mock_redis)
        await cache.delete("test", "123")

        mock_redis.delete.assert_called_once_with("copythat:test:123")

    @pytest.mark.asyncio
    async def test_invalidate_pattern_removes_matching_keys(self):
        """Test invalidating keys by pattern"""
        mock_redis = AsyncMock()
        mock_redis.keys.return_value = ["copythat:test:1", "copythat:test:2"]

        cache = RedisCache(mock_redis)
        await cache.invalidate_pattern("test:*")

        mock_redis.keys.assert_called_once_with("copythat:test:*")
        mock_redis.delete.assert_called_once_with("copythat:test:1", "copythat:test:2")

    @pytest.mark.asyncio
    async def test_invalidate_pattern_no_op_when_no_matches(self):
        """Test invalidate pattern does nothing when no keys match"""
        mock_redis = AsyncMock()
        mock_redis.keys.return_value = []

        cache = RedisCache(mock_redis)
        await cache.invalidate_pattern("nonexistent:*")

        mock_redis.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_or_set_returns_cached_value(self):
        """Test get_or_set returns cached value when available"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = json.dumps({"cached": True})

        cache = RedisCache(mock_redis)
        factory = AsyncMock(return_value={"computed": True})

        result = await cache.get_or_set("test", "123", factory)

        assert result == {"cached": True}
        factory.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_or_set_computes_and_caches_when_not_cached(self):
        """Test get_or_set computes and caches value when not in cache"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        cache = RedisCache(mock_redis)
        factory = AsyncMock(return_value={"computed": True})

        result = await cache.get_or_set("test", "123", factory)

        assert result == {"computed": True}
        factory.assert_called_once()
        mock_redis.setex.assert_called_once()
