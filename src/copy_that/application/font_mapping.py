from __future__ import annotations

from typing import TypedDict


class FontFamilyProfile(TypedDict, total=False):
    category: str
    primary_traits: list[str]
    recommended_contexts: list[str]
    google_font_family: str


FONT_PROFILES: dict[str, FontFamilyProfile] = {
    "geometric_sans": {
        "category": "Geometric Sans",
        "primary_traits": ["Innovation", "Precision", "Tech-forward"],
        "recommended_contexts": ["Modern", "Minimalist", "Technical"],
        "google_font_family": "Montserrat",
    },
    "humanist_sans": {
        "category": "Humanist Sans",
        "primary_traits": ["Approachable", "Warm", "Friendly"],
        "recommended_contexts": ["Organic", "Warm palettes", "Accessible"],
        "google_font_family": "Work Sans",
    },
    "serif": {
        "category": "Serif",
        "primary_traits": ["Elegant", "Refined", "Editorial"],
        "recommended_contexts": ["Luxury", "Editorial", "Narrative"],
        "google_font_family": "Merriweather",
    },
    "slab_serif": {
        "category": "Slab Serif",
        "primary_traits": ["Bold", "Confident", "Brutalist"],
        "recommended_contexts": ["Brutalist", "Poster", "Brand"],
        "google_font_family": "Roboto Slab",
    },
    "display": {
        "category": "Display",
        "primary_traits": ["Playful", "Expressive"],
        "recommended_contexts": ["Hero", "Poster", "Playful"],
        "google_font_family": "Bebas Neue",
    },
}

STYLE_TO_FONT_CATEGORY: dict[str, str] = {
    "minimalist": "geometric_sans",
    "technical": "geometric_sans",
    "elegant": "serif",
    "brutalist": "slab_serif",
    "playful": "display",
}


def font_category_for_style(style: str) -> str:
    return STYLE_TO_FONT_CATEGORY.get(style, "humanist_sans")
