"""W3C Design Tokens adapter (colors only for now)."""

from __future__ import annotations

from typing import Any

from core.tokens.model import Token
from core.tokens.repository import TokenRepository


def tokens_to_w3c(repo: TokenRepository) -> dict[str, Any]:
    """Convert tokens stored in the repository to W3C Design Tokens JSON."""
    payload: dict[str, Any] = {}
    # Build lookup to allow references from composite tokens
    hex_to_id = {}
    for tok in repo.find_by_type("color"):
        hex_val = tok.attributes.get("hex")
        if isinstance(tok.value, dict) and tok.value.get("space") == "oklch":
            # coloraide okLCH stored, attributes still carry original hex
            hex_val = hex_val or tok.attributes.get("value_hex")
        if hex_val:
            hex_to_id[hex_val.lower()] = tok.id

    sections = [
        ("color", repo.find_by_type("color"), _token_to_w3c_color_entry),
        ("spacing", repo.find_by_type("spacing"), _token_to_w3c_spacing_entry),
        ("shadow", repo.find_by_type("shadow"), lambda t: _token_to_w3c_shadow_entry(t, hex_to_id)),
        (
            "typography",
            repo.find_by_type("typography"),
            lambda t: _token_to_w3c_typography_entry(t, hex_to_id),
        ),
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
    for token_id, entry in data.get("spacing", {}).items():
        repo.upsert_token(_w3c_spacing_entry_to_token(token_id, entry))
    for token_id, entry in data.get("shadow", {}).items():
        repo.upsert_token(_w3c_shadow_entry_to_token(token_id, entry))
    for token_id, entry in data.get("typography", {}).items():
        repo.upsert_token(_w3c_typography_entry_to_token(token_id, entry))


def _token_to_w3c_color_entry(token: Token) -> dict[str, Any]:
    entry = {"value": token.value, "$type": "color"}
    if isinstance(token.value, dict) and token.value.get("space") == "oklch":
        entry["colorSpace"] = "oklch"
    entry.update(token.attributes)
    return entry


def _w3c_color_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    value = entry.get("value")
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$type"}}
    return Token(id=token_id, type="color", value=value, attributes=attributes)


def _token_to_w3c_spacing_entry(token: Token) -> dict[str, Any]:
    raw = token.value
    entry: dict[str, Any] = {"$type": "dimension"}
    if isinstance(raw, str):
        entry["value"] = raw
    elif isinstance(raw, dict):
        px = raw.get("px")
        rem = raw.get("rem")
        if px is not None:
            entry["value"] = f"{px}px"
        if rem is not None:
            entry["rem"] = rem
    else:
        entry["value"] = raw
    entry.update(token.attributes)
    return entry


def _w3c_spacing_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    raw_value = entry.get("value")
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$type"}}
    value: dict[str, Any] = {}
    if isinstance(raw_value, dict) and "value" in raw_value:
        value["px"] = raw_value.get("value")
    elif isinstance(raw_value, str):
        value["value"] = raw_value
    return Token(id=token_id, type="spacing", value=value, attributes=attributes)


def _ref_or_value(color_value: Any, hex_to_id: dict[str, str]) -> Any:
    if isinstance(color_value, str):
        key = color_value.lower()
        if key in hex_to_id:
            return f"{{{hex_to_id[key]}}}"
        if color_value.startswith("{"):
            return color_value
    return color_value


def _token_to_w3c_shadow_entry(token: Token, hex_to_id: dict[str, str]) -> dict[str, Any]:
    value = token.value or {}
    if isinstance(value, dict) and "color" in value:
        value = dict(value)
        value["color"] = _ref_or_value(value.get("color"), hex_to_id)
    entry = {"value": value, "$type": "shadow"}
    entry.update(token.attributes)
    return entry


def _w3c_shadow_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    value = entry.get("value") or []
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$type"}}
    return Token(id=token_id, type="shadow", value=value, attributes=attributes)


def _token_to_w3c_typography_entry(token: Token, hex_to_id: dict[str, str]) -> dict[str, Any]:
    value = token.value or {}
    if isinstance(value, dict) and "color" in value:
        value = dict(value)
        value["color"] = _ref_or_value(value.get("color"), hex_to_id)
    entry = {"value": value, "$type": "typography"}
    entry.update(token.attributes)
    return entry


def _w3c_typography_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    value = entry.get("value") or {}
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$type"}}
    return Token(id=token_id, type="typography", value=value, attributes=attributes)
