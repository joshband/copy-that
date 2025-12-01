from core.tokens.adapters.w3c import tokens_to_w3c, w3c_to_tokens
from core.tokens.model import Token, TokenType
from core.tokens.repository import InMemoryTokenRepository
from core.tokens.typography import make_typography_token


def test_typography_exports_dtcg_shape_and_roundtrip() -> None:
    repo = InMemoryTokenRepository()
    repo.upsert_token(Token(id="color.text.primary", type=TokenType.COLOR, value="#111111"))
    repo.upsert_token(Token(id="font.family.primary", type=TokenType.FONT_FAMILY, value="Inter"))

    typo = make_typography_token(
        "typography.body",
        font_family_token_id="font.family.primary",
        font_size_px=16,
        line_height_px=24,
        font_weight=500,
        color_token_id="color.text.primary",
        attributes={"role": "body"},
    )
    repo.upsert_token(typo)

    exported = tokens_to_w3c(repo)
    entry = exported["typography"]["typography.body"]
    assert entry["$type"] == "typography"
    value = entry["$value"]
    assert value["fontFamily"][0] == "{font.family.primary}"
    assert value["fontSize"] == {"value": 16.0, "unit": "px"}
    assert value["lineHeight"] == {"value": 24.0, "unit": "px"}
    assert value["fontWeight"] == 500
    assert value["color"] == "{color.text.primary}"

    roundtrip_repo = InMemoryTokenRepository()
    w3c_to_tokens(exported, roundtrip_repo)
    roundtripped = tokens_to_w3c(roundtrip_repo)
    assert (
        roundtripped["typography"]["typography.body"]["$value"]["fontFamily"][0]
        == "{font.family.primary}"
    )
