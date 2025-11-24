"""
Utilities for diffing token sets between generations.
"""

from collections.abc import Iterable
from dataclasses import dataclass

from copy_that.pipeline.types import TokenResult


@dataclass
class TokenChange:
    """Represents a change in a token."""

    path: str
    before: TokenResult | None
    after: TokenResult | None


def diff_tokens(
    before: Iterable[TokenResult], after: Iterable[TokenResult]
) -> dict[str, list[TokenChange]]:
    """
    Compute added/removed/changed tokens between two token sets.

    Tokens are keyed by their full_path (or name if path missing).
    """

    def key(token: TokenResult) -> str:
        return getattr(token, "full_path", None) or ".".join(token.path + [token.name])

    before_map = {key(t): t for t in before}
    after_map = {key(t): t for t in after}

    added = [
        TokenChange(path=k, before=None, after=after_map[k])
        for k in after_map.keys() - before_map.keys()
    ]
    removed = [
        TokenChange(path=k, before=before_map[k], after=None)
        for k in before_map.keys() - after_map.keys()
    ]

    changed: list[TokenChange] = []
    for k in before_map.keys() & after_map.keys():
        if before_map[k] != after_map[k]:
            changed.append(TokenChange(path=k, before=before_map[k], after=after_map[k]))

    return {"added": added, "removed": removed, "changed": changed}
