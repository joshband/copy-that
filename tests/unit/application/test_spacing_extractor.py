"""Unit tests for AI spacing extractor parsing and fallbacks."""

from copy_that.application.spacing_extractor import AISpacingExtractor


def test_parse_spacing_response_deduplicates_and_orders():
    extractor = AISpacingExtractor(api_key="dummy", model="dummy")
    payload = {
        "tokens": [
            {"value_px": 8, "name": "spacing-sm", "semantic_role": "padding", "confidence": 0.9},
            {"value_px": 16, "name": "spacing-md", "semantic_role": "padding", "confidence": 0.8},
            {"value_px": 8, "name": "dup", "semantic_role": "padding", "confidence": 0.7},
        ],
        "base_unit": 8,
        "scale_system": "8pt",
        "grid_compliance": 0.9,
        "extraction_confidence": 0.85,
    }

    result = extractor._parse_spacing_response(payload, max_tokens=5)  # type: ignore[attr-defined]
    assert len(result.tokens) == 2
    assert result.base_unit == 8
    assert result.scale_system == "8pt"
    assert result.unique_values == [8, 16]
    assert result.grid_compliance == 0.9
    assert result.extraction_confidence == 0.85


def test_parse_spacing_response_fallback_on_empty():
    extractor = AISpacingExtractor(api_key="dummy", model="dummy")
    result = extractor._parse_spacing_response({}, max_tokens=3)  # type: ignore[attr-defined]
    assert result.tokens  # fallback tokens present
    assert result.base_unit == 4
    assert result.scale_system == "4pt"
