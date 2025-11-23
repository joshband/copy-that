"""
Aggregation module for token deduplication and provenance tracking.

This module provides:
- AggregationAgent: Orchestrates deduplication and provenance tracking
- ColorDeduplicator: Deduplicates similar colors using Delta-E comparison
- ProvenanceTracker: Tracks source images for each token
- ProvenanceRecord: Record of provenance information
"""

from copy_that.pipeline.aggregation.agent import AggregationAgent
from copy_that.pipeline.aggregation.deduplicator import ColorDeduplicator
from copy_that.pipeline.aggregation.provenance import ProvenanceRecord, ProvenanceTracker

__all__ = [
    "AggregationAgent",
    "ColorDeduplicator",
    "ProvenanceTracker",
    "ProvenanceRecord",
]
