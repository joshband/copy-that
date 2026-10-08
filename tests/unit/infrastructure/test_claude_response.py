"""claude_text reads text blocks by type, so a leading thinking block can't break parsing."""

from types import SimpleNamespace

from copy_that.infrastructure.claude_response import claude_text


def test_skips_leading_thinking_block():
    message = SimpleNamespace(
        content=[
            SimpleNamespace(type="thinking", thinking="", signature="sig"),
            SimpleNamespace(type="text", text='{"colors": []}'),
        ]
    )
    assert claude_text(message) == '{"colors": []}'


def test_joins_multiple_text_blocks():
    message = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="ab"), SimpleNamespace(type="text", text="c")]
    )
    assert claude_text(message) == "abc"


def test_no_text_blocks_returns_empty_string():
    assert claude_text(SimpleNamespace(content=[SimpleNamespace(type="thinking")])) == ""
    assert claude_text(SimpleNamespace(content=None)) == ""
