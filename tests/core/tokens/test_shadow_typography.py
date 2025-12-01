from core.tokens.model import RelationType, Token, TokenType
from core.tokens.shadow import ShadowLayer, make_shadow_token
from core.tokens.typography import make_typography_token


def test_make_shadow_token_uses_color_references() -> None:
    token = make_shadow_token(
        "token/shadow/elevation-1",
        layers=[
            ShadowLayer(x=0, y=2, blur=4, spread=0, color_token_id="token/color/text/primary"),
            ShadowLayer(
                x=0,
                y=1,
                blur=3,
                spread=0,
                color_token_id="token/color/text/muted",
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
        font_family_token_id="token/font/family/inter",
        font_size_token_id="token/font/size/12px",
        line_height_px=16,
        font_weight="600",
        letter_spacing_em=0.1,
        casing="uppercase",
        color_token_id="token/color/text/primary",
        attributes={"role": "label"},
    )

    assert isinstance(token, Token)
    assert token.type == TokenType.TYPOGRAPHY
    assert token.value["color"] == "token/color/text/primary"
    assert token.value["fontFamily"] == "token/font/family/inter"
    assert token.value["fontSize"] == {"token": "token/font/size/12px"}
    assert token.attributes["role"] == "label"
    rel_targets = {rel.target for rel in token.relations}
    assert "token/color/text/primary" in rel_targets
    assert "token/font/family/inter" in rel_targets
    assert "token/font/size/12px" in rel_targets
