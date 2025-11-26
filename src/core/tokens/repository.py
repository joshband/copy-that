"""Repository abstractions for the token graph."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .model import Token


class TokenRepository(ABC):
    """Abstract repository for persisting and querying tokens."""

    @abstractmethod
    def upsert_token(self, token: Token) -> Token:
        """Insert or update a token."""

    @abstractmethod
    def get_token(self, token_id: str) -> Token | None:
        """Return a token by id."""

    @abstractmethod
    def link(self, token_id: str, relation: str, target_token_id: str) -> None:
        """Associate two tokens via a named relation."""

    @abstractmethod
    def find_by_type(self, token_type: str) -> list[Token]:
        """Return all tokens of a given type."""

    @abstractmethod
    def find_by_attributes(self, **attributes: Any) -> list[Token]:
        """Return tokens whose attributes contain the provided key/value pairs."""


class InMemoryTokenRepository(TokenRepository):
    """Simple in-memory repository used for tests."""

    def __init__(self) -> None:
        self._tokens: dict[str, Token] = {}

    def upsert_token(self, token: Token) -> Token:
        self._tokens[token.id] = token
        return token

    def get_token(self, token_id: str) -> Token | None:
        return self._tokens.get(token_id)

    def link(self, token_id: str, relation: str, target_token_id: str) -> None:
        token = self._require_token(token_id)
        self._require_token(target_token_id)
        token.relations[relation] = target_token_id

    def find_by_type(self, token_type: str) -> list[Token]:
        return [token for token in self._tokens.values() if token.type == token_type]

    def find_by_attributes(self, **attributes: Any) -> list[Token]:
        return [
            token
            for token in self._tokens.values()
            if _attributes_match(token.attributes, attributes)
        ]

    def _require_token(self, token_id: str) -> Token:
        token = self.get_token(token_id)
        if token is None:
            raise KeyError(f"Token '{token_id}' not found")
        return token


def _attributes_match(
    token_attributes: dict[str, Any], required_attributes: dict[str, Any]
) -> bool:
    return all(token_attributes.get(key) == value for key, value in required_attributes.items())
