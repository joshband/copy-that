from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ColorToken:
    id: int
    project_id: int
    extraction_job_id: int | None
    library_id: int | None
    role: str | None

    hex: str
    rgb: str
    hsl: str | None
    hsv: str | None
    name: str

    design_intent: str | None
    semantic_names: str | None
    extraction_metadata: str | None
    category: str | None
    confidence: float | None
    harmony: str | None
    harmony_confidence: float | None
    hue_angles: str | None
    temperature: str | None
    saturation_level: str | None
    lightness_level: str | None
    usage: str | None
    count: int | None
    prominence_percentage: float | None
    wcag_contrast_on_white: float | None
    wcag_contrast_on_black: float | None
    wcag_aa_compliant_text: bool | None
    wcag_aaa_compliant_text: bool | None
    wcag_aa_compliant_normal: bool | None
    wcag_aaa_compliant_normal: bool | None
    colorblind_safe: bool | None
    tint_color: str | None
    shade_color: str | None
    tone_color: str | None
    closest_web_safe: str | None
    closest_css_named: str | None
    delta_e_to_dominant: float | None
    is_neutral: bool | None
    background_role: str | None
    foreground_role: str | None
    contrast_category: str | None
    is_accent: bool | None
    state_variants: str | None
    kmeans_cluster_id: int | None
    sam_segmentation_mask: str | None
    clip_embeddings: str | None
    histogram_significance: float | None
    provenance: str | None

    created_at: datetime


@dataclass(frozen=True, slots=True)
class ColorTokenCreate:
    hex: str
    rgb: str
    hsl: str | None
    hsv: str | None
    name: str
    design_intent: str | None
    semantic_names: str | None
    extraction_metadata: str | None
    category: str | None
    confidence: float | None
    harmony: str | None
    temperature: str | None
    saturation_level: str | None
    lightness_level: str | None
    usage: str | None
    count: int | None
    prominence_percentage: float | None
    wcag_contrast_on_white: float | None
    wcag_contrast_on_black: float | None
    wcag_aa_compliant_text: bool | None
    wcag_aaa_compliant_text: bool | None
    wcag_aa_compliant_normal: bool | None
    wcag_aaa_compliant_normal: bool | None
    colorblind_safe: bool | None
    tint_color: str | None
    shade_color: str | None
    tone_color: str | None
    closest_web_safe: str | None
    closest_css_named: str | None
    delta_e_to_dominant: float | None
    is_neutral: bool | None
    background_role: str | None
    foreground_role: str | None
    contrast_category: str | None
    harmony_confidence: float | None = None
    hue_angles: str | None = None
    is_accent: bool | None = None
    state_variants: str | None = None
    kmeans_cluster_id: int | None = None
    sam_segmentation_mask: str | None = None
    clip_embeddings: str | None = None
    histogram_significance: float | None = None
    library_id: int | None = None
    role: str | None = None
    provenance: str | None = None
