"""P2b: gradient + duration/cubicBezier synthesis at export."""

from __future__ import annotations

from copy_that.core_tokens.adapters.w3c import tokens_to_w3c_flat
from copy_that.core_tokens.repository import InMemoryTokenRepository
from copy_that.generators.plugins.css import CSSGenerator
from copy_that.services.motion_service import (
    synthesize_gradient_tokens_from_colors,
    synthesize_transition_tokens,
)


class _ColorRow:
    def __init__(self, hex: str):
        self.hex = hex


def test_synthesize_gradient_tokens_from_color_pairs():
    tokens = synthesize_gradient_tokens_from_colors(
        [_ColorRow("#FF0000"), _ColorRow("#00FF00"), _ColorRow("#0000FF")]
    )
    assert len(tokens) == 2
    assert tokens[0].type == "gradient"
    assert tokens[0].value["stops"][0]["color"] == "#FF0000"
    assert tokens[0].value["stops"][1]["color"] == "#00FF00"


def test_synthesize_transition_tokens_include_duration_and_easing():
    tokens = synthesize_transition_tokens()
    types = {t.type for t in tokens}
    assert "duration" in types
    assert "cubicBezier" in types
    ids = {t.id for t in tokens}
    assert "duration.fast" in ids
    assert "cubicBezier.ease" in ids


def test_synthesize_gradient_from_single_color():
    tokens = synthesize_gradient_tokens_from_colors([_ColorRow("#FF0000")])
    assert len(tokens) == 1
    assert tokens[0].type == "gradient"
    assert tokens[0].value["stops"][0]["color"] == "#FF0000"
    assert tokens[0].value["stops"][1]["color"] == "#FFFFFF"


def test_w3c_and_css_emit_motion_tokens():
    repo = InMemoryTokenRepository()
    for token in synthesize_gradient_tokens_from_colors(
        [_ColorRow("#111111"), _ColorRow("#EEEEEE")]
    ):
        repo.upsert_token(token)
    for token in synthesize_transition_tokens():
        repo.upsert_token(token)

    payload = tokens_to_w3c_flat(repo)
    assert "gradient" in payload
    assert "duration" in payload
    assert "cubicBezier" in payload

    css = CSSGenerator(tokens=payload).generate()
    assert "linear-gradient(" in css
    assert "150ms" in css
    assert "cubic-bezier(" in css
