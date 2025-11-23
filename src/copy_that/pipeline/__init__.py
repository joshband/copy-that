"""
Pipeline module for token extraction

This module provides the core interfaces and types for the
multi-agent token extraction pipeline.

Components:
- types: Core type definitions (TokenType, TokenResult, PipelineTask, ProcessedImage)
- interfaces: Abstract base classes (BasePipelineAgent)
- exceptions: Pipeline exception classes
"""

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
)

__all__ = [
    # Types
    "TokenType",
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
