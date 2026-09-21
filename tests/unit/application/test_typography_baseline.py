import pytest

pytest.importorskip("PIL")

from copy_that.extractors.typography.cv_extractor import CVTypographyExtractor


def test_typography_baseline_and_overlay_from_groups():
    extractor = CVTypographyExtractor()
    groups = {
        (16, "middle", True): [
            {"text": "Hello", "height": 16, "left": 0, "top": 0, "width": 40, "confidence": 0.9},
            {"text": "World", "height": 16, "left": 0, "top": 20, "width": 40, "confidence": 0.9},
        ]
    }

    tokens = extractor._groups_to_tokens(groups)
    assert tokens
    tok = tokens[0]
    assert 1.2 <= tok.line_height <= 2.0
    meta = tok.extraction_metadata or {}
    assert meta.get("baseline_spacing_px") >= tok.font_size
    assert isinstance(meta.get("baseline_overlay"), str)
