"""Typography recommendation utilities."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from core.tokens.graph import TokenGraph
from core.tokens.model import Token, TokenType
from core.tokens.repository import TokenRepository
from core.tokens.typography import make_typography_token
from layout import metrics as layout_metrics
from layout.layout_graph import PanelGraph


@dataclass(slots=True)
class TypographyDescriptor:
    """Describes a typography recommendation for a given UI role."""

    role: str
    classification: str
    weight: str
    width: str
    tracking: str
    case_style: str
    sample_families: list[str]
    size: str
    line_height: str


def recommend_typography(
    panel_graph: PanelGraph,
    repo: TokenRepository,
    *,
    color_tokens: Mapping[str, str],
) -> dict[str, TypographyDescriptor]:
    """Create typography tokens for core roles and return their descriptors."""
    if not color_tokens:
        raise ValueError("At least one color token reference is required")

    regularity = layout_metrics.regularity_score(panel_graph)
    density = layout_metrics.density(panel_graph)
    row_count = len(panel_graph.rows())

    descriptors = {
        "headline": _descriptor_for_role(
            "headline", regularity=regularity, density=density, rows=row_count
        ),
        "controlLabel": _descriptor_for_role(
            "controlLabel", regularity=regularity, density=density, rows=row_count
        ),
        "panelCaption": _descriptor_for_role(
            "panelCaption", regularity=regularity, density=density, rows=row_count
        ),
    }

    graph = TokenGraph(repo)

    def _slugify_family(name: str) -> str:
        return name.lower().replace(" ", "-")

    for role, descriptor in descriptors.items():
        token_id = f"token/typography/{role}"
        color_ref = _color_for_role(role, color_tokens)
        family_id = f"token/font/family/{_slugify_family(descriptor.sample_families[0])}"
        size_id = f"token/font/size/{descriptor.size.replace(' ', '').replace('%', 'pct')}"
        line_height_id = (
            f"token/font/lineHeight/{descriptor.line_height.replace(' ', '').replace('%', 'pct')}"
        )

        # Base tokens for family/size/line-height
        graph.add_token(
            Token(
                id=family_id,
                type=TokenType.TYPOGRAPHY,
                value=descriptor.sample_families[0],
                attributes={"role": "fontFamily"},
            )
        )
        graph.add_token(
            Token(
                id=size_id,
                type=TokenType.TYPOGRAPHY,
                value=descriptor.size,
                attributes={"role": "fontSize"},
            )
        )
        graph.add_token(
            Token(
                id=line_height_id,
                type=TokenType.TYPOGRAPHY,
                value=descriptor.line_height,
                attributes={"role": "lineHeight"},
            )
        )
        repo.upsert_token(
            make_typography_token(
                token_id,
                font_family_ref=family_id,
                size_ref=size_id,
                line_height_ref=line_height_id,
                weight_ref=descriptor.weight,
                letter_spacing_ref=descriptor.tracking,
                casing=descriptor.case_style,
                color_ref=color_ref,
                attributes={
                    "role": role,
                    "classification": descriptor.classification,
                    "width": descriptor.width,
                },
            )
        )
    return descriptors


def _descriptor_for_role(
    role: str, *, regularity: float, density: float, rows: int
) -> TypographyDescriptor:
    tall_layout = rows <= 3
    high_density = density > 0.008
    rounded = regularity >= 0.65

    if rounded:
        families = ["Space Grotesk", "Sora", "Circular Std"]
        classification = "geometric-sans"
    elif high_density:
        families = ["IBM Plex Sans", "Eurostile", "Inter"]
        classification = "technical-grotesk"
    else:
        families = ["GT Walsheim", "Avenir Next", "Neue Haas Grotesk"]
        classification = "humanist-sans"

    if role == "headline":
        size = "2rem" if tall_layout or not high_density else "1.75rem"
        line_height = "120%"
        weight = "600" if rounded else "500"
        tracking = "0.01em" if rounded else "0.02em"
        case_style = "title"
        width = "wide" if not high_density else "normal"
    elif role == "controlLabel":
        size = "0.875rem" if not high_density else "0.8125rem"
        line_height = "140%"
        weight = "500" if rounded else "550" if high_density else "500"
        tracking = "0.04em" if high_density else "0.025em"
        case_style = "upper" if high_density else "sentence"
        width = "condensed" if high_density else "normal"
    else:  # panelCaption
        size = "0.75rem"
        line_height = "150%"
        weight = "400"
        tracking = "0.03em"
        case_style = "sentence"
        width = "normal"

    return TypographyDescriptor(
        role=role,
        classification=classification,
        weight=str(weight),
        width=width,
        tracking=tracking,
        case_style=case_style,
        sample_families=families,
        size=size,
        line_height=line_height,
    )


def _color_for_role(role: str, color_tokens: Mapping[str, str]) -> str:
    primary = color_tokens.get("primary")
    accent = color_tokens.get("accent")
    muted = color_tokens.get("muted") or color_tokens.get("secondary")
    fallback = primary or accent or muted
    if fallback is None:
        # copy to list to provide deterministic fallback
        fallback = next(iter(color_tokens.values()))
    if role == "headline":
        return primary or accent or fallback
    if role == "controlLabel":
        return accent or primary or fallback
    return muted or primary or fallback
