"""Security headers middleware"""

import os
import secrets

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


def _is_production_env() -> bool:
    """Check if running in production environment (called at runtime, not import time)."""
    return os.getenv("ENVIRONMENT", "local") == "production"


def _build_csp_policy(nonce: str | None = None, is_production: bool = False) -> str:
    """
    Build Content Security Policy based on environment.

    In production: Strict CSP with nonces for inline scripts/styles
    In development: Relaxed CSP with unsafe-inline for easier debugging
    """
    if is_production:
        # Production: Use nonces instead of unsafe-inline
        nonce_directive = f"'nonce-{nonce}'" if nonce else ""
        return (
            "default-src 'self'; "
            f"script-src 'self' {nonce_directive} https://cdn.jsdelivr.net; "
            f"style-src 'self' {nonce_directive} https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self' https://cdn.jsdelivr.net; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    else:
        # Development: Allow unsafe-inline for easier debugging
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self' https://cdn.jsdelivr.net ws: wss:"
        )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check environment at runtime (not import time) to allow test mocking
        is_production = _is_production_env()

        # Generate nonce for this request (used for inline scripts/styles in production)
        nonce = secrets.token_urlsafe(16) if is_production else None

        # Store nonce in request state for templates to use
        if nonce:
            request.state.csp_nonce = nonce

        response = await call_next(request)

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS filter (legacy, but still useful for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )

        # Content Security Policy
        response.headers["Content-Security-Policy"] = _build_csp_policy(nonce, is_production)

        # HSTS (only in production)
        if is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response
