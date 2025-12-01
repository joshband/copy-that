from core.tokens.graph import TokenGraph
from core.tokens.model import RelationType, Token, TokenRelation, TokenType
from core.tokens.repository import InMemoryTokenRepository


def test_detect_cycles_lists_cycles() -> None:
    repo = InMemoryTokenRepository()
    graph = TokenGraph(repo)
    a = Token(id="token/a", type=TokenType.COLOR)
    b = Token(
        id="token/b",
        type=TokenType.COLOR,
        relations=[TokenRelation(type=RelationType.ALIAS_OF, target="token/a")],
    )
    c = Token(
        id="token/c",
        type=TokenType.COLOR,
        relations=[TokenRelation(type=RelationType.ALIAS_OF, target="token/b")],
    )
    # introduce cycle back to c
    a.relations.append(TokenRelation(type=RelationType.ALIAS_OF, target="token/c"))
    for t in (a, b, c):
        graph.add_token(t)

    cycles = graph.detect_cycles()
    assert cycles and any(cycle[0] == "token/a" for cycle in cycles)


def test_find_dangling_refs() -> None:
    repo = InMemoryTokenRepository()
    graph = TokenGraph(repo)
    valid = Token(id="token/ok", type=TokenType.COLOR)
    dangling_rel = TokenRelation(type=RelationType.ALIAS_OF, target="token/missing")
    bad = Token(id="token/bad", type=TokenType.COLOR, relations=[dangling_rel])
    graph.add_token(valid)
    graph.add_token(bad)

    missing = graph.find_dangling_refs()
    assert missing == [("token/bad", dangling_rel)]


def test_summarize_reports_counts() -> None:
    repo = InMemoryTokenRepository()
    graph = TokenGraph(repo)
    base = Token(id="token/spacing/base", type=TokenType.SPACING)
    derived = Token(
        id="token/spacing/lg",
        type=TokenType.SPACING,
        relations=[
            TokenRelation(type=RelationType.MULTIPLE_OF, target=base.id, meta={"multiplier": 4})
        ],
    )
    alias = Token(
        id="token/color/text",
        type=TokenType.COLOR,
        relations=[TokenRelation(type=RelationType.ALIAS_OF, target="token/color/base")],
    )
    for t in (base, derived, alias):
        graph.add_token(t)

    summary = graph.summarize()
    assert summary["counts"][TokenType.SPACING.value] == 2
    assert summary["relation_counts"]["multipleOf"] == 1
    assert summary["relation_counts"]["aliasOf"] == 1
