from __future__ import annotations

from copy_that.application.ports.security import PasswordHasher, TokenCodec
from copy_that.infrastructure.security.authentication import (
    TokenData,
    TokenPair,
    create_token_pair,
    decode_token,
    get_password_hash,
    verify_password,
)


class PasslibPasswordHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        return get_password_hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)


class JoseTokenCodec(TokenCodec):
    def create_token_pair(self, user_id: str, email: str, roles: list[str]) -> TokenPair:
        return create_token_pair(user_id, email, roles)

    def decode(self, token: str) -> TokenData:
        return decode_token(token)
