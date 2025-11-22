"""
Spacing extraction services.

This module contains AI-powered extraction services for spacing tokens
following the AIColorExtractor pattern.
"""

from .spacing_extractor import (
    AISpacingExtractor,
    extract_spacing,
    extract_spacing_from_file,
)

from .batch_spacing_extractor import (
    BatchSpacingExtractor,
    extract_spacing_batch,
)

from .spacing_utils import (
    px_to_rem,
    rem_to_px,
    px_to_em,
    detect_base_unit,
    detect_scale_system,
    detect_scale_position,
    check_grid_compliance,
    suggest_grid_aligned_value,
    suggest_responsive_scales,
    generate_scale_from_base,
    compute_all_spacing_properties,
    compute_all_spacing_properties_with_metadata,
    calculate_spacing_similarity,
    merge_similar_spacings,
)

__all__ = [
    # Extractors
    "AISpacingExtractor",
    "extract_spacing",
    "extract_spacing_from_file",
    "BatchSpacingExtractor",
    "extract_spacing_batch",

    # Utils
    "px_to_rem",
    "rem_to_px",
    "px_to_em",
    "detect_base_unit",
    "detect_scale_system",
    "detect_scale_position",
    "check_grid_compliance",
    "suggest_grid_aligned_value",
    "suggest_responsive_scales",
    "generate_scale_from_base",
    "compute_all_spacing_properties",
    "compute_all_spacing_properties_with_metadata",
    "calculate_spacing_similarity",
    "merge_similar_spacings",
]
