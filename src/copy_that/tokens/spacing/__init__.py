"""
Spacing token aggregation module

Provides aggregation and deduplication for spacing tokens.
"""

from .aggregator import AggregatedSpacingToken, SpacingAggregator, SpacingTokenLibrary

__all__ = ["SpacingAggregator", "AggregatedSpacingToken", "SpacingTokenLibrary"]
