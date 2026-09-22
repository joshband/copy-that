from copy_that.core_tokens.adapters.w3c import tokens_to_w3c, tokens_to_w3c_flat, w3c_to_tokens
from copy_that.core_tokens.model import RelationType, Token, TokenRelation, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository


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
    assert gradient_entry["$extensions"]["com.copythat.composes"] == ["color.base"]
    stops = gradient_entry["$value"]["stops"]
    assert stops[0]["color"] == "{color.base}"

    round_trip_repo = InMemoryTokenRepository()
    w3c_to_tokens(payload, round_trip_repo)

    gradient_token = round_trip_repo.get_token("color.gradient")
    assert gradient_token is not None
    assert any(rel.type == RelationType.COMPOSES for rel in gradient_token.relations)
    assert gradient_token.value["stops"][0]["color"] == "{color.base}"


def test_color_metadata_preserved_through_w3c_and_flatten():
    repo = InMemoryTokenRepository()
    token = Token(
        id="color.primary",
        type=TokenType.COLOR,
        value="#010203",
        attributes={
            "hex": "#010203",
            "contrast_targets": [{"background": "#FFFFFF", "ratio": 10.0}],
            "role_scores": {"text": 1.0, "background": 0.1},
        },
    )
    repo.upsert_token(token)

    sectioned = tokens_to_w3c(repo)
    flat = tokens_to_w3c_flat(repo)

    section_entry = sectioned["color"]["color.primary"]
    assert section_entry["contrast_targets"][0]["background"] == "#FFFFFF"
    assert section_entry["role_scores"]["text"] == 1.0

    flat_entry = flat["color"]["color.primary"]
    assert flat_entry["contrast_targets"][0]["ratio"] == 10.0
    assert flat_entry["role_scores"]["background"] == 0.1

    round_trip_repo = InMemoryTokenRepository()
    w3c_to_tokens(sectioned, round_trip_repo)
    rt = round_trip_repo.get_token("color.primary")
    assert rt
    assert rt.attributes["contrast_targets"][0]["ratio"] == 10.0
    assert rt.attributes["role_scores"]["text"] == 1.0
