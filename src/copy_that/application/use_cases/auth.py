from __future__ import annotations

from datetime import datetime

from copy_that.application.errors import (
    AlreadyExistsError,
    AuthenticationFailedError,
    DisabledAccountError,
    InvalidRefreshTokenError,
)
from copy_that.application.ports.security import PasswordHasher, TokenCodec, TokenPair
from copy_that.application.ports.users import UserRepository
from copy_that.domain.users import User


async def register_user(
    repo: UserRepository,
    password_hasher: PasswordHasher,
    *,
    email: str,
    password: str,
    full_name: str | None,
) -> User:
    existing = await repo.get_by_email(email=email)
    if existing is not None:
        raise AlreadyExistsError("Email already registered")

    hashed_password = password_hasher.hash(password)
    return await repo.create(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        roles=["user"],
    )


async def login_and_issue_tokens(
    repo: UserRepository,
    password_hasher: PasswordHasher,
    token_codec: TokenCodec,
    *,
    email: str,
    password: str,
    now: datetime,
) -> TokenPair:
    user = await repo.get_by_email(email=email)
    if user is None or not password_hasher.verify(password, user.hashed_password):
        raise AuthenticationFailedError("Invalid email or password")

    if not user.is_active:
        raise DisabledAccountError("Account is disabled")

    await repo.set_last_login(user_id=user.id, last_login=now)
    return token_codec.create_token_pair(user.id, user.email, user.roles)


async def refresh_tokens(
    repo: UserRepository,
    token_codec: TokenCodec,
    *,
    refresh_token: str,
) -> TokenPair:
    try:
        token_data = token_codec.decode(refresh_token)
    except Exception as e:
        raise InvalidRefreshTokenError("Invalid refresh token") from e
    if token_data.token_type != "refresh":
        raise InvalidRefreshTokenError("Invalid refresh token")

    user = await repo.get_by_id(user_id=token_data.user_id)
    if user is None or not user.is_active:
        raise InvalidRefreshTokenError("Invalid user")

    return token_codec.create_token_pair(user.id, user.email, user.roles)
