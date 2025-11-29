from copy_that.application import color_utils
from copy_that.application.color_extractor import ExtractedColorToken


def make_token(
    hex_value: str,
    prominence: float = 0.0,
    count: int = 1,
    confidence: float = 0.9,
) -> ExtractedColorToken:
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
        kmeans_cluster_id=None,
        sam_segmentation_mask=None,
        clip_embeddings=None,
        extraction_metadata=None,
        histogram_significance=None,
    )


def test_cluster_color_tokens_merges_near_duplicates():
    tokens = [
        make_token("#FFFFFF", prominence=10),
        make_token("#FEFEFE", prominence=5),
        make_token("#000000"),
    ]

    clustered = color_utils.cluster_color_tokens(tokens, threshold=2.5)

    assert len(clustered) == 2  # whites merged
    merged_rep = next(tok for tok in clustered if tok.hex.lower().startswith("#f"))
    assert "merged_hex" in (merged_rep.extraction_metadata or {})


def test_assign_background_roles_picks_primary():
    tokens = [
        make_token("#111111", prominence=60, count=5),
        make_token("#eeeeee", prominence=20, count=1),
    ]

    backgrounds = color_utils.assign_background_roles(tokens)

    assert backgrounds[0].lower() == "#111111"
    assert tokens[0].background_role == "primary"
    assert tokens[1].background_role is None or tokens[1].background_role == "secondary"


def test_apply_contrast_categories_labels_against_background():
    bg = "#ffffff"
    tokens = [make_token("#111111"), make_token("#cccccc")]

    color_utils.apply_contrast_categories(tokens, bg)

    categories = {tok.hex: tok.contrast_category for tok in tokens}
    assert categories["#111111"] == "high"
    assert categories["#cccccc"] in {"low", "medium"}
