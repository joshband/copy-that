"""Compatibility shim for typography extraction."""

from __future__ import annotations

from copy_that.application.typography_extractor import (
    AITypographyExtractor,
    ExtractedTypographyToken,
    TypographyExtractionResult,
    extract_typography,
    extract_typography_from_file,
)

__all__ = [
    "AITypographyExtractor",
    "ExtractedTypographyToken",
    "TypographyExtractionResult",
    "extract_typography",
    "extract_typography_from_file",
]
