from copy_that.core_tokens.adapters import w3c
from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository


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

    shadow_entry = exported["shadow"]["token/shadow/elevation-1"]
    assert shadow_entry["$value"] == initial["shadow"]["token/shadow/elevation-1"]["$value"]

    typography_entry = exported["typography"]["token/typography/label"]
    assert typography_entry["$value"] == initial["typography"]["token/typography/label"]["$value"]
    assert typography_entry["role"] == "label"


def test_export_adds_provenance_extensions() -> None:
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="color.primary",
            type=TokenType.COLOR,
            value="#112233",
            attributes={
                "hex": "#112233",
                "confidence": 0.87,
                "extraction_metadata": {
                    "source": "cv",
                    "stage": "slic",
                    "artifacts": ["overlay"],
                    "palette_count": 4,
                },
                "provenance": {"image_1": 0.9},
            },
        )
    )

    exported = w3c.tokens_to_w3c(repo)

    provenance = exported["color"]["color.primary"]["$extensions"]["provenance"]
    assert provenance["pipeline"] == "color"
    assert provenance["algorithm"] == ["cv"]
    assert provenance["artifacts"] == ["overlay"]
    assert provenance["stage"] == "slic"
    assert provenance["params"]["palette_count"] == 4
    assert provenance["confidence"] == 0.87
    assert provenance["sources"] == {"image_1": 0.9}
