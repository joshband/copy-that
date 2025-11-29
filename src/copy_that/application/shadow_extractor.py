from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from copy_that.application import color_utils as cu


@dataclass
class ShadowStyle:
    color: str
    opacity: float
    x: float
    y: float
    blur: float
    spread: float


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
        seen: set[tuple[str, float, int, int, int, int]] = set()
        tokens: dict[str, dict[str, Any]] = {}
        idx = 1

        for layer in layers:
            shadow = getattr(layer, "shadow", None)
            if not shadow:
                continue
            color_hex = cu.normalize_hex(getattr(shadow, "color", "#000000"))
            alpha = float(getattr(shadow, "opacity", 1.0))
            x = round(getattr(shadow, "x", 0))
            y = round(getattr(shadow, "y", 0))
            blur = round(getattr(shadow, "blur", 0))
            spread = round(getattr(shadow, "spread", 0))
            key = (color_hex.lower(), round(alpha, 2), x, y, blur, spread)
            if key in seen:
                continue
            seen.add(key)

            # Reference existing color token if available
            color_value: str = color_hex
            if color_hex.lower() in self.color_map:
                color_value = f"{{{self.color_map[color_hex.lower()]}}}"

            tokens[f"shadow.{idx}"] = {
                "$type": "shadow",
                "$value": {
                    "color": color_value if alpha >= 1 else f"{color_value}{int(alpha * 100)}%",
                    "x": {"value": x, "unit": "px"},
                    "y": {"value": y, "unit": "px"},
                    "blur": {"value": blur, "unit": "px"},
                    "spread": {"value": spread, "unit": "px"},
                },
            }
            idx += 1

        return tokens
