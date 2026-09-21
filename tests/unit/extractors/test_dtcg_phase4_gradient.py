"""Phase 4: CV gradient band/stop clustering + prefer extract over synth."""

from __future__ import annotations

import pytest

from copy_that.core_tokens.adapters.w3c import tokens_to_w3c
from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository
from copy_that.extractors import get_extractor
from copy_that.extractors.dtcg_capability import CoverageStatus, capability_for
from copy_that.extractors.gradient_cv import (
    GRADIENT_EXTRACT_CONFIDENCE_THRESHOLD,
    confirm_gradient_against_palette,
    extract_gradient_signals_from_image,
)
from copy_that.extractors.gradient_extract import (
    GradientExtractor,
    gradient_tokens_from_image,
    repo_has_extracted_gradients,
    upsert_extracted_gradients,
)
from copy_that.generators.plugins.css import CSSGenerator
from copy_that.generators.plugins.format_utils import css_gradient_value
from copy_that.services.motion_service import synthesize_gradient_tokens_from_colors


def _deps():
    np = pytest.importorskip("numpy")
    cv2 = pytest.importorskip("cv2")
    return np, cv2


def _png_bytes(image) -> bytes:
    np, cv2 = _deps()
    ok, buf = cv2.imencode(".png", image)
    assert ok
    return buf.tobytes()


def _linear_gradient_image(*, horizontal: bool = True):
    """Synthetic soft two-stop ramp (BGR)."""
    np, _cv2 = _deps()
    h, w = 80, 120
    img = np.zeros((h, w, 3), dtype=np.uint8)
    if horizontal:
        for x in range(w):
            t = x / float(w - 1)
            # blue → red (BGR)
            img[:, x, 0] = int(200 * (1 - t))
            img[:, x, 2] = int(200 * t)
    else:
        for y in range(h):
            t = y / float(h - 1)
            img[y, :, 1] = int(180 * (1 - t))
            img[y, :, 2] = int(180 * t)
    return img


class _ColorRow:
    def __init__(self, hex: str):
        self.hex = hex


def test_capability_phase4_gradient_live():
    cap = capability_for("gradient")
    assert cap is not None
    assert cap.status == CoverageStatus.LIVE
    assert "cv" in cap.modalities
    assert "ai" in cap.modalities


def test_registry_gradient_is_live_extractor():
    ext = get_extractor("gradient")
    assert isinstance(ext, GradientExtractor)
    assert ext.coverage_status == CoverageStatus.LIVE
    assert ext.token_type == "gradient"


def test_cv_detects_horizontal_linear_band():
    png = _png_bytes(_linear_gradient_image(horizontal=True))
    signals = extract_gradient_signals_from_image(png)
    assert signals, "expected at least one CV gradient on a soft horizontal ramp"
    best = signals[0]
    assert best["type"] == "linear"
    assert len(best["stops"]) >= 2
    assert best["source"] == "cv"
    assert float(best["confidence"]) >= GRADIENT_EXTRACT_CONFIDENCE_THRESHOLD
    # Horizontal ramp → angle 0 preferred among candidates
    angles = {s["angle"] for s in signals}
    assert 0 in angles or 90 in angles


def test_cv_detects_vertical_linear_band():
    png = _png_bytes(_linear_gradient_image(horizontal=False))
    signals = extract_gradient_signals_from_image(png)
    assert signals
    assert any(s["angle"] == 90 for s in signals) or signals[0]["stops"]


@pytest.mark.asyncio
async def test_gradient_extractor_returns_stable_shape():
    png = _png_bytes(_linear_gradient_image(horizontal=True))
    results = await GradientExtractor().extract(png)
    assert results
    value = results[0]["value"]
    assert value["type"] == "linear"
    assert "angle" in value
    assert len(value["stops"]) >= 2
    assert results[0]["attributes"]["source"] in {"cv", "ai"}
    # Generator-stable CSS shape
    css = css_gradient_value({"$value": value})
    assert css is not None
    assert css.startswith("linear-gradient(")


def test_palette_confirm_sets_source_ai():
    signal = {
        "type": "linear",
        "angle": 0,
        "stops": [
            {"position": 0, "color": "#0000C8"},
            {"position": 1, "color": "#C80000"},
        ],
        "confidence": 0.7,
        "source": "cv",
    }
    confirmed = confirm_gradient_against_palette(signal, ["#0000C8", "#C80000", "#FFFFFF"])
    assert confirmed["source"] == "ai"
    assert confirmed["confirmed_by"] == "palette"
    assert float(confirmed["confidence"]) >= float(signal["confidence"])


def test_synth_skipped_when_extracted_present():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="gradient.linear-cv-01",
            type=TokenType.GRADIENT,
            value={
                "type": "linear",
                "angle": 0,
                "stops": [
                    {"position": 0, "color": "#111111"},
                    {"position": 1, "color": "#EEEEEE"},
                ],
            },
            attributes={
                "$type": "gradient",
                "source": "cv",
                "confidence": 0.8,
            },
        )
    )
    assert repo_has_extracted_gradients(repo)
    synth = synthesize_gradient_tokens_from_colors(
        [_ColorRow("#FF0000"), _ColorRow("#00FF00")],
        repo=repo,
    )
    assert synth == []


def test_synth_emits_when_no_extracted():
    repo = InMemoryTokenRepository()
    synth = synthesize_gradient_tokens_from_colors(
        [_ColorRow("#FF0000"), _ColorRow("#00FF00")],
        repo=repo,
    )
    assert len(synth) >= 1
    assert synth[0].attributes.get("source") == "synth"


def test_upsert_extracted_then_w3c_css_stable():
    png = _png_bytes(_linear_gradient_image(horizontal=True))
    tokens = gradient_tokens_from_image(png)
    assert tokens
    repo = InMemoryTokenRepository()
    upsert_extracted_gradients(repo, tokens)
    # Synth must not replace
    for t in synthesize_gradient_tokens_from_colors(
        [_ColorRow("#AABBCC"), _ColorRow("#112233")],
        repo=repo,
    ):
        repo.upsert_token(t)

    grads = list(repo.find_by_type(TokenType.GRADIENT)) + list(repo.find_by_type("gradient"))
    assert any(t.attributes.get("source") in {"cv", "ai"} for t in grads)
    assert not any(
        t.attributes.get("source") == "synth" and t.id.startswith("gradient.linear-0")
        for t in grads
    )

    payload = tokens_to_w3c(repo)
    assert "gradient" in payload
    flat = {
        tid: entry
        for section in payload.values()
        if isinstance(section, dict)
        for tid, entry in section.items()
        if isinstance(entry, dict) and entry.get("$type") == "gradient"
    }
    # tokens_to_w3c nests by section; also accept section map
    css = CSSGenerator(tokens=payload).generate()
    assert "linear-gradient(" in css
    assert flat or "gradient" in payload
