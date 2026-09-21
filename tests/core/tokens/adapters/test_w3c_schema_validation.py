import json
from pathlib import Path

from jsonschema import Draft202012Validator

from copy_that.design_tokens import make_resolver_2025_10
from copy_that.design_tokens.resolver import validate_resolver_cross_fields
from copy_that.domain.w3c_design_tokens import SUPPORTED_W3C_TYPES
from copy_that.core_tokens.adapters.w3c import tokens_to_w3c
from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository

SCHEMA_DIR = (
    Path(__file__).resolve().parents[4]
    / "src"
    / "copy_that"
    / "design_tokens"
    / "schemas"
    / "2025_10"
)


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def _validate(schema_name: str, payload: dict) -> None:
    schema = _load_schema(schema_name)
    Draft202012Validator(schema).validate(payload)


def test_w3c_format_schema_accepts_export() -> None:
    repo = InMemoryTokenRepository()
    repo.upsert_token(Token(id="color.primary", type=TokenType.COLOR, value="#ff00ff"))
    repo.upsert_token(Token(id="spacing.md", type=TokenType.SPACING, value={"px": 8}))

    exported = tokens_to_w3c(repo)

    _validate("format.schema.json", exported)


def test_w3c_color_schema_accepts_color_section() -> None:
    repo = InMemoryTokenRepository()
    repo.upsert_token(Token(id="color.primary", type=TokenType.COLOR, value="#ff00ff"))

    exported = tokens_to_w3c(repo)

    _validate("color.schema.json", exported["color"])


def test_w3c_resolver_schema_accepts_resolver_doc() -> None:
    resolver = {
        "version": "2025.10",
        "sources": {"base": "tokens/base.json", "dark": "tokens/dark.json"},
        "contexts": {"light": ["base"], "dark": ["base", "dark"]},
        "resolutionOrder": ["light", "dark"],
    }

    _validate("resolver.schema.json", resolver)


def test_w3c_resolver_generator_validates() -> None:
    resolver = make_resolver_2025_10(
        sources={"base": "tokens/base.json", "dark": "tokens/dark.json"},
        contexts={"light": ["base"], "dark": ["base", "dark"]},
        resolution_priority=["light", "dark"],
    )

    _validate("resolver.schema.json", resolver)


def test_w3c_resolver_cross_fields_valid() -> None:
    resolver = make_resolver_2025_10(
        sources={"base": "tokens/base.json", "dark": "tokens/dark.json"},
        contexts={"light": ["base"], "dark": ["base", "dark"]},
        resolution_priority=["light", "dark"],
    )

    assert validate_resolver_cross_fields(resolver) == []


def test_w3c_resolver_cross_fields_invalid_sources() -> None:
    resolver = make_resolver_2025_10(
        sources={"base": "tokens/base.json"},
        contexts={"light": ["base", "missing"]},
        resolution_priority=["light"],
    )

    errors = validate_resolver_cross_fields(resolver)
    assert "context 'light' references unknown sources: missing" in errors


def test_w3c_resolver_cross_fields_invalid_resolution_order() -> None:
    resolver = make_resolver_2025_10(
        sources={"base": "tokens/base.json"},
        contexts={"light": ["base"], "dark": ["base"]},
        resolution_priority=["light", "unknown"],
    )

    errors = validate_resolver_cross_fields(resolver)
    assert "resolutionOrder references unknown context: unknown" in errors
    assert "resolutionOrder missing contexts: dark" in errors


def test_w3c_exported_types_are_spec_valid() -> None:
    repo = InMemoryTokenRepository()
    repo.upsert_token(Token(id="color.primary", type=TokenType.COLOR, value="#111111"))
    repo.upsert_token(Token(id="spacing.base", type=TokenType.SPACING, value={"px": 8}))
    repo.upsert_token(Token(id="font.family.base", type=TokenType.FONT_FAMILY, value="Inter"))
    repo.upsert_token(Token(id="font.size.base", type=TokenType.FONT_SIZE, value={"px": 16}))
    repo.upsert_token(
        Token(
            id="typography.body",
            type=TokenType.TYPOGRAPHY,
            value={"fontFamily": "font.family.base", "fontSize": {"px": 16}},
        )
    )
    repo.upsert_token(
        Token(
            id="shadow.card",
            type=TokenType.SHADOW,
            value={"x": 0, "y": 2, "blur": 4, "color": "#000000"},
        )
    )
    repo.upsert_token(Token(id="layout.grid", type=TokenType.GRID, value={"columns": 12}))
    repo.upsert_token(
        Token(
            id="layout.border",
            type=TokenType.LAYOUT,
            value={"border": {"width": 1, "color": "#000000", "style": "solid"}},
        )
    )

    exported = tokens_to_w3c(repo)

    # Official 13 + Compat+ layout/grid/spacing/opacity may appear on some entries
    allowed = set(SUPPORTED_W3C_TYPES) | {"layout", "grid", "spacing", "opacity"}

    for section in exported.values():
        if not isinstance(section, dict):
            continue
        for entry in section.values():
            if isinstance(entry, dict) and "$type" in entry:
                assert entry["$type"] in allowed
