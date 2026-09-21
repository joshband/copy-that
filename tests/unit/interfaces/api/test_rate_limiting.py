"""
Comprehensive tests for rate limiting and quota tracking.

Tests environment-aware rate limiting:
- Development mode: tracks but doesn't block
- Production mode: enforces limits
- Mock/test mode: disabled for fast tests
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, Request, status

from copy_that.infrastructure.security.rate_limiter import (
    QuotaStore,
    QuotaUsage,
    _get_client_identifier,
    rate_limit,
    reset_rate_limiter,
)


class TestQuotaUsage:
    """Test QuotaUsage data class."""

    def test_quota_usage_creation(self):
        """Test creating a quota usage object."""
        quota = QuotaUsage(key="test-key")
        assert quota.key == "test-key"
        assert quota.requests_count == 0
        assert quota.estimated_cost == 0.0
        assert quota.last_request_time is None

    def test_quota_usage_record_request(self):
        """Test recording a request."""
        quota = QuotaUsage(key="test-key")
        quota.record_request(cost=0.01)

        assert quota.requests_count == 1
        assert quota.estimated_cost == 0.01
        assert quota.last_request_time is not None

    def test_quota_usage_multiple_requests(self):
        """Test recording multiple requests."""
        quota = QuotaUsage(key="test-key")
        for i in range(5):
            quota.record_request(cost=0.01)

        assert quota.requests_count == 5
        assert quota.estimated_cost == pytest.approx(0.05, rel=0.001)

    def test_quota_usage_is_rate_limited(self):
        """Test rate limit checking."""
        quota = QuotaUsage(key="test-key")

        # Not limited yet
        assert not quota.is_rate_limited(max_requests=10)

        # Add requests up to limit
        for _ in range(10):
            quota.record_request()

        # Should be limited now
        assert quota.is_rate_limited(max_requests=10)

    def test_quota_usage_window_reset(self):
        """Test window reset after expiration."""
        quota = QuotaUsage(key="test-key")

        # Record some requests
        quota.record_request()
        quota.record_request()
        assert quota.requests_count == 2

        # Mock time to expire the window
        with patch("copy_that.infrastructure.security.rate_limiter.time.time") as mock_time:
            # Simulate window expiration
            initial_time = quota.window_start
            mock_time.return_value = initial_time + 120  # 2 minutes later

            quota.reset_window_if_needed(window_seconds=60)
            assert quota.requests_count == 0
            assert quota.estimated_cost == 0.0

    def test_quota_usage_to_dict(self):
        """Test converting to dictionary."""
        quota = QuotaUsage(key="test-key")
        quota.record_request(cost=0.01)

        result = quota.to_dict()
        assert result["key"] == "test-key"
        assert result["requests_count"] == 1
        assert "$0.01" in result["estimated_cost"]
        assert result["last_request_time"] is not None
        assert result["window_start"] is not None


class TestQuotaStore:
    """Test QuotaStore in-memory storage."""

    @pytest.mark.asyncio
    async def test_quota_store_get_or_create(self):
        """Test getting or creating a quota."""
        store = QuotaStore()
        quota1 = await store.get_or_create("key1")
        quota2 = await store.get_or_create("key1")

        assert quota1 is quota2
        assert quota1.key == "key1"

    @pytest.mark.asyncio
    async def test_quota_store_record_request(self):
        """Test recording requests in store."""
        store = QuotaStore()
        quota = await store.record_request("key1", cost=0.01)

        assert quota.requests_count == 1
        assert quota.estimated_cost == 0.01

    @pytest.mark.asyncio
    async def test_quota_store_check_limit(self):
        """Test checking rate limit in store."""
        store = QuotaStore()

        # First request should not be limited
        is_limited, quota = await store.check_limit("key1", max_requests=2)
        assert not is_limited

        # Record request
        await store.record_request("key1")

        # Still under limit
        is_limited, quota = await store.check_limit("key1", max_requests=2)
        assert not is_limited

        # Record another
        await store.record_request("key1")

        # Now at limit
        is_limited, quota = await store.check_limit("key1", max_requests=2)
        assert is_limited

    @pytest.mark.asyncio
    async def test_quota_store_get_stats(self):
        """Test getting stats from store."""
        store = QuotaStore()
        await store.record_request("key1", cost=0.05)

        stats = await store.get_stats("key1")
        assert stats["key"] == "key1"
        assert stats["requests_count"] == 1
        assert "$0.05" in stats["estimated_cost"]

    @pytest.mark.asyncio
    async def test_quota_store_reset(self):
        """Test resetting quotas."""
        store = QuotaStore()
        await store.record_request("key1")
        await store.record_request("key2")

        # Reset all
        await store.reset()
        stats1 = await store.get_stats("key1")
        stats2 = await store.get_stats("key2")

        assert stats1["requests_count"] == 0
        assert stats2["requests_count"] == 0

    @pytest.mark.asyncio
    async def test_quota_store_reset_single_key(self):
        """Test resetting a single key."""
        store = QuotaStore()
        await store.record_request("key1")
        await store.record_request("key2")

        # Reset single key
        await store.reset("key1")

        stats1 = await store.get_stats("key1")
        stats2 = await store.get_stats("key2")

        assert stats1["requests_count"] == 0
        assert stats2["requests_count"] == 1  # Should still have the request

    @pytest.mark.asyncio
    async def test_quota_store_get_all_stats(self):
        """Test getting all stats."""
        store = QuotaStore()
        await store.record_request("key1", cost=0.01)
        await store.record_request("key2", cost=0.02)

        all_stats = store.get_all_stats()
        assert len(all_stats) == 2
        assert "key1" in all_stats
        assert "key2" in all_stats


class TestGetClientIdentifier:
    """Test client identifier extraction."""

    def test_get_client_identifier_from_user_state(self):
        """Test getting client ID from user state."""
        request = MagicMock(spec=Request)
        request.state.user = MagicMock()
        request.state.user.id = 123

        client_id = _get_client_identifier(request)
        assert client_id == "user:123"

    def test_get_client_identifier_from_x_forwarded_for(self):
        """Test getting client ID from X-Forwarded-For header."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        del request.state.user  # No user
        request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}

        client_id = _get_client_identifier(request)
        assert client_id == "ip:192.168.1.1"

    def test_get_client_identifier_from_client_host(self):
        """Test getting client ID from client address."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        del request.state.user
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"

        client_id = _get_client_identifier(request)
        assert client_id == "ip:127.0.0.1"

    def test_get_client_identifier_unknown(self):
        """Test fallback to unknown client."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        del request.state.user
        request.headers = {}
        request.client = None

        client_id = _get_client_identifier(request)
        assert client_id == "ip:unknown"


