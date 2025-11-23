"""
Pipeline exceptions module

Contains exception classes for the token extraction pipeline:
- PipelineError: Base exception for all pipeline errors
- PreprocessingError: Errors during image preprocessing
- ExtractionError: Errors during token extraction
- AggregationError: Errors during token aggregation
- ValidationError: Errors during token validation
- GenerationError: Errors during code/output generation
"""

from typing import Any


class PipelineError(Exception):
    """
    Base exception for all pipeline-related errors.

    Provides a consistent interface for error handling with
    optional details for debugging and logging.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """
        Initialize the pipeline error.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        """Return the error message."""
        return self.message

    def __repr__(self) -> str:
        """Return a detailed representation of the error."""
        if self.details:
            return f"{self.__class__.__name__}({self.message!r}, details={self.details!r})"
        return f"{self.__class__.__name__}({self.message!r})"


class PreprocessingError(PipelineError):
    """
    Exception raised during image preprocessing.

    Indicates failures in image loading, format conversion,
    resizing, or other preprocessing operations.
    """

    pass


class ExtractionError(PipelineError):
    """
    Exception raised during token extraction.

    Indicates failures in AI model calls, response parsing,
    or token identification from images.
    """

    pass


class AggregationError(PipelineError):
    """
    Exception raised during token aggregation.

    Indicates failures in merging tokens from multiple sources,
    deduplication, or conflict resolution.
    """

    pass


class ValidationError(PipelineError):
    """
    Exception raised during token validation.

    Indicates that extracted or aggregated tokens fail
    validation rules or schema requirements.
    """

    pass


class GenerationError(PipelineError):
    """
    Exception raised during output generation.

    Indicates failures in generating export formats like
    CSS, W3C tokens, React components, etc.
    """

    pass
