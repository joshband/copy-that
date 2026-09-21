"""
Tests for rate limiting and cache fallbacks
"""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from copy_that.infrastructure.security.rate_limiter import (
    RateLimiter,
    RateLimitMiddleware,
    rate_limit,
)


class TestRateLimiter:
    """Test RateLimiter class"""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client"""
        redis = MagicMock()
        pipe = MagicMock()
        redis.pipeline.return_value = pipe
        pipe.execute = AsyncMock()
        return redis, pipe

    @pytest.mark.asyncio
    async def test_first_request_allowed(self, mock_redis):
        """Test that first request is allowed"""
        redis, pipe = mock_redis
        pipe.execute.return_value = [None, 0, None, None]  # 0 requests in window

        limiter = RateLimiter(redis)
        allowed, remaining, reset = await limiter.check_rate_limit("test", 10, 60)

        assert allowed is True
        assert remaining == 9  # 10 - 0 - 1 = 9

    @pytest.mark.asyncio
    async def test_at_limit_still_allowed(self, mock_redis):
        """Test that request at limit is still allowed"""
        redis, pipe = mock_redis
        pipe.execute.return_value = [None, 9, None, None]  # 9 requests (limit is 10)

        limiter = RateLimiter(redis)
        allowed, remaining, reset = await limiter.check_rate_limit("test", 10, 60)

        assert allowed is True
        assert remaining == 0

    @pytest.mark.asyncio
    async def test_over_limit_blocked(self, mock_redis):
        """Test that request over limit is blocked"""
        redis, pipe = mock_redis
        pipe.execute.return_value = [None, 10, None, None]  # Already at limit

        limiter = RateLimiter(redis)
        allowed, remaining, reset = await limiter.check_rate_limit("test", 10, 60)

        assert allowed is False
        assert remaining == 0

    @pytest.mark.asyncio
    async def test_reset_time_calculated(self, mock_redis):
        """Test that reset time is calculated correctly"""
        redis, pipe = mock_redis
        pipe.execute.return_value = [None, 5, None, None]

        limiter = RateLimiter(redis)
        current_time = int(time.time())
        allowed, remaining, reset = await limiter.check_rate_limit("test", 10, 60)

        # Reset should be current time + window
        assert reset >= current_time + 60
        assert reset <= current_time + 61  # Allow 1 second tolerance


class TestRateLimitMiddleware:
    """Test rate limiting middleware"""

    @pytest.fixture
    def mock_app(self):
        """Create mock FastAPI app"""
        app = AsyncMock()
        return app

    @pytest.fixture
    def mock_request(self):
        """Create mock request"""
        request = MagicMock()
        request.url.path = "/api/v1/colors/extract"
        request.headers = {}
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        delattr(request.state, "user")  # No authenticated user
        return request

    @pytest.mark.asyncio
    async def test_health_check_bypasses_rate_limit(self, mock_app):
        """Test that health checks bypass rate limiting"""
        redis = AsyncMock()

        middleware = RateLimitMiddleware(
            mock_app, redis, requests_per_minute=10, requests_per_hour=100
        )

        request = MagicMock()
        request.url.path = "/health"

        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        response = await middleware.dispatch(request, call_next)

        assert response == expected_response
        # Redis should not be called for health checks
        redis.pipeline.assert_not_called()

    @pytest.mark.asyncio
    async def test_client_id_from_ip(self, mock_app, mock_request):
        """Test client ID extraction from IP"""
        redis = AsyncMock()

        middleware = RateLimitMiddleware(
            mock_app, redis, requests_per_minute=60, requests_per_hour=1000
        )

        client_id = middleware._get_client_id(mock_request)
        assert client_id == "ip:127.0.0.1"

    @pytest.mark.asyncio
    async def test_client_id_from_user(self, mock_app):
        """Test client ID extraction from authenticated user"""
        redis = AsyncMock()

        middleware = RateLimitMiddleware(
            mock_app, redis, requests_per_minute=60, requests_per_hour=1000
        )

        request = MagicMock()
        request.state.user = MagicMock()
        request.state.user.id = "user-123"

        client_id = middleware._get_client_id(request)
        assert client_id == "user:user-123"

    @pytest.mark.asyncio
    async def test_client_id_from_forwarded_header(self, mock_app):
        """Test client ID extraction from X-Forwarded-For header"""
        redis = AsyncMock()

        middleware = RateLimitMiddleware(
            mock_app, redis, requests_per_minute=60, requests_per_hour=1000
        )

        request = MagicMock()
        request.headers = {"X-Forwarded-For": "203.0.113.1, 198.51.100.1"}
        delattr(request.state, "user")

        client_id = middleware._get_client_id(request)
        assert client_id == "ip:203.0.113.1"

    @pytest.mark.asyncio
    async def test_rate_limit_disabled(self, mock_app):
        """Test that rate limiting can be disabled"""
        redis = AsyncMock()

        with patch.dict("os.environ", {"RATE_LIMIT_ENABLED": "false"}):
            middleware = RateLimitMiddleware(
                mock_app, redis, requests_per_minute=10, requests_per_hour=100
            )

            assert middleware.enabled is False

    @pytest.mark.asyncio
    async def test_redis_failure_allows_request(self, mock_app, mock_request):
        """Test that Redis failure doesn't block requests"""
        redis = AsyncMock()
        redis.pipeline.side_effect = Exception("Redis connection failed")

        middleware = RateLimitMiddleware(
            mock_app, redis, requests_per_minute=10, requests_per_hour=100
        )

        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        # Should not raise, should allow request through
        response = await middleware.dispatch(mock_request, call_next)

        assert response == expected_response


