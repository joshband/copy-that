"""Heuristic / AI-cue motion profiles for DTCG duration / cubicBezier / transition.

Screenshot motion is weak; Phase 5 prefers UI-kit fingerprints and style cues
already on the token graph. Preset export remains the fallback below threshold.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import TokenRepository

MOTION_EXTRACT_CONFIDENCE_THRESHOLD = 0.55

MotionSource = Literal["heuristic", "ai", "extracted"]


@dataclass(frozen=True, slots=True)
class MotionProfile:
    """Named duration + easing set with stable token ids for generators."""

    name: str
    durations_ms: tuple[tuple[str, int], ...]  # (id suffix, ms) → duration.{suffix}
    easings: tuple[tuple[str, tuple[float, float, float, float]], ...]
    # (transition id suffix, duration suffix, easing suffix)
    transitions: tuple[tuple[str, str, str], ...]


# Stable ids match P2b presets so CSS/React/Tailwind shapes stay stable.
_STANDARD_TRANSITIONS: tuple[tuple[str, str, str], ...] = (
    ("fast", "fast", "ease"),
    ("normal", "normal", "ease-in-out"),
)

PROFILES: dict[str, MotionProfile] = {
    "material": MotionProfile(
        name="material",
        # Material-ish short/medium scale (not claiming MD3 API fidelity)
        durations_ms=(("fast", 100), ("normal", 200), ("slow", 300)),
        easings=(
            ("ease", (0.2, 0.0, 0.0, 1.0)),
            ("ease-in-out", (0.2, 0.0, 0.0, 1.0)),
        ),
        transitions=_STANDARD_TRANSITIONS,
    ),
    "ios": MotionProfile(
        name="ios",
        durations_ms=(("fast", 200), ("normal", 250), ("slow", 350)),
        easings=(
            ("ease", (0.25, 0.1, 0.25, 1.0)),
            ("ease-in-out", (0.42, 0.0, 0.58, 1.0)),
        ),
        transitions=_STANDARD_TRANSITIONS,
    ),
    "fluent": MotionProfile(
        name="fluent",
        durations_ms=(("fast", 167), ("normal", 250), ("slow", 333)),
        easings=(
            ("ease", (0.1, 0.9, 0.2, 1.0)),
            ("ease-in-out", (0.33, 0.0, 0.67, 1.0)),
        ),
        transitions=_STANDARD_TRANSITIONS,
    ),
    "snappy": MotionProfile(
        name="snappy",
        durations_ms=(("fast", 100), ("normal", 150), ("slow", 220)),
        easings=(
            ("ease", (0.25, 0.1, 0.25, 1.0)),
            ("ease-in-out", (0.4, 0.0, 0.2, 1.0)),
        ),
        transitions=_STANDARD_TRANSITIONS,
    ),
    "soft": MotionProfile(
        name="soft",
        durations_ms=(("fast", 180), ("normal", 280), ("slow", 400)),
        easings=(
            ("ease", (0.33, 0.0, 0.2, 1.0)),
            ("ease-in-out", (0.45, 0.0, 0.55, 1.0)),
        ),
        transitions=_STANDARD_TRANSITIONS,
    ),
}

# Font family substrings → UI kit hints (case-insensitive)
_FONT_KIT_HINTS: tuple[tuple[str, str, float], ...] = (
    ("roboto", "material", 0.28),
    ("product sans", "material", 0.22),
    ("sf pro", "ios", 0.3),
    ("san francisco", "ios", 0.3),
    ("new york", "ios", 0.18),
    ("segoe", "fluent", 0.3),
    ("sitka", "fluent", 0.15),
)

_STYLE_TO_PROFILE: dict[str, str] = {
    "minimalist": "snappy",
    "minimal": "snappy",
    "brutalist": "snappy",
    "technical": "snappy",
    "playful": "soft",
    "friendly": "soft",
    "organic": "soft",
    "elegant": "soft",
    "material": "material",
    "ios": "ios",
    "fluent": "fluent",
}


def _collect_font_families(repo: TokenRepository) -> list[str]:
    families: list[str] = []
    for token in (
        list(repo.find_by_type(TokenType.FONT_FAMILY_DTCG))
        + list(repo.find_by_type("fontFamily"))
        + list(repo.find_by_type(TokenType.FONT_FAMILY))
        + list(repo.find_by_type(TokenType.TYPOGRAPHY))
    ):
        val = token.value
        if isinstance(val, str) and val.strip():
            families.append(val)
        elif isinstance(val, dict):
            fam = val.get("fontFamily")
            if isinstance(fam, str) and fam.strip():
                families.append(fam)
            elif isinstance(fam, list):
                families.extend(str(x) for x in fam if x)
    return families


def _collect_radii_px(repo: TokenRepository) -> list[float]:
    radii: list[float] = []
    for token in list(repo.find_by_type(TokenType.LAYOUT)) + list(repo.find_by_type("layout")):
        val = token.value
        if not isinstance(val, dict):
            continue
        radius = val.get("radius")
        if isinstance(radius, (int, float)):
            radii.append(float(radius))
        elif isinstance(radius, dict) and isinstance(radius.get("value"), (int, float)):
            radii.append(float(radius["value"]))
    return radii


def _collect_spacing_values(repo: TokenRepository) -> list[float]:
    values: list[float] = []
    for token in (
        list(repo.find_by_type(TokenType.SPACING))
        + list(repo.find_by_type(TokenType.DIMENSION))
        + list(repo.find_by_type("spacing"))
        + list(repo.find_by_type("dimension"))
    ):
        val = token.value
        if isinstance(val, (int, float)):
            values.append(float(val))
        elif isinstance(val, dict) and isinstance(val.get("value"), (int, float)):
            values.append(float(val["value"]))
    return values


def score_ui_kit_cues(repo: TokenRepository) -> dict[str, float]:
    """Accumulate soft scores per kit from fonts, radii, and spacing rhythm."""
    scores: dict[str, float] = dict.fromkeys(PROFILES, 0.0)

    for family in _collect_font_families(repo):
        lower = family.lower()
        for needle, kit, weight in _FONT_KIT_HINTS:
            if needle in lower:
                scores[kit] = scores.get(kit, 0.0) + weight

    radii = _collect_radii_px(repo)
    if radii:
        median = sorted(radii)[len(radii) // 2]
        # Material/Fluent often use 4/8/12; iOS ~10/14; soft UIs larger
        if median <= 4:
            scores["snappy"] += 0.22
            scores["material"] += 0.12
        elif 6 <= median <= 12:
            scores["material"] += 0.18
            scores["fluent"] += 0.12
            scores["ios"] += 0.1
        elif 13 <= median <= 18:
            scores["ios"] += 0.2
            scores["soft"] += 0.1
        else:
            scores["soft"] += 0.25

    spacing = _collect_spacing_values(repo)
    if spacing:
        # 8px rhythm → Material / Fluent lean
        eights = sum(1 for v in spacing if abs(v % 8) < 0.51 or abs(v % 8 - 8) < 0.51)
        if eights >= max(2, len(spacing) // 3):
            scores["material"] += 0.15
            scores["fluent"] += 0.1

    return scores


def detect_ui_kit_profile(repo: TokenRepository) -> tuple[str | None, float]:
    """Return (profile_name, confidence) when cues clear the extract threshold."""
    scores = score_ui_kit_cues(repo)
    if not scores:
        return None, 0.0
    best_name = max(scores, key=lambda k: scores[k])
    best = scores[best_name]
    # Map raw cue score → confidence; require meaningful signal
    confidence = min(0.85, 0.4 + best)
    if confidence < MOTION_EXTRACT_CONFIDENCE_THRESHOLD or best < 0.2:
        return None, confidence
    return best_name, round(confidence, 3)


def profile_from_style_cues(
    style_hint: str | None = None,
    *,
    visual_weight: str | None = None,
    primary_style: str | None = None,
) -> tuple[str | None, float]:
    """AI/style-hint path: map narrative style → motion profile with modest conf."""
    key = (style_hint or primary_style or "").strip().lower()
    if key in _STYLE_TO_PROFILE:
        conf = 0.62 if style_hint else 0.58
        return _STYLE_TO_PROFILE[key], conf
    if visual_weight == "heavy":
        return "snappy", 0.56
    if visual_weight == "light":
        return "soft", 0.56
    return None, 0.0


def tokens_from_profile(
    profile: MotionProfile,
    *,
    source: MotionSource,
    confidence: float,
    kit: str | None = None,
) -> list[Token]:
    """Emit duration + cubicBezier + transition tokens for a profile."""
    attrs_base: dict[str, Any] = {
        "source": source,
        "confidence": round(confidence, 3),
        "motion_profile": profile.name,
    }
    if kit:
        attrs_base["ui_kit"] = kit

    tokens: list[Token] = []
    for suffix, ms in profile.durations_ms:
        tokens.append(
            Token(
                id=f"duration.{suffix}",
                type=TokenType.DURATION,
                value={"value": ms, "unit": "ms"},
                attributes={
                    **attrs_base,
                    "$type": "duration",
                    "role": "transition-duration",
                },
            )
        )
    for suffix, curve in profile.easings:
        tokens.append(
            Token(
                id=f"cubicBezier.{suffix}",
                type=TokenType.CUBIC_BEZIER,
                value=list(curve),
                attributes={
                    **attrs_base,
                    "$type": "cubicBezier",
                    "role": "easing",
                },
            )
        )
    for t_suffix, d_suffix, e_suffix in profile.transitions:
        tokens.append(
            Token(
                id=f"transition.{t_suffix}",
                type=TokenType.TRANSITION,
                value={
                    "duration": f"{{duration.{d_suffix}}}",
                    "delay": {"value": 0, "unit": "ms"},
                    "timingFunction": f"{{cubicBezier.{e_suffix}}}",
                },
                attributes={
                    **attrs_base,
                    "$type": "transition",
                    "role": "transition",
                },
            )
        )
    return tokens


def resolve_motion_tokens(
    repo: TokenRepository,
    *,
    style_hint: str | None = None,
    visual_weight: str | None = None,
    primary_style: str | None = None,
    confidence_threshold: float = MOTION_EXTRACT_CONFIDENCE_THRESHOLD,
) -> list[Token]:
    """Prefer UI-kit heuristic; fall back to style/AI cues when strong enough."""
    kit, kit_conf = detect_ui_kit_profile(repo)
    if kit and kit_conf >= confidence_threshold and kit in PROFILES:
        return tokens_from_profile(
            PROFILES[kit],
            source="heuristic",
            confidence=kit_conf,
            kit=kit,
        )

    style_name, style_conf = profile_from_style_cues(
        style_hint,
        visual_weight=visual_weight,
        primary_style=primary_style,
    )
    if style_name and style_conf >= confidence_threshold and style_name in PROFILES:
        source: MotionSource = "ai" if (style_hint or primary_style) else "heuristic"
        return tokens_from_profile(
            PROFILES[style_name],
            source=source,
            confidence=style_conf,
            kit=style_name,
        )
    return []


def filter_by_types(
    tokens: Sequence[Token],
    types: set[str],
) -> list[Token]:
    out: list[Token] = []
    for token in tokens:
        t = token.type.value if isinstance(token.type, TokenType) else str(token.type)
        if t in types:
            out.append(token)
    return out
