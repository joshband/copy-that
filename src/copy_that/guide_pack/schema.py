"""Design Guide Pack — product-layer brand guide over DTCG tokens.

Not new DTCG ``$type``s. Components reference token ids; semantics live in
``com.copythat.*`` $extensions on the token graph.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Literal

from pydantic import BaseModel, Field

GuideSource = Literal["extract", "derive", "synth", "preset", "illustrative"]


class GuidePackMeta(BaseModel):
    version: str = "1.0.0"
    project_id: int | None = None
    title: str = "Design Guide Pack"
    generated_at: str | None = None
    token_snapshot_hash: str = Field(
        ...,
        description="Stable hash of sorted token ids + types from the export graph",
    )
    token_ids: list[str] = Field(default_factory=list)
    type_coverage: dict[str, str] = Field(
        default_factory=dict,
        description="Official DTCG type → live|derive|synth|stub from capability map",
    )
    source_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Counts of extract / derive / synth / preset across exported tokens",
    )


class GuideBrand(BaseModel):
    name: str = "Untitled"
    voice: str = ""
    palette_roles: dict[str, str] = Field(
        default_factory=dict,
        description="role → token id (e.g. primary → color.primary)",
    )
    typography_voices: dict[str, str] = Field(
        default_factory=dict,
        description="voice → typography token id",
    )
    materials: list[str] = Field(
        default_factory=list,
        description="Material labels only — not DTCG types",
    )


class GuideFoundations(BaseModel):
    colors: list[str] = Field(default_factory=list)
    spacing: list[str] = Field(default_factory=list)
    typography: list[str] = Field(default_factory=list)
    shadows: list[str] = Field(default_factory=list)
    gradients: list[str] = Field(default_factory=list)
    shape: list[str] = Field(default_factory=list)
    opacity: list[str] = Field(default_factory=list)
    motion: list[str] = Field(default_factory=list)


class GuideComponentSlot(BaseModel):
    name: str
    token_ref: str | None = None
    css_property: str | None = None


class GuideComponent(BaseModel):
    id: str
    name: str
    description: str = ""
    slots: list[GuideComponentSlot] = Field(default_factory=list)
    source: GuideSource = "illustrative"


class GuideApplication(BaseModel):
    id: str
    title: str
    notes: str = ""
    token_refs: list[str] = Field(default_factory=list)
    source: GuideSource = "illustrative"


class GuideExports(BaseModel):
    w3c: str | None = None
    css: str | None = None
    react: str | None = None
    tailwind: str | None = None
    guide_html: str | None = None


class GuidePack(BaseModel):
    """Structured Design Guide Pack companion to W3C token export."""

    meta: GuidePackMeta
    brand: GuideBrand = Field(default_factory=GuideBrand)
    foundations: GuideFoundations = Field(default_factory=GuideFoundations)
    components: list[GuideComponent] = Field(default_factory=list)
    applications: list[GuideApplication] = Field(default_factory=list)
    exports: GuideExports = Field(default_factory=GuideExports)
    insights: list[str] = Field(default_factory=list)

    def to_component_meta(self) -> dict[str, Any]:
        """Derive generator ``component_meta`` for CSS/React/Tailwind grouping."""
        roles = dict(self.brand.palette_roles)
        roles.update(self.brand.typography_voices)
        components: dict[str, Any] = {}
        for comp in self.components:
            slots = {
                slot.name: slot.token_ref
                for slot in comp.slots
                if slot.token_ref
            }
            components[comp.id] = {
                "name": comp.name,
                "slots": slots,
                "source": comp.source,
            }
        return {
            "brand": {
                "name": self.brand.name,
                "voice": self.brand.voice,
                "roles": roles,
                "materials": list(self.brand.materials),
            },
            "foundations": self.foundations.model_dump(),
            "components": components,
            "guide_pack_version": self.meta.version,
            "token_snapshot_hash": self.meta.token_snapshot_hash,
        }


def snapshot_hash(token_ids: list[str]) -> str:
    payload = json.dumps(sorted(token_ids), separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
