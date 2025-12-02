from copy_that.application.color_extractor import ExtractedColorToken
from copy_that.interfaces.api.colors import _add_colors_to_repo
from copy_that.services.colors_service import add_role_tokens
from core.tokens.repository import InMemoryTokenRepository


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
