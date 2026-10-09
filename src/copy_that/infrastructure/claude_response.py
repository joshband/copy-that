"""Read Claude Messages API responses by block type.

Current Claude models think by default, so a response can begin with `thinking` blocks;
`message.content[0].text` is not safe. Read text blocks instead.
"""

from __future__ import annotations

from typing import Any


def claude_text(message: Any) -> str:
    """Concatenate the text of every `text` block in a Claude response ("" if none)."""
    blocks = getattr(message, "content", None)
    if not isinstance(blocks, list):
        return ""
    parts = [text for block in blocks if isinstance(text := getattr(block, "text", None), str)]
    return "".join(parts)
