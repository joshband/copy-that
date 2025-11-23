"""
Pipeline module for token extraction

This module provides the core interfaces and types for the
multi-agent token extraction pipeline with W3C Design Tokens support.

Architecture:
- Agents: Orchestrate pipeline stages (preprocessing, extraction, aggregation, validation, generation)
- Extractors: Handle actual token extraction (wrapped by agents)
- Adapters: Transform between schema layers
- Generators: Output code in various formats

Components:
- types: Core type definitions with W3C support
  - TokenType: Extraction categories (color, spacing, typography, shadow, gradient)
  - W3CTokenType: W3C $type values (color, dimension, fontFamily, etc.)
  - TokenResult: Extraction results with W3C fields (path, description, reference, extensions)
  - PipelineTask: Task definitions
  - ProcessedImage: Image metadata
- interfaces: Abstract base classes (BasePipelineAgent)
- exceptions: Pipeline exception classes

W3C Design Tokens Format:
https://design-tokens.github.io/community-group/format/
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
    W3CTokenType,
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
