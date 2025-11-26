"""
Pipeline module for token extraction (legacy)

This package is deprecated in favor of the token-graph + panel pipeline
(`core.tokens.*`, `cv_pipeline.*`, `layout.*`, `typography.*`, `pipeline/panel_to_tokens.py`).
New work should target the token graph APIs; the legacy agents/orchestrators will be removed
once downstream call sites are migrated. See docs/architecture/legacy_pipeline_retirement.md.
"""

from __future__ import annotations

import warnings

from copy_that.pipeline.exceptions import (
    AggregationError,
    ExtractionError,
    GenerationError,
    PipelineError,
    PreprocessingError,
    ValidationError,
)
from copy_that.pipeline.interfaces import BasePipelineAgent
from copy_that.pipeline.types import (
    PipelineTask,
    ProcessedImage,
    TokenResult,
    TokenType,
    W3CTokenType,
)

warnings.warn(
    "copy_that.pipeline is legacy and will be removed after migration to the token graph pipeline.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    # Types
    "TokenType",
    "W3CTokenType",
    "TokenResult",
    "PipelineTask",
    "ProcessedImage",
    # Interfaces
    "BasePipelineAgent",
    # Exceptions
    "PipelineError",
    "PreprocessingError",
    "ExtractionError",
    "AggregationError",
    "ValidationError",
    "GenerationError",
]
