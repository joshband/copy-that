"""Derive DTCG fontFamily / fontWeight atoms from typography on a graph."""

from __future__ import annotations

from typing import Any

from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import TokenRepository
from copy_that.extractors.base import BaseExtractor
from copy_that.extractors.dtcg_capability import CoverageStatus
from copy_that.services.type_coverage_service import synthesize_font_atoms_from_typography


def _type_value(token: Token) -> str:
    return token.type.value if isinstance(token.type, TokenType) else str(token.type)


def _upsert_font_atoms(repo: TokenRepository) -> list[Token]:
    """Run synthesis once and upsert every font atom (family + weight)."""
    created = synthesize_font_atoms_from_typography([], repo=repo)
    upserted: list[Token] = []
    for token in created:
        if repo.get_token(token.id) is None:
            repo.upsert_token(token)
        upserted.append(token)
    return upserted


class FontFamilyDeriveExtractor(BaseExtractor):
    """Code/heuristic fontFamily atoms — dual-written at typography build.

    Async ``extract`` returns [] (screenshot→fontFamily is via typography extract).
    """

    token_type = "fontFamily"
    coverage_status = CoverageStatus.DERIVE

    async def extract(self, input_data: str | bytes) -> list[dict[str, Any]]:
        return []

    def derive_from_repo(self, repo: TokenRepository) -> list[Token]:
        return [
            t
            for t in synthesize_font_atoms_from_typography([], repo=repo)
            if _type_value(t) == "fontFamily"
        ]

    def derive_and_upsert(self, repo: TokenRepository) -> list[Token]:
        # Upsert both atom kinds so typography rewiring does not orphan weights
        return [t for t in _upsert_font_atoms(repo) if _type_value(t) == "fontFamily"]


class FontWeightDeriveExtractor(BaseExtractor):
    """Code/heuristic fontWeight atoms — dual-written at typography build."""

    token_type = "fontWeight"
    coverage_status = CoverageStatus.DERIVE

    async def extract(self, input_data: str | bytes) -> list[dict[str, Any]]:
        return []

    def derive_from_repo(self, repo: TokenRepository) -> list[Token]:
        return [
            t
            for t in synthesize_font_atoms_from_typography([], repo=repo)
            if _type_value(t) == "fontWeight"
        ]

    def derive_and_upsert(self, repo: TokenRepository) -> list[Token]:
        return [t for t in _upsert_font_atoms(repo) if _type_value(t) == "fontWeight"]
