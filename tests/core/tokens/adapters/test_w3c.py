from core.tokens.adapters import w3c
from core.tokens.repository import InMemoryTokenRepository


def test_roundtrip_color_tokens() -> None:
    initial = {
        "color": {
            "token/color/primary": {
                "$value": "#ffffff",
                "$type": "color",
                "description": "Primary brand color",
            },
            "token/color/secondary": {
                "$value": "#000000",
                "$type": "color",
            },
            "token/color/alias": {"$type": "color", "$value": "{token/color/primary}"},
        }
    }

    repo = InMemoryTokenRepository()
    w3c.w3c_to_tokens(initial, repo)

    exported = w3c.tokens_to_w3c(repo)

    assert exported == initial


def test_roundtrip_shadow_and_typography_tokens() -> None:
    initial = {
        "shadow": {
            "token/shadow/elevation-1": {
                "$type": "shadow",
                "$value": [
                    {
                        "x": 0,
                        "y": 2,
                        "blur": 4,
                        "spread": 0,
                        "color": "{token/color/primary}",
                    }
                ],
            }
        },
        "typography": {
            "token/typography/label": {
                "$type": "typography",
                "$value": {
                    "fontFamily": ["Inter"],
                    "fontSize": {"value": 12, "unit": "px"},
                    "lineHeight": {"value": 16, "unit": "px"},
                    "fontWeight": "600",
                    "color": "{token/color/primary}",
                },
                "role": "label",
            }
        },
    }

    repo = InMemoryTokenRepository()
    w3c.w3c_to_tokens(initial, repo)

    exported = w3c.tokens_to_w3c(repo)

    assert exported["shadow"] == initial["shadow"]
    assert exported["typography"] == initial["typography"]