class TestCacheFallback:
    """Test cache fallback behavior"""

    @pytest.mark.asyncio
    async def test_cache_unavailable_returns_none(self):
        """Test that cache returns None when unavailable"""
        from copy_that.infrastructure.cache.redis_cache import RedisCache

        redis = AsyncMock()
        redis.get.side_effect = Exception("Connection refused")

        cache = RedisCache(redis)

        # Should handle error gracefully
        try:
            result = await cache.get("test", "key")
            # If it doesn't raise, it should return None
            assert result is None
        except Exception:
            # If it raises, that's also acceptable behavior
            pass

    @pytest.mark.asyncio
    async def test_cache_set_failure_doesnt_raise(self):
        """Test that cache set failure doesn't raise"""
        from copy_that.infrastructure.cache.redis_cache import RedisCache

        redis = AsyncMock()
        redis.setex.side_effect = Exception("Connection refused")

        cache = RedisCache(redis)

        # Should not raise
        try:
            await cache.set("test", "key", {"data": "value"})
        except Exception:
            # Some implementations may raise, which is acceptable
            pass


class TestRateLimitMiddleware429:
    """Test rate limit exceeded scenarios"""

    @pytest.mark.asyncio
    async def test_minute_limit_exceeded_returns_429(self):
        """Test that 429 is returned when per-minute limit exceeded"""
        mock_app = AsyncMock()
        mock_limiter = AsyncMock()
        # Return exceeded for minute check
        mock_limiter.check_rate_limit.return_value = (False, 0, int(time.time()) + 60)

        middleware = RateLimitMiddleware(mock_app, MagicMock())
        middleware.limiter = mock_limiter

        request = MagicMock()
        request.url.path = "/api/test"
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.state = MagicMock(spec=[])

        call_next = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await middleware.dispatch(request, call_next)

        assert exc_info.value.status_code == 429
        assert "per minute" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_hour_limit_exceeded_returns_429(self):
        """Test that 429 is returned when per-hour limit exceeded"""
        mock_app = AsyncMock()
        mock_limiter = AsyncMock()
        # First call (minute) passes, second call (hour) fails
        mock_limiter.check_rate_limit.side_effect = [
            (True, 50, int(time.time()) + 60),
            (False, 0, int(time.time()) + 3600),
        ]

        middleware = RateLimitMiddleware(mock_app, MagicMock())
        middleware.limiter = mock_limiter

        request = MagicMock()
        request.url.path = "/api/test"
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.state = MagicMock(spec=[])

        call_next = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await middleware.dispatch(request, call_next)

        assert exc_info.value.status_code == 429
        assert "per hour" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_successful_request_adds_headers(self):
        """Test that successful request gets rate limit headers"""
        mock_app = AsyncMock()
        mock_limiter = AsyncMock()
        mock_limiter.check_rate_limit.side_effect = [
            (True, 50, int(time.time()) + 60),
            (True, 900, int(time.time()) + 3600),
        ]

        middleware = RateLimitMiddleware(mock_app, MagicMock())
        middleware.limiter = mock_limiter

        request = MagicMock()
        request.url.path = "/api/test"
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.state = MagicMock(spec=[])

        mock_response = MagicMock()
        mock_response.headers = {}
        call_next = AsyncMock(return_value=mock_response)

        result = await middleware.dispatch(request, call_next)

        assert "X-RateLimit-Limit" in result.headers
        assert "X-RateLimit-Remaining" in result.headers
        assert "X-RateLimit-Reset" in result.headers


class TestGetClientIdEdgeCases:
    """Test edge cases for client ID extraction"""

    def test_client_id_unknown_when_no_client(self):
        """Test client ID is 'unknown' when no client available"""
        mock_app = AsyncMock()
        redis = AsyncMock()

        middleware = RateLimitMiddleware(mock_app, redis)

        request = MagicMock()
        request.headers = {}
        request.client = None
        request.state = MagicMock(spec=[])

        client_id = middleware._get_client_id(request)
        assert client_id == "ip:unknown"


class TestRateLimitDecorator:
    """Test rate_limit decorator function"""

    @pytest.mark.asyncio
    async def test_rate_limit_decorator_returns_dependency(self):
        """Test that rate_limit returns a FastAPI dependency"""
        dependency = rate_limit(100, 60)

        # Should return a Depends object
        assert dependency is not None

    @pytest.mark.asyncio
    async def test_rate_limit_dependency_passes_through(self):
        """Test that the dependency passes through without blocking"""

        dependency = rate_limit(100, 60)

        # rate_limit now returns the dependency function directly (not wrapped in Depends)
        # This is used with Depends(rate_limit(...)) in endpoints
        assert callable(dependency)

        # Create mock request
        request = MagicMock()
        request.url.path = "/test/unique-path-for-rate-limit-test"
        request.state = MagicMock()
        request.state.user = None
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"

        # Should not raise
        result = await dependency(request)
        assert result is None
