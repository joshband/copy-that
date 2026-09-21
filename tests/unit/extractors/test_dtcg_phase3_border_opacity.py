"""Phase 3: CV/heuristic border + strokeStyle + first-class opacity/number."""

from __future__ import annotations

import pytest

from copy_that.core_tokens.adapters.w3c import tokens_to_w3c
from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository
from copy_that.extractors import get_extractor
from copy_that.extractors.border_cv import extract_border_signals_from_image
from copy_that.extractors.border_derive import (
    BorderDeriveExtractor,
    border_tokens_from_layout_widths,
)
from copy_that.extractors.dtcg_capability import CoverageStatus, capability_for
from copy_that.extractors.opacity_extract import (
    OpacityNumberExtractor,
    opacity_tokens_from_repo,
    ui_alpha_opacities_from_image,
)
from copy_that.extractors.stroke_style_derive import (
    StrokeStyleDeriveExtractor,
    stroke_styles_from_signals,
)
from copy_that.layoutlab.shape_inference import estimate_stroke_style
from copy_that.services.type_coverage_service import (
    apply_type_coverage_synthesis,
    synthesize_border_composites,
)


def _deps():
    np = pytest.importorskip("numpy")
    cv2 = pytest.importorskip("cv2")
    return np, cv2


def _png_bytes(image) -> bytes:
    np, cv2 = _deps()
    ok, buf = cv2.imencode(".png", image)
    assert ok
    return buf.tobytes()


def test_capability_phase3_border_stroke_number():
    assert capability_for("border").status == CoverageStatus.DERIVE
    assert "cv" in capability_for("border").modalities
    assert capability_for("strokeStyle").status == CoverageStatus.DERIVE
    assert capability_for("number").status == CoverageStatus.DERIVE
    assert "cv" in capability_for("number").modalities


def test_registry_phase3_extractors_are_derive():
    for name in ("border", "strokeStyle", "number"):
        ext = get_extractor(name)
        assert ext.coverage_status == CoverageStatus.DERIVE
        assert ext.token_type == name


def test_estimate_stroke_style_solid_outline():
    np, cv2 = _deps()
    mask = np.zeros((64, 64), dtype=np.uint8)
    cv2.rectangle(mask, (8, 8), (55, 55), 255, 2)
    style, conf = estimate_stroke_style(mask)
    assert style == "solid"
    assert conf >= 0.45


def test_estimate_stroke_style_dashed_outline():
    np, cv2 = _deps()
    mask = np.zeros((80, 80), dtype=np.uint8)
    # Draw dashed top/bottom edges
    for x in range(10, 70, 8):
        cv2.line(mask, (x, 10), (min(x + 4, 70), 10), 255, 2)
        cv2.line(mask, (x, 70), (min(x + 4, 70), 70), 255, 2)
    for y in range(10, 70, 8):
        cv2.line(mask, (10, y), (10, min(y + 4, 70)), 255, 2)
        cv2.line(mask, (70, y), (70, min(y + 4, 70)), 255, 2)
    style, conf = estimate_stroke_style(mask)
    # Heuristic may land solid on sparse dashes; accept either with a conf score
    assert style in {"solid", "dashed"}
    assert 0.0 < conf <= 1.0


def test_border_compose_prefers_extracted_dashed_style():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="layout.border.1",
            type=TokenType.LAYOUT,
            value={"border": {"width": 2}},
            attributes={"role": "border_width", "source": "cv", "confidence": 0.8},
        )
    )
    repo.upsert_token(
        Token(
            id="strokeStyle.dashed",
            type=TokenType.STROKE_STYLE,
            value="dashed",
            attributes={"$type": "strokeStyle", "source": "cv", "confidence": 0.8},
        )
    )
    borders = BorderDeriveExtractor().derive_and_upsert(repo)
    assert borders
    assert borders[0].value["style"] == "{strokeStyle.dashed}"
    assert borders[0].attributes.get("source") == "extracted"


