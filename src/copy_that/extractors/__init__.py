"""Modular extractor registry - single source of truth for all extractors.

This enables zero coupling: extractors are completely independent modules
that are registered here. Services use get_extractor() to access them.
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
    """
    if name not in _REGISTRY:
        raise ValueError(f"Unknown extractor: {name}. Available: {list(_REGISTRY.keys())}")
    return _REGISTRY[name]()


# Lazy registration - import on demand
def _register_all() -> None:
    """Register all available extractors."""
    try:
        from copy_that.extractors.color.extractor import ColorExtractor

        register_extractor("color", ColorExtractor)
    except ImportError as e:
        logger.warning(f"Failed to register color extractor: {e}")

    try:
        from copy_that.extractors.spacing.extractor import SpacingExtractor

        register_extractor("spacing", SpacingExtractor)
    except ImportError as e:
        logger.warning(f"Failed to register spacing extractor: {e}")

    try:
        from copy_that.extractors.typography.ai_extractor import AITypographyExtractor

        register_extractor("typography", AITypographyExtractor)
    except ImportError as e:
        logger.warning(f"Failed to register typography extractor: {e}")

    try:
        from copy_that.extractors.shadow.extractor import ShadowExtractor

        register_extractor("shadow", ShadowExtractor)
    except ImportError as e:
        logger.warning(f"Failed to register shadow extractor: {e}")


# Auto-register on module import
_register_all()

__all__ = ["get_extractor", "register_extractor"]
