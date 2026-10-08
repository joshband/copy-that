from copy_that.core_tokens.adapters import w3c
from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository


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
    layout_entries = exported["layout"]
    assert layout_entries["token/layout/grid/columns"]["$type"] == "number"
    assert layout_entries["token/layout/grid/columns"]["$value"] == 12
    assert layout_entries["token/layout/grid/gutter"]["$type"] == "dimension"
    assert layout_entries["token/layout/grid/gutter"]["$value"]["value"] == 16
    assert layout_entries["token/layout/grid/margin/left"]["$value"]["value"] == 24

    repo_round_trip = InMemoryTokenRepository()
    w3c.w3c_to_tokens({"layout": layout_entries}, repo_round_trip)
    columns = repo_round_trip.get_token("token/layout/grid/columns")
    gutter = repo_round_trip.get_token("token/layout/grid/gutter")
    margin_left = repo_round_trip.get_token("token/layout/grid/margin/left")
    assert columns is not None
    assert gutter is not None
    assert margin_left is not None
    assert columns.value == 12
    assert gutter.value == {"px": 16}
    assert margin_left.value == {"px": 24}
