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
    layout_entries = exported["layout"]
    assert layout_entries["token/layout/card/radius"]["$type"] == "dimension"
    assert layout_entries["token/layout/card/radius"]["$value"]["value"] == 12
    assert layout_entries["token/layout/card/border/width"]["$type"] == "dimension"
    assert layout_entries["token/layout/card/border/width"]["$value"]["value"] == 2
    assert layout_entries["token/layout/card/border/color"]["$type"] == "color"
    assert layout_entries["token/layout/card/border/color"]["$value"] == "#000000"

    repo_round_trip = InMemoryTokenRepository()
    w3c.w3c_to_tokens({"layout": layout_entries}, repo_round_trip)
    radius = repo_round_trip.get_token("token/layout/card/radius")
    border_width = repo_round_trip.get_token("token/layout/card/border/width")
    border_color = repo_round_trip.get_token("token/layout/card/border/color")
    assert radius is not None
    assert border_width is not None
    assert border_color is not None
    assert radius.value == {"px": 12}
    assert border_width.value == {"px": 2}
    assert border_color.value == "#000000"
