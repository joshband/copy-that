import json
from pathlib import Path

import pytest

from copy_that.application.cv.spacing_cv_extractor import CVSpacingExtractor

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures"
MANIFEST = FIXTURE_ROOT / "manifest.json"


def _load_manifest():
    if not MANIFEST.exists():
        return {"cases": []}
    return json.loads(MANIFEST.read_text())


def _load_bytes(path: Path) -> bytes:
    return path.read_bytes()


def test_ui_regression_manifest():
    manifest = _load_manifest()
    cases = manifest.get("cases", [])
    if not cases:
        pytest.skip("No regression fixtures configured yet")

    extractor = CVSpacingExtractor()
    for case in cases:
        file_name = case.get("file")
        expect = case.get("expect", {})
        if not file_name:
            continue
        img_path = FIXTURE_ROOT / file_name
        if not img_path.exists():
            pytest.skip(f"Fixture missing: {img_path}")
        result = extractor.extract_from_bytes(_load_bytes(img_path))
        tokens = result.tokens or []
        if "min_components" in expect:
            assert len(tokens) >= expect["min_components"]
        if "max_spacing_tokens" in expect:
            assert len(tokens) <= expect["max_spacing_tokens"]
        gaps = result.gap_clusters.get("x") if hasattr(result, "gap_clusters") else None
        if expect.get("expected_gaps") and gaps:
            for gap in expect["expected_gaps"]:
                assert any(abs(g - gap) <= 2 for g in gaps), f"Expected gap {gap}px not found"
