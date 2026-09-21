from dataclasses import dataclass

from copy_that.application.shadow_extractor import ShadowExtractor, ShadowStyle


@dataclass
class Layer:
    name: str
    shadow: ShadowStyle | None = None


def test_duplicate_shadows_single_token():
    style = ShadowStyle(color="#000000", opacity=0.25, x=0, y=4, blur=8, spread=0)
    layers = [Layer(name="card1", shadow=style), Layer(name="card2", shadow=style)]
    extractor = ShadowExtractor(color_token_map={"#000000": "color.black"})

    tokens = extractor.extract_shadow_tokens(layers)

    assert len(tokens) == 1
    token = list(tokens.values())[0]
    assert token["$type"] == "shadow"
    val = token["$value"]
    assert val["color"] in ("{color.black}", "{color.black}25%")
    assert val["blur"]["value"] == 8 and val["blur"]["unit"] == "px"
    assert val["y"]["value"] == 4


def test_shadow_without_color_reference():
    style = ShadowStyle(color="#ff0000", opacity=1.0, x=2, y=2, blur=4, spread=0)
    layers = [Layer(name="btn", shadow=style)]
    extractor = ShadowExtractor()

    tokens = extractor.extract_shadow_tokens(layers)
    assert len(tokens) == 1
    token = list(tokens.values())[0]
    val = token["$value"]
    assert val["color"].lower() == "#ff0000"
    assert val["x"]["unit"] == "px"
