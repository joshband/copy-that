from core.tokens.adapters import w3c
from core.tokens.model import Token, TokenType
from core.tokens.repository import InMemoryTokenRepository


def test_layout_grid_export_and_round_trip():
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="token/layout/grid",
            type=TokenType.LAYOUT,
            value={"columns": 12, "gutter": 16, "margin": {"left": 24, "right": 24}},
            attributes={"role": "grid"},
        )
    )
    exported = w3c.tokens_to_w3c(repo)
    entry = exported["layout"]["token/layout/grid"]
    assert entry["$type"] == "layout"
    assert entry["$value"]["columns"] == 12
    assert entry["$value"]["gutter"]["value"] == 16
    assert entry["$value"]["margin"]["left"]["value"] == 24

    repo_round_trip = InMemoryTokenRepository()
    w3c.w3c_to_tokens({"layout": {"token/layout/grid": entry}}, repo_round_trip)
    token = repo_round_trip.get_token("token/layout/grid")
    assert token is not None
    assert token.value["columns"] == 12
    assert token.value["gutter"] == 16
    assert token.value["margin"]["left"] == 24
