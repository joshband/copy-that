from copy_that.application.color_extractor import ExtractedColorToken
from copy_that.core_tokens.repository import InMemoryTokenRepository
from copy_that.interfaces.api.colors import _add_colors_to_repo
from copy_that.services.colors_service import add_role_tokens


def make_token(hex_value: str, background_role: str | None = None) -> ExtractedColorToken:
    return ExtractedColorToken(
        hex=hex_value,
        rgb="rgb(0,0,0)",
        hsl=None,
        hsv=None,
        name=hex_value,
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
        prominence_percentage=10.0,
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
        background_role=background_role,
        contrast_category=None,
        kmeans_cluster_id=None,
        sam_segmentation_mask=None,
        clip_embeddings=None,
        extraction_metadata=None,
        histogram_significance=None,
    )


def test_role_alias_tokens_added():
    repo = InMemoryTokenRepository()
    ns = "token/color/test"
    tokens = [
        make_token("#111111", background_role="primary"),
        make_token("#FFFFFF"),
        make_token("#EEEEEE"),
    ]
    _add_colors_to_repo(repo, tokens, ns)
    add_role_tokens(repo, ns, ["#111111"])

    aliases = {
        tok.id: tok
        for tok in repo.find_by_type("color")
        if "text/" in tok.id or "background" in tok.id
    }
    assert f"{ns}/background" in aliases
    # expect text/onDark alias pointing to light color
    has_on_dark = any(id.endswith("text/onDark") for id in aliases)
    has_on_light = any(id.endswith("text/onLight") for id in aliases)
    assert has_on_dark or has_on_light
    # alias value should be a reference string
    for tok in aliases.values():
        assert isinstance(tok.value, str)
        assert tok.value.startswith("{")


def test_post_process_and_response_with_oklch_hex():
    """Non-stream extract fails when CV state variants carry oklch(...) as hex."""
    from copy_that.application.color_extractor import ColorExtractionResult
    from copy_that.interfaces.api import colors as colors_api
    from copy_that.services.colors_service import post_process_colors

    oklch_hover = "oklch(0.73589 0.21747 38.802)"
    tokens = [
        make_token("#111111", background_role="primary"),
        make_token("#ff5500"),
        make_token(oklch_hover),
    ]
    tokens[2].extraction_metadata = {"state_role": "hover"}

    processed, backgrounds = post_process_colors(tokens, ["#111111"])
    assert backgrounds
    for tok in processed:
        assert tok.hex.startswith("#"), f"expected #RRGGBB, got {tok.hex!r}"
        assert len(tok.hex.lstrip("#")) == 6
        assert all(c in "0123456789abcdefABCDEF" for c in tok.hex.lstrip("#"))

    result = ColorExtractionResult(
        colors=processed,
        dominant_colors=[processed[0].hex],
        color_palette="test",
        extraction_confidence=0.9,
        extractor_used="cv",
        background_colors=backgrounds,
    )
    response = colors_api._result_to_response(result)
    assert len(response.colors) >= 1
    for color in response.colors:
        assert color.hex.startswith("#")
        assert "oklch" not in color.hex.lower()
