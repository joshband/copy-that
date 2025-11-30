"""Lightweight graph abstraction over the token repository."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from core.tokens.model import RelationType, Token, TokenRelation, TokenType, TokenValue
from core.tokens.repository import TokenRepository, _coerce_relation, _normalize_type


class TokenGraph:
    """Small helper around TokenRepository with graph semantics."""

    def __init__(self, repo: TokenRepository):
        self.repo = repo

    def add_token(self, token: Token) -> Token:
        return self.repo.upsert_token(token)

    def add_alias(
        self, alias_id: str, target_id: str, token_type: TokenType | str, **attrs: Any
    ) -> Token:
        alias = Token(
            id=alias_id,
            type=token_type,
            value=None,
            attributes=attrs,
            relations=[TokenRelation(type=RelationType.ALIAS_OF, target=target_id)],
        )
        return self.repo.upsert_token(alias)

    def add_multiple_of(
        self,
        token_id: str,
        base_id: str,
        multiplier: float,
        token_type: TokenType | str,
        value: TokenValue,
        **attrs: Any,
    ) -> Token:
        rel = TokenRelation(
            type=RelationType.MULTIPLE_OF, target=base_id, meta={"multiplier": multiplier}
        )
        token = Token(
            id=token_id,
            type=token_type,
            value=value,
            attributes=attrs,
            relations=[rel],
        )
        return self.repo.upsert_token(token)

    def add_relation(
        self,
        source_id: str,
        relation: RelationType | str,
        target_id: str,
        meta: dict[str, Any] | None = None,
    ) -> None:
        token = self.repo.get_token(source_id)
        if token is None:
            raise KeyError(f"Token '{source_id}' not found")
        coerced = _coerce_relation(relation, target_id)
        token.relations.append(
            TokenRelation(type=coerced.type, target=coerced.target, meta=meta or {})
        )
        self.repo.upsert_token(token)

    def get_token(self, token_id: str) -> Token | None:
        return self.repo.get_token(token_id)

    def find_by_type(self, token_type: TokenType | str) -> list[Token]:
        return self.repo.find_by_type(token_type)

    def resolve_alias(self, token_id: str) -> Token | None:
        """Follow aliasOf edges to the base token; stop on cycles or missing targets."""
        current = self.repo.get_token(token_id)
        seen: set[str] = set()
        while current and current.id not in seen:
            seen.add(current.id)
            alias_edge = next(
                (rel for rel in current.relations if rel.type == RelationType.ALIAS_OF), None
            )
            if not alias_edge:
                return current
            current = self.repo.get_token(alias_edge.target)
        return None

    def detect_cycles(self) -> list[list[str]]:
        """Detect cycles across aliasOf and multipleOf edges; return list of cycles."""
        graph: dict[str, list[str]] = defaultdict(list)
        for token in self._all_tokens():
            for rel in token.relations:
                if rel.type in {RelationType.ALIAS_OF, RelationType.MULTIPLE_OF}:
                    graph[token.id].append(rel.target)

        cycles: list[list[str]] = []
        path: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def dfs(node: str) -> None:
            if node in visiting:
                if node in path:
                    cycle_start = path.index(node)
                    cycles.append(path[cycle_start:] + [node])
                return
            if node in visited:
                return
            visited.add(node)
            visiting.add(node)
            path.append(node)
            for neighbor in graph.get(node, []):
                dfs(neighbor)
            path.pop()
            visiting.remove(node)

        for node in graph:
            dfs(node)
        return cycles

    def find_dangling_refs(self) -> list[tuple[str, TokenRelation]]:
        """Return relations whose targets do not exist in the repo."""
        missing: list[tuple[str, TokenRelation]] = []
        for token in self._all_tokens():
            for rel in token.relations:
                if self.repo.get_token(rel.target) is None:
                    missing.append((token.id, rel))
        return missing

    def summarize(self) -> dict[str, Any]:
        tokens = self._all_tokens()
        counts: dict[str, int] = defaultdict(int)
        alias_count = 0
        multiple_count = 0
        compose_count = 0
        for tok in tokens:
            counts[_normalize_type(tok.type)] += 1
            for rel in tok.relations:
                if rel.type == RelationType.ALIAS_OF:
                    alias_count += 1
                elif rel.type == RelationType.MULTIPLE_OF:
                    multiple_count += 1
                elif rel.type == RelationType.COMPOSES:
                    compose_count += 1
        cycles = self.detect_cycles()
        dangling = self.find_dangling_refs()
        return {
            "counts": dict(counts),
            "relation_counts": {
                "aliasOf": alias_count,
                "multipleOf": multiple_count,
                "composes": compose_count,
            },
            "cycle_count": len(cycles),
            "cycles": cycles,
            "dangling_relations": [
                {"source": src, "type": rel.type.value, "target": rel.target}
                for src, rel in dangling
            ],
        }

    def multiples_of(self, base_id: str) -> list[tuple[Token, float | None]]:
        """Return tokens that are multiples of the given base id with their multiplier."""
        matches: list[tuple[Token, float | None]] = []
        for token in self._all_tokens():
            for rel in token.relations:
                if rel.type == RelationType.MULTIPLE_OF and rel.target == base_id:
                    multiplier = None
                    if isinstance(rel.meta, dict) and "multiplier" in rel.meta:
                        try:
                            multiplier = float(rel.meta["multiplier"])
                        except Exception:
                            multiplier = None
                    matches.append((token, multiplier))
        return matches

    def _all_tokens(self) -> list[Token]:
        tokens: list[Token] = []
        if hasattr(self.repo, "_tokens"):
            tokens.extend(self.repo._tokens.values())  # type: ignore[attr-defined]
            return tokens
        seen: set[str] = set()
        for token_type in TokenType:
            for token in self.repo.find_by_type(token_type):
                if token.id not in seen:
                    seen.add(token.id)
                    tokens.append(token)
        return tokens
