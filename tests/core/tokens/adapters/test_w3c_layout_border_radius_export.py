from core.tokens.adapters import w3c
from core.tokens.model import Token, TokenType
from core.tokens.repository import InMemoryTokenRepository


def test_layout_radius_border_export_and_round_trip():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="token/layout/card",
            type=TokenType.LAYOUT,
            value={"radius": 12, "border": {"width": 2, "color": "#000000"}},
            attributes={"role": "card-shape"},
        )
    )
    exported = w3c.tokens_to_w3c(repo)
    entry = exported["layout"]["token/layout/card"]
    assert entry["$type"] == "layout"
    assert entry["$value"]["radius"]["value"] == 12
    assert entry["$value"]["border"]["width"]["value"] == 2

    repo_round_trip = InMemoryTokenRepository()
    w3c.w3c_to_tokens({"layout": {"token/layout/card": entry}}, repo_round_trip)
    token = repo_round_trip.get_token("token/layout/card")
    assert token is not None
    assert token.value["radius"] == 12
    assert token.value["border"]["width"] == 2
