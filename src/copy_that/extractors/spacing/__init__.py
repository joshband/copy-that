"""Spacing token extraction modules."""

# Note: Importing adapters, orchestrator, and base for new multi-extractor system
# Old SpacingExtractor has import issues, use adapters instead

from .adapters import CVSpacingExtractorAdapter
from .base import ExtractionResult, SpacingExtractorProtocol
from .models import SpacingToken
from .orchestrator import SpacingExtractionOrchestrator

__all__ = [
    "CVSpacingExtractorAdapter",
    "ExtractionResult",
    "SpacingExtractorProtocol",
    "SpacingToken",
    "SpacingExtractionOrchestrator",
]
