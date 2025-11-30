"""W3C Design Tokens adapter with alias/dimension/composite support."""

from __future__ import annotations

from typing import Any

from core.tokens.model import RelationType, Token, TokenRelation, TokenType
from core.tokens.repository import TokenRepository


def tokens_to_w3c(repo: TokenRepository) -> dict[str, Any]:
    """Convert tokens stored in the repository to W3C Design Tokens JSON."""
    payload: dict[str, Any] = {}
    tokens = _all_tokens(repo)

    # Build lookup to allow references from composite tokens
    hex_to_id: dict[str, str] = {}
    for tok in tokens:
        if tok.type != TokenType.COLOR:
            continue
        hex_val = tok.attributes.get("hex")
        if isinstance(tok.value, dict) and tok.value.get("space") == "oklch":
            hex_val = hex_val or tok.attributes.get("value_hex")
        if hex_val:
            hex_to_id[hex_val.lower()] = tok.id

    for token in tokens:
        section = _section_for_type(token.type)
        if not section:
            continue
        entry: dict[str, Any]
        if _is_alias(token):
            target = token.relations[0].target  # single alias edge
            entry = {"$type": _type_name(token.type), "$value": _wrap_ref(target)}
            entry.update(token.attributes)
        elif token.type == TokenType.SPACING or token.type == TokenType.LAYOUT:
            entry = _token_to_w3c_spacing_entry(token)
        elif token.type == TokenType.SHADOW:
            entry = _token_to_w3c_shadow_entry(token, hex_to_id)
        elif token.type == TokenType.TYPOGRAPHY:
            entry = _token_to_w3c_typography_entry(token, hex_to_id)
        elif token.type == TokenType.COLOR:
            entry = _token_to_w3c_color_entry(token)
        else:
            entry = {"$type": _type_name(token.type), "value": token.value}
            entry.update(token.attributes)
        payload.setdefault(section, {})[token.id] = entry
    return payload


def w3c_to_tokens(data: dict[str, Any], repo: TokenRepository) -> None:
    """Load tokens from W3C Design Tokens JSON into the repository."""
    section_map: dict[str, TokenType] = {
        "color": TokenType.COLOR,
        "spacing": TokenType.SPACING,
        "shadow": TokenType.SHADOW,
        "typography": TokenType.TYPOGRAPHY,
        "layout": TokenType.LAYOUT,
    }
    for section, token_type in section_map.items():
        for token_id, entry in data.get(section, {}).items():
            token = _w3c_entry_to_token(token_id, entry, token_type)
            repo.upsert_token(token)


def _token_to_w3c_color_entry(token: Token) -> dict[str, Any]:
    entry = {"value": token.value, "$type": "color"}
    if isinstance(token.value, dict) and token.value.get("space") == "oklch":
        entry["colorSpace"] = "oklch"
    entry.update(token.attributes)
    return entry


def _w3c_entry_to_token(token_id: str, entry: dict[str, Any], token_type: TokenType) -> Token:
    raw_value = entry.get("value") if "value" in entry else entry.get("$value")
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$value", "$type"}}
    if isinstance(raw_value, str) and raw_value.startswith("{") and raw_value.endswith("}"):
        target = raw_value.strip("{}")
        return Token(
            id=token_id,
            type=token_type,
            value=None,
            attributes=attributes,
            relations=[TokenRelation(type=RelationType.ALIAS_OF, target=target)],
        )
    if token_type == TokenType.COLOR:
        return Token(id=token_id, type=token_type, value=raw_value, attributes=attributes)
    if token_type == TokenType.SPACING:
        return _w3c_spacing_entry_to_token(token_id, entry)
    if token_type == TokenType.SHADOW:
        return _w3c_shadow_entry_to_token(token_id, entry)
    if token_type == TokenType.TYPOGRAPHY:
        return _w3c_typography_entry_to_token(token_id, entry)
    if token_type == TokenType.LAYOUT:
        return _w3c_layout_entry_to_token(token_id, entry)
    return Token(id=token_id, type=token_type, value=raw_value, attributes=attributes)


def _token_to_w3c_spacing_entry(token: Token) -> dict[str, Any]:
    raw = token.value or {}
    entry: dict[str, Any] = {"$type": "dimension"}
    if isinstance(raw, dict):
        px = raw.get("px")
        rem = raw.get("rem")
        entry["value"] = {"value": px, "unit": "px"} if px is not None else raw
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
    if isinstance(raw_value, dict):
        if "value" in raw_value and raw_value.get("unit") == "px":
            value["px"] = raw_value.get("value")
        else:
            value.update(raw_value)
    elif isinstance(raw_value, str):
        value["value"] = raw_value
    return Token(id=token_id, type=TokenType.SPACING, value=value, attributes=attributes)


