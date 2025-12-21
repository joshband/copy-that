from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from copy_that.application import color_utils as cu
from copy_that.application.perf import track_perf


@dataclass
class ShadowStyle:
    color: str
    opacity: float
    x: float
    y: float
    blur: float
    spread: float
    inset: bool = False


class ShadowExtractor:
    """
    Minimal shadow extractor that deduplicates shadow styles and references known colors.

    Pass in a color_token_map (hex -> token_id) so we can emit references instead of raw hex.
    """

    def __init__(self, color_token_map: dict[str, str] | None = None):
        self.color_map = {k.lower(): v for k, v in (color_token_map or {}).items()}

    def extract_shadow_tokens(self, layers: Iterable[Any]) -> dict[str, dict[str, Any]]:
        """
        Args:
            layers: iterable of objects with a `shadow` attribute or None.

        Returns:
            Dict of shadow token name -> token payload with $type and $value.
        """
        seen: set[tuple[str, float, int, int, int, int, bool]] = set()
        tokens: dict[str, dict[str, Any]] = {}
        idx = 1

        with track_perf(
            "extract.shadow.ai",
            {"layers_type": type(layers).__name__},
            measure_memory=True,
        ):
            for layer in layers:
                raw_shadow = getattr(layer, "shadow", None)
                if not raw_shadow:
                    continue
                styles = self._normalize_shadow(raw_shadow)
                if not styles:
                    continue
                value: list[dict[str, Any]] = []
                for style in styles:
                    key = (
                        style.color.lower(),
                        round(style.opacity, 2),
                        int(style.x),
                        int(style.y),
                        int(style.blur),
                        int(style.spread),
                        bool(style.inset),
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    color_hex = cu.normalize_hex(style.color)
                    color_value: str = color_hex
                    if color_hex.lower() in self.color_map:
                        color_value = f"{{{self.color_map[color_hex.lower()]}}}"
                    color_token = (
                        color_value if style.opacity >= 1 else f"{color_value}{int(style.opacity * 100)}%"
                    )
                    layer_value = {
                        "color": color_token,
                        "x": {"value": int(round(style.x)), "unit": "px"},
                        "y": {"value": int(round(style.y)), "unit": "px"},
                        "blur": {"value": int(round(style.blur)), "unit": "px"},
                        "spread": {"value": int(round(style.spread)), "unit": "px"},
                        "inset": bool(style.inset),
                        "type": "inner" if style.inset else "drop",
                    }
                    value.append(layer_value)
                if value:
                    tokens[f"shadow.{idx}"] = {"$type": "shadow", "$value": value}
                    idx += 1

        return tokens

    @staticmethod
    def _normalize_shadow(raw_shadow: Any) -> list[ShadowStyle]:
        """Coerce various shadow representations into ShadowStyle objects."""
        styles: list[ShadowStyle] = []
        raw_list = raw_shadow if isinstance(raw_shadow, (list, tuple)) else [raw_shadow]
        for raw in raw_list:
            if raw is None:
                continue
            # Dict input
            if isinstance(raw, dict):
                styles.append(
                    ShadowStyle(
                        color=raw.get("color", "#000000"),
                        opacity=float(raw.get("opacity", raw.get("alpha", 1.0))),
                        x=float(raw.get("x", 0)),
                        y=float(raw.get("y", 0)),
                        blur=float(raw.get("blur", raw.get("radius", 0))),
                        spread=float(raw.get("spread", 0)),
                        inset=bool(raw.get("inset") or (str(raw.get("type", "")).lower().startswith("inner"))),
                    )
                )
                continue
            # Object with attributes
            inset_attr = getattr(raw, "inset", None) or getattr(raw, "insetShadow", None)
            raw_type = getattr(raw, "type", None)
            styles.append(
                ShadowStyle(
                    color=getattr(raw, "color", "#000000"),
                    opacity=float(getattr(raw, "opacity", getattr(raw, "alpha", 1.0))),
                    x=float(getattr(raw, "x", 0)),
                    y=float(getattr(raw, "y", 0)),
                    blur=float(getattr(raw, "blur", getattr(raw, "radius", 0))),
                    spread=float(getattr(raw, "spread", 0)),
                    inset=bool(
                        inset_attr
                        or (isinstance(raw_type, str) and raw_type.lower().startswith("inner"))
                        or getattr(raw, "is_inner", False)
                    ),
                )
            )
        return styles
