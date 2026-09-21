"""Phase 1: DTCG schema + capability registry + stubs + border derive."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from copy_that.core_tokens.adapters.w3c import tokens_to_w3c
from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository
from copy_that.design_tokens.validation import validate_w3c_export
from copy_that.domain.w3c_design_tokens import SUPPORTED_W3C_TYPES
from copy_that.extractors import get_extractor, list_registered_extractors
from copy_that.extractors.border_derive import (
    BorderDeriveExtractor,
    border_tokens_from_layout_widths,
)
from copy_that.extractors.dtcg_capability import (
    OFFICIAL_DTCG_TYPES,
    CoverageStatus,
    list_capabilities,
)
from copy_that.services.motion_service import (
    synthesize_gradient_tokens_from_colors,
    synthesize_transition_tokens,
)
from copy_that.services.type_coverage_service import apply_type_coverage_synthesis

SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "src"
    / "copy_that"
    / "design_tokens"
    / "schemas"
    / "2025_10"
    / "format.schema.json"
)


class _ColorRow:
    def __init__(self, hex: str):
        self.hex = hex


class _TypoRow:
    def __init__(self, font_family: str, font_weight: int, line_height: float = 1.5):
        self.font_family = font_family
        self.font_weight = font_weight
        self.line_height = line_height


def test_format_schema_enum_covers_official_13():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    enum = set(schema["$defs"]["typeName"]["enum"])
    assert enum >= OFFICIAL_DTCG_TYPES
    assert enum >= SUPPORTED_W3C_TYPES


def test_capability_map_covers_official_13():
    caps = {c.dtcg_type for c in list_capabilities()}
    assert caps == OFFICIAL_DTCG_TYPES == SUPPORTED_W3C_TYPES


def test_registry_lists_live_derive_and_stubs():
    names = set(list_registered_extractors())
    assert {"color", "spacing", "typography", "shadow", "border"} <= names
    for derive_name in (
        "dimension",
        "fontFamily",
        "fontWeight",
        "border",
        "number",
        "strokeStyle",
        "duration",
        "cubicBezier",
        "transition",
    ):
        assert derive_name in names
        extractor = get_extractor(derive_name)
        assert extractor.token_type == derive_name
        assert getattr(extractor, "coverage_status", None) == CoverageStatus.DERIVE

    gradient_ext = get_extractor("gradient")
    assert gradient_ext.token_type == "gradient"
    assert getattr(gradient_ext, "coverage_status", None) == CoverageStatus.LIVE


def test_border_derive_from_layout_widths():
    tokens = border_tokens_from_layout_widths([1, 2])
    assert tokens
    assert all(t.type == "border" or t.type == TokenType.BORDER for t in tokens)
    assert tokens[0].value["width"]["value"] in {1.0, 2.0}

    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="layout.border.1",
            type=TokenType.LAYOUT,
            value={"border": {"width": 3}},
            attributes={"role": "border_width"},
        )
    )
    derived = BorderDeriveExtractor().derive_and_upsert(repo)
    assert repo.get_token(derived[0].id) is not None


def test_full_synth_export_validates_format_schema():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="color.primary",
            type=TokenType.COLOR,
            value="#FF0000",
            attributes={"hex": "#FF0000"},
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

    payload = tokens_to_w3c(repo)
    # Must not raise (previous bug: enum missing gradient/duration/…)
    validate_w3c_export(payload)
    Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))).validate(payload)
