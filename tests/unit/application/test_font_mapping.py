from copy_that.application.font_mapping import FONT_PROFILES, font_category_for_style


def test_font_category_for_style_mapping() -> None:
    assert font_category_for_style("minimalist") == "geometric_sans"
    assert font_category_for_style("technical") == "geometric_sans"
    assert font_category_for_style("elegant") == "serif"
    assert font_category_for_style("brutalist") == "slab_serif"
    assert font_category_for_style("playful") == "display"
    assert font_category_for_style("unknown") == "humanist_sans"


def test_font_profiles_have_google_font_family() -> None:
    assert all(profile.get("google_font_family") for profile in FONT_PROFILES.values())
