"""Modular extractor registry - single source of truth for all extractors.

This enables zero coupling: extractors are completely independent modules
that are registered here. Services use get_extractor() to access them.

DTCG Format 2025.10 coverage: live extractors for color/spacing/typography/shadow/
gradient; derive for border/strokeStyle/number(opacity)/dimension/fontFamily/
fontWeight/duration/cubicBezier/transition. See ``dtcg_capability.py``.

Multi-extractor orchestration (Phase 2.5) is exposed via API ``/extract/multi``
endpoints, not via ``get_extractor()``. Registry entries for spacing/typography/
shadow are zero-arg single extractors (adapters or legacy classes) suitable for
``get_extractor(name)`` construction.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from copy_that.extractors.color.extractor import ColorExtractor
    from copy_that.extractors.color.openai_extractor import OpenAIColorExtractor
    from copy_that.extractors.shadow.extractor import ShadowExtractor
    from copy_that.extractors.spacing.extractor import SpacingExtractor
    from copy_that.extractors.typography.ai_extractor import AITypographyExtractor

logger = logging.getLogger(__name__)

# Registry of available extractors
_REGISTRY: dict[str, type] = {}


def register_extractor(name: str, extractor_class: type) -> None:
    """Register an extractor in the global registry."""
    _REGISTRY[name] = extractor_class
    logger.debug(f"Registered extractor: {name}")


def get_extractor(name: str):
    """Get an extractor by name from the registry.

    Usage:
        extractor = get_extractor("color")
        tokens = await extractor.extract(image_data)

    Note: ``get_extractor("color")`` remains the legacy single-extractor path.
    Multi-extract goes through API ``/{type}/extract/multi``.
    """
    if name not in _REGISTRY:
        raise ValueError(f"Unknown extractor: {name}. Available: {list(_REGISTRY.keys())}")
    return _REGISTRY[name]()


def list_registered_extractors() -> list[str]:
    """Return sorted extractor names currently registered."""
    return sorted(_REGISTRY)


# Lazy registration - import on demand
def _register_all() -> None:
    """Register all available extractors."""
    try:
        from copy_that.application.color_extractor import AIColorExtractor as ColorExtractor

        register_extractor("color", ColorExtractor)
    except ImportError as e:
        logger.warning(f"Failed to register color extractor: {e}")

    try:
        from copy_that.extractors.spacing.adapters import CVSpacingExtractorAdapter

        # Zero-arg CV adapter — do NOT register SpacingExtractionOrchestrator
        # (requires extractors=...). Multi path: POST /api/v1/spacing/extract/multi
        register_extractor("spacing", CVSpacingExtractorAdapter)
        register_extractor("spacing_cv", CVSpacingExtractorAdapter)
    except ImportError as e:
        logger.warning(f"Failed to register spacing extractor: {e}")

    try:
        from copy_that.extractors.typography.adapters import CVTypographyExtractorAdapter
        from copy_that.extractors.typography.ai_extractor import AITypographyExtractor

        register_extractor("typography", AITypographyExtractor)
        register_extractor("typography_cv", CVTypographyExtractorAdapter)
    except ImportError as e:
        logger.warning(f"Failed to register typography extractor: {e}")

    try:
        from copy_that.extractors.shadow.adapters import CVShadowExtractorAdapter
        from copy_that.extractors.shadow.extractor import ShadowExtractor

        register_extractor("shadow", ShadowExtractor)
        register_extractor("shadow_cv", CVShadowExtractorAdapter)
    except ImportError as e:
        logger.warning(f"Failed to register shadow extractor: {e}")

    # Phase 1–3: derive extractors + stubs for remaining DTCG types
    try:
        from copy_that.extractors.border_derive import BorderDeriveExtractor

        register_extractor("border", BorderDeriveExtractor)
    except ImportError as e:
        logger.warning(f"Failed to register border derive extractor: {e}")

    try:
        from copy_that.extractors.dimension_derive import DimensionDeriveExtractor
        from copy_that.extractors.font_atoms_derive import (
            FontFamilyDeriveExtractor,
            FontWeightDeriveExtractor,
        )
        from copy_that.extractors.opacity_extract import OpacityNumberExtractor
        from copy_that.extractors.stroke_style_derive import StrokeStyleDeriveExtractor

        register_extractor("dimension", DimensionDeriveExtractor)
        register_extractor("fontFamily", FontFamilyDeriveExtractor)
        register_extractor("fontWeight", FontWeightDeriveExtractor)
        register_extractor("number", OpacityNumberExtractor)
        register_extractor("strokeStyle", StrokeStyleDeriveExtractor)
    except ImportError as e:
        logger.warning(f"Failed to register Phase 2–3 derive extractors: {e}")

    try:
        from copy_that.extractors.gradient_extract import GradientExtractor

        register_extractor("gradient", GradientExtractor)
    except ImportError as e:
        logger.warning(f"Failed to register gradient extractor: {e}")

    try:
        from copy_that.extractors.motion_extract import (
            CubicBezierExtractor,
            DurationExtractor,
            TransitionExtractor,
        )

        register_extractor("duration", DurationExtractor)
        register_extractor("cubicBezier", CubicBezierExtractor)
        register_extractor("transition", TransitionExtractor)
    except ImportError as e:
        logger.warning(f"Failed to register Phase 5 motion extractors: {e}")


# Auto-register on module import
_register_all()

__all__ = ["get_extractor", "register_extractor", "list_registered_extractors"]
