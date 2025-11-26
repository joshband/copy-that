"""W3C Design Tokens adapter (colors only for now)."""

from __future__ import annotations

from typing import Any

from core.tokens.model import Token
from core.tokens.repository import TokenRepository


def tokens_to_w3c(repo: TokenRepository) -> dict[str, Any]:
    """Convert tokens stored in the repository to W3C Design Tokens JSON."""
    color_tokens = {
        token.id: _token_to_w3c_color_entry(token)
        for token in repo.find_by_type("color")
        if token.value is not None
    }

    payload: dict[str, Any] = {}
    if color_tokens:
        payload["color"] = color_tokens
    return payload


def w3c_to_tokens(data: dict[str, Any], repo: TokenRepository) -> None:
    """Load tokens from W3C Design Tokens JSON into the repository."""
    for token_id, entry in data.get("color", {}).items():
        repo.upsert_token(_w3c_color_entry_to_token(token_id, entry))


def _token_to_w3c_color_entry(token: Token) -> dict[str, Any]:
    entry = {"value": token.value, "$type": "color"}
    entry.update(token.attributes)
    return entry


def _w3c_color_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    value = entry.get("value")
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$type"}}
    return Token(id=token_id, type="color", value=value, attributes=attributes)
