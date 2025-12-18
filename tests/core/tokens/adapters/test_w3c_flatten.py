from core.tokens.adapters.w3c import tokens_to_w3c, tokens_to_w3c_flat
from core.tokens.model import RelationType, Token, TokenRelation, TokenType
from core.tokens.repository import InMemoryTokenRepository
from core.tokens.shadow import ShadowLayer, make_shadow_token


def test_alias_export_adds_value_alias_in_flattened() -> None:
    repo = InMemoryTokenRepository()
    base = Token(id="token/color/base", type=TokenType.COLOR, value="#abcdef")
    alias = Token(
        id="token/color/alias",
        type=TokenType.COLOR,
        value=None,
        relations=[TokenRelation(type=RelationType.ALIAS_OF, target=base.id)],
    )
    repo.upsert_token(base)
    repo.upsert_token(alias)

    dtcg = tokens_to_w3c(repo)
    flat = tokens_to_w3c_flat(repo)

    alias_entry = dtcg["color"]["token/color/alias"]
    assert alias_entry["$value"] == "{token/color/base}"
    assert "value" not in alias_entry

    flat_entry = flat["color"]["token/color/alias"]
    assert flat_entry["value"] == "{token/color/base}"
    assert flat_entry["$value"] == "{token/color/base}"


def test_composite_shadow_flatten_retains_value_alias() -> None:
    repo = InMemoryTokenRepository()
    color = Token(id="token/color/primary", type=TokenType.COLOR, value="#000000")
    repo.upsert_token(color)
    shadow = make_shadow_token(
        "token/shadow/card",
        [ShadowLayer(x=0, y=2, blur=4, spread=0, color_token_id=color.id)],
    )
    repo.upsert_token(shadow)

    dtcg = tokens_to_w3c(repo)
    flat = tokens_to_w3c_flat(repo)

    shadow_entry = dtcg["shadow"]["token/shadow/card"]
    assert shadow_entry["$type"] == "shadow"
    assert "value" not in shadow_entry
    assert shadow_entry["$value"][0]["color"] == "{token/color/primary}"

    flat_entry = flat["shadow"]["token/shadow/card"]
    assert flat_entry["value"] == shadow_entry["$value"]
    assert flat_entry["$value"][0]["color"] == "{token/color/primary}"
