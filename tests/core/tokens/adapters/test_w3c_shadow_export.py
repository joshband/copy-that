from core.tokens.adapters import w3c
from core.tokens.model import RelationType, Token, TokenRelation, TokenType
from core.tokens.repository import InMemoryTokenRepository


def test_shadow_export_wraps_color_ref_and_preserves_relations() -> None:
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="token/color/primary",
            type=TokenType.COLOR,
            value="#abcdef",
            attributes={"hex": "#abcdef"},
            relations=[],
        )
    )
    repo.upsert_token(
        Token(
            id="token/shadow/panel",
            type=TokenType.SHADOW,
            value=[{"x": 0, "y": 2, "blur": 4, "spread": 1, "color": "token/color/primary"}],
            attributes={},
            relations=[
                TokenRelation(
                    type=RelationType.COMPOSES,
                    target="token/color/primary",
                    meta={"role": "shadow-color"},
                )
            ],
        )
    )

    exported = w3c.tokens_to_w3c(repo)

    shadow_entry = exported["shadow"]["token/shadow/panel"]
    assert shadow_entry["$value"][0]["color"] == "{token/color/primary}"

    roundtrip_repo = InMemoryTokenRepository()
    w3c.w3c_to_tokens(exported, roundtrip_repo)
    rt_shadow = roundtrip_repo.get_token("token/shadow/panel")
    assert rt_shadow is not None
    assert any(rel.type == RelationType.COMPOSES and rel.target == "token/color/primary" for rel in rt_shadow.relations)
