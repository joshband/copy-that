"""Unit tests for Fal→OpenAI mood board shim helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "mood_board_fal_openai_shim.py"


@pytest.fixture(scope="module")
def shim():
    spec = importlib.util.spec_from_file_location("mood_board_fal_openai_shim", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_parse_size_defaults(shim) -> None:
    assert shim.parse_size(None) == {"width": 1024, "height": 1024}
    assert shim.parse_size("512x768") == {"width": 512, "height": 768}


def test_fal_generate_requires_key(shim, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shim, "FAL_KEY", "")
    with pytest.raises(RuntimeError, match="FAL_KEY"):
        shim.fal_generate(prompt="x", size="512x512", n=1)
