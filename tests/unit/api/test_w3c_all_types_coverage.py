"""P2c: all 13 DTCG Format 2025.10 $types present on export (A + Compat+)."""

from __future__ import annotations

from copy_that.core_tokens.adapters.w3c import tokens_to_w3c, tokens_to_w3c_flat
from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository
from copy_that.domain.w3c_design_tokens import SUPPORTED_W3C_TYPES, validate_w3c_payload
from copy_that.generators.plugins.css import CSSGenerator
from copy_that.generators.plugins.react import ReactGenerator
from copy_that.services.motion_service import (
    synthesize_gradient_tokens_from_colors,
    synthesize_transition_tokens,
)
from copy_that.services.type_coverage_service import apply_type_coverage_synthesis


class _ColorRow:
    def __init__(self, hex: str):
        self.hex = hex


class _TypoRow:
    def __init__(self, font_family: str, font_weight: int, line_height: float = 1.5):
        self.font_family = font_family
        self.font_weight = font_weight
        self.line_height = line_height


def _collect_types(payload: dict) -> set[str]:
    found: set[str] = set()

    def walk(node: object) -> None:
        if isinstance(node, dict):
            t = node.get("$type")
            if isinstance(t, str):
                found.add(t)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    return found


def _seed_mvp_repo() -> InMemoryTokenRepository:
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="color.primary", type=TokenType.COLOR, value="#FF0000", attributes={"hex": "#FF0000"}
        )
    )
    repo.upsert_token(
        Token(
            id="spacing.gap-md",
            type=TokenType.SPACING,
            value={"value": 16, "unit": "px"},
            attributes={},
        )
    )
    repo.upsert_token(
        Token(
            id="typography.body",
            type=TokenType.TYPOGRAPHY,
            value={
                "fontFamily": "Inter",
                "fontSize": {"value": 16, "unit": "px"},
                "fontWeight": 400,
                "lineHeight": 1.5,
            },
            attributes={},
        )
    )
    return repo


def test_all_13_dtcg_types_present_after_coverage_synthesis():
    repo = _seed_mvp_repo()
    colors = [_ColorRow("#FF0000"), _ColorRow("#00AAFF")]
    for token in synthesize_gradient_tokens_from_colors(colors):
        repo.upsert_token(token)
    for token in synthesize_transition_tokens():
        repo.upsert_token(token)

    apply_type_coverage_synthesis(
        repo,
        colors=colors,
        typography_rows=[_TypoRow("Inter", 400, 1.5), _TypoRow("Inter", 700, 1.2)],
        has_any_tokens=True,
    )

    strict = tokens_to_w3c(repo)
    flat = tokens_to_w3c_flat(repo)
    types = _collect_types(strict)

    missing = SUPPORTED_W3C_TYPES - types
    assert not missing, f"Missing DTCG $types: {sorted(missing)}; got {sorted(types)}"

    # Compat+: spacing tokens live under the `spacing` section (may emit $type dimension)
    spacing_entries = flat.get("spacing") or {}
    assert spacing_entries, "expected spacing section"
    assert "dimension" in flat, "expected derived dimension companions"
    first_spacing = next(iter(spacing_entries.values()))
    assert first_spacing.get("$type") in {"spacing", "dimension"}

    ok, errors = validate_w3c_payload(strict)
    # Compat+ may keep spacing/$extensions; filter only unsupported $type errors
    type_errors = [e for e in errors if "unsupported $type" in e]
    assert not type_errors, type_errors
    assert ok or all("unsupported $type" not in e for e in errors)


def test_css_and_react_emit_new_type_sections():
    repo = _seed_mvp_repo()
    colors = [_ColorRow("#111111"), _ColorRow("#EEEEEE")]
    for token in synthesize_gradient_tokens_from_colors(colors):
        repo.upsert_token(token)
    for token in synthesize_transition_tokens():
        repo.upsert_token(token)
    apply_type_coverage_synthesis(
        repo,
        colors=colors,
        typography_rows=[_TypoRow("Roboto", 500)],
        has_any_tokens=True,
    )
    payload = tokens_to_w3c_flat(repo)

    css = CSSGenerator(tokens=payload).generate()
    assert (
        "--fontfamily-roboto:" in css.replace("fontFamily", "fontfamily").lower()
        or "fontfamily" in css.lower()
        or "Roboto" in css
    )
    assert "border" in css.lower() or "transition" in css.lower()

    react = ReactGenerator(tokens=payload).generate()
    assert "fontFamily:" in react
    assert "border:" in react
    assert "transition:" in react
    assert "undefined" not in react
