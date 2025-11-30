from copy_that.application.typography_recommender import StyleAttributes, TypographyRecommender


def test_minimalist_recommendation_uses_geometric_sans() -> None:
    recommender = TypographyRecommender()
    style: StyleAttributes = {
        "primary_style": "minimalist",
        "color_temperature": "warm",
        "visual_weight": "balanced",
    }

    tokens = recommender.recommend(style)

    ids = {tok.id for tok in tokens}
    assert "typography.heading.lg" in ids
    assert "typography.body" in ids

    heading = next(tok for tok in tokens if tok.id == "typography.heading.lg")
    body = next(tok for tok in tokens if tok.id == "typography.body")

    assert heading.value and heading.value.get("fontFamily") == "font.family.geometric_sans"
    assert body.value and body.value.get("fontFamily") == "font.family.geometric_sans"
    assert heading.value["fontSize"]["px"] == 32.0
    assert body.value["fontSize"]["px"] == 16.0
    assert heading.value["fontWeight"] == 700
    assert body.value["fontWeight"] == 450


def test_brutalist_heavy_recommendation_prefers_slab_serif() -> None:
    recommender = TypographyRecommender()
    style: StyleAttributes = {
        "primary_style": "brutalist",
        "color_temperature": "cool",
        "visual_weight": "heavy",
    }

    tokens = recommender.recommend(style)

    heading = next(tok for tok in tokens if tok.id == "typography.heading.lg")
    caption = next(tok for tok in tokens if tok.id == "typography.caption")

    assert heading.value and heading.value.get("fontFamily") == "font.family.slab_serif"
    assert caption.value and caption.value.get("fontFamily") == "font.family.slab_serif"
    assert heading.value["fontWeight"] == 800
    assert caption.value["fontWeight"] == 500
