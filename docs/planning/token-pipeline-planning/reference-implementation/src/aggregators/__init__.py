"""
Spacing token aggregation services.

This module contains aggregation and deduplication logic for spacing tokens
following the ColorAggregator pattern.
"""

from .spacing_aggregator import (
    SpacingAggregator,
    AggregatedSpacingToken,
    SpacingTokenLibrary,
)

__all__ = [
    "SpacingAggregator",
    "AggregatedSpacingToken",
    "SpacingTokenLibrary",
]
