"""DTCG gradient extraction (Phase 4).

CV linear-band / stop clustering is primary. Optional palette confirm maps to
``source=ai``. Color-pair synth remains export fallback when confidence is low
or no image extract landed on the graph.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import TokenRepository
from copy_that.extractors.base import BaseExtractor
from copy_that.extractors.dtcg_capability import CoverageStatus
from copy_that.extractors.gradient_cv import (
    GRADIENT_EXTRACT_CONFIDENCE_THRESHOLD,
    confirm_gradient_against_palette,
    extract_gradient_signals_from_image,
)


def _signals_to_tokens(
    signals: list[dict[str, Any]],
    *,
    namespace: str = "gradient",
) -> list[Token]:
    tokens: list[Token] = []
    for idx, signal in enumerate(signals, start=1):
        stops = signal.get("stops") or []
        if len(stops) < 2:
            continue
        conf = float(signal.get("confidence") or 0.0)
        source = str(signal.get("source") or "cv")
        angle = int(signal.get("angle") or 90)
        token_id = f"{namespace}.linear-cv-{idx:02d}"
        attrs: dict[str, Any] = {
            "$type": "gradient",
            "role": "gradient",
            "source": source,
            "confidence": conf,
        }
        if signal.get("confirmed_by"):
            attrs["confirmed_by"] = signal["confirmed_by"]
        if signal.get("axis"):
            attrs["axis"] = signal["axis"]
        tokens.append(
            Token(
                id=token_id,
                type=TokenType.GRADIENT,
                value={
                    "type": str(signal.get("type") or "linear"),
                    "angle": angle,
                    "stops": [
                        {
                            "position": float(s["position"]),
                            "color": str(s["color"]),
                        }
                        for s in stops
                        if isinstance(s, dict) and s.get("color")
                    ],
                },
                attributes=attrs,
            )
        )
    return tokens


def gradient_tokens_from_image(
    input_data: str | bytes,
    *,
    palette_hexes: Sequence[str] | None = None,
    confidence_threshold: float = GRADIENT_EXTRACT_CONFIDENCE_THRESHOLD,
    confirm_with_palette: bool = True,
    max_gradients: int = 2,
) -> list[Token]:
    """Run CV band detection (+ optional palette confirm) → Token list."""
    signals = extract_gradient_signals_from_image(
        input_data,
        confidence_threshold=confidence_threshold,
        max_gradients=max_gradients,
    )
    hexes = [h.upper() if h.startswith("#") else f"#{h}" for h in (palette_hexes or []) if h]
    if confirm_with_palette and hexes:
        signals = [confirm_gradient_against_palette(s, hexes) for s in signals]
    return _signals_to_tokens(signals)


def repo_has_extracted_gradients(
    repo: TokenRepository,
    *,
    confidence_threshold: float = GRADIENT_EXTRACT_CONFIDENCE_THRESHOLD,
) -> bool:
    """True when the graph already has CV/AI gradients at/above threshold."""
    existing = list(repo.find_by_type(TokenType.GRADIENT)) + list(repo.find_by_type("gradient"))
    for token in existing:
        source = str(token.attributes.get("source") or "")
        conf = float(token.attributes.get("confidence") or 0.0)
        if source in {"cv", "ai", "extracted"} and conf >= confidence_threshold:
            return True
    return False


def upsert_extracted_gradients(
    repo: TokenRepository,
    tokens: Sequence[Token],
) -> list[Token]:
    """Insert extracted gradients without clobbering existing ids."""
    upserted: list[Token] = []
    for token in tokens:
        if repo.get_token(token.id) is None:
            repo.upsert_token(token)
            upserted.append(token)
    return upserted


class GradientExtractor(BaseExtractor):
    """CV (+ optional palette confirm) gradient extractor.

    Registry name ``gradient``. Image path is primary; export-time color-pair
    synth stays in :mod:`motion_service` as fallback only.
    """

    token_type = "gradient"
    coverage_status = CoverageStatus.LIVE

    async def extract(self, input_data: str | bytes) -> list[dict[str, Any]]:
        tokens = gradient_tokens_from_image(input_data)
        return [
            {
                "id": t.id,
                "type": "gradient",
                "value": t.value,
                "attributes": t.attributes,
            }
            for t in tokens
        ]

    def extract_with_palette(
        self,
        input_data: str | bytes,
        palette_hexes: Sequence[str],
    ) -> list[Token]:
        """Sync helper for color-pipeline wiring (optional AI/palette confirm)."""
        return gradient_tokens_from_image(input_data, palette_hexes=palette_hexes)
