"""Ensure typography response mapping clamps 0–1 fields from CV extractors."""

from copy_that.application.typography_extractor import ExtractedTypographyToken
from copy_that.interfaces.api.typography import _typography_token_responses


def test_prominence_above_one_is_clamped() -> None:
    token = ExtractedTypographyToken(
        font_family="System",
        font_weight=400,
        font_style="normal",
        font_size=16,
        line_height=1.2,
        letter_spacing=None,
        text_transform=None,
        text_align="left",
        semantic_role="body",
        category="text",
        name=None,
        confidence=0.6,
        prominence=2.0,
        is_readable=True,
        readability_score=0.9,
        extraction_metadata={"source": "cv_ocr_extractor"},
    )
    responses = _typography_token_responses([token])
    assert len(responses) == 1
    assert responses[0].prominence == 1.0
