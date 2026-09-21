"""Synthesize P2b motion tokens (gradient / duration / cubicBezier) at export time.

Phase 4: color-pair gradient synth is fallback only when no CV/AI extract meets
the confidence threshold (see :mod:`copy_that.extractors.gradient_extract`).

Phase 5: duration / cubicBezier presets are fallback only when no UI-kit /
style-cue extract meets the confidence threshold
(see :mod:`copy_that.extractors.motion_extract`). Presets never claim high
confidence.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from copy_that.core_tokens.model import Token
from copy_that.core_tokens.repository import TokenRepository

# Honest preset confidence — below extract threshold (0.55)
_PRESET_MOTION_CONFIDENCE = 0.35


def _color_hex(row: Any) -> str | None:
    hex_val = getattr(row, "hex", None)
    if isinstance(hex_val, str) and hex_val.startswith("#"):
        return hex_val.upper()
    return None


def synthesize_gradient_tokens_from_colors(
    colors: Sequence[Any],
    *,
    namespace: str = "gradient",
    max_gradients: int = 2,
    repo: TokenRepository | None = None,
    prefer_extracted: bool = True,
    confidence_threshold: float = 0.55,
) -> list[Token]:
    """Build simple linear gradients from the first distinct project colors.

    When ``prefer_extracted`` and ``repo`` already hold CV/AI gradients at/above
    ``confidence_threshold``, returns ``[]`` so extract wins over synth.
    """
    if prefer_extracted and repo is not None:
        try:
            from copy_that.extractors.gradient_extract import repo_has_extracted_gradients

            if repo_has_extracted_gradients(repo, confidence_threshold=confidence_threshold):
                return []
        except Exception:
            pass

    hexes: list[str] = []
    seen: set[str] = set()
    for row in colors:
        hx = _color_hex(row)
        if not hx or hx in seen:
            continue
        seen.add(hx)
        hexes.append(hx)
        if len(hexes) >= max_gradients + 1:
            break

    if len(hexes) < 2:
        # Single-color projects still get a usable gradient (pair with white/black).
        if len(hexes) == 1:
            companion = "#FFFFFF" if hexes[0].upper() not in {"#FFFFFF", "#FFF"} else "#111111"
            hexes.append(companion)
        else:
            return []

    tokens: list[Token] = []
    for idx in range(min(max_gradients, len(hexes) - 1)):
        start, end = hexes[idx], hexes[idx + 1]
        token_id = f"{namespace}.linear-{idx + 1:02d}"
        pair_source = len(seen) >= 2
        tokens.append(
            Token(
                id=token_id,
                type="gradient",
                value={
                    "type": "linear",
                    "angle": 90,
                    "stops": [
                        {"position": 0, "color": start},
                        {"position": 1, "color": end},
                    ],
                },
                attributes={
                    "$type": "gradient",
                    "role": "gradient",
                    # Plan Phase 4 provenance: cv | ai | synth (color-pair is synth_kind)
                    "source": "synth",
                    "synth_kind": "color-pair" if pair_source else "companion",
                    "confidence": 0.55 if pair_source else 0.4,
                },
            )
        )
    return tokens


def synthesize_transition_tokens(
    repo: TokenRepository | None = None,
    *,
    prefer_extracted: bool = True,
    confidence_threshold: float = 0.55,
) -> list[Token]:
    """Emit a small standard duration + easing set when a project has other tokens.

    When ``prefer_extracted`` and ``repo`` already hold heuristic/AI motion at/above
    ``confidence_threshold``, returns ``[]`` so extract wins over presets.
    """
    if prefer_extracted and repo is not None:
        try:
            from copy_that.extractors.motion_extract import repo_has_extracted_motion

            if repo_has_extracted_motion(
                repo,
                confidence_threshold=confidence_threshold,
                types={"duration", "cubicBezier"},
            ):
                return []
        except Exception:
            pass

    durations = (
        ("duration.fast", 150),
        ("duration.normal", 200),
        ("duration.slow", 300),
    )
    tokens: list[Token] = [
        Token(
            id=name,
            type="duration",
            value={"value": ms, "unit": "ms"},
            attributes={
                "$type": "duration",
                "role": "transition-duration",
                "source": "preset",
                "confidence": _PRESET_MOTION_CONFIDENCE,
            },
        )
        for name, ms in durations
    ]
    tokens.append(
        Token(
            id="cubicBezier.ease",
            type="cubicBezier",
            value=[0.25, 0.1, 0.25, 1.0],
            attributes={
                "$type": "cubicBezier",
                "role": "easing",
                "source": "preset",
                "confidence": _PRESET_MOTION_CONFIDENCE,
            },
        )
    )
    tokens.append(
        Token(
            id="cubicBezier.ease-in-out",
            type="cubicBezier",
            value=[0.42, 0.0, 0.58, 1.0],
            attributes={
                "$type": "cubicBezier",
                "role": "easing",
                "source": "preset",
                "confidence": _PRESET_MOTION_CONFIDENCE,
            },
        )
    )
    return tokens
