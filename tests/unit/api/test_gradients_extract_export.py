"""API / export wiring for CV gradient extract → prefer over synth."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from copy_that.core_tokens.adapters.w3c import tokens_to_w3c_flat
from copy_that.core_tokens.repository import InMemoryTokenRepository
from copy_that.extractors.gradient_extract import (
    gradient_tokens_from_image,
    repo_has_extracted_gradients,
)
from copy_that.services.gradient_service import db_gradients_to_repo
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
    """Synthetic soft two-stop ramp (BGR) — matches phase4 fixture."""
    np, _cv2 = _deps()
    h, w = 80, 120
    img = np.zeros((h, w, 3), dtype=np.uint8)
    if horizontal:
        for x in range(w):
            t = x / float(w - 1)
            img[:, x, 0] = int(200 * (1 - t))
            img[:, x, 2] = int(200 * t)
    else:
        for y in range(h):
            t = y / float(h - 1)
            img[y, :, 1] = int(180 * (1 - t))
            img[y, :, 2] = int(180 * t)
    return img


def test_cv_fixture_yields_gradient_type_without_synth():
    png = _png_bytes(_linear_gradient_image(horizontal=True))
    tokens = gradient_tokens_from_image(png)
    assert tokens, "expected CV gradient tokens on horizontal band fixture"
    assert all(t.type.value == "gradient" or str(t.type) == "gradient" for t in tokens)

    repo = InMemoryTokenRepository()
    for t in tokens:
        repo.upsert_token(t)
    assert repo_has_extracted_gradients(repo)

    class _Color:
        def __init__(self, hex_value: str) -> None:
            self.hex_value = hex_value
            self.hex = hex_value

    synth = synthesize_gradient_tokens_from_colors(
        [_Color("#FF0000"), _Color("#0000FF")],
        repo=repo,
        prefer_extracted=True,
    )
    assert synth == []

    flat = tokens_to_w3c_flat(repo)
    gradient_entries = [
        entry
        for section in flat.values()
        if isinstance(section, dict)
        for entry in section.values()
        if isinstance(entry, dict) and entry.get("$type") == "gradient"
    ]
    assert gradient_entries, "W3C export should include $type: gradient from CV extract"
    for entry in gradient_entries:
        assert "confidence" not in entry  # namespaced into $extensions
        ext = entry.get("$extensions") or {}
        assert ext.get("com.copythat.source") == "extract"
        assert isinstance(ext.get("com.copythat.confidence"), float)


def test_db_gradients_to_repo_prefers_extract_over_synth():
    row = SimpleNamespace(
        id=1,
        project_id=1,
        name="linear-cv-01",
        gradient_type="linear",
        angle=0.0,
        stops_json=json.dumps(
            [
                {"position": 0.0, "color": "#FF0000"},
                {"position": 1.0, "color": "#0000FF"},
            ]
        ),
        source="cv",
        confidence=0.8,
        axis="horizontal",
        confirmed_by=None,
    )
    repo = db_gradients_to_repo([row], namespace="token/gradient/export/project/1")
    assert repo_has_extracted_gradients(repo)

    class _Color:
        def __init__(self, hex_value: str) -> None:
            self.hex_value = hex_value
            self.hex = hex_value

    synth = synthesize_gradient_tokens_from_colors(
        [_Color("#112233"), _Color("#445566")],
        repo=repo,
        prefer_extracted=True,
    )
    assert synth == []
    flat = tokens_to_w3c_flat(repo)
    assert any(
        isinstance(entry, dict) and entry.get("$type") == "gradient"
        for section in flat.values()
        if isinstance(section, dict)
        for entry in section.values()
    )
