"""Lightweight conformance helpers for the W3C Design Tokens format (TR 2025.10).

Conversion logic lives in `copy_that.core_tokens.adapters.w3c`. This module provides a small
validator used by unit tests to catch obvious non-conformance issues early.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

SUPPORTED_W3C_TYPES: set[str] = {
    # Primitive types (Format module)
    "color",
    "dimension",
    "fontFamily",
    "fontWeight",
    "duration",
    "cubicBezier",
    "number",
    # Composite types (Format module)
    "strokeStyle",
    "border",
    "transition",
    "shadow",
    "gradient",
    "typography",
}

# Minimal empty scaffold used by orchestrator/unit tests.
#
# This is intentionally Copy That–oriented (token-type group roots) rather than a full
# DTCG spec document. Export logic lives in `copy_that.core_tokens.adapters.w3c`.
W3C_TOKEN_SCAFFOLD: dict[str, Any] = {
    "color": {},
    "spacing": {},
    "typography": {},
    "shadow": {},
}


def empty_scaffold() -> dict[str, Any]:
    """Return a deep-copied W3C scaffold template."""
    return deepcopy(W3C_TOKEN_SCAFFOLD)


def validate_w3c_payload(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate basic DTCG structural rules.

    Returns (is_valid, errors).
    """

    errors: list[str] = []

    def invalid_name(name: str, *, allow_root: bool) -> bool:
        if not allow_root and name.startswith("$"):
            return True
        return bool(any(ch in name for ch in ("{", "}", ".")))

    def is_token_object(obj: Any) -> bool:
        return isinstance(obj, dict) and ("$value" in obj or "$ref" in obj)

    def walk(node: Any, path: list[str]) -> None:
        if not isinstance(node, dict):
            return

        if is_token_object(node):
            # Token objects should only have $-prefixed properties.
            for key in node:
                if isinstance(key, str) and not key.startswith("$"):
                    errors.append(f"{'.'.join(path)}: token has non-$ property '{key}'")
            token_type = node.get("$type")
            if not isinstance(token_type, str):
                errors.append(f"{'.'.join(path)}: missing or invalid $type")
            elif token_type not in SUPPORTED_W3C_TYPES:
                errors.append(f"{'.'.join(path)}: unsupported $type '{token_type}'")
            if "$value" not in node and "$ref" not in node:
                errors.append(f"{'.'.join(path)}: missing $value/$ref")
            return

        for key, value in node.items():
            if not isinstance(key, str):
                continue
            if key.startswith("$") and key != "$root":
                continue
            allow_root = key == "$root"
            if invalid_name(key, allow_root=allow_root):
                errors.append(f"{'.'.join(path)}: invalid name '{key}'")
            walk(value, path + [key])

    walk(payload, [])
    return (len(errors) == 0, errors)