def _wrap_ref(token_id: str) -> str:
    return token_id if token_id.startswith("{") else f"{{{token_id}}}"


def _looks_like_token_ref(value: str) -> bool:
    return value.startswith(("token/", "color.", "font.", "spacing.", "layout."))


def _ref_or_value(color_value: Any, hex_to_id: dict[str, str]) -> Any:
    if isinstance(color_value, str):
        if color_value.startswith("{"):
            return color_value
        key = color_value.lower()
        if key in hex_to_id:
            return _wrap_ref(hex_to_id[key])
        if _looks_like_token_ref(color_value):
            return _wrap_ref(color_value)
    return color_value


def _token_to_w3c_shadow_entry(token: Token, hex_to_id: dict[str, str]) -> dict[str, Any]:
    value = token.value or {}
    if isinstance(value, list):
        mapped = []
        for layer in value:
            if not isinstance(layer, dict):
                continue
            layer_copy = dict(layer)
            if "color" in layer_copy:
                layer_copy["color"] = _ref_or_value(layer_copy["color"], hex_to_id)
            mapped.append(layer_copy)
        value = mapped
    elif isinstance(value, dict) and "color" in value:
        value = dict(value)
        value["color"] = _ref_or_value(value.get("color"), hex_to_id)
    entry = {"value": value, "$type": "shadow"}
    entry.update(token.attributes)
    return entry


def _w3c_shadow_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    value = entry.get("value") or []
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$type"}}
    return Token(id=token_id, type=TokenType.SHADOW, value=value, attributes=attributes)


def _token_to_w3c_typography_entry(token: Token, hex_to_id: dict[str, str]) -> dict[str, Any]:
    value = token.value or {}
    if isinstance(value, dict):
        value = dict(value)
        if "color" in value:
            value["color"] = _ref_or_value(value.get("color"), hex_to_id)
        if (
            "fontFamily" in value
            and isinstance(value["fontFamily"], str)
            and _looks_like_token_ref(value["fontFamily"])
        ):
            value["fontFamily"] = _wrap_ref(value["fontFamily"])
        if "fontSize" in value:
            fs = value["fontSize"]
            if isinstance(fs, dict) and "token" in fs:
                value["fontSize"] = _wrap_ref(str(fs["token"]))
            elif isinstance(fs, str) and _looks_like_token_ref(fs):
                value["fontSize"] = _wrap_ref(fs)
        if (
            "lineHeight" in value
            and isinstance(value["lineHeight"], str)
            and _looks_like_token_ref(value["lineHeight"])
        ):
            value["lineHeight"] = _wrap_ref(value["lineHeight"])
    entry = {"value": value, "$type": "typography"}
    entry.update(token.attributes)
    return entry


def _w3c_typography_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    value = entry.get("value") or {}
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$type"}}
    return Token(id=token_id, type=TokenType.TYPOGRAPHY, value=value, attributes=attributes)


def _token_to_w3c_layout_entry(token: Token) -> dict[str, Any]:
    value = token.value or {}
    entry: dict[str, Any] = {"$type": "dimension", "value": value}
    entry.update(token.attributes)
    return entry


def _w3c_layout_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    value = entry.get("value") or {}
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$type"}}
    return Token(id=token_id, type=TokenType.LAYOUT, value=value, attributes=attributes)


def _is_alias(token: Token) -> bool:
    return (
        token.value in (None, {}, [])
        and len(token.relations) == 1
        and token.relations[0].type == RelationType.ALIAS_OF
    )


def _section_for_type(token_type: TokenType | str) -> str | None:
    if isinstance(token_type, TokenType):
        return token_type.value
    return str(token_type)


def _type_name(token_type: TokenType | str) -> str:
    return token_type.value if isinstance(token_type, TokenType) else str(token_type)


def _all_tokens(repo: TokenRepository) -> list[Token]:
    tokens: list[Token] = []
    if hasattr(repo, "_tokens"):
        tokens.extend(repo._tokens.values())  # type: ignore[attr-defined]
        return tokens
    seen: set[str] = set()
    for token_type in TokenType:
        for token in repo.find_by_type(token_type):
            if token.id not in seen:
                seen.add(token.id)
                tokens.append(token)
    return tokens
