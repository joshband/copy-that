from core.tokens.model import RelationType, Token, TokenType
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
    assert token.type == TokenType.SHADOW
    assert token.value[0]["color"] == "token/color/text/primary"
    assert token.value[1]["color"] == "token/color/text/muted"
    assert token.value[1]["inset"] is True
    assert token.relations[0].type == RelationType.COMPOSES
    assert token.relations[0].target == "token/color/text/primary"
    assert token.relations[1].target == "token/color/text/muted"


def test_make_typography_token_references_color() -> None:
    token = make_typography_token(
        "token/typography/label",
        font_family_ref="token/font/family/inter",
        size_ref="token/font/size/12px",
        line_height_ref="token/font/lineHeight/16px",
        weight_ref="600",
        letter_spacing_ref="0.1em",
        casing="uppercase",
        color_ref="token/color/text/primary",
        attributes={"role": "label"},
    )

    assert isinstance(token, Token)
    assert token.type == TokenType.TYPOGRAPHY
    assert token.value["color"] == "token/color/text/primary"
    assert token.value["fontFamily"] == "token/font/family/inter"
    assert token.value["fontSize"] == "token/font/size/12px"
    assert token.attributes["role"] == "label"
    rel_targets = {rel.target for rel in token.relations}
    assert "token/color/text/primary" in rel_targets
    assert "token/font/family/inter" in rel_targets
    assert "token/font/size/12px" in rel_targets
