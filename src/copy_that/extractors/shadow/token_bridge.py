"""Normalize shadow token shapes between extractors and the orchestrator aggregator."""

from __future__ import annotations

from typing import Any

from .extractor import ShadowStyle


def extracted_to_shadow_style(token: Any) -> ShadowStyle:
    """Normalize AI/CV ExtractedShadowToken (or ShadowStyle) → ShadowStyle for aggregator."""
    if isinstance(token, ShadowStyle):
        return token

    def _num(primary: str, fallback: str, default: float = 0.0) -> float:
        value = getattr(token, primary, None)
        if value is None:
            value = getattr(token, fallback, default)
        return float(value if value is not None else default)

    color = getattr(token, "color_hex", None) or getattr(token, "color", "#000000")
    opacity = float(getattr(token, "opacity", 1.0) or 1.0)
    x = _num("x_offset", "x")
    y = _num("y_offset", "y")
    blur = _num("blur_radius", "blur")
    spread = _num("spread_radius", "spread")
    confidence = float(getattr(token, "confidence", 0.5) or 0.5)

    meta: dict[str, Any] = {}
    existing = getattr(token, "extraction_metadata", None)
    if isinstance(existing, dict):
        meta.update(existing)
    semantic = getattr(token, "semantic_name", None) or getattr(token, "semantic_role", None)
    if semantic:
        meta.setdefault("semantic_name", semantic)
    shadow_type = getattr(token, "shadow_type", None)
    if shadow_type:
        meta.setdefault("shadow_type", shadow_type)
    is_inset = getattr(token, "is_inset", None)
    if is_inset is not None:
        meta.setdefault("is_inset", bool(is_inset))

    return ShadowStyle(
        color=str(color),
        opacity=opacity,
        x=x,
        y=y,
        blur=blur,
        spread=spread,
        confidence=confidence,
        extraction_metadata=meta or None,
    )


def shadow_style_to_api_dict(style: ShadowStyle, index: int = 0) -> dict[str, Any]:
    """Convert ShadowStyle to ShadowTokenResponse-compatible dict."""
    meta = style.extraction_metadata or {}
    name = meta.get("semantic_name") or meta.get("name") or f"shadow-{index + 1}"
    return {
        "x_offset": style.x,
        "y_offset": style.y,
        "blur_radius": style.blur,
        "spread_radius": style.spread,
        "color_hex": style.color,
        "opacity": style.opacity,
        "name": str(name),
        "shadow_type": meta.get("shadow_type"),
        "semantic_role": meta.get("semantic_name") or meta.get("semantic_role"),
        "confidence": float(style.confidence),
    }