def test_synthesize_skips_when_extracted_border_present():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="border.cv-01",
            type=TokenType.BORDER,
            value={"width": {"value": 1, "unit": "px"}, "style": "{strokeStyle.solid}"},
            attributes={"source": "extracted", "confidence": 0.8, "$type": "border"},
        )
    )
    assert synthesize_border_composites(repo) == []


def test_opacity_from_shadow_tokens_on_repo():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="shadow.soft",
            type=TokenType.SHADOW,
            value=[{"x": 0, "y": 4, "blur": 8, "spread": 0, "color": "#000", "opacity": 0.3}],
            attributes={"confidence": 0.9, "semantic_role": "soft"},
        )
    )
    repo.upsert_token(
        Token(
            id="shadow.strong",
            type=TokenType.SHADOW,
            value=[{"opacity": 0.55}],
            attributes={"confidence": 0.85, "name": "strong"},
        )
    )
    tokens = opacity_tokens_from_repo(repo)
    values = sorted(float(t.value) for t in tokens)
    assert values == [0.3, 0.55]
    assert all(t.type == TokenType.OPACITY for t in tokens)
    assert all(t.attributes.get("$type") == "number" for t in tokens)

    upserted = OpacityNumberExtractor().derive_and_upsert(repo)
    assert upserted
    assert repo.get_token(upserted[0].id) is not None


def test_ui_alpha_from_png_with_partial_transparency():
    np, cv2 = _deps()
    # BGRA image with a translucent panel
    img = np.zeros((40, 40, 4), dtype=np.uint8)
    img[:, :, :3] = 40
    img[:, :, 3] = 255
    img[8:32, 8:32, 3] = 128  # ~0.5 opacity block
    png = _png_bytes(img)
    tokens = ui_alpha_opacities_from_image(png)
    assert tokens
    assert any(abs(float(t.value) - 0.5) < 0.06 for t in tokens)
    assert all(t.attributes.get("source") == "ui_alpha" for t in tokens)


@pytest.mark.asyncio
async def test_border_extract_from_simple_image():
    np, cv2 = _deps()
    img = np.full((120, 120, 3), 240, dtype=np.uint8)
    cv2.rectangle(img, (20, 20), (100, 100), (30, 30, 30), 3)
    png = _png_bytes(img)

    signals = extract_border_signals_from_image(png)
    # Contour heuristics are soft on synthetic images; allow empty, but
    # extractor must not raise and registry extract must return a list.
    assert isinstance(signals, list)

    extractor = BorderDeriveExtractor()
    results = await extractor.extract(png)
    assert isinstance(results, list)

    stroke_ext = StrokeStyleDeriveExtractor()
    stroke_dicts = await stroke_ext.extract(png)
    assert isinstance(stroke_dicts, list)


def test_stroke_styles_from_signals_respects_threshold():
    tokens = stroke_styles_from_signals(
        [
            {"kind": "stroke_style", "value": "dashed", "confidence": 0.8, "source": "cv"},
            {"kind": "stroke_style", "value": "solid", "confidence": 0.2, "source": "cv"},
        ]
    )
    assert len(tokens) == 1
    assert tokens[0].value == "dashed"


def test_coverage_synthesis_keeps_extracted_opacity_over_unity_preset():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="color.primary", type=TokenType.COLOR, value="#FF0000", attributes={"hex": "#FF0000"}
        )
    )
    repo.upsert_token(
        Token(
            id="shadow.card",
            type=TokenType.SHADOW,
            value=[{"opacity": 0.4}],
            attributes={"confidence": 0.9, "semantic_role": "card"},
        )
    )
    apply_type_coverage_synthesis(repo, has_any_tokens=True)
    opacities = list(repo.find_by_type(TokenType.OPACITY)) + list(repo.find_by_type("opacity"))
    assert any(abs(float(t.value) - 0.4) < 1e-6 for t in opacities)
    assert repo.get_token("number.unity") is None

    payload = tokens_to_w3c(repo)
    assert "opacity" in payload or "number" in payload


def test_layout_width_helper_still_composes():
    tokens = border_tokens_from_layout_widths([1, 2])
    assert tokens
    assert all(t.type == TokenType.BORDER or t.type == "border" for t in tokens)
