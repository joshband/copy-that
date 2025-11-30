from core.tokens.adapters.w3c import tokens_to_w3c
from core.tokens.model import RelationType, Token, TokenType
from core.tokens.repository import InMemoryTokenRepository
from core.tokens.shadow import ShadowLayer, make_shadow_token
from core.tokens.typography import make_typography_token


def test_shadow_w3c_uses_references() -> None:
    repo = InMemoryTokenRepository()
    color = Token(
        id="token/color/primary",
        type=TokenType.COLOR,
        value="#000000",
        attributes={"hex": "#000000"},
    )
    repo.upsert_token(color)
    shadow = make_shadow_token(
        "token/shadow/elev",
        [ShadowLayer(x=0, y=2, blur=4, spread=0, color_ref=color.id)],
    )
    repo.upsert_token(shadow)

    w3c = tokens_to_w3c(repo)
    shadow_entry = w3c["shadow"]["token/shadow/elev"]["value"][0]
    assert shadow_entry["color"] == "{token/color/primary}"
    assert shadow.relations[0].type == RelationType.COMPOSES
    assert shadow.relations[0].target == color.id


def test_typography_w3c_uses_references() -> None:
    repo = InMemoryTokenRepository()
    color = Token(
        id="token/color/text",
        type=TokenType.COLOR,
        value="#111111",
        attributes={"hex": "#111111"},
    )
    family = Token(id="token/font/family/inter", type=TokenType.TYPOGRAPHY, value="Inter")
    size = Token(id="token/font/size/16px", type=TokenType.TYPOGRAPHY, value="16px")
    repo.upsert_token(color)
    repo.upsert_token(family)
    repo.upsert_token(size)
    typo = make_typography_token(
        "token/typography/body",
        font_family_ref=family.id,
        size_ref=size.id,
        line_height_ref="token/font/lineHeight/22px",
        weight_ref="600",
        letter_spacing_ref=None,
        casing=None,
        color_ref=color.id,
        attributes={"role": "body"},
    )
    repo.upsert_token(typo)

    w3c = tokens_to_w3c(repo)
    entry = w3c["typography"]["token/typography/body"]["value"]
    assert entry["color"] == "{token/color/text}"
    assert entry["fontFamily"] == "{token/font/family/inter}"
    assert entry["fontSize"] == "{token/font/size/16px}"
