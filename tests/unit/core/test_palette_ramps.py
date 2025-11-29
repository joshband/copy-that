from coloraide import Color

from core.tokens.color import make_color_ramp


def test_ramp_monotonic_lightness_and_hue_stable():
    ramp = make_color_ramp("#ff5500", prefix="color.accent")
    tokens = list(ramp.values())
    # Ensure steps sorted by id suffix
    tokens.sort(key=lambda t: int(t.id.split(".")[-1]))

    lightnesses = []
    hues = []
    for tok in tokens:
        c = Color("oklch", [tok.value["l"], tok.value["c"], tok.value["h"]])
        l, _c, h = c.convert("oklch").coords()
        lightnesses.append(l)
        hues.append(h)

    # monotonic lightness
    assert all(lightnesses[i] <= lightnesses[i + 1] for i in range(len(lightnesses) - 1))
    # hue drift small
    assert max(hues) - min(hues) < 1.0
