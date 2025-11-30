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
            entry = {"$type": _type_name(token.type), "$value": token.value}
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
    entry = {"$value": token.value, "$type": "color"}
    if isinstance(token.value, dict) and token.value.get("space") == "oklch":
        entry["colorSpace"] = "oklch"
    entry.update(token.attributes)
    return entry


def _w3c_entry_to_token(token_id: str, entry: dict[str, Any], token_type: TokenType) -> Token:
    raw_value = entry.get("$value") if "$value" in entry else entry.get("value")
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
        entry["$value"] = {"value": px, "unit": "px"} if px is not None else raw
        if rem is not None:
            entry["rem"] = rem
        if token.relations:
            _inject_spacing_relations(entry, token.relations)
    else:
        entry["$value"] = raw
    entry.update(token.attributes)
    return entry


def _w3c_spacing_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    raw_value = entry.get("$value") if "$value" in entry else entry.get("value")
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$value", "$type"}}
    value: dict[str, Any] = {}
    relations: list[TokenRelation] = []
    if isinstance(raw_value, dict):
        if "value" in raw_value and raw_value.get("unit") == "px":
            value["px"] = raw_value.get("value")
            if "rem" in entry:
                value["rem"] = entry.get("rem")
        else:
            value.update(raw_value)
        if "multipleOf" in entry:
            relations.append(
                TokenRelation(
                    type=RelationType.MULTIPLE_OF,
                    target=str(entry["multipleOf"]),
                    meta={"multiplier": entry.get("multiplier")},
                )
            )
    elif isinstance(raw_value, str):
        value["value"] = raw_value
    return Token(
        id=token_id, type=TokenType.SPACING, value=value, attributes=attributes, relations=relations
    )


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
    entry = {"$value": value, "$type": "shadow"}
    entry.update(token.attributes)
    return entry


def _w3c_shadow_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    value = entry.get("$value") if "$value" in entry else entry.get("value") or []
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$value", "$type"}}
    return Token(id=token_id, type=TokenType.SHADOW, value=value, attributes=attributes)


def _token_to_w3c_typography_entry(token: Token, hex_to_id: dict[str, str]) -> dict[str, Any]:
    raw = token.value or {}
    entry: dict[str, Any] = {"$type": "typography", "$value": {}}
    if not isinstance(raw, dict):
        entry["$value"] = raw
        entry.update(token.attributes)
        return entry

    val = dict(raw)
    font_family = val.get("fontFamily")
    if isinstance(font_family, str):
        entry["$value"]["fontFamily"] = (
            [_wrap_ref(font_family)] if _looks_like_token_ref(font_family) else [font_family]
        )
    elif isinstance(font_family, list):
        entry["$value"]["fontFamily"] = font_family

    font_size = val.get("fontSize")
    if isinstance(font_size, dict):
        if "px" in font_size:
            entry["$value"]["fontSize"] = {"value": font_size.get("px"), "unit": "px"}
        elif "value" in font_size and "unit" in font_size:
            entry["$value"]["fontSize"] = {
                "value": font_size.get("value"),
                "unit": font_size.get("unit"),
            }
        if "token" in font_size:
            entry["$value"]["fontSizeToken"] = _wrap_ref(str(font_size["token"]))
    elif isinstance(font_size, str):
        entry["$value"]["fontSize"] = (
            _wrap_ref(font_size) if _looks_like_token_ref(font_size) else font_size
        )

    line_height = val.get("lineHeight")
    if isinstance(line_height, dict):
        if "px" in line_height:
            entry["$value"]["lineHeight"] = {"value": line_height.get("px"), "unit": "px"}
        elif "value" in line_height:
            entry["$value"]["lineHeight"] = {
                "value": line_height.get("value"),
                "unit": line_height.get("unit", ""),
            }
    elif isinstance(line_height, str):
        entry["$value"]["lineHeight"] = line_height

    if "fontWeight" in val:
        entry["$value"]["fontWeight"] = val["fontWeight"]

    letter_spacing = val.get("letterSpacing")
    if isinstance(letter_spacing, dict):
        if "em" in letter_spacing:
            entry["$value"]["letterSpacing"] = {"value": letter_spacing["em"], "unit": "em"}
        elif "value" in letter_spacing:
            entry["$value"]["letterSpacing"] = {
                "value": letter_spacing.get("value"),
                "unit": letter_spacing.get("unit", ""),
            }

    if "casing" in val:
        entry["$value"]["casing"] = val["casing"]

    color_ref = val.get("color")
    if isinstance(color_ref, str):
        entry["$value"]["color"] = _ref_or_value(color_ref, hex_to_id)

    entry.update(token.attributes)
    return entry


