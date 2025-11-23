"""Extraction pipeline module.

Provides ExtractionAgent for extracting design tokens from images
using Claude Tool Use with configurable schemas.
"""

from copy_that.pipeline.extraction.agent import ExtractionAgent
from copy_that.pipeline.extraction.prompts import (
    get_extraction_prompt,
    get_system_prompt,
    PROMPT_REGISTRY,
)
from copy_that.pipeline.extraction.schemas import (
    SCHEMA_REGISTRY,
    BaseExtractionSchema,
    ColorExtractionSchema,
    GradientExtractionSchema,
    get_all_schemas,
    get_tool_schema,
    ShadowExtractionSchema,
    SpacingExtractionSchema,
    TypographyExtractionSchema,
    validate_extraction_result,
)

__all__ = [
    # Agent
    "ExtractionAgent",
    # Schemas
    "SCHEMA_REGISTRY",
    "BaseExtractionSchema",
    "ColorExtractionSchema",
    "SpacingExtractionSchema",
    "TypographyExtractionSchema",
    "ShadowExtractionSchema",
    "GradientExtractionSchema",
    "get_tool_schema",
    "get_all_schemas",
    "validate_extraction_result",
    # Prompts
    "PROMPT_REGISTRY",
    "get_extraction_prompt",
    "get_system_prompt",
]
