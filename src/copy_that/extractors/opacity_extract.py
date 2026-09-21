"""First-class opacity / DTCG number extraction (Phase 3).

Promotes shadow opacities and UI alpha (PNG alpha histogram) into Compat+
``opacity`` tokens with ``$type: number``. Export synth remains fallback only
when no extracted opacity meets the confidence threshold.
"""

from __future__ import annotations

import re
from base64 import b64decode
from collections.abc import Sequence
from typing import Any

from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import TokenRepository
from copy_that.extractors.base import BaseExtractor
from copy_that.extractors.dtcg_capability import CoverageStatus
from copy_that.services.layout_service import synthesize_opacity_tokens_from_shadows

OPACITY_EXTRACT_CONFIDENCE_THRESHOLD = 0.55

try:
    import cv2
    import numpy as np
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "token"


def _decode_rgba(input_data: str | bytes) -> Any | None:
    if np is None or cv2 is None:
        return None
    raw = input_data
    if isinstance(raw, str):
        if raw.startswith("data:"):
            raw = raw.split(",", 1)[-1]
        try:
            raw = b64decode(raw)
        except Exception:
            return None
    if not isinstance(raw, (bytes, bytearray)):
        return None
    arr = np.frombuffer(raw, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)


def ui_alpha_opacities_from_image(
    input_data: str | bytes,
    *,
    confidence_threshold: float = OPACITY_EXTRACT_CONFIDENCE_THRESHOLD,
    max_tokens: int = 6,
) -> list[Token]:
    """Cluster non-opaque PNG alpha values into opacity number tokens."""
    image = _decode_rgba(input_data)
    if image is None or np is None:
        return []
    if image.ndim < 3 or image.shape[2] < 4:
        return []

    alpha = image[:, :, 3].astype(np.float64)
    # Ignore fully transparent and fully opaque
    partial = alpha[(alpha > 8) & (alpha < 247)]
    if partial.size < 32:
        return []

    # Quantize to 0.05 steps for stable token ids
    values = (np.round((partial / 255.0) * 20) / 20.0).astype(np.float64)
    unique, counts = np.unique(values, return_counts=True)
    order = np.argsort(-counts)
    tokens: list[Token] = []
    for idx in order[:max_tokens]:
        opacity = float(unique[idx])
        count = int(counts[idx])
        share = count / float(partial.size)
        conf = min(0.9, 0.45 + share * 1.2)
        if conf < confidence_threshold:
            continue
        slug = str(opacity).replace(".", "-")
        tokens.append(
            Token(
                id=f"opacity.ui-{slug}",
                type=TokenType.OPACITY,
                value=round(opacity, 3),
                attributes={
                    "$type": "number",
                    "role": "opacity",
                    "source": "ui_alpha",
                    "confidence": round(conf, 3),
                    "sample_share": round(share, 4),
                },
            )
        )
    return tokens


def opacity_tokens_from_shadow_tokens(
    shadows: Sequence[Token] | Sequence[Any],
    *,
    confidence_threshold: float = OPACITY_EXTRACT_CONFIDENCE_THRESHOLD,
) -> list[Token]:
    """Promote unique shadow opacities into first-class opacity tokens."""
    # Reuse layout_service helper when rows look like DB/shadow objects
    if shadows and not isinstance(shadows[0], Token):
        tokens = synthesize_opacity_tokens_from_shadows(shadows)
        for token in tokens:
            token.attributes.setdefault("confidence", 0.75)
            token.attributes.setdefault("source", "shadow")
            if isinstance(token.type, str):
                token.type = TokenType.OPACITY
        return [
            t
            for t in tokens
            if float(t.attributes.get("confidence") or 0.0) >= confidence_threshold
        ]

    seen: set[float] = set()
    out: list[Token] = []
    for shadow in shadows:
        if not isinstance(shadow, Token):
            continue
        opacity: float | None = None
        attrs = shadow.attributes or {}
        if attrs.get("opacity") is not None:
            try:
                opacity = round(float(attrs["opacity"]), 3)
            except (TypeError, ValueError):
                opacity = None
        val = shadow.value
        if opacity is None and isinstance(val, list) and val:
            layer = val[0] if isinstance(val[0], dict) else {}
            if isinstance(layer, dict) and layer.get("opacity") is not None:
                try:
                    opacity = round(float(layer["opacity"]), 3)
                except (TypeError, ValueError):
                    opacity = None
        if opacity is None and isinstance(val, dict) and val.get("opacity") is not None:
            try:
                opacity = round(float(val["opacity"]), 3)
            except (TypeError, ValueError):
                opacity = None
        if opacity is None or opacity in seen:
            continue
        seen.add(opacity)
        conf = float(attrs.get("confidence") or 0.75)
        if conf < confidence_threshold:
            continue
        role = attrs.get("semantic_role") or attrs.get("name") or shadow.id
        slug = _slug(str(role))
        if not slug.startswith("shadow"):
            slug = f"shadow-{slug}"
        out.append(
            Token(
                id=f"opacity.{slug}",
                type=TokenType.OPACITY,
                value=opacity,
                attributes={
                    "$type": "number",
                    "role": "opacity",
                    "source": "shadow",
                    "confidence": conf,
                    "from": shadow.id,
                },
            )
        )
    return out


def opacity_tokens_from_repo(
    repo: TokenRepository,
    *,
    confidence_threshold: float = OPACITY_EXTRACT_CONFIDENCE_THRESHOLD,
) -> list[Token]:
    """Derive opacity tokens from shadow tokens already on the graph."""
    shadows = list(repo.find_by_type(TokenType.SHADOW)) + list(repo.find_by_type("shadow"))
    return opacity_tokens_from_shadow_tokens(shadows, confidence_threshold=confidence_threshold)


class OpacityNumberExtractor(BaseExtractor):
    """First-class opacity → DTCG ``number`` (Compat+ ``opacity`` section).

    Registry name remains ``number`` (official `$type`). Image path combines
    UI alpha + returns descriptors; ``derive_from_repo`` uses shadow opacities.
    """

    token_type = "number"
    coverage_status = CoverageStatus.DERIVE

    async def extract(self, input_data: str | bytes) -> list[dict[str, Any]]:
        tokens = ui_alpha_opacities_from_image(input_data)
        return [
            {
                "id": t.id,
                "type": "opacity",
                "value": t.value,
                "attributes": t.attributes,
            }
            for t in tokens
        ]

    def derive_from_repo(self, repo: TokenRepository) -> list[Token]:
        return opacity_tokens_from_repo(repo)

    def derive_and_upsert(self, repo: TokenRepository) -> list[Token]:
        created = self.derive_from_repo(repo)
        upserted: list[Token] = []
        for token in created:
            if repo.get_token(token.id) is None:
                repo.upsert_token(token)
                upserted.append(token)
        return upserted
