"""W3C Design Tokens adapter with alias/dimension/composite support."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from core.tokens.model import RelationType, Token, TokenRelation, TokenType
from core.tokens.repository import TokenRepository

_TYPE_OVERRIDES: dict[TokenType, str] = {
    TokenType.FONT_FAMILY: "fontFamily",
    TokenType.FONT_SIZE: "dimension",
}
_TYPE_NAME_OVERRIDES: dict[str, str] = {
    "font.family": "fontFamily",
    "font.size": "dimension",
    "spacing": "dimension",
}


def tokens_to_w3c(repo: TokenRepository) -> dict[str, Any]:
    """Convert tokens to DTCG TR 2025.10 grouped by section (no legacy 'value' alias)."""
    payload: dict[str, Any] = {}
    tokens = _all_tokens(repo)

    # Build lookup to allow references from composite tokens
    hex_to_id: dict[str, str] = {}
    for tok in tokens:
        if tok.type != TokenType.COLOR:
            continue
        hex_val = tok.attributes.get("hex")
        if isinstance(tok.value, str) and tok.value.startswith("#"):
            hex_val = hex_val or tok.value
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
            _apply_extensions(entry, token)
        elif token.type in (TokenType.SPACING, "spacing"):
            entries = _spacing_token_entries(token)
            _merge_entries(payload, section, entries)
            continue
        elif token.type == TokenType.LAYOUT:
            entries = _layout_token_entries(token, hex_to_id)
            _merge_entries(payload, section, entries)
            continue
        elif token.type == TokenType.SHADOW:
            entry = _token_to_w3c_shadow_entry(token, hex_to_id)
        elif token.type == TokenType.TYPOGRAPHY:
            entry = _token_to_w3c_typography_entry(token, hex_to_id)
        elif token.type == TokenType.COLOR:
            entry = _token_to_w3c_color_entry(token, hex_to_id)
        elif token.type == TokenType.FONT_SIZE:
            entry = _token_to_w3c_dimension_entry(token)
        elif token.type == TokenType.GRID:
            entries = _layout_token_entries(token, hex_to_id)
            _merge_entries(payload, section, entries)
            continue
        else:
            entry = {"$type": _type_name(token.type), "$value": token.value}
            entry.update(token.attributes)
        payload.setdefault(section, {})[token.id] = entry
    return payload


def tokens_to_w3c_sections(repo: TokenRepository) -> dict[str, Any]:
    """Alias for DTCG-sectioned output (internal representation)."""
    return tokens_to_w3c(repo)


def tokens_to_w3c_flat(repo: TokenRepository) -> dict[str, Any]:
    """Flattened section map with legacy 'value' alias for API/UI compatibility."""

    def add_value_alias(entry: dict[str, Any]) -> dict[str, Any]:
        clone = deepcopy(entry)
        if "$value" in clone and "value" not in clone:
            clone["value"] = clone["$value"]
        if "$ref" in clone and "value" not in clone:
            clone["value"] = clone["$ref"]
        return clone

    dtcg = tokens_to_w3c(repo)
    flat: dict[str, Any] = {}
    for section, tokens in dtcg.items():
        if not isinstance(tokens, dict):
            continue
        flat[section] = {token_id: add_value_alias(entry) for token_id, entry in tokens.items()}
    return flat


def w3c_to_tokens(data: dict[str, Any], repo: TokenRepository) -> None:
    """Load tokens from W3C Design Tokens JSON into the repository."""
    section_map: dict[str, TokenType] = {
        "color": TokenType.COLOR,
        "spacing": TokenType.SPACING,
        "shadow": TokenType.SHADOW,
        "typography": TokenType.TYPOGRAPHY,
        "layout": TokenType.LAYOUT,
        "layout.grid": TokenType.GRID,
        "font.family": TokenType.FONT_FAMILY,
        "font.size": TokenType.FONT_SIZE,
    }
    for section, token_type in section_map.items():
        for token_id, entry in data.get(section, {}).items():
            token = _w3c_entry_to_token(token_id, entry, token_type)
            repo.upsert_token(token)


def _token_to_w3c_color_entry(token: Token, hex_to_id: dict[str, str]) -> dict[str, Any]:
    raw_value = token.value
    if isinstance(raw_value, str):
        value = raw_value if raw_value.startswith("#") else _ref_or_value(raw_value, hex_to_id)
    else:
        value = _map_color_value(raw_value, hex_to_id)
    entry = {"$value": value, "$type": "color"}
    if isinstance(raw_value, dict) and raw_value.get("space") == "oklch":
        entry["colorSpace"] = "oklch"
    entry.update(token.attributes)
    _apply_extensions(entry, token)
    return entry


def _w3c_entry_to_token(token_id: str, entry: dict[str, Any], token_type: TokenType) -> Token:
    raw_value = entry.get("$value") if "$value" in entry else entry.get("value")
    attributes = {
        k: v for k, v in entry.items() if k not in {"value", "$value", "$type", "$extensions"}
    }
    extensions = entry.get("$extensions") if isinstance(entry, dict) else None
    relations: list[TokenRelation] = []
    if isinstance(extensions, dict):
        composes = extensions.get("composes")
        if isinstance(composes, list):
            for target in composes:
                relations.append(TokenRelation(type=RelationType.COMPOSES, target=str(target)))
    if isinstance(raw_value, str) and raw_value.startswith("{") and raw_value.endswith("}"):
        target = raw_value.strip("{}")
        relations.append(TokenRelation(type=RelationType.ALIAS_OF, target=target))
        return Token(
            id=token_id,
            type=token_type,
            value=None,
            attributes=attributes,
            relations=relations,
        )
    if token_type == TokenType.COLOR:
        return Token(
            id=token_id,
            type=token_type,
            value=raw_value,
            attributes=attributes,
            relations=relations,
        )
    if token_type == TokenType.SPACING:
        return _w3c_spacing_entry_to_token(token_id, entry, relations)
    if token_type == TokenType.SHADOW:
        return _w3c_shadow_entry_to_token(token_id, entry, relations)
    if token_type == TokenType.TYPOGRAPHY:
        return _w3c_typography_entry_to_token(token_id, entry, relations)
    if token_type == TokenType.LAYOUT:
        return _w3c_layout_entry_to_token(token_id, entry, relations)
    if token_type == TokenType.GRID:
        return _w3c_grid_entry_to_token(token_id, entry, relations)
    return Token(
        id=token_id, type=token_type, value=raw_value, attributes=attributes, relations=relations
    )


def _token_to_w3c_spacing_entry(token: Token) -> dict[str, Any]:
    raw = token.value or {}
    entry = _spacing_dimension_entry(raw)
    if token.relations:
        _inject_spacing_relations(entry, token.relations)
    entry.update(token.attributes)
    _apply_extensions(entry, token)
    return entry


def _spacing_dimension_entry(raw: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {"$type": "dimension"}
    if isinstance(raw, dict):
        px = raw.get("px")
        rem = raw.get("rem")
        if px is not None:
            entry["$value"] = {"value": px, "unit": "px"}
            if rem is not None:
                entry["rem"] = rem
        elif rem is not None and "value" not in raw:
            entry["$value"] = {"value": rem, "unit": "rem"}
        else:
            entry["$value"] = _dimension_value(raw)
    else:
        entry["$value"] = _dimension_value(raw)
    return entry


def _spacing_token_entries(token: Token) -> dict[str, Any]:
    raw = token.value or {}
    if not isinstance(raw, dict):
        return {token.id: _token_to_w3c_spacing_entry(token)}

    directional_keys = {
        "top",
        "right",
        "bottom",
        "left",
        "inline",
        "block",
        "inline_start",
        "inline_end",
        "block_start",
        "block_end",
    }
    present = [key for key in directional_keys if key in raw and raw.get(key) is not None]
    if not present:
        return {token.id: _token_to_w3c_spacing_entry(token)}

    entries: dict[str, Any] = {}
    use_root = len(present) == 1
    for key in present:
        token_id = token.id if use_root else f"{token.id}/{key}"
        entry = _spacing_dimension_entry(raw.get(key))
        _merge_entry_metadata(entry, token)
        if token.relations:
            _inject_spacing_relations(entry, token.relations)
        entries[token_id] = entry
    return entries


def _token_to_w3c_dimension_entry(token: Token) -> dict[str, Any]:
    raw = token.value or {}
    entry: dict[str, Any] = {"$type": "dimension"}
    if isinstance(raw, dict):
        px = raw.get("px")
        rem = raw.get("rem")
        if px is not None:
            entry["$value"] = {"value": px, "unit": "px"}
            if rem is not None:
                entry["rem"] = rem
        elif "value" in raw and "unit" in raw:
            entry["$value"] = {"value": raw.get("value"), "unit": raw.get("unit")}
        else:
            entry["$value"] = raw
    else:
        entry["$value"] = raw
    entry.update(token.attributes)
    _apply_extensions(entry, token)
    return entry


def _w3c_spacing_entry_to_token(
    token_id: str, entry: dict[str, Any], relations: list[TokenRelation] | None = None
) -> Token:
    raw_value = entry.get("$value") if "$value" in entry else entry.get("value")
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$value", "$type"}}
    value: dict[str, Any] = {}
    rels: list[TokenRelation] = list(relations or [])
    if isinstance(raw_value, dict):
        # Composite/directional spacing
        directional_keys = {
            "top",
            "right",
            "bottom",
            "left",
            "inline",
            "block",
            "inline_start",
            "inline_end",
            "block_start",
            "block_end",
        }
        if any(k in raw_value for k in directional_keys):
            for key, raw in raw_value.items():
                if isinstance(raw, dict) and raw.get("unit") == "px":
                    value[key] = raw.get("value")
                else:
                    value[key] = raw
        elif "value" in raw_value and raw_value.get("unit") == "px":
            value["px"] = raw_value.get("value")
            if "rem" in entry:
                value["rem"] = entry.get("rem")
        else:
            value.update(raw_value)
        if "multipleOf" in entry:
            rels.append(
                TokenRelation(
                    type=RelationType.MULTIPLE_OF,
                    target=str(entry["multipleOf"]),
                    meta={"multiplier": entry.get("multiplier")},
                )
            )
    elif isinstance(raw_value, str):
        value["value"] = raw_value
    return Token(
        id=token_id, type=TokenType.SPACING, value=value, attributes=attributes, relations=rels
    )


def _wrap_ref(token_id: str) -> str:
    return token_id if token_id.startswith("{") else f"{{{token_id}}}"


def _looks_like_token_ref(value: str) -> bool:
    return value.startswith(
        (
            "token/",
            "color.",
            "font.",
            "spacing.",
            "layout.",
            "layout.grid",
            "shadow.",
        )
    )


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


def _map_color_value(value: Any, hex_to_id: dict[str, str]) -> Any:
    """Recursively wrap color references inside gradients/composites."""
    if isinstance(value, dict):
        mapped = {}
        for key, val in value.items():
            if key == "color":
                mapped[key] = _ref_or_value(val, hex_to_id)
            else:
                mapped[key] = _map_color_value(val, hex_to_id)
        return mapped
    if isinstance(value, list):
        return [_map_color_value(v, hex_to_id) for v in value]
    if isinstance(value, str):
        return _ref_or_value(value, hex_to_id)
    return value


def _extensions_from_relations(relations: list[TokenRelation]) -> dict[str, Any]:
    """Encode supported relations into the $extensions block."""
    composes = [rel.target for rel in relations if rel.type == RelationType.COMPOSES]
    return {"composes": composes} if composes else {}


def _parse_json_dict(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _pipeline_for_type(token_type: TokenType | str) -> str:
    if isinstance(token_type, TokenType):
        mapping: dict[TokenType, str] = {
            TokenType.COLOR: "color",
            TokenType.SPACING: "spacing",
            TokenType.SHADOW: "shadow",
            TokenType.TYPOGRAPHY: "typography",
            TokenType.LAYOUT: "layout",
            TokenType.GRID: "layout.grid",
            TokenType.FONT_FAMILY: "typography",
            TokenType.FONT_SIZE: "typography",
        }
        return mapping.get(token_type, token_type.value)
    name = str(token_type)
    if name.startswith("font."):
        return "typography"
    if name.startswith("layout.grid"):
        return "layout.grid"
    if name.startswith("layout"):
        return "layout"
    return name.split(".")[0]


def _provenance_from_token(token: Token) -> dict[str, Any] | None:
    meta = _parse_json_dict(token.attributes.get("extraction_metadata"))
    provenance_sources = _parse_json_dict(token.attributes.get("provenance"))
    artifacts_attr = token.attributes.get("artifacts")
    confidence = token.attributes.get("confidence")
    category = token.attributes.get("category")
    if not any(
        [meta, provenance_sources, artifacts_attr, category, isinstance(confidence, (int, float))]
    ):
        return None
    algorithms: list[str] = []
    if meta:
        extractor_sources = meta.get("extractor_sources")
        if isinstance(extractor_sources, list):
            algorithms = [str(item) for item in extractor_sources if item]
        else:
            source = meta.get("source") or meta.get("extractor") or meta.get("model")
            if source:
                if isinstance(source, list):
                    algorithms = [str(item) for item in source if item]
                else:
                    algorithms = [str(source)]
    if not algorithms:
        if isinstance(category, str) and category:
            algorithms = [category]
        else:
            algorithms = ["unknown"]

    artifacts: list[str] = []
    if meta and isinstance(meta.get("artifacts"), list):
        artifacts = [str(item) for item in meta.get("artifacts", []) if item]
    elif isinstance(artifacts_attr, list):
        artifacts = [str(item) for item in artifacts_attr if item]

    provenance: dict[str, Any] = {
        "pipeline": _pipeline_for_type(token.type),
        "algorithm": algorithms,
        "artifacts": artifacts,
    }

    if meta:
        reserved = {"source", "extractor", "extractor_sources", "artifacts", "stage", "model"}
        params = {k: v for k, v in meta.items() if k not in reserved}
        if params:
            provenance["params"] = params
        stage = meta.get("stage")
        if stage:
            provenance["stage"] = stage

    if isinstance(confidence, (int, float)):
        provenance["confidence"] = float(confidence)

    if provenance_sources:
        provenance["sources"] = provenance_sources

    return provenance


def _extensions_from_token(token: Token) -> dict[str, Any]:
    extensions = _extensions_from_relations(token.relations) if token.relations else {}
    provenance = _provenance_from_token(token)
    if provenance:
        extensions["provenance"] = provenance
    return extensions


def _apply_extensions(entry: dict[str, Any], token: Token) -> None:
    extensions = _extensions_from_token(token)
    if not extensions:
        return
    if isinstance(entry.get("$extensions"), dict):
        entry["$extensions"].update(extensions)
    else:
        entry["$extensions"] = extensions


def _token_to_w3c_shadow_entry(token: Token, hex_to_id: dict[str, str]) -> dict[str, Any]:
    value = token.value or {}
    if isinstance(value, list):
        mapped = []
        for layer in value:
            if not isinstance(layer, dict):
                continue
            mapped.append(_map_color_value(layer, hex_to_id))
        value = mapped
    elif isinstance(value, dict):
        value = _map_color_value(value, hex_to_id)
    entry = {"$value": value, "$type": "shadow"}
    entry.update(token.attributes)
    _apply_extensions(entry, token)
    return entry


def _w3c_shadow_entry_to_token(
    token_id: str, entry: dict[str, Any], relations: list[TokenRelation] | None = None
) -> Token:
    raw_value = entry.get("$value") if "$value" in entry else entry.get("value") or []
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$value", "$type"}}
    rels: list[TokenRelation] = list(relations or [])

    def _attach_shadow_color_relation(target: str) -> None:
        for rel in rels:
            if rel.type == RelationType.COMPOSES and rel.target == target:
                if rel.meta is None:
                    rel.meta = {"role": "shadow-color"}
                elif "role" not in rel.meta:
                    rel.meta = {**rel.meta, "role": "shadow-color"}
                return
        rels.append(
            TokenRelation(
                type=RelationType.COMPOSES,
                target=target,
                meta={"role": "shadow-color"},
            )
        )

    def _normalize_color(color_val: Any) -> Any:
        if isinstance(color_val, str):
            if color_val.startswith("{") and color_val.endswith("}"):
                target = color_val.strip("{}")
                _attach_shadow_color_relation(target)
                return target
            if _looks_like_token_ref(color_val):
                _attach_shadow_color_relation(color_val)
                return color_val
        return color_val

    value: Any
    if isinstance(raw_value, list):
        value = []
        for layer in raw_value:
            if not isinstance(layer, dict):
                continue
            layer_copy = dict(layer)
            if "color" in layer_copy:
                layer_copy["color"] = _normalize_color(layer_copy["color"])
            value.append(layer_copy)
    elif isinstance(raw_value, dict):
        value = dict(raw_value)
        if "color" in value:
            value["color"] = _normalize_color(value["color"])
    else:
        value = raw_value

    return Token(
        id=token_id,
        type=TokenType.SHADOW,
        value=value,
        attributes=attributes,
        relations=rels,
    )


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
        if "token" in line_height:
            entry["$value"]["lineHeightToken"] = _wrap_ref(str(line_height["token"]))
    elif isinstance(line_height, (int, float, str)):
        entry["$value"]["lineHeight"] = line_height

    if "fontWeight" in val:
        entry["$value"]["fontWeight"] = val["fontWeight"]

    if "fontStyle" in val:
        entry["$value"]["fontStyle"] = val["fontStyle"]

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

    if "textAlign" in val:
        entry["$value"]["textAlign"] = val["textAlign"]

    color_ref = val.get("color")
    if isinstance(color_ref, str):
        entry["$value"]["color"] = _ref_or_value(color_ref, hex_to_id)
    entry.update(token.attributes)
    _apply_extensions(entry, token)
    return entry


def _w3c_typography_entry_to_token(
    token_id: str, entry: dict[str, Any], relations: list[TokenRelation] | None = None
) -> Token:
    raw_value = entry.get("$value") if "$value" in entry else entry.get("value") or {}
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$value", "$type"}}
    rels: list[TokenRelation] = list(relations or [])
    if not isinstance(raw_value, dict):
        return Token(
            id=token_id,
            type=TokenType.TYPOGRAPHY,
            value=raw_value,
            attributes=attributes,
            relations=rels,
        )

    value: dict[str, Any] = {}
    font_family = raw_value.get("fontFamily")
    if isinstance(font_family, list) and font_family:
        fam_val = font_family[0]
        if isinstance(fam_val, str) and fam_val.startswith("{"):
            fam_id = fam_val.strip("{}")
            value["fontFamily"] = fam_id
            rels.append(
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
            rels.append(
                TokenRelation(
                    type=RelationType.COMPOSES, target=cleaned, meta={"role": "font-size"}
                )
            )
    if font_size_token and isinstance(font_size_token, str) and font_size_token.startswith("{"):
        token_id_ref = font_size_token.strip("{}")
        rels.append(
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
    line_height_token = raw_value.get("lineHeightToken")
    if isinstance(line_height, dict):
        if "value" in line_height and line_height.get("unit") == "px":
            value["lineHeight"] = {"px": line_height.get("value")}
        else:
            value["lineHeight"] = line_height
    elif isinstance(line_height, str):
        value["lineHeight"] = line_height
    if (
        line_height_token
        and isinstance(line_height_token, str)
        and line_height_token.startswith("{")
    ):
        token_id_ref = line_height_token.strip("{}")
        rels.append(
            TokenRelation(
                type=RelationType.COMPOSES, target=token_id_ref, meta={"role": "line-height"}
            )
        )
        lh_val = value.get("lineHeight")
        if isinstance(lh_val, dict):
            lh_val["token"] = token_id_ref
        else:
            value["lineHeight"] = {"token": token_id_ref}

    if "fontWeight" in raw_value:
        value["fontWeight"] = raw_value["fontWeight"]

    if "fontStyle" in raw_value:
        value["fontStyle"] = raw_value["fontStyle"]

    letter_spacing = raw_value.get("letterSpacing")
    if isinstance(letter_spacing, dict):
        if "value" in letter_spacing and letter_spacing.get("unit") == "em":
            value["letterSpacing"] = {"em": letter_spacing.get("value")}
        else:
            value["letterSpacing"] = letter_spacing

    if "casing" in raw_value:
        value["casing"] = raw_value["casing"]

    if "textAlign" in raw_value:
        value["textAlign"] = raw_value["textAlign"]

    color_ref = raw_value.get("color")
    if isinstance(color_ref, str):
        cleaned = (
            color_ref.strip("{}")
            if color_ref.startswith("{") and color_ref.endswith("}")
            else color_ref
        )
        value["color"] = cleaned
        if cleaned:
            rels.append(
                TokenRelation(
                    type=RelationType.COMPOSES, target=cleaned, meta={"role": "text-color"}
                )
            )

    return Token(
        id=token_id,
        type=TokenType.TYPOGRAPHY,
        value=value,
        attributes=attributes,
        relations=rels,
    )


def _token_to_w3c_layout_entry(token: Token) -> dict[str, Any]:
    value = token.value or {}
    if isinstance(value, dict) and any(
        k in value for k in ("columns", "gutter", "margin", "radius", "border")
    ):
        entry: dict[str, Any] = {"$type": "layout", "$value": {}}
        columns = value.get("columns")
        gutter = value.get("gutter")
        margin = value.get("margin")
        radius = value.get("radius")
        border = value.get("border")
        if columns is not None:
            entry["$value"]["columns"] = columns
        if gutter is not None:
            entry["$value"]["gutter"] = _dimension_dict(gutter)
        if margin is not None:
            if isinstance(margin, dict):
                entry["$value"]["margin"] = {k: _dimension_dict(v) for k, v in margin.items()}
            else:
                entry["$value"]["margin"] = _dimension_dict(margin)
        if radius is not None:
            entry["$value"]["radius"] = _dimension_dict(radius)
        if border is not None:
            if isinstance(border, dict):
                entry["$value"]["border"] = {k: _dimension_dict(v) for k, v in border.items()}
            else:
                entry["$value"]["border"] = _dimension_dict(border)
    else:
        entry = {"$type": "dimension", "$value": value}
    entry.update(token.attributes)
    _apply_extensions(entry, token)
    return entry


def _w3c_layout_entry_to_token(
    token_id: str, entry: dict[str, Any], relations: list[TokenRelation] | None = None
) -> Token:
    value = entry.get("$value") if "$value" in entry else entry.get("value") or {}
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$value", "$type"}}
    if entry.get("$type") == "dimension" and isinstance(value, dict) and "value" in value:
        unit = value.get("unit")
        if unit == "px":
            return Token(
                id=token_id,
                type=TokenType.LAYOUT,
                value={"px": value.get("value")},
                attributes=attributes,
                relations=relations or [],
            )
        return Token(
            id=token_id,
            type=TokenType.LAYOUT,
            value={"value": value.get("value"), "unit": unit},
            attributes=attributes,
            relations=relations or [],
        )
    if isinstance(value, dict) and any(
        k in value for k in ("columns", "gutter", "margin", "radius", "border")
    ):
        parsed: dict[str, Any] = {}
        if value.get("columns") is not None:
            parsed["columns"] = value.get("columns")
        gutter = value.get("gutter")
        margin = value.get("margin")
        radius = value.get("radius")
        border = value.get("border")
        if isinstance(gutter, dict) and "value" in gutter:
            parsed["gutter"] = gutter.get("value")
        elif gutter is not None:
            parsed["gutter"] = gutter
        if isinstance(margin, dict):
            parsed["margin"] = {}
            for key, raw in margin.items():
                if isinstance(raw, dict) and "value" in raw:
                    parsed["margin"][key] = raw.get("value")
                else:
                    parsed["margin"][key] = raw
        elif margin is not None:
            parsed["margin"] = margin
        if isinstance(radius, dict) and "value" in radius:
            parsed["radius"] = radius.get("value")
        elif radius is not None:
            parsed["radius"] = radius
        if isinstance(border, dict):
            parsed["border"] = {}
            for key, raw in border.items():
                if isinstance(raw, dict) and "value" in raw:
                    parsed["border"][key] = raw.get("value")
                else:
                    parsed["border"][key] = raw
        elif border is not None:
            parsed["border"] = border
        return Token(
            id=token_id,
            type=TokenType.LAYOUT,
            value=parsed,
            attributes=attributes,
            relations=relations or [],
        )
    return Token(
        id=token_id,
        type=TokenType.LAYOUT,
        value=value,
        attributes=attributes,
        relations=relations or [],
    )


def _token_to_w3c_grid_entry(token: Token) -> dict[str, Any]:
    value = token.value or {}
    entry: dict[str, Any] = {"$type": "grid", "$value": value}
    entry.update(token.attributes)
    _apply_extensions(entry, token)
    return entry


def _w3c_grid_entry_to_token(
    token_id: str, entry: dict[str, Any], relations: list[TokenRelation] | None = None
) -> Token:
    value = entry.get("$value") if "$value" in entry else entry.get("value") or {}
    attributes = {k: v for k, v in entry.items() if k not in {"value", "$value", "$type"}}
    if entry.get("$type") == "dimension" and isinstance(value, dict) and "value" in value:
        unit = value.get("unit")
        if unit == "px":
            value = {"px": value.get("value")}
        else:
            value = {"value": value.get("value"), "unit": unit}
    return Token(
        id=token_id,
        type=TokenType.GRID,
        value=value,
        attributes=attributes,
        relations=relations or [],
    )


def _layout_token_entries(token: Token, hex_to_id: dict[str, str]) -> dict[str, Any]:
    raw = token.value or {}
    if not isinstance(raw, dict):
        return {token.id: _token_to_w3c_dimension_entry(token)}

    composite_keys = ("columns", "gutter", "margin", "radius", "border")
    present = [k for k in composite_keys if k in raw]
    if not present:
        return {token.id: _token_to_w3c_dimension_entry(token)}

    if len(present) == 1:
        return _layout_property_entries(
            token, present[0], raw[present[0]], hex_to_id, use_root=True
        )

    entries: dict[str, Any] = {}
    for key in present:
        entries.update(_layout_property_entries(token, key, raw[key], hex_to_id, use_root=False))
    return entries


def _layout_property_entries(
    token: Token,
    key: str,
    value: Any,
    hex_to_id: dict[str, str],
    *,
    use_root: bool,
) -> dict[str, Any]:
    entries: dict[str, Any] = {}

    def add_entry(token_id: str, entry: dict[str, Any]) -> None:
        _merge_entry_metadata(entry, token)
        entries[token_id] = entry

    if key == "columns":
        token_id = token.id if use_root else f"{token.id}/columns"
        add_entry(token_id, {"$type": "number", "$value": value})
        return entries

    if key in ("gutter", "radius"):
        token_id = token.id if use_root else f"{token.id}/{key}"
        add_entry(token_id, {"$type": "dimension", "$value": _dimension_value(value)})
        return entries

    if key == "margin":
        if isinstance(value, dict):
            dimension_keys = {"value", "unit", "px", "rem"}
            if set(value.keys()) <= dimension_keys:
                token_id = token.id if use_root else f"{token.id}/margin"
                add_entry(token_id, {"$type": "dimension", "$value": _dimension_value(value)})
                return entries
            for side, raw in value.items():
                token_id = f"{token.id}/margin/{side}"
                add_entry(token_id, {"$type": "dimension", "$value": _dimension_value(raw)})
            return entries
        token_id = token.id if use_root else f"{token.id}/margin"
        add_entry(token_id, {"$type": "dimension", "$value": _dimension_value(value)})
        return entries

    if key == "border":
        if isinstance(value, dict):
            width = value.get("width")
            color = value.get("color")
            style = value.get("style")
            if use_root and width is not None and color is None and style is None:
                add_entry(token.id, {"$type": "dimension", "$value": _dimension_value(width)})
                return entries
            if width is not None:
                add_entry(
                    f"{token.id}/border/width",
                    {"$type": "dimension", "$value": _dimension_value(width)},
                )
            if color is not None:
                add_entry(
                    f"{token.id}/border/color",
                    {"$type": "color", "$value": _ref_or_value(color, hex_to_id)},
                )
            if style is not None:
                add_entry(
                    f"{token.id}/border/style",
                    {"$type": "strokeStyle", "$value": style},
                )
            return entries
        token_id = token.id if use_root else f"{token.id}/border/width"
        add_entry(token_id, {"$type": "dimension", "$value": _dimension_value(value)})
        return entries

    token_id = token.id if use_root else f"{token.id}/{key}"
    add_entry(token_id, {"$type": "dimension", "$value": _dimension_value(value)})
    return entries


def _merge_entry_metadata(entry: dict[str, Any], token: Token) -> None:
    attributes = {k: v for k, v in token.attributes.items() if k not in {"$type", "$value"}}
    if attributes:
        entry.update(attributes)
    _apply_extensions(entry, token)


def _merge_entries(payload: dict[str, Any], section: str, entries: dict[str, Any]) -> None:
    group = payload.setdefault(section, {})
    group.update(entries)


def _dimension_value(raw: Any) -> Any:
    if isinstance(raw, (int, float)):
        return {"value": raw, "unit": "px"}
    if isinstance(raw, dict):
        if "px" in raw:
            return {"value": raw.get("px"), "unit": "px"}
        if "value" in raw and "unit" in raw:
            return {"value": raw.get("value"), "unit": raw.get("unit")}
        if "value" in raw and "unit" not in raw:
            return {"value": raw.get("value"), "unit": "px"}
        return raw
    return raw


def _dimension_dict(raw: Any) -> Any:
    if isinstance(raw, (int, float)):
        return {"value": raw, "unit": "px"}
    return raw


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
    if isinstance(token_type, TokenType):
        return _TYPE_OVERRIDES.get(token_type, token_type.value)
    name = str(token_type)
    return _TYPE_NAME_OVERRIDES.get(name, name)


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
