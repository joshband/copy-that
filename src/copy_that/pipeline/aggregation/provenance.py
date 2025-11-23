"""
Provenance tracking for token aggregation.

This module provides functionality to track which source images
contributed to each token during the aggregation pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from copy_that.pipeline import TokenResult


@dataclass
class ProvenanceRecord:
    """Record of a single source contribution to a token."""

    image_id: str
    confidence: float
    timestamp: datetime
    metadata: dict[str, Any] | None = None


class ProvenanceTracker:
    """
    Tracks which images contributed to each token.

    Maintains provenance records for tokens and can calculate
    weighted confidence scores based on multiple extractions.
    """

    def __init__(self) -> None:
        """Initialize empty provenance tracker."""
        self._provenance: dict[str, list[ProvenanceRecord]] = {}

    def add_provenance(self, token_id: str, record: ProvenanceRecord) -> None:
        """
        Add provenance record for a token.

        Skip duplicate image_ids for the same token.

        Args:
            token_id: The token identifier.
            record: The provenance record to add.
        """
        if token_id not in self._provenance:
            self._provenance[token_id] = []

        # Skip duplicate image_ids
        existing_image_ids = {r.image_id for r in self._provenance[token_id]}
        if record.image_id not in existing_image_ids:
            self._provenance[token_id].append(record)

    def get_source_images(self, token_id: str) -> list[str]:
        """
        Get list of source image IDs for a token.

        Args:
            token_id: The token identifier.

        Returns:
            List of image IDs that contributed to this token.
        """
        if token_id not in self._provenance:
            return []
        return [record.image_id for record in self._provenance[token_id]]

    def get_tracked_token_ids(self) -> list[str]:
        """
        Get all tracked token IDs.

        Returns:
            List of all token IDs being tracked.
        """
        return list(self._provenance.keys())

    def get_provenance_records(self, token_id: str) -> list[ProvenanceRecord]:
        """
        Get all provenance records for a token.

        Args:
            token_id: The token identifier.

        Returns:
            List of provenance records for the token.
        """
        return self._provenance.get(token_id, [])

    def calculate_weighted_confidence(self, token_id: str) -> float:
        """
        Calculate weighted confidence for a token.

        Formula: min(1.0, sum(confidence) * (1 + 0.1 * (count - 1)))

        More sources = higher confidence, capped at 1.0.

        Args:
            token_id: The token identifier.

        Returns:
            Weighted confidence score between 0.0 and 1.0.
        """
        records = self._provenance.get(token_id, [])
        if not records:
            return 0.0

        total_confidence = sum(record.confidence for record in records)
        count = len(records)
        boost_factor = 1 + 0.1 * (count - 1)

        return min(1.0, total_confidence * boost_factor)

    def merge_provenance(self, target_id: str, source_id: str) -> None:
        """
        Merge provenance from source to target token.

        All provenance records from source are added to target,
        skipping duplicates.

        Args:
            target_id: The target token identifier.
            source_id: The source token identifier.
        """
        if source_id not in self._provenance:
            return

        for record in self._provenance[source_id]:
            self.add_provenance(target_id, record)

    def apply_to_token(self, token_id: str, token: TokenResult) -> TokenResult:
        """
        Apply provenance to token's extensions field.

        Adds com.copythat.provenance with sources and weighted_confidence.
        Preserves existing extensions.

        Args:
            token_id: The token identifier.
            token: The token to apply provenance to.

        Returns:
            Updated token with provenance in extensions.
        """
        source_images = self.get_source_images(token_id)
        weighted_confidence = self.calculate_weighted_confidence(token_id)

        # Preserve existing extensions
        extensions = dict(token.extensions) if token.extensions else {}

        # Add provenance data
        extensions["com.copythat.provenance"] = {
            "sources": source_images,
            "weighted_confidence": weighted_confidence,
        }

        # Create updated token with new extensions
        return token.model_copy(update={"extensions": extensions})

    def clear_provenance(self, token_id: str) -> None:
        """
        Clear provenance for a token.

        Args:
            token_id: The token identifier to clear.
        """
        if token_id in self._provenance:
            del self._provenance[token_id]

    def get_all_source_images(self) -> list[str]:
        """
        Get all unique source images across all tokens.

        Returns:
            List of unique image IDs from all tracked tokens.
        """
        all_images: set[str] = set()
        for records in self._provenance.values():
            for record in records:
                all_images.add(record.image_id)
        return list(all_images)
