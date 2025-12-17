from __future__ import annotations

from typing import Protocol


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, plain_password: str, hashed_password: str) -> bool: ...


class TokenData(Protocol):
    user_id: str
    email: str
    roles: list[str]
    token_type: str


class TokenPair(Protocol):
    access_token: str
    refresh_token: str
    token_type: str


class TokenCodec(Protocol):
    def create_token_pair(self, user_id: str, email: str, roles: list[str]) -> TokenPair: ...

    def decode(self, token: str) -> TokenData: ...
