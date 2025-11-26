"""Lightweight aggregation helpers that operate on TokenRepository data."""

from __future__ import annotations

from collections.abc import Iterable

from core.tokens.model import Token
from core.tokens.repository import TokenRepository


def dedupe_by_id(tokens: Iterable[Token]) -> list[Token]:
    """Remove duplicate ids, keeping the last occurrence."""
    seen: dict[str, Token] = {}
    for token in tokens:
        seen[token.id] = token
    return list(seen.values())


def simple_color_merge(repo: TokenRepository) -> TokenRepository:
    """
    Merge color tokens by hex value; keeps the highest confidence if present.

    This is a minimal stand-in for legacy color aggregation. For richer clustering,
    replace with a proper dedupe algorithm.
    """
    colors = repo.find_by_type("color")
    merged: dict[str, Token] = {}
    for token in colors:
        raw_hex = token.attributes.get("hex") or token.value
        key = str(raw_hex).lower()
        current = merged.get(key)
        if current is None:
            merged[key] = token
            continue
        # prefer higher confidence
        prev_conf = float(current.attributes.get("confidence") or 0)
        new_conf = float(token.attributes.get("confidence") or 0)
        if new_conf >= prev_conf:
            merged[key] = token

    out = TokenRepositoryClone(list(merged.values()))
    out.replace_tokens(list(merged.values()))
    return out


class TokenRepositoryClone(TokenRepository):
    """In-memory clone wrapper to allow simple replacements."""

    def __init__(self, tokens: list[Token] | None = None) -> None:
        self._tokens = {t.id: t for t in tokens or []}

    def replace_tokens(self, tokens: list[Token]) -> None:
        self._tokens = {t.id: t for t in tokens}

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

    def find_by_attributes(self, **attributes: object) -> list[Token]:
        return [
            token
            for token in self._tokens.values()
            if all(token.attributes.get(k) == v for k, v in attributes.items())
        ]

    def _require_token(self, token_id: str) -> Token:
        token = self.get_token(token_id)
        if token is None:
            raise KeyError(token_id)
        return token
