from core.tokens.adapters.w3c import tokens_to_w3c, w3c_to_tokens
from core.tokens.model import Token, TokenType
from core.tokens.repository import InMemoryTokenRepository


def test_directional_spacing_exports_as_dimensions():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="spacing.composite",
            type=TokenType.SPACING,
            value={"top": 4, "inline": 8, "left": 6},
            attributes={"alias": "test"},
        )
    )
    payload = tokens_to_w3c(repo)
    assert "spacing.composite" not in payload["spacing"]
    entry_top = payload["spacing"]["spacing.composite/top"]
    entry_inline = payload["spacing"]["spacing.composite/inline"]
    entry_left = payload["spacing"]["spacing.composite/left"]
    assert entry_top["$type"] == "dimension"
    assert entry_top["$value"] == {"value": 4, "unit": "px"}
    assert entry_inline["$value"]["value"] == 8
    assert entry_left["$value"]["value"] == 6
    assert entry_top["alias"] == "test"


def test_directional_spacing_round_trip():
    repo = InMemoryTokenRepository()
    data = {
        "spacing": {
            "spacing.card/top": {"$type": "dimension", "$value": {"value": 12, "unit": "px"}},
            "spacing.card/bottom": {"$type": "dimension", "$value": {"value": 12, "unit": "px"}},
            "spacing.card/inline": {"$type": "dimension", "$value": {"value": 16, "unit": "px"}},
        }
    }
    w3c_to_tokens(data, repo)
    token = repo.get_token("spacing.card/top")
    assert token is not None
    assert token.value["px"] == 12
    inline = repo.get_token("spacing.card/inline")
    assert inline is not None
    assert inline.value["px"] == 16
