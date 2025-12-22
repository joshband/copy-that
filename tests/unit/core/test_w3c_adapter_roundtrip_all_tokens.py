from core.tokens.adapters.w3c import tokens_to_w3c, tokens_to_w3c_flat, w3c_to_tokens
from core.tokens.model import RelationType, Token, TokenRelation, TokenType
from core.tokens.repository import InMemoryTokenRepository


def test_roundtrip_all_token_types_with_relations_and_references():
    repo = InMemoryTokenRepository()

    # Base primitives
    color_base = Token(
        id="color.base",
        type=TokenType.COLOR,
        value="#112233",
        attributes={"hex": "#112233"},
    )
    spacing_base = Token(id="spacing.base", type=TokenType.SPACING, value={"px": 4})
    font_family = Token(id="font.family.base", type=TokenType.FONT_FAMILY, value="Inter")
    font_size = Token(id="font.size.base", type=TokenType.FONT_SIZE, value={"px": 16})

    # Composite values
    spacing_large = Token(
        id="spacing.large",
        type=TokenType.SPACING,
        value={"px": 8},
        relations=[
            TokenRelation(
                type=RelationType.MULTIPLE_OF, target="spacing.base", meta={"multiplier": 2}
            )
        ],
    )
    shadow = Token(
        id="shadow.layered",
        type=TokenType.SHADOW,
        value=[
            {"x": {"value": 0, "unit": "px"}, "y": {"value": 2, "unit": "px"}, "color": "#112233"},
            {"x": {"value": 0, "unit": "px"}, "y": {"value": 6, "unit": "px"}, "color": "#000000"},
        ],
        relations=[TokenRelation(type=RelationType.COMPOSES, target="color.base")],
    )
    typography = Token(
        id="typography.body",
        type=TokenType.TYPOGRAPHY,
        value={
            "fontFamily": "{font.family.base}",
            "fontSize": {"px": 16, "token": "font.size.base"},
            "lineHeight": {"value": 24, "unit": "px", "token": "spacing.large"},
            "color": "{color.base}",
        },
        relations=[TokenRelation(type=RelationType.COMPOSES, target="font.family.base")],
    )
    layout_token = Token(id="layout.card", type=TokenType.LAYOUT, value={"px": 320})
    grid = Token(
        id="layout.grid.desktop",
        type=TokenType.GRID,
        value={"columns": 12, "gutter": {"value": 16, "unit": "px"}, "margin": {"value": 24}},
    )

    for tok in [
        color_base,
        spacing_base,
        font_family,
        font_size,
        spacing_large,
        shadow,
        typography,
        layout_token,
        grid,
    ]:
        repo.upsert_token(tok)

    payload = tokens_to_w3c(repo)
    flat = tokens_to_w3c_flat(repo)

    # Color reference mapping inside shadows and typography
    shadow_entry = payload["shadow"]["shadow.layered"]
    assert shadow_entry["$value"][0]["color"] == "{color.base}"
    assert shadow_entry["$extensions"]["composes"] == ["color.base"]

    typography_entry = payload["typography"]["typography.body"]
    assert typography_entry["$extensions"]["composes"] == ["font.family.base"]
    assert typography_entry["$value"]["color"] == "{color.base}"
    assert typography_entry["$value"]["fontSizeToken"] == "{font.size.base}"

    # Grid section is decomposed into spec-valid tokens
    grid_entries = payload["layout.grid"]
    assert grid_entries["layout.grid.desktop/columns"]["$type"] == "number"
    assert grid_entries["layout.grid.desktop/columns"]["$value"] == 12
    assert grid_entries["layout.grid.desktop/gutter"]["$type"] == "dimension"
    assert grid_entries["layout.grid.desktop/margin"]["$type"] == "dimension"

    # Font tokens map to W3C types
    font_family_entry = payload["font.family"]["font.family.base"]
    assert font_family_entry["$type"] == "fontFamily"
    font_size_entry = payload["font.size"]["font.size.base"]
    assert font_size_entry["$type"] == "dimension"
    assert font_size_entry["$value"] == {"value": 16, "unit": "px"}

    # Spacing captures multipleOf metadata
    spacing_entry = payload["spacing"]["spacing.large"]
    assert spacing_entry["multipleOf"] == "spacing.base"
    assert spacing_entry["multiplier"] == 2
    flat_spacing = flat["spacing"]["spacing.large"]
    assert flat_spacing["value"]["value"] == 8
    assert flat_spacing["multipleOf"] == "spacing.base"

    # Round-trip back into a fresh repo
    round_trip_repo = InMemoryTokenRepository()
    w3c_to_tokens(payload, round_trip_repo)

    rt_shadow = round_trip_repo.get_token("shadow.layered")
    assert rt_shadow
    assert any(rel.type == RelationType.COMPOSES for rel in rt_shadow.relations)

    rt_spacing = round_trip_repo.get_token("spacing.large")
    assert rt_spacing
    assert any(rel.type == RelationType.MULTIPLE_OF for rel in rt_spacing.relations)

    rt_typography = round_trip_repo.get_token("typography.body")
    assert rt_typography
    assert any(rel.target == "font.family.base" for rel in rt_typography.relations)

    rt_grid_columns = round_trip_repo.get_token("layout.grid.desktop/columns")
    rt_grid_gutter = round_trip_repo.get_token("layout.grid.desktop/gutter")
    rt_grid_margin = round_trip_repo.get_token("layout.grid.desktop/margin")
    assert rt_grid_columns and rt_grid_columns.type == TokenType.GRID
    assert rt_grid_gutter and rt_grid_gutter.type == TokenType.GRID
    assert rt_grid_margin and rt_grid_margin.type == TokenType.GRID
