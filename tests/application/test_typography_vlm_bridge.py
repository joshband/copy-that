from copy_that.application.typography_recommender import TypographyRecommender


def test_attributes_from_vlm_applies_defaults() -> None:
    recommender = TypographyRecommender()
    attrs = recommender.attributes_from_vlm({})

    assert attrs["primary_style"] == "minimalist"
    assert attrs["color_temperature"] == "neutral"
    assert attrs["visual_weight"] == "balanced"
    assert attrs["contrast_level"] == "medium"
    assert attrs["vlm_confidence"] == 0.0


def test_attributes_from_vlm_maps_fields() -> None:
    recommender = TypographyRecommender()
    raw = {
        "primary_style": "brutalist",
        "mood": "bold",
        "color_temperature": "cool",
        "visual_weight": "heavy",
        "contrast_level": "high",
        "confidence": 0.82,
        "complexity": "high",
    }

    attrs = recommender.attributes_from_vlm(raw)

    assert attrs["primary_style"] == "brutalist"
    assert attrs["vlm_mood"] == "bold"
    assert attrs["vlm_confidence"] == 0.82
    assert attrs["vlm_complexity"] == "high"
