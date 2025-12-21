from core.tokens.adapters.w3c import tokens_to_w3c, w3c_to_tokens
from core.tokens.model import RelationType, Token, TokenRelation, TokenType
from core.tokens.repository import InMemoryTokenRepository


def test_color_alias_and_composite_extensions_round_trip():
    repo = InMemoryTokenRepository()
    base = Token(
        id="color.base",
        type=TokenType.COLOR,
        value="#112233",
        attributes={"hex": "#112233"},
    )
    gradient = Token(
        id="color.gradient",
        type=TokenType.COLOR,
        value={
            "type": "linear",
            "stops": [
                {"position": 0, "color": "#112233"},
                {"position": 1, "color": "{color.accent}"},
            ],
        },
        relations=[TokenRelation(type=RelationType.COMPOSES, target="color.base")],
    )
    alias = Token(
        id="color.alias",
        type=TokenType.COLOR,
        value=None,
        relations=[TokenRelation(type=RelationType.ALIAS_OF, target="color.base")],
    )

    repo.upsert_token(base)
    repo.upsert_token(gradient)
    repo.upsert_token(alias)

    payload = tokens_to_w3c(repo)
    assert payload["color"]["color.alias"]["$value"] == "{color.base}"

    gradient_entry = payload["color"]["color.gradient"]
    assert gradient_entry["$extensions"]["composes"] == ["color.base"]
    stops = gradient_entry["$value"]["stops"]
    assert stops[0]["color"] == "{color.base}"

    round_trip_repo = InMemoryTokenRepository()
    w3c_to_tokens(payload, round_trip_repo)

    gradient_token = round_trip_repo.get_token("color.gradient")
    assert gradient_token is not None
    assert any(rel.type == RelationType.COMPOSES for rel in gradient_token.relations)
    assert gradient_token.value["stops"][0]["color"] == "{color.base}"
