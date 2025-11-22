"""
Unit tests for security headers middleware
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from copy_that.interfaces.api.middleware.security_headers import SecurityHeadersMiddleware


class TestSecurityHeadersMiddleware:
    """Tests for SecurityHeadersMiddleware"""

    @pytest.mark.asyncio
    async def test_adds_basic_security_headers(self):
        """Test that basic security headers are added"""
        mock_app = MagicMock()
        middleware = SecurityHeadersMiddleware(mock_app)

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.headers = {}

        call_next = AsyncMock(return_value=mock_response)

        with patch.dict("os.environ", {}, clear=True):
            result = await middleware.dispatch(mock_request, call_next)

        assert result.headers["X-Frame-Options"] == "DENY"
        assert result.headers["X-Content-Type-Options"] == "nosniff"
        assert result.headers["X-XSS-Protection"] == "1; mode=block"
        assert result.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert "Content-Security-Policy" in result.headers

    @pytest.mark.asyncio
    async def test_csp_header_contains_required_directives(self):
        """Test that CSP header contains all required directives"""
        mock_app = MagicMock()
        middleware = SecurityHeadersMiddleware(mock_app)

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.headers = {}

        call_next = AsyncMock(return_value=mock_response)

        with patch.dict("os.environ", {}, clear=True):
            result = await middleware.dispatch(mock_request, call_next)

        csp = result.headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp
        assert "style-src 'self'" in csp
        assert "img-src 'self'" in csp
        assert "font-src 'self'" in csp
        assert "connect-src 'self'" in csp

    @pytest.mark.asyncio
    async def test_hsts_added_in_production(self):
        """Test that HSTS header is added in production environment"""
        mock_app = MagicMock()
        middleware = SecurityHeadersMiddleware(mock_app)

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.headers = {}

        call_next = AsyncMock(return_value=mock_response)

        with patch.dict("os.environ", {"ENVIRONMENT": "production"}):
            result = await middleware.dispatch(mock_request, call_next)

        assert "Strict-Transport-Security" in result.headers
        assert "max-age=31536000" in result.headers["Strict-Transport-Security"]
        assert "includeSubDomains" in result.headers["Strict-Transport-Security"]

    @pytest.mark.asyncio
    async def test_hsts_not_added_in_development(self):
        """Test that HSTS header is not added in development environment"""
        mock_app = MagicMock()
        middleware = SecurityHeadersMiddleware(mock_app)

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.headers = {}

        call_next = AsyncMock(return_value=mock_response)

        with patch.dict("os.environ", {"ENVIRONMENT": "development"}):
            result = await middleware.dispatch(mock_request, call_next)

        assert "Strict-Transport-Security" not in result.headers

    @pytest.mark.asyncio
    async def test_hsts_not_added_when_no_environment(self):
        """Test that HSTS header is not added when ENVIRONMENT is not set"""
        mock_app = MagicMock()
        middleware = SecurityHeadersMiddleware(mock_app)

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.headers = {}

        call_next = AsyncMock(return_value=mock_response)

        with patch.dict("os.environ", {}, clear=True):
            result = await middleware.dispatch(mock_request, call_next)

        assert "Strict-Transport-Security" not in result.headers

    @pytest.mark.asyncio
    async def test_passes_through_response(self):
        """Test that the original response is passed through"""
        mock_app = MagicMock()
        middleware = SecurityHeadersMiddleware(mock_app)

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.status_code = 200

        call_next = AsyncMock(return_value=mock_response)

        result = await middleware.dispatch(mock_request, call_next)

        call_next.assert_called_once_with(mock_request)
        assert result == mock_response
