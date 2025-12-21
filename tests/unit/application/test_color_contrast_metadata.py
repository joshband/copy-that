from __future__ import annotations

import base64
import io
from typing import TYPE_CHECKING

import pytest

_COLOR_DEPS: tuple[object, object, object, object] | None = None

if TYPE_CHECKING:
    from copy_that.application.color_extractor import ExtractedColorToken


def _import_color_deps():
    global _COLOR_DEPS
    if _COLOR_DEPS is None:
        pytest.importorskip("coloraide")
        PIL = pytest.importorskip("PIL")
        from copy_that.application import color_utils
        from copy_that.application.color_extractor import ExtractedColorToken
        from copy_that.application.cv.color_cv_extractor import CVColorExtractor

        _COLOR_DEPS = (color_utils, CVColorExtractor, ExtractedColorToken, PIL.Image)
    return _COLOR_DEPS


def make_token(
    hex_value: str,
    prominence: float = 0.0,
    count: int = 1,
    confidence: float = 0.9,
) -> ExtractedColorToken:
    _, _, ExtractedColorToken, _ = _import_color_deps()
    return ExtractedColorToken(
        hex=hex_value,
        rgb="rgb(0,0,0)",
        hsl=None,
        hsv=None,
        name=hex_value,
        design_intent=None,
        semantic_names=None,
        category=None,
        confidence=confidence,
        harmony=None,
        temperature=None,
        saturation_level=None,
        lightness_level=None,
        usage=[],
        count=count,
        prominence_percentage=prominence,
        wcag_contrast_on_white=None,
        wcag_contrast_on_black=None,
        wcag_aa_compliant_text=None,
        wcag_aaa_compliant_text=None,
        wcag_aa_compliant_normal=None,
        wcag_aaa_compliant_normal=None,
        colorblind_safe=None,
        tint_color=None,
        shade_color=None,
        tone_color=None,
        closest_web_safe=None,
        closest_css_named=None,
        delta_e_to_dominant=None,
        is_neutral=None,
        background_role=None,
        contrast_category=None,
        foreground_role=None,
        kmeans_cluster_id=None,
        sam_segmentation_mask=None,
        clip_embeddings=None,
        extraction_metadata=None,
        histogram_significance=None,
    )


def test_contrast_metadata_records_wcag_and_scores():
    color_utils, _, _, _ = _import_color_deps()
    tokens = [make_token("#000000"), make_token("#777777")]
    color_utils.annotate_contrast_metadata(tokens, ["#ffffff"])

    strong = tokens[0]
    weaker = tokens[1]
    assert strong.contrast_targets
    assert weaker.contrast_targets
    stronger_ratio = strong.contrast_targets[0]["ratio"]
    weaker_ratio = weaker.contrast_targets[0]["ratio"]
    assert stronger_ratio > weaker_ratio
    assert strong.role_scores and strong.role_scores["text"] >= weaker.role_scores["text"]
    assert strong.contrast_targets[0]["aa_normal"] is True
    assert weaker.contrast_targets[0]["aa_normal"] in {True, False}


def test_cluster_respects_contrast_separation_with_backgrounds():
    color_utils, _, _, _ = _import_color_deps()
    tokens = [make_token("#101010"), make_token("#151515")]
    clustered = color_utils.cluster_color_tokens(tokens, threshold=3.0, backgrounds=["#ffffff"])
    assert len(clustered) == 2  # contrast separation keeps close grays distinct


def test_cv_extractor_surfaces_contrast_debug_payload():
    _, CVColorExtractor, _, Image = _import_color_deps()
    img = Image.new("RGB", (2, 1), "#FFFFFF")
    img.putpixel((1, 0), (0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode()
    extractor = CVColorExtractor(max_colors=2, use_superpixels=False)
    result = extractor.extract_from_base64(encoded)

    assert result.debug and "contrast_matrix" in result.debug
    for token in result.colors:
        assert token.contrast_targets
