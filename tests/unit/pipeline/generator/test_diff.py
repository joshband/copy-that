"""Tests for token diff utilities."""

from copy_that.pipeline import TokenResult, TokenType
from copy_that.pipeline.generator.diff import diff_tokens


def test_diff_tokens_added_removed_changed():
    """Diff should categorize added, removed, and changed tokens."""
    before = [
        TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            path=["color"],
            value="#FF0000",
            confidence=0.9,
        ),
        TokenResult(
            token_type=TokenType.COLOR,
            name="secondary",
            path=["color"],
            value="#00FF00",
            confidence=0.9,
        ),
    ]
    after = [
        TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            path=["color"],
            value="#FF1111",
            confidence=0.9,
        ),
        TokenResult(
            token_type=TokenType.COLOR,
            name="accent",
            path=["color"],
            value="#0000FF",
            confidence=0.9,
        ),
    ]

    result = diff_tokens(before, after)

    assert len(result["added"]) == 1
    assert len(result["removed"]) == 1
    assert len(result["changed"]) == 1
    assert result["added"][0].after.name == "accent"
    assert result["removed"][0].before.name == "secondary"
    assert result["changed"][0].path.endswith("primary")
