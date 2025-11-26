from core.tokens.spacing import make_spacing_token


def test_make_spacing_token_records_values() -> None:
    token = make_spacing_token(
        "token/spacing/example",
        value_px=16,
        value_rem=1.0,
        attributes={"role": "padding"},
    )

    assert token.id == "token/spacing/example"
    assert token.type == "spacing"
    assert token.value == {"px": 16, "rem": 1.0}
    assert token.attributes["role"] == "padding"