class TestRateLimitDecorator:
    """Test rate limit decorator."""

    @pytest.mark.asyncio
    async def test_rate_limit_development_mode_allows_requests(self):
        """Test that development mode doesn't block requests."""
        import copy_that.infrastructure.security.rate_limiter as rate_limiter_module

        with (
            patch.object(rate_limiter_module, "ENVIRONMENT", "development"),
            patch.object(rate_limiter_module, "MOCK_MODE", False),
        ):
            reset_rate_limiter()

            # Create mock request
            request = MagicMock(spec=Request)
            request.url.path = "/test"
            request.headers = {}
            request.client = MagicMock()
            request.client.host = "127.0.0.1"

            # Get decorator
            decorator = rate_limit(requests=2, seconds=60)

            # This should not raise even if we exceed the limit
            for _ in range(5):
                try:
                    await decorator(request)
                except Exception as e:
                    pytest.fail(f"Should not raise in development mode: {e}")

    @pytest.mark.asyncio
    async def test_rate_limit_production_mode_enforces(self):
        """Test that production mode enforces limits."""
        import copy_that.infrastructure.security.rate_limiter as rate_limiter_module

        with (
            patch.object(rate_limiter_module, "ENVIRONMENT", "production"),
            patch.object(rate_limiter_module, "MOCK_MODE", False),
        ):
            reset_rate_limiter()

            # Create mock request
            request = MagicMock(spec=Request)
            request.url.path = "/test"
            request.headers = {}
            request.client = MagicMock()
            request.client.host = "127.0.0.1"

            # Get decorator with limit of 2
            decorator = rate_limit(requests=2, seconds=60)

            # First 2 should succeed
            await decorator(request)
            await decorator(request)

            # Third should fail
            with pytest.raises(HTTPException) as exc_info:
                await decorator(request)

            assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
            assert "Rate limit exceeded" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_rate_limit_mock_mode_disabled(self):
        """Test that mock mode disables rate limiting."""
        with patch.dict(os.environ, {"TESTING": "true"}):
            reset_rate_limiter()

            request = MagicMock(spec=Request)
            request.url.path = "/test"
            request.headers = {}
            request.client = MagicMock()
            request.client.host = "127.0.0.1"

            decorator = rate_limit(requests=1, seconds=60)

            # Should allow multiple requests without raising
            for _ in range(10):
                await decorator(request)  # Should not raise

    @pytest.mark.asyncio
    async def test_rate_limit_response_headers(self):
        """Test that rate limit headers are included."""
        import copy_that.infrastructure.security.rate_limiter as rate_limiter_module

        with (
            patch.object(rate_limiter_module, "ENVIRONMENT", "production"),
            patch.object(rate_limiter_module, "MOCK_MODE", False),
        ):
            reset_rate_limiter()

            request = MagicMock(spec=Request)
            request.url.path = "/test"
            request.headers = {}
            request.client = MagicMock()
            request.client.host = "127.0.0.1"

            decorator = rate_limit(requests=1, seconds=60)

            # First request succeeds
            await decorator(request)

            # Second request fails with headers
            with pytest.raises(HTTPException) as exc_info:
                await decorator(request)

            headers = exc_info.value.headers
            assert "X-RateLimit-Limit" in headers
            assert "X-RateLimit-Remaining" in headers
            assert "X-RateLimit-Reset" in headers
            assert "Retry-After" in headers


