from core.tokens.adapters import w3c
from core.tokens.repository import InMemoryTokenRepository


def test_roundtrip_color_tokens() -> None:
    initial = {
        "color": {
            "token/color/primary": {
                "value": "#ffffff",
                "$type": "color",
                "description": "Primary brand color",
            },
            "token/color/secondary": {
                "value": "#000000",
                "$type": "color",
            },
        }
    }

    repo = InMemoryTokenRepository()
    w3c.w3c_to_tokens(initial, repo)

    exported = w3c.tokens_to_w3c(repo)

    assert exported == initial
