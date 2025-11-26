"""W3C Design Tokens adapter (colors only for now)."""

from __future__ import annotations

from typing import Any

from core.tokens.model import Token
from core.tokens.repository import TokenRepository


def tokens_to_w3c(repo: TokenRepository) -> dict[str, Any]:
    """Convert tokens stored in the repository to W3C Design Tokens JSON."""
    payload: dict[str, Any] = {}
    sections = [
        ("color", repo.find_by_type("color"), _token_to_w3c_color_entry),
        ("shadow", repo.find_by_type("shadow"), _token_to_w3c_shadow_entry),
        ("typography", repo.find_by_type("typography"), _token_to_w3c_typography_entry),
    ]
    for section, tokens, encoder in sections:
        entries = {token.id: encoder(token) for token in tokens if token.value is not None}
        if entries:
            payload[section] = entries
    return payload


def w3c_to_tokens(data: dict[str, Any], repo: TokenRepository) -> None:
    """Load tokens from W3C Design Tokens JSON into the repository."""
    for token_id, entry in data.get("color", {}).items():
        repo.upsert_token(_w3c_color_entry_to_token(token_id, entry))
    for token_id, entry in data.get("shadow", {}).items():
        repo.upsert_token(_w3c_shadow_entry_to_token(token_id, entry))
    for token_id, entry in data.get("typography", {}).items():
        repo.upsert_token(_w3c_typography_entry_to_token(token_id, entry))


def _token_to_w3c_color_entry(token: Token) -> dict[str, Any]:
    entry = {"value": token.value, "$type": "color"}
    entry.update(token.attributes)
    return entry


def _w3c_color_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    value = entry.get("value")
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$type"}}
    return Token(id=token_id, type="color", value=value, attributes=attributes)


def _token_to_w3c_shadow_entry(token: Token) -> dict[str, Any]:
    entry = {"value": token.value, "$type": "shadow"}
    entry.update(token.attributes)
    return entry


def _w3c_shadow_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    value = entry.get("value") or []
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$type"}}
    return Token(id=token_id, type="shadow", value=value, attributes=attributes)


def _token_to_w3c_typography_entry(token: Token) -> dict[str, Any]:
    entry = {"value": token.value, "$type": "typography"}
    entry.update(token.attributes)
    return entry


def _w3c_typography_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    value = entry.get("value") or {}
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$type"}}
    return Token(id=token_id, type="typography", value=value, attributes=attributes)