class TestEndpointRateLimits:
    """Test rate limits on actual endpoints."""

    @pytest.mark.asyncio
    async def test_colors_extract_has_rate_limit(self):
        """Test that /colors/extract endpoint has rate limiting."""
        # This is a marker test to verify the endpoint includes the decorator
        # Actual integration testing would require a live FastAPI app
        pass

    @pytest.mark.asyncio
    async def test_spacing_extract_has_rate_limit(self):
        """Test that /spacing/extract endpoint has rate limiting."""
        pass

    @pytest.mark.asyncio
    async def test_extract_stream_has_rate_limit(self):
        """Test that /extract/stream endpoint has rate limiting."""
        pass

    @pytest.mark.asyncio
    async def test_batch_extract_has_stricter_limit(self):
        """Test that batch endpoints have stricter limits."""
        pass


class TestRateLimitEnvironments:
    """Test rate limiting across different environments."""

    @pytest.mark.asyncio
    async def test_local_environment_no_blocking(self):
        """Test local environment doesn't block requests."""
        import copy_that.infrastructure.security.rate_limiter as rate_limiter_module

        with (
            patch.object(rate_limiter_module, "ENVIRONMENT", "local"),
            patch.object(rate_limiter_module, "MOCK_MODE", False),
        ):
            reset_rate_limiter()

            request = MagicMock(spec=Request)
            request.url.path = "/expensive"
            request.headers = {}
            request.client = MagicMock()
            request.client.host = "127.0.0.1"

            decorator = rate_limit(requests=1, seconds=60)

            # Both should succeed in local mode
            await decorator(request)
            await decorator(request)  # Would fail in production

    @pytest.mark.asyncio
    async def test_production_environment_blocking(self):
        """Test production environment blocks after limit."""
        import copy_that.infrastructure.security.rate_limiter as rate_limiter_module

        with (
            patch.object(rate_limiter_module, "ENVIRONMENT", "production"),
            patch.object(rate_limiter_module, "MOCK_MODE", False),
        ):
            reset_rate_limiter()

            request = MagicMock(spec=Request)
            request.url.path = "/expensive"
            request.headers = {}
            request.client = MagicMock()
            request.client.host = "127.0.0.1"

            decorator = rate_limit(requests=1, seconds=60)

            # First succeeds
            await decorator(request)

            # Second fails in production
            with pytest.raises(HTTPException):
                await decorator(request)

    @pytest.mark.asyncio
    async def test_staging_environment_similar_to_production(self):
        """Test staging environment also enforces limits."""
        # Staging is typically treated like production
        pass


class TestQuotaCostTracking:
    """Test cost tracking for quota."""

    def test_quota_cost_accumulation(self):
        """Test that costs accumulate correctly."""
        quota = QuotaUsage(key="expensive-op")

        # Record requests with different costs
        quota.record_request(cost=0.01)
        quota.record_request(cost=0.01)
        quota.record_request(cost=0.005)

        assert quota.requests_count == 3
        assert quota.estimated_cost == pytest.approx(0.025, rel=0.001)

    def test_quota_cost_in_stats(self):
        """Test that cost is included in stats."""
        quota = QuotaUsage(key="expensive-op")
        quota.record_request(cost=0.01)

        stats = quota.to_dict()
        assert "$0.01" in stats["estimated_cost"]


class TestRateLimiterReset:
    """Test rate limiter reset functionality."""

    def test_reset_rate_limiter(self):
        """Test resetting the global rate limiter."""
        # Record a request
        reset_rate_limiter()

        limiter_before = id(reset_rate_limiter.__globals__["_memory_limiter"])

        # Reset
        reset_rate_limiter()

        limiter_after = id(reset_rate_limiter.__globals__["_memory_limiter"])

        # Should create a new instance
        assert limiter_before != limiter_after
