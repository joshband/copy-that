from copy_that.application import color_utils
from copy_that.application.color_extractor import ExtractedColorToken


def make_tok(hex_val: str, prom: float = 10.0) -> ExtractedColorToken:
    return ExtractedColorToken(
        hex=hex_val,
        rgb="rgb(0,0,0)",
        hsl=None,
        hsv=None,
        name=hex_val,
        design_intent=None,
        semantic_names=None,
        category=None,
        confidence=0.9,
        harmony=None,
        temperature=None,
        saturation_level=None,
        lightness_level=None,
        usage=[],
        count=1,
        prominence_percentage=prom,
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
        kmeans_cluster_id=None,
        sam_segmentation_mask=None,
        clip_embeddings=None,
        extraction_metadata=None,
        histogram_significance=None,
    )


def test_text_role_on_dark_background():
    bg = make_tok("#111111", prom=60)
    bg.background_role = "primary"
    fg = make_tok("#ffffff", prom=20)
    tokens = [bg, fg]
    color_utils.assign_text_roles(tokens, primary_background=bg.hex)
    assert fg.extraction_metadata.get("text_role") == "color.text.onDark"
    assert (
        fg.extraction_metadata.get("contrast_to_background")
        and fg.extraction_metadata["contrast_to_background"] >= 4.5
    )


def test_text_role_on_light_background():
    bg = make_tok("#ffffff", prom=60)
    bg.background_role = "primary"
    fg = make_tok("#000000", prom=20)
    tokens = [bg, fg]
    color_utils.assign_text_roles(tokens, primary_background=bg.hex)
    assert fg.extraction_metadata.get("text_role") == "color.text.onLight"
    assert (
        fg.extraction_metadata.get("contrast_to_background")
        and fg.extraction_metadata["contrast_to_background"] >= 4.5
    )
