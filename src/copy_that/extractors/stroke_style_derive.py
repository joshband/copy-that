"""Derive DTCG strokeStyle tokens from CV/heuristic signals or presets."""

from __future__ import annotations

from typing import Any

from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import TokenRepository
from copy_that.extractors.base import BaseExtractor
from copy_that.extractors.border_cv import (
    BORDER_EXTRACT_CONFIDENCE_THRESHOLD,
    extract_border_signals_from_image,
)
from copy_that.extractors.dtcg_capability import CoverageStatus
from copy_that.services.type_coverage_service import synthesize_stroke_style_presets


def _type_str(token: Token) -> str:
    return token.type.value if isinstance(token.type, TokenType) else str(token.type)


def stroke_styles_from_signals(
    signals: list[dict[str, Any]],
    *,
    confidence_threshold: float = BORDER_EXTRACT_CONFIDENCE_THRESHOLD,
) -> list[Token]:
    """Build strokeStyle tokens from CV/heuristic descriptors."""
    tokens: list[Token] = []
    seen: set[str] = set()
    for signal in signals:
        if signal.get("kind") != "stroke_style":
            continue
        style = str(signal.get("value") or "solid").lower()
        if style not in {"solid", "dashed", "dotted", "double", "groove", "ridge", "outset", "inset"}:
            style = "solid"
        conf = float(signal.get("confidence") or 0.0)
        if conf < confidence_threshold:
            continue
        token_id = str(signal.get("id") or f"strokeStyle.{style}")
        if token_id in seen:
            continue
        seen.add(token_id)
        tokens.append(
            Token(
                id=token_id,
                type=TokenType.STROKE_STYLE,
                value=style,
                attributes={
                    "$type": "strokeStyle",
                    "role": "stroke",
                    "source": str(signal.get("source") or "cv"),
                    "confidence": conf,
                },
            )
        )
    return tokens


def ensure_stroke_style_refs(repo: TokenRepository, *, prefer_extracted: bool = True) -> list[Token]:
    """Ensure solid (and dashed when useful) exist; prefer extracted when present."""
    existing = [
        t
        for t in list(repo.find_by_type(TokenType.STROKE_STYLE))
        + list(repo.find_by_type("strokeStyle"))
    ]
    extracted = [
        t
        for t in existing
        if str(t.attributes.get("source") or "") in {"cv", "extracted", "heuristic"}
        and float(t.attributes.get("confidence") or 0.0) >= BORDER_EXTRACT_CONFIDENCE_THRESHOLD
    ]
    if prefer_extracted and extracted:
        # Still guarantee solid ref for border composites that point at it
        ids = {t.id for t in existing}
        created: list[Token] = []
        if "strokeStyle.solid" not in ids and not any(
            str(t.value) == "solid" for t in existing
        ):
            solid = synthesize_stroke_style_presets(include_dashed=False)[0]
            if repo.get_token(solid.id) is None:
                repo.upsert_token(solid)
                created.append(solid)
        return created

    created = []
    for token in synthesize_stroke_style_presets(include_dashed=True):
        if repo.get_token(token.id) is None:
            repo.upsert_token(token)
            created.append(token)
    return created


class StrokeStyleDeriveExtractor(BaseExtractor):
    """CV/heuristic strokeStyle — presets only as fallback below confidence bar."""

    token_type = "strokeStyle"
    coverage_status = CoverageStatus.DERIVE

    async def extract(self, input_data: str | bytes) -> list[dict[str, Any]]:
        signals = extract_border_signals_from_image(input_data)
        tokens = stroke_styles_from_signals(signals)
        return [
            {
                "id": t.id,
                "type": _type_str(t),
                "value": t.value,
                "attributes": t.attributes,
            }
            for t in tokens
        ]

    def derive_from_repo(self, repo: TokenRepository) -> list[Token]:
        """Collect strokeStyle already on the graph (no image)."""
        return [
            t
            for t in list(repo.find_by_type(TokenType.STROKE_STYLE))
            + list(repo.find_by_type("strokeStyle"))
        ]

    def derive_and_upsert(self, repo: TokenRepository) -> list[Token]:
        return ensure_stroke_style_refs(repo, prefer_extracted=True)
