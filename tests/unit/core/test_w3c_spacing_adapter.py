from core.tokens.adapters.w3c import tokens_to_w3c, w3c_to_tokens
from core.tokens.model import Token, TokenType
from core.tokens.repository import InMemoryTokenRepository


def test_composite_spacing_exports_logical_properties():
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
    entry = payload["spacing"]["spacing.composite"]
    assert entry["$type"] == "spacing"
    assert entry["$value"]["top"]["value"] == 4
    assert entry["logical"]["paddingInline"]["value"] == 8
    assert "fallback" in entry["logical"]


def test_composite_spacing_round_trip():
    repo = InMemoryTokenRepository()
    data = {
        "spacing": {
            "spacing.card": {
                "$type": "spacing",
                "$value": {
                    "top": {"value": 12, "unit": "px"},
                    "bottom": {"value": 12, "unit": "px"},
                    "inline": {"value": 16, "unit": "px"},
                },
            }
        }
    }
    w3c_to_tokens(data, repo)
    token = repo.get_token("spacing.card")
    assert token is not None
    assert token.value["top"] == 12
    assert token.value["inline"] == 16
