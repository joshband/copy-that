from core.tokens.model import Token
from core.tokens.repository import InMemoryTokenRepository


def test_upsert_and_get_token() -> None:
    repo = InMemoryTokenRepository()
    token = Token(id="token/color/primary", type="color", value="#ffffff")

    repo.upsert_token(token)

    assert repo.get_token("token/color/primary") is token


def test_upsert_overwrites_existing_token() -> None:
    repo = InMemoryTokenRepository()
    original = Token(id="token/color/primary", type="color", value="#ffffff")
    updated = Token(id="token/color/primary", type="color", value="#000000")

    repo.upsert_token(original)
    repo.upsert_token(updated)

    stored = repo.get_token("token/color/primary")
    assert stored is updated
    assert stored.value == "#000000"


def test_link_adds_relation() -> None:
    repo = InMemoryTokenRepository()
    color = Token(id="token/color/primary", type="color")
    shadow = Token(id="token/shadow/elevation-1", type="shadow")
    repo.upsert_token(color)
    repo.upsert_token(shadow)

    repo.link("token/shadow/elevation-1", "color", "token/color/primary")

    assert shadow.relations["color"] == "token/color/primary"


def test_find_by_type() -> None:
    repo = InMemoryTokenRepository()
    repo.upsert_token(Token(id="token/color/primary", type="color"))
    repo.upsert_token(Token(id="token/color/secondary", type="color"))
    repo.upsert_token(Token(id="token/shadow/elevation-1", type="shadow"))

    colors = repo.find_by_type("color")

    assert {token.id for token in colors} == {
        "token/color/primary",
        "token/color/secondary",
    }


def test_find_by_attributes_matches_subset() -> None:
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="token/color/primary",
            type="color",
            attributes={"role": "text", "theme": "light"},
        )
    )
    repo.upsert_token(
        Token(
            id="token/color/secondary",
            type="color",
            attributes={"role": "accent", "theme": "light"},
        )
    )

    matches = repo.find_by_attributes(role="text")

    assert [token.id for token in matches] == ["token/color/primary"]
