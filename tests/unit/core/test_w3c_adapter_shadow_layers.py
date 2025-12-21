from core.tokens.adapters.w3c import tokens_to_w3c, w3c_to_tokens
from core.tokens.model import Token, TokenType
from core.tokens.repository import InMemoryTokenRepository


def test_w3c_shadow_layers_round_trip_with_inset():
    repo = InMemoryTokenRepository()
    shadow = Token(
        id="shadow.multi",
        type=TokenType.SHADOW,
        value=[
            {"color": "#000000", "x": {"value": 0, "unit": "px"}, "y": {"value": 4, "unit": "px"}, "blur": {"value": 8, "unit": "px"}, "spread": {"value": 0, "unit": "px"}, "inset": False},
            {"color": "#111111", "x": {"value": 0, "unit": "px"}, "y": {"value": 2, "unit": "px"}, "blur": {"value": 4, "unit": "px"}, "spread": {"value": 0, "unit": "px"}, "inset": True},
        ],
    )
    repo.upsert_token(shadow)

    payload = tokens_to_w3c(repo)
    entry = payload["shadow"]["shadow.multi"]
    assert entry["$value"][1]["inset"] is True

    rt_repo = InMemoryTokenRepository()
    w3c_to_tokens(payload, rt_repo)
    rt_shadow = rt_repo.get_token("shadow.multi")
    assert rt_shadow
    assert isinstance(rt_shadow.value, list)
    assert rt_shadow.value[1]["inset"] is True
