"""DTCG Format 2025.10 type capability map for extractors.

Tracks how each official `$type` is produced today (extract / derive / synth /
stub) so registry listing and Phase 2+ work stay honest vs P2c export-complete.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal


class CoverageStatus(StrEnum):
    LIVE = "live"  # Image/CV/AI extractor registered and used on MVP path
    DERIVE = "derive"  # Heuristic from other tokens / layout (not screenshot-primary)
    SYNTH = "synth"  # Export-time preset or synthesis (P2c)
    STUB = "stub"  # Registry placeholder; returns no tokens yet


Modality = Literal["cv", "ai", "code", "derive", "preset", "stub"]


@dataclass(frozen=True, slots=True)
class DtcgTypeCapability:
    dtcg_type: str
    status: CoverageStatus
    modalities: tuple[Modality, ...]
    extractor_name: str | None
    notes: str


# Official Format 2025.10 types only (not Compat+ section names).
DTCG_TYPE_CAPABILITIES: dict[str, DtcgTypeCapability] = {
    "color": DtcgTypeCapability(
        dtcg_type="color",
        status=CoverageStatus.LIVE,
        modalities=("ai", "cv", "code"),
        extractor_name="color",
        notes="Hex Compat+; Color Module object form deferred.",
    ),
    "dimension": DtcgTypeCapability(
        dtcg_type="dimension",
        status=CoverageStatus.DERIVE,
        modalities=("code", "derive"),
        extractor_name="dimension",
        notes=(
            "Companions dual-written at spacing build; spacing section retained "
            "(Compat+). Export synth falls back if missing."
        ),
    ),
    "fontFamily": DtcgTypeCapability(
        dtcg_type="fontFamily",
        status=CoverageStatus.DERIVE,
        modalities=("derive", "code"),
        extractor_name="fontFamily",
        notes="Persisted atoms at typography build with COMPOSES; export synth fallback.",
    ),
    "fontWeight": DtcgTypeCapability(
        dtcg_type="fontWeight",
        status=CoverageStatus.DERIVE,
        modalities=("derive", "code"),
        extractor_name="fontWeight",
        notes="Persisted atoms at typography build with COMPOSES; export synth fallback.",
    ),
    "duration": DtcgTypeCapability(
        dtcg_type="duration",
        status=CoverageStatus.DERIVE,
        modalities=("ai", "code", "preset"),
        extractor_name="duration",
        notes=(
            "UI-kit / style-cue heuristic (Phase 5); presets at export only below "
            "confidence threshold (presets never claim high confidence)."
        ),
    ),
    "cubicBezier": DtcgTypeCapability(
        dtcg_type="cubicBezier",
        status=CoverageStatus.DERIVE,
        modalities=("ai", "code", "preset"),
        extractor_name="cubicBezier",
        notes="Easing from UI-kit / style cues; preset fallback with low confidence.",
    ),
    "number": DtcgTypeCapability(
        dtcg_type="number",
        status=CoverageStatus.DERIVE,
        modalities=("cv", "derive", "code"),
        extractor_name="number",
        notes=(
            "First-class opacity from shadows + UI alpha (Compat+ opacity section); "
            "line-height numbers still derived at export."
        ),
    ),
    "strokeStyle": DtcgTypeCapability(
        dtcg_type="strokeStyle",
        status=CoverageStatus.DERIVE,
        modalities=("cv", "derive", "preset"),
        extractor_name="strokeStyle",
        notes="CV/heuristic solid vs dashed; presets only below confidence threshold.",
    ),
    "border": DtcgTypeCapability(
        dtcg_type="border",
        status=CoverageStatus.DERIVE,
        modalities=("cv", "derive", "code"),
        extractor_name="border",
        notes="CV edge width/radius + compose from layout widths + strokeStyle (+ color).",
    ),
    "transition": DtcgTypeCapability(
        dtcg_type="transition",
        status=CoverageStatus.DERIVE,
        modalities=("ai", "code", "derive", "preset"),
        extractor_name="transition",
        notes=(
            "Composed with duration + cubicBezier from UI-kit / style cues; "
            "synth compose when extract missing."
        ),
    ),
    "shadow": DtcgTypeCapability(
        dtcg_type="shadow",
        status=CoverageStatus.LIVE,
        modalities=("cv", "ai"),
        extractor_name="shadow",
        notes="Primary extract; synth fallback if empty.",
    ),
    "gradient": DtcgTypeCapability(
        dtcg_type="gradient",
        status=CoverageStatus.LIVE,
        modalities=("cv", "ai", "code"),
        extractor_name="gradient",
        notes=(
            "CV linear-band / stop clustering (+ optional palette confirm → source=ai); "
            "color-pair synth fallback below confidence."
        ),
    ),
    "typography": DtcgTypeCapability(
        dtcg_type="typography",
        status=CoverageStatus.LIVE,
        modalities=("ai", "cv"),
        extractor_name="typography",
        notes="Composite extract; fontFamily/fontWeight atoms dual-written with COMPOSES.",
    ),
}

OFFICIAL_DTCG_TYPES: frozenset[str] = frozenset(DTCG_TYPE_CAPABILITIES)


def capability_for(dtcg_type: str) -> DtcgTypeCapability | None:
    return DTCG_TYPE_CAPABILITIES.get(dtcg_type)


def list_capabilities() -> list[DtcgTypeCapability]:
    return [DTCG_TYPE_CAPABILITIES[name] for name in sorted(DTCG_TYPE_CAPABILITIES)]
