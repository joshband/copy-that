import pytest

pytest.importorskip("coloraide")

from copy_that.application.shadow_extractor import ShadowExtractor


class DummyShadow:
    def __init__(
        self, color="#000", opacity=0.5, x=1, y=2, blur=3, spread=4, inset=False, type=None
    ):
        self.color = color
        self.opacity = opacity
        self.x = x
        self.y = y
        self.blur = blur
        self.spread = spread
        self.inset = inset
        self.type = type


def test_shadow_extractor_handles_multi_layer_and_inset():
    layers = [
        type(
            "L",
            (),
            {
                "shadow": [
                    DummyShadow("#112233", 0.8, 2, 4, 12, 0),
                    DummyShadow("#334455", 1, 0, 8, 16, 2, True),
                ]
            },
        )()
    ]
    extractor = ShadowExtractor(color_token_map={"#334455": "color.dark"})
    tokens = extractor.extract_shadow_tokens(layers)

    assert "shadow.1" in tokens
    value = tokens["shadow.1"]["$value"]
    assert isinstance(value, list) and len(value) == 2
    first, second = value
    assert first["type"] == "drop"
    assert first["color"].startswith("#112233")
    assert second["type"] == "inner"
    assert second["inset"] is True
    assert second["color"] == "{color.dark}"


def test_shadow_extractor_deduplicates_layers():
    shared = DummyShadow("#000000", 1, 0, 4, 8, 0)
    layers = [type("L", (), {"shadow": [shared, shared]})()]
    tokens = ShadowExtractor().extract_shadow_tokens(layers)
    assert len(tokens["shadow.1"]["$value"]) == 1
