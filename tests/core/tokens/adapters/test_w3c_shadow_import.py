from copy_that.core_tokens.adapters import w3c
from copy_that.core_tokens.model import RelationType
from copy_that.core_tokens.repository import InMemoryTokenRepository


def test_w3c_shadow_import_creates_color_relation() -> None:
    data = {
        "color": {
            "token/color/primary": {
                "$type": "color",
                "$value": "#123456",
            }
        },
        "shadow": {
            "token/shadow/elevation-1": {
                "$type": "shadow",
                "$value": [
                    {"x": 0, "y": 2, "blur": 4, "spread": 0, "color": "{token/color/primary}"}
                ],
            }
        },
    }

    repo = InMemoryTokenRepository()
    w3c.w3c_to_tokens(data, repo)

    shadow = repo.get_token("token/shadow/elevation-1")
    assert shadow is not None
    assert any(rel.type == RelationType.COMPOSES and rel.target == "token/color/primary" for rel in shadow.relations)
