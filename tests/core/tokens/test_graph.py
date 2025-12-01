from core.tokens.graph import TokenGraph
from core.tokens.model import RelationType, Token, TokenType
from core.tokens.repository import InMemoryTokenRepository


def test_alias_and_resolve() -> None:
    repo = InMemoryTokenRepository()
    graph = TokenGraph(repo)
    base = Token(id="token/color/base", type=TokenType.COLOR, value={"val": 1})
    graph.add_token(base)

    alias = graph.add_alias("token/color/alias", "token/color/base", TokenType.COLOR)

    resolved = graph.resolve_alias(alias.id)
    assert resolved is base
    assert alias.relations[0].type == RelationType.ALIAS_OF
    assert alias.relations[0].target == base.id
    multiples = graph.multiples_of("token/color/base")
    assert multiples == []


def test_detect_cycles() -> None:
    repo = InMemoryTokenRepository()
    graph = TokenGraph(repo)
    a = Token(id="token/color/a", type=TokenType.COLOR)
    b = Token(id="token/color/b", type=TokenType.COLOR)
    graph.add_token(a)
    graph.add_token(b)

    graph.add_alias("token/color/a", "token/color/b", TokenType.COLOR)
    assert graph.detect_cycles() == []

    # Introduce a cycle
    graph.add_relation("token/color/b", RelationType.ALIAS_OF, "token/color/a")
    assert graph.detect_cycles()


def test_multiples_of_spacing() -> None:
    repo = InMemoryTokenRepository()
    graph = TokenGraph(repo)
    base = Token(id="spacing/base", type=TokenType.SPACING, value={"px": 8, "rem": 0.5})
    graph.add_token(base)
    derived = graph.add_multiple_of(
        "spacing/lg",
        "spacing/base",
        4.0,
        TokenType.SPACING,
        {"px": 32, "rem": 2.0},
        role="lg",
    )

    multiples = graph.multiples_of("spacing/base")
    assert len(multiples) == 1
    assert multiples[0][0] is derived
    assert multiples[0][1] == 4.0
