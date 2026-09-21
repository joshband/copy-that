"""Smoke helper for Midjourney sibling mood-board fixtures."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "mood_board_smoke_midjourney_pair.py"
IMG_A = Path(__file__).resolve().parents[3] / "test_images" / "IMG_8324.jpeg"
IMG_B = Path(__file__).resolve().parents[3] / "test_images" / "IMG_8325.jpeg"


@pytest.fixture(scope="module")
def smoke_mod():
    spec = importlib.util.spec_from_file_location("mood_board_smoke_midjourney_pair", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.skipif(not IMG_A.is_file() or not IMG_B.is_file(), reason="test images missing")
def test_extract_palette_from_midjourney_pair(smoke_mod) -> None:
    colors = smoke_mod.extract_palette([IMG_A, IMG_B], max_colors=6)
    assert 3 <= len(colors) <= 6
    for c in colors:
        assert c["hex"].startswith("#") and len(c["hex"]) == 7
