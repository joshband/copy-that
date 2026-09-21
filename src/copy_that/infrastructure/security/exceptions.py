from __future__ import annotations


class SecurityError(Exception):
    pass


class InvalidTokenError(SecurityError):
    pass


class MissingUserIdError(SecurityError):
    pass
