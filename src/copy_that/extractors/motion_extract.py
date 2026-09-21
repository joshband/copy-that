"""DTCG motion extraction (Phase 5): duration / cubicBezier / transition.

UI-kit and style/AI cues on the token graph are primary. Screenshot CV is not
attempted (weak signal). Export presets remain fallback when confidence is below
threshold — never invent high confidence on presets.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import TokenRepository
from copy_that.extractors.base import BaseExtractor
from copy_that.extractors.dtcg_capability import CoverageStatus
from copy_that.extractors.motion_heuristic import (
    MOTION_EXTRACT_CONFIDENCE_THRESHOLD,
    filter_by_types,
    resolve_motion_tokens,
)

_EXTRACTED_SOURCES = frozenset({"heuristic", "ai", "extracted"})


def motion_tokens_from_repo(
    repo: TokenRepository,
    *,
    style_hint: str | None = None,
    visual_weight: str | None = None,
    primary_style: str | None = None,
    confidence_threshold: float = MOTION_EXTRACT_CONFIDENCE_THRESHOLD,
) -> list[Token]:
    """Heuristic / style-cue motion set, or empty when below threshold."""
    return resolve_motion_tokens(
        repo,
        style_hint=style_hint,
        visual_weight=visual_weight,
        primary_style=primary_style,
        confidence_threshold=confidence_threshold,
    )


def repo_has_extracted_motion(
    repo: TokenRepository,
    *,
    confidence_threshold: float = MOTION_EXTRACT_CONFIDENCE_THRESHOLD,
    types: set[str] | None = None,
) -> bool:
    """True when the graph already has heuristic/AI motion at/above threshold."""
    wanted = types or {"duration", "cubicBezier", "transition"}
    buckets: list[Token] = []
    if "duration" in wanted:
        buckets.extend(
            list(repo.find_by_type(TokenType.DURATION)) + list(repo.find_by_type("duration"))
        )
    if "cubicBezier" in wanted:
        buckets.extend(
            list(repo.find_by_type(TokenType.CUBIC_BEZIER)) + list(repo.find_by_type("cubicBezier"))
        )
    if "transition" in wanted:
        buckets.extend(
            list(repo.find_by_type(TokenType.TRANSITION)) + list(repo.find_by_type("transition"))
        )
    for token in buckets:
        source = str(token.attributes.get("source") or "")
        conf = float(token.attributes.get("confidence") or 0.0)
        if source in _EXTRACTED_SOURCES and conf >= confidence_threshold:
            return True
    return False


def upsert_extracted_motion(
    repo: TokenRepository,
    tokens: Sequence[Token],
) -> list[Token]:
    """Insert extracted motion tokens; overwrite presets with same id when extract wins."""
    upserted: list[Token] = []
    for token in tokens:
        existing = repo.get_token(token.id)
        if existing is None:
            repo.upsert_token(token)
            upserted.append(token)
            continue
        existing_source = str(existing.attributes.get("source") or "")
        # Prefer extract over preset/synth; keep higher-confidence extract
        if existing_source in {"preset", "synth", ""}:
            repo.upsert_token(token)
            upserted.append(token)
            continue
        if existing_source in _EXTRACTED_SOURCES:
            old_conf = float(existing.attributes.get("confidence") or 0.0)
            new_conf = float(token.attributes.get("confidence") or 0.0)
            if new_conf > old_conf:
                repo.upsert_token(token)
                upserted.append(token)
    return upserted


def upsert_motion_from_repo(
    repo: TokenRepository,
    *,
    style_hint: str | None = None,
    visual_weight: str | None = None,
    primary_style: str | None = None,
    confidence_threshold: float = MOTION_EXTRACT_CONFIDENCE_THRESHOLD,
) -> list[Token]:
    """Resolve + upsert motion tokens onto ``repo`` when cues are strong enough."""
    tokens = motion_tokens_from_repo(
        repo,
        style_hint=style_hint,
        visual_weight=visual_weight,
        primary_style=primary_style,
        confidence_threshold=confidence_threshold,
    )
    if not tokens:
        return []
    return upsert_extracted_motion(repo, tokens)


class _MotionDeriveExtractor(BaseExtractor):
    """Shared derive path for duration / cubicBezier / transition."""

    token_type: str = "duration"
    coverage_status = CoverageStatus.DERIVE
    _type_filter: set[str] = {"duration"}

    async def extract(self, input_data: str | bytes) -> list[dict[str, Any]]:
        # Screenshots lack reliable motion signal; image path is intentionally empty.
        _ = input_data
        return []

    def derive_and_upsert(
        self,
        repo: TokenRepository,
        *,
        style_hint: str | None = None,
        visual_weight: str | None = None,
        primary_style: str | None = None,
    ) -> list[Token]:
        all_tokens = upsert_motion_from_repo(
            repo,
            style_hint=style_hint,
            visual_weight=visual_weight,
            primary_style=primary_style,
        )
        return filter_by_types(all_tokens, self._type_filter)


class DurationExtractor(_MotionDeriveExtractor):
    token_type = "duration"
    _type_filter = {"duration"}


class CubicBezierExtractor(_MotionDeriveExtractor):
    token_type = "cubicBezier"
    _type_filter = {"cubicBezier"}


class TransitionExtractor(_MotionDeriveExtractor):
    token_type = "transition"
    _type_filter = {"transition"}
