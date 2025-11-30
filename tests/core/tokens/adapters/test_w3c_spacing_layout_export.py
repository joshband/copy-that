from core.tokens.adapters import w3c
from core.tokens.model import RelationType, Token, TokenRelation, TokenType
from core.tokens.repository import InMemoryTokenRepository


def test_spacing_dimension_and_layout_export() -> None:
    repo = InMemoryTokenRepository()
    spacing_base = Token(
        id="token/spacing/base",
        type=TokenType.SPACING,
        value={"px": 8, "rem": 0.5},
        attributes={"name": "base"},
    )
    spacing_lg = Token(
        id="token/spacing/lg",
        type=TokenType.SPACING,
        value={"px": 32, "rem": 2.0},
        attributes={"name": "lg"},
        relations=[
            TokenRelation(
                type=RelationType.MULTIPLE_OF, target="token/spacing/base", meta={"multiplier": 4}
            )
        ],
    )
    layout_grid = Token(
        id="token/layout/grid",
        type=TokenType.LAYOUT,
        value={"columns": 12},
        attributes={"role": "grid", "gutter_ref": "token/spacing/base"},
        relations=[TokenRelation(type=RelationType.COMPOSES, target="token/spacing/base")],
    )
    for tok in (spacing_base, spacing_lg, layout_grid):
        repo.upsert_token(tok)

    exported = w3c.tokens_to_w3c(repo)

    spacing_entry = exported["spacing"]["token/spacing/base"]
    assert spacing_entry["$type"] == "dimension"
    assert spacing_entry["value"] == {"value": 8, "unit": "px"}
    assert spacing_entry["rem"] == 0.5

    layout_entry = exported["layout"]["token/layout/grid"]
    assert layout_entry["$type"] == "dimension"
    assert layout_entry["value"]["columns"] == 12
