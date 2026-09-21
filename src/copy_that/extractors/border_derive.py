"""Derive DTCG border composites from layout / CV signals.

Phase 1 registered a layout-width compose path. Phase 3 adds CV/heuristic
``extract`` (edge width, radius, dashed vs solid) and prefers extracted
strokeStyle + borders over P2c synth when confidence ≥ threshold.
"""

from __future__ import annotations

from typing import Any

from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import InMemoryTokenRepository, TokenRepository
from copy_that.extractors.base import BaseExtractor
from copy_that.extractors.border_cv import (
    BORDER_EXTRACT_CONFIDENCE_THRESHOLD,
    extract_border_signals_from_image,
)
from copy_that.extractors.dtcg_capability import CoverageStatus
from copy_that.extractors.stroke_style_derive import (
    ensure_stroke_style_refs,
    stroke_styles_from_signals,
)
from copy_that.services.type_coverage_service import synthesize_border_composites


def _signals_to_layout_tokens(signals: list[dict[str, Any]]) -> list[Token]:
    tokens: list[Token] = []
    for signal in signals:
        kind = signal.get("kind")
        conf = float(signal.get("confidence") or 0.0)
        source = str(signal.get("source") or "cv")
        if kind == "border_width":
            tokens.append(
                Token(
                    id=str(signal.get("id") or f"layout.border.{signal.get('value')}"),
                    type=TokenType.LAYOUT,
                    value={"border": {"width": int(signal["value"])}},
                    attributes={
                        "role": "border_width",
                        "source": source,
                        "confidence": conf,
                    },
                )
            )
        elif kind == "corner_radius":
            tokens.append(
                Token(
                    id=str(signal.get("id") or f"layout.radius.{signal.get('value')}"),
                    type=TokenType.LAYOUT,
                    value={"radius": int(signal["value"])},
                    attributes={
                        "role": "corner_radius",
                        "source": source,
                        "confidence": conf,
                    },
                )
            )
    return tokens


def _preferred_stroke_ref(repo: TokenRepository) -> str:
    """Pick dashed if confidently extracted, else solid."""
    styles = list(repo.find_by_type(TokenType.STROKE_STYLE)) + list(
        repo.find_by_type("strokeStyle")
    )
    best_dashed: Token | None = None
    best_solid: Token | None = None
    for token in styles:
        style = str(token.value or "").lower()
        conf = float(token.attributes.get("confidence") or 0.0)
        source = str(token.attributes.get("source") or "")
        extracted = source in {"cv", "extracted", "heuristic"}
        if style == "dashed" and extracted and conf >= BORDER_EXTRACT_CONFIDENCE_THRESHOLD:
            if best_dashed is None or conf > float(best_dashed.attributes.get("confidence") or 0):
                best_dashed = token
        if style == "solid":
            if best_solid is None or conf > float(best_solid.attributes.get("confidence") or 0):
                best_solid = token
    if best_dashed is not None:
        return f"{{{best_dashed.id}}}"
    if best_solid is not None:
        return f"{{{best_solid.id}}}"
    return "{strokeStyle.solid}"


def compose_borders_from_repo(
    repo: TokenRepository,
    *,
    skip_if_extracted: bool = True,
) -> list[Token]:
    """Compose border tokens; skip synth defaults when extracted borders exist."""
    existing = list(repo.find_by_type(TokenType.BORDER)) + list(repo.find_by_type("border"))
    if skip_if_extracted and any(
        str(t.attributes.get("source") or "") in {"cv", "extracted", "heuristic"}
        and float(t.attributes.get("confidence") or 0.7) >= BORDER_EXTRACT_CONFIDENCE_THRESHOLD
        for t in existing
    ):
        return []

    ensure_stroke_style_refs(repo, prefer_extracted=True)
    style_ref = _preferred_stroke_ref(repo)
    tokens = synthesize_border_composites(repo)
    # Retarget style ref + bump provenance when layout widths were CV-sourced
    layout_ids = {
        t.id
        for t in repo.find_by_type(TokenType.LAYOUT)
        if str(t.attributes.get("role") or "") == "border_width"
        and str(t.attributes.get("source") or "") in {"cv", "extracted", "heuristic"}
    }
    for token in tokens:
        if isinstance(token.value, dict):
            token.value = {**token.value, "style": style_ref}
        from_id = str(token.attributes.get("from") or "")
        if from_id in layout_ids:
            token.attributes["source"] = "extracted"
            token.attributes["confidence"] = float(
                next(
                    (
                        t.attributes.get("confidence")
                        for t in repo.find_by_type(TokenType.LAYOUT)
                        if t.id == from_id
                    ),
                    0.7,
                )
            )
    return tokens


class BorderDeriveExtractor(BaseExtractor):
    """CV/heuristic border compose — image path + layout derive.

    ``extract`` runs classical contour heuristics (width / radius / stroke).
    ``derive_from_repo`` composes DTCG ``border`` composites from layout widths.
    """

    token_type = "border"
    coverage_status = CoverageStatus.DERIVE

    async def extract(self, input_data: str | bytes) -> list[dict[str, Any]]:
        signals = extract_border_signals_from_image(input_data)
        if not signals:
            return []

        repo = InMemoryTokenRepository()
        for layout in _signals_to_layout_tokens(signals):
            repo.upsert_token(layout)
        for style in stroke_styles_from_signals(signals):
            repo.upsert_token(style)

        borders = compose_borders_from_repo(repo, skip_if_extracted=False)
        for border in borders:
            if repo.get_token(border.id) is None:
                repo.upsert_token(border)

        out: list[dict[str, Any]] = []
        for token in list(repo.find_by_type(TokenType.LAYOUT)) + list(
            repo.find_by_type(TokenType.STROKE_STYLE)
        ) + list(repo.find_by_type(TokenType.BORDER)) + list(repo.find_by_type("border")) + list(
            repo.find_by_type("strokeStyle")
        ):
            out.append(
                {
                    "id": token.id,
                    "type": token.type.value if isinstance(token.type, TokenType) else str(token.type),
                    "value": token.value,
                    "attributes": token.attributes,
                }
            )
        return out

    def derive_from_repo(self, repo: TokenRepository) -> list[Token]:
        """Compose border tokens from layout widths already in ``repo``."""
        return compose_borders_from_repo(repo, skip_if_extracted=True)

    def derive_and_upsert(self, repo: TokenRepository) -> list[Token]:
        created = compose_borders_from_repo(repo, skip_if_extracted=True)
        for token in created:
            if repo.get_token(token.id) is None:
                repo.upsert_token(token)
        return created


def border_tokens_from_layout_widths(widths_px: list[int]) -> list[Token]:
    """Helper for tests: seed layout widths then derive border composites."""
    repo = InMemoryTokenRepository()
    for idx, width in enumerate(sorted({int(w) for w in widths_px if w > 0}), start=1):
        repo.upsert_token(
            Token(
                id=f"layout.border.{idx}",
                type=TokenType.LAYOUT,
                value={"border": {"width": width}},
                attributes={"role": "border_width", "source": "heuristic", "confidence": 0.8},
            )
        )
    return BorderDeriveExtractor().derive_from_repo(repo)
