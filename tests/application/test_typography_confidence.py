from copy_that.application.typography_recommender import StyleAttributes, TypographyRecommender


def test_confidence_combines_vlm_and_style() -> None:
    recommender = TypographyRecommender()
    style: StyleAttributes = {"primary_style": "minimalist", "vlm_confidence": 0.9}

    result = recommender.recommend_with_confidence(style)

    assert result["confidence"] >= 0.7
    assert len(result["tokens"]) >= 2


def test_confidence_defaults_low_when_unknown_style() -> None:
    recommender = TypographyRecommender()
    style: StyleAttributes = {"primary_style": "unknown-style", "vlm_confidence": 0.2}

    result = recommender.recommend_with_confidence(style)

    assert result["confidence"] <= 0.5
