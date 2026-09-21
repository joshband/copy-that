from __future__ import annotations


class ApplicationError(Exception):
    pass


class AlreadyExistsError(ApplicationError):
    pass


class AuthenticationFailedError(ApplicationError):
    pass


class DisabledAccountError(ApplicationError):
    pass


class InvalidRefreshTokenError(ApplicationError):
    pass
