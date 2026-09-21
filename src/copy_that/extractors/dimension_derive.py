"""Derive DTCG dimension companions from spacing tokens on a graph."""

from __future__ import annotations

from typing import Any

from copy_that.core_tokens.model import Token
from copy_that.core_tokens.repository import TokenRepository
from copy_that.extractors.base import BaseExtractor
from copy_that.extractors.dtcg_capability import CoverageStatus
from copy_that.services.type_coverage_service import synthesize_dimension_from_spacing


class DimensionDeriveExtractor(BaseExtractor):
    """Code/heuristic dimension companions from Compat+ spacing.

    Spacing section is retained; companions land under ``dimension`` with
    ``$type: dimension``. Async ``extract`` returns [] (image path is spacing CV).
    """

    token_type = "dimension"
    coverage_status = CoverageStatus.DERIVE

    async def extract(self, input_data: str | bytes) -> list[dict[str, Any]]:
        return []

    def derive_from_repo(self, repo: TokenRepository) -> list[Token]:
        return synthesize_dimension_from_spacing(repo)

    def derive_and_upsert(self, repo: TokenRepository) -> list[Token]:
        created = self.derive_from_repo(repo)
        for token in created:
            if repo.get_token(token.id) is None:
                repo.upsert_token(token)
        return created