def _w3c_typography_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    raw_value = entry.get("$value") if "$value" in entry else entry.get("value") or {}
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$value", "$type"}}
    relations: list[TokenRelation] = []
    if not isinstance(raw_value, dict):
        return Token(id=token_id, type=TokenType.TYPOGRAPHY, value=raw_value, attributes=attributes)

    value: dict[str, Any] = {}
    font_family = raw_value.get("fontFamily")
    if isinstance(font_family, list) and font_family:
        fam_val = font_family[0]
        if isinstance(fam_val, str) and fam_val.startswith("{"):
            fam_id = fam_val.strip("{}")
            value["fontFamily"] = fam_id
            relations.append(
                TokenRelation(
                    type=RelationType.COMPOSES, target=fam_id, meta={"role": "font-family"}
                )
            )
        elif fam_val:
            value["fontFamily"] = fam_val
    elif isinstance(font_family, str):
        value["fontFamily"] = font_family

    font_size = raw_value.get("fontSize")
    font_size_token = raw_value.get("fontSizeToken")
    if isinstance(font_size, dict):
        if "value" in font_size and font_size.get("unit") == "px":
            value["fontSize"] = {"px": font_size.get("value")}
        else:
            value["fontSize"] = font_size
    elif isinstance(font_size, str):
        cleaned = (
            font_size.strip("{}")
            if font_size.startswith("{") and font_size.endswith("}")
            else font_size
        )
        value["fontSize"] = cleaned
        if font_size.startswith("{") and font_size.endswith("}"):
            relations.append(
                TokenRelation(
                    type=RelationType.COMPOSES, target=cleaned, meta={"role": "font-size"}
                )
            )
    if font_size_token and isinstance(font_size_token, str) and font_size_token.startswith("{"):
        token_id_ref = font_size_token.strip("{}")
        relations.append(
            TokenRelation(
                type=RelationType.COMPOSES, target=token_id_ref, meta={"role": "font-size"}
            )
        )
        fs_val = value.get("fontSize")
        if isinstance(fs_val, dict):
            fs_val["token"] = token_id_ref
        else:
            value["fontSize"] = {"token": token_id_ref}

    line_height = raw_value.get("lineHeight")
    if isinstance(line_height, dict):
        if "value" in line_height and line_height.get("unit") == "px":
            value["lineHeight"] = {"px": line_height.get("value")}
        else:
            value["lineHeight"] = line_height
    elif isinstance(line_height, str):
        value["lineHeight"] = line_height

    if "fontWeight" in raw_value:
        value["fontWeight"] = raw_value["fontWeight"]

    letter_spacing = raw_value.get("letterSpacing")
    if isinstance(letter_spacing, dict):
        if "value" in letter_spacing and letter_spacing.get("unit") == "em":
            value["letterSpacing"] = {"em": letter_spacing.get("value")}
        else:
            value["letterSpacing"] = letter_spacing

    if "casing" in raw_value:
        value["casing"] = raw_value["casing"]

    color_ref = raw_value.get("color")
    if isinstance(color_ref, str):
        cleaned = (
            color_ref.strip("{}")
            if color_ref.startswith("{") and color_ref.endswith("}")
            else color_ref
        )
        value["color"] = cleaned
        if cleaned:
            relations.append(
                TokenRelation(
                    type=RelationType.COMPOSES, target=cleaned, meta={"role": "text-color"}
                )
            )

    return Token(
        id=token_id,
        type=TokenType.TYPOGRAPHY,
        value=value,
        attributes=attributes,
        relations=relations,
    )


def _token_to_w3c_layout_entry(token: Token) -> dict[str, Any]:
    value = token.value or {}
    entry: dict[str, Any] = {"$type": "dimension", "$value": value}
    entry.update(token.attributes)
    return entry


def _w3c_layout_entry_to_token(token_id: str, entry: dict[str, Any]) -> Token:
    value = entry.get("$value") if "$value" in entry else entry.get("value") or {}
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$value", "$type"}}
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


def _inject_spacing_relations(entry: dict[str, Any], relations: list[TokenRelation]) -> None:
    for rel in relations:
        if rel.type != RelationType.MULTIPLE_OF:
            continue
        entry["multipleOf"] = rel.target
        if "multiplier" in rel.meta:
            entry["multiplier"] = rel.meta.get("multiplier")
