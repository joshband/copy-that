"""Build a GuidePack from an export TokenRepository + optional overview metrics."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from copy_that.core_tokens.adapters.w3c import tokens_to_w3c_flat
from copy_that.core_tokens.model import Token, TokenType
from copy_that.core_tokens.repository import TokenRepository
from copy_that.extractors.dtcg_capability import DTCG_TYPE_CAPABILITIES
from copy_that.guide_pack.schema import (
    GuideApplication,
    GuideBrand,
    GuideComponent,
    GuideComponentSlot,
    GuideExports,
    GuideFoundations,
    GuidePack,
    GuidePackMeta,
    snapshot_hash,
)


def _token_source(token: Token) -> str:
    raw = token.attributes.get("source")
    if isinstance(raw, str) and raw:
        key = raw.lower()
        if key in {"cv", "ai", "extracted", "extract"}:
            return "extract"
        if key in {"derive", "derived"}:
            return "derive"
        if key in {"synth", "synthetic"}:
            return "synth"
        if key == "preset":
            return "preset"
    # Infer from capability when attribute missing
    type_name = token.type.value if isinstance(token.type, TokenType) else str(token.type)
    cap = DTCG_TYPE_CAPABILITIES.get(type_name)
    if cap is None:
        return "derive"
    return str(cap.status.value)


def _collect_ids_by_section(flat: dict[str, Any]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for section, entries in flat.items():
        if section in {"meta"} or not isinstance(entries, dict):
            continue
        ids = [k for k, v in entries.items() if isinstance(v, dict) and ("$type" in v or "$value" in v)]
        if ids:
            out[section] = sorted(ids)
    return out


def _first_id(ids: list[str], *needles: str) -> str | None:
    lowered = [(i, i.lower()) for i in ids]
    for needle in needles:
        for original, low in lowered:
            if needle in low:
                return original
    return ids[0] if ids else None


def build_guide_pack(
    repo: TokenRepository,
    *,
    project_id: int | None = None,
    project_name: str | None = None,
    insights: list[str] | None = None,
    metrics: Any | None = None,
) -> GuidePack:
    """Construct a GuidePack from the export token graph."""
    flat = tokens_to_w3c_flat(repo)
    by_section = _collect_ids_by_section(flat)

    all_tokens: list[Token] = []
    if hasattr(repo, "_tokens"):
        all_tokens = list(repo._tokens.values())  # type: ignore[attr-defined]
    else:
        for t in TokenType:
            all_tokens.extend(repo.find_by_type(t))

    token_ids = sorted({t.id for t in all_tokens})
    source_counts: dict[str, int] = {"extract": 0, "derive": 0, "synth": 0, "preset": 0}
    for token in all_tokens:
        src = _token_source(token)
        source_counts[src] = source_counts.get(src, 0) + 1

    type_coverage = {
        name: cap.status.value for name, cap in DTCG_TYPE_CAPABILITIES.items()
    }

    colors = by_section.get("color", [])
    spacing = by_section.get("spacing", []) + by_section.get("dimension", [])
    typography = by_section.get("typography", [])
    shadows = by_section.get("shadow", [])
    gradients = by_section.get("gradient", [])
    shape = by_section.get("layout", []) + by_section.get("border", [])
    opacity = by_section.get("opacity", []) + [
        i for i in by_section.get("number", []) if "opacity" in i.lower() or "alpha" in i.lower()
    ]
    motion = (
        by_section.get("duration", [])
        + by_section.get("cubicBezier", [])
        + by_section.get("transition", [])
    )

    brand_name = project_name or (f"Project {project_id}" if project_id else "Design System")
    voice_bits: list[str] = []
    if metrics is not None:
        tone = getattr(metrics, "emotional_tone", None)
        if tone is not None and getattr(tone, "primary", None):
            voice_bits.append(str(tone.primary))
        maturity = getattr(metrics, "design_system_maturity", None)
        if maturity:
            voice_bits.append(f"{maturity} token system")
        temp = getattr(metrics, "color_temperature", None)
        if temp:
            voice_bits.append(f"{temp} palette")
    voice = (
        "; ".join(voice_bits)
        if voice_bits
        else "Extracted foundations with honest derive/synth coverage for remaining DTCG types."
    )

    palette_roles: dict[str, str] = {}
    primary = _first_id(colors, "primary", "brand", "base")
    if primary:
        palette_roles["primary"] = primary
    secondary = _first_id([c for c in colors if c != primary], "secondary", "accent")
    if secondary:
        palette_roles["secondary"] = secondary
    text = _first_id(colors, "text", "foreground", "ink")
    if text:
        palette_roles["text"] = text

    typography_voices: dict[str, str] = {}
    heading = _first_id(typography, "heading", "display", "title", "h1")
    if heading:
        typography_voices["heading"] = heading
    body = _first_id([t for t in typography if t != heading], "body", "paragraph", "text")
    if body:
        typography_voices["body"] = body

    materials: list[str] = []
    if shadows:
        materials.append("elevation")
    if gradients:
        materials.append("gradient wash")
    if shape:
        materials.append("surface radius")

    foundations = GuideFoundations(
        colors=colors,
        spacing=sorted(set(spacing)),
        typography=typography,
        shadows=shadows,
        gradients=gradients,
        shape=sorted(set(shape)),
        opacity=sorted(set(opacity)),
        motion=sorted(set(motion)),
    )

    components: list[GuideComponent] = []
    if primary or heading:
        slots = []
        if primary:
            slots.append(
                GuideComponentSlot(name="background", token_ref=primary, css_property="background-color")
            )
        if text:
            slots.append(GuideComponentSlot(name="label", token_ref=text, css_property="color"))
        if heading:
            slots.append(
                GuideComponentSlot(name="type", token_ref=heading, css_property="font")
            )
        components.append(
            GuideComponent(
                id="button.primary",
                name="Primary button",
                description="Illustrative component referencing brand roles — not a DTCG type.",
                slots=slots,
                source="illustrative",
            )
        )
    if shadows:
        components.append(
            GuideComponent(
                id="card.elevated",
                name="Elevated card",
                description="Surface using extracted/synth shadow tokens.",
                slots=[
                    GuideComponentSlot(
                        name="elevation",
                        token_ref=shadows[0],
                        css_property="box-shadow",
                    )
                ],
                source="illustrative",
            )
        )

    applications: list[GuideApplication] = [
        GuideApplication(
            id="css-vars",
            title="CSS custom properties",
            notes="Map foundations to :root variables; group by brand roles when GuidePack is supplied.",
            token_refs=(colors[:3] + spacing[:3]),
            source="illustrative",
        ),
        GuideApplication(
            id="react-theme",
            title="React theme module",
            notes="Theme object grouped by brand palette / typography voices.",
            token_refs=list(palette_roles.values()) + list(typography_voices.values()),
            source="illustrative",
        ),
    ]

    insight_list = list(insights or [])
    if metrics is not None:
        for item in getattr(metrics, "insights", None) or []:
            if isinstance(item, str) and item not in insight_list:
                insight_list.append(item)

    q = f"?project_id={project_id}" if project_id is not None else ""
    exports = GuideExports(
        w3c=f"/api/v1/design-tokens/export/w3c{q}",
        css=f"/api/v1/design-tokens/export/css{q}",
        react=f"/api/v1/design-tokens/export/react{q}",
        tailwind=f"/api/v1/design-tokens/export/tailwind{q}",
        guide_html=f"/api/v1/design-tokens/export/guide-html{q}",
    )

    return GuidePack(
        meta=GuidePackMeta(
            version="1.0.0",
            project_id=project_id,
            title=f"{brand_name} — Design Guide",
            generated_at=datetime.now(UTC).isoformat(),
            token_snapshot_hash=snapshot_hash(token_ids),
            token_ids=token_ids,
            type_coverage=type_coverage,
            source_counts=source_counts,
        ),
        brand=GuideBrand(
            name=brand_name,
            voice=voice,
            palette_roles=palette_roles,
            typography_voices=typography_voices,
            materials=materials,
        ),
        foundations=foundations,
        components=components,
        applications=applications,
        exports=exports,
        insights=insight_list[:12],
    )
