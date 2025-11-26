from core.tokens.model import Token
from core.tokens.shadow import ShadowLayer, make_shadow_token
from core.tokens.typography import make_typography_token


def test_make_shadow_token_uses_color_references() -> None:
    token = make_shadow_token(
        "token/shadow/elevation-1",
        layers=[
            ShadowLayer(x=0, y=2, blur=4, spread=0, color_ref="token/color/text/primary"),
            ShadowLayer(
                x=0,
                y=1,
                blur=3,
                spread=0,
                color_ref="token/color/text/muted",
                inset=True,
            ),
        ],
    )

    assert isinstance(token, Token)
    assert token.type == "shadow"
    assert token.value[0]["color"] == "token/color/text/primary"
    assert token.value[1]["color"] == "token/color/text/muted"
    assert token.value[1]["inset"] is True


def test_make_typography_token_references_color() -> None:
    token = make_typography_token(
        "token/typography/label",
        font_family="Inter",
        size="12px",
        line_height="16px",
        weight="600",
        letter_spacing="0.1em",
        casing="uppercase",
        color_ref="token/color/text/primary",
        attributes={"role": "label"},
    )

    assert isinstance(token, Token)
    assert token.type == "typography"
    assert token.value["color"] == "token/color/text/primary"
    assert token.value["fontFamily"] == "Inter"
    assert token.value["fontWeight"] == "600"
    assert token.attributes["role"] == "label"
