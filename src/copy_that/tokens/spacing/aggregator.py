"""
Spacing Aggregator

Batch spacing aggregation using percentage-based deduplication.
Follows the pattern of ColorAggregator from tokens/color/aggregator.py.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from copy_that.application.spacing_models import SpacingToken
from copy_that.application.spacing_utils import (
    calculate_spacing_similarity,
    detect_base_unit,
    detect_scale_system,
)

logger = logging.getLogger(__name__)


@dataclass
class AggregatedSpacingToken:
    """
    A spacing token with provenance and aggregation metadata.

    Follows the pattern of AggregatedColorToken from color/aggregator.py.
    """

    # Core spacing properties
    value_px: int
    name: str
    confidence: float

    # Optional properties
    semantic_role: str | None = None
    spacing_type: str | None = None
    scale_position: int | None = None
    base_unit: int | None = None
    grid_aligned: bool | None = None
    responsive_scales: dict[str, int] | None = None

    # Aggregation metadata
    provenance: dict[str, float] = field(default_factory=dict)  # {"image_0": 0.95, "image_1": 0.88}
    role: str | None = None  # Set during curation: 'primary', 'secondary', etc.
    merged_values: list[int] = field(default_factory=list)  # Original values merged into this

    def add_provenance(self, image_id: str, confidence: float) -> None:
        """Track that this spacing was found in an image with given confidence."""
        self.provenance[image_id] = confidence

    def merge_provenance(self, other: "AggregatedSpacingToken") -> None:
        """Merge provenance from another token (during deduplication)."""
        self.provenance.update(other.provenance)

    def update_from_source(self, source: SpacingToken, image_id: str) -> None:
        """
        Update token properties from a source extraction.

        Args:
            source: Source SpacingToken
            image_id: ID of the source image
        """
        # Track merged values
        if source.value_px not in self.merged_values:
            self.merged_values.append(source.value_px)

        # Update to highest confidence version
        if source.confidence > self.confidence:
            self.confidence = source.confidence
            # Keep average value when merging
            if self.merged_values:
                self.value_px = round(sum(self.merged_values) / len(self.merged_values))
            self.name = source.name

            if source.semantic_role:
                self.semantic_role = source.semantic_role
            if source.grid_aligned is not None:
                self.grid_aligned = source.grid_aligned

        # Always track provenance
        self.add_provenance(image_id, source.confidence)

    @property
    def value_rem(self) -> float:
        """Convert px to rem (assuming 16px base)."""
        return round(self.value_px / 16, 4)


@dataclass
class SpacingTokenLibrary:
    """
    Aggregated, deduplicated spacing token set from an extraction session.

    Follows the pattern of TokenLibrary from color/aggregator.py.
    """

    tokens: list[AggregatedSpacingToken] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)
    token_type: str = "spacing"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "tokens": [
                {
                    "value_px": t.value_px,
                    "value_rem": t.value_rem,
                    "name": t.name,
                    "confidence": t.confidence,
                    "semantic_role": t.semantic_role,
                    "role": t.role,
                    "grid_aligned": t.grid_aligned,
                    "provenance": t.provenance,
                    "merged_values": t.merged_values,
                }
                for t in self.tokens
            ],
            "statistics": self.statistics,
            "token_type": self.token_type,
        }


class SpacingAggregator:
    """
    Batch spacing aggregation using percentage-based deduplication.

    Unlike ColorAggregator which uses Delta-E for perceptual color difference,
    SpacingAggregator uses percentage-based comparison because spacing is
    a single-dimensional value.

    Example:
        >>> tokens_batch = [[token1, token2], [token3, token4]]
        >>> library = SpacingAggregator.aggregate_batch(
        ...     tokens_batch,
        ...     similarity_threshold=10.0  # 10% threshold
        ... )
        >>> print(f"Aggregated to {len(library.tokens)} unique values")
    """

    DEFAULT_SIMILARITY_THRESHOLD = 10.0  # 10% difference threshold

    @staticmethod
    def aggregate_batch(
        spacing_batch: list[list[SpacingToken]],
        similarity_threshold: float | None = None,
    ) -> SpacingTokenLibrary:
        """
        Aggregate spacing tokens from multiple image extractions.

        Args:
            spacing_batch: List of spacing lists, one per image
            similarity_threshold: Percentage threshold for deduplication
                                 (lower = stricter, e.g., 5% vs 15%)

        Returns:
            SpacingTokenLibrary with deduplicated tokens and statistics

        Example:
            >>> # 15px and 16px would be merged at 10% threshold
            >>> # (6.7% difference < 10%)
            >>> library = SpacingAggregator.aggregate_batch(
            ...     [[token_15px], [token_16px]],
            ...     similarity_threshold=10.0
            ... )
        """
        if similarity_threshold is None:
            similarity_threshold = SpacingAggregator.DEFAULT_SIMILARITY_THRESHOLD

        library = SpacingTokenLibrary()

        if not spacing_batch or all(not spacings for spacings in spacing_batch):
            # Empty batch
            library.statistics = {
                "spacing_count": 0,
                "image_count": len(spacing_batch),
                "avg_confidence": 0.0,
                "min_confidence": 0.0,
                "max_confidence": 0.0,
                "scale_system": "unknown",
                "base_unit": 0,
                "grid_compliance": 0.0,
            }
            return library

        # Flatten and index spacings by image
        image_count = len(spacing_batch)
        image_index = 0

        for image_spacings in spacing_batch:
            image_id = f"image_{image_index}"

            for source_spacing in image_spacings:
                # Try to find existing spacing to merge
                existing_token = SpacingAggregator._find_matching_token(
                    source_spacing,
                    library.tokens,
                    similarity_threshold,
                )

                if existing_token:
                    # Merge with existing token
                    existing_token.update_from_source(source_spacing, image_id)
                else:
                    # Create new token
                    new_token = AggregatedSpacingToken(
                        value_px=source_spacing.value_px,
                        name=source_spacing.name,
                        confidence=source_spacing.confidence,
                        semantic_role=source_spacing.semantic_role,
                        spacing_type=source_spacing.spacing_type.value
                        if source_spacing.spacing_type
                        else None,
                        scale_position=source_spacing.scale_position,
                        base_unit=source_spacing.base_unit,
                        grid_aligned=source_spacing.grid_aligned,
                        responsive_scales=source_spacing.responsive_scales,
                        merged_values=[source_spacing.value_px],
                    )
                    new_token.add_provenance(image_id, source_spacing.confidence)
                    library.tokens.append(new_token)

            image_index += 1

        # Sort tokens by value
        library.tokens.sort(key=lambda t: t.value_px)

        # Generate statistics
        library.statistics = SpacingAggregator._generate_statistics(library.tokens, image_count)

        logger.info(
            f"Aggregated {len(spacing_batch)} images into {len(library.tokens)} unique spacing values"
        )

        return library

    @staticmethod
    def _find_matching_token(
        source: SpacingToken,
        existing_tokens: list[AggregatedSpacingToken],
        similarity_threshold: float,
    ) -> AggregatedSpacingToken | None:
        """
        Find existing token matching source spacing using percentage similarity.

        Args:
            source: Source spacing to match
            existing_tokens: List of existing tokens
            similarity_threshold: Percentage threshold for match

        Returns:
            Matching token or None

        Example:
            >>> # With 10% threshold:
            >>> # 16px matches existing 15px (6.7% diff < 10%)
            >>> # 20px does not match 15px (33% diff > 10%)
        """
        for existing in existing_tokens:
            # Calculate percentage similarity
            is_similar, percentage_diff = calculate_spacing_similarity(
                source.value_px, existing.value_px, similarity_threshold
            )

            if is_similar:
                return existing

        return None

    @staticmethod
    def _generate_statistics(
        tokens: list[AggregatedSpacingToken], image_count: int
    ) -> dict[str, Any]:
        """
        Generate library statistics.

        Args:
            tokens: Aggregated tokens
            image_count: Number of images in batch

        Returns:
            Statistics dictionary
        """
        if not tokens:
            return {
                "spacing_count": 0,
                "image_count": image_count,
                "avg_confidence": 0.0,
                "min_confidence": 0.0,
                "max_confidence": 0.0,
                "scale_system": "unknown",
                "base_unit": 0,
                "grid_compliance": 0.0,
                "value_range": {"min": 0, "max": 0},
            }

        # Confidence statistics
        confidences = [t.confidence for t in tokens]
        avg_confidence = sum(confidences) / len(confidences)

        # Value statistics
        values = [t.value_px for t in tokens]
        min_value = min(values)
        max_value = max(values)

        # Scale analysis
        scale_system = detect_scale_system(values)
        base_unit = detect_base_unit(values)

        # Grid compliance
        grid_aligned_count = sum(1 for t in tokens if t.grid_aligned)
        grid_compliance = grid_aligned_count / len(tokens) if tokens else 0

        # Find most common spacing values (highest confidence)
        sorted_tokens = sorted(tokens, key=lambda t: t.confidence, reverse=True)
        common_count = min(5, len(tokens))
        common_values = [t.value_px for t in sorted_tokens[:common_count]]

        return {
            "spacing_count": len(tokens),
            "image_count": image_count,
            "avg_confidence": round(avg_confidence, 4),
            "min_confidence": round(min(confidences), 4),
            "max_confidence": round(max(confidences), 4),
            "scale_system": scale_system,
            "base_unit": base_unit,
            "grid_compliance": round(grid_compliance, 4),
            "value_range": {"min": min_value, "max": max_value},
            "common_values": common_values,
            "multi_image_spacings": len([t for t in tokens if len(t.provenance) > 1]),
            "total_merged": sum(len(t.merged_values) for t in tokens),
        }

    @staticmethod
    def suggest_token_roles(library: SpacingTokenLibrary) -> SpacingTokenLibrary:
        """
        Suggest semantic roles for tokens based on their values.

        Analyzes the token distribution and assigns roles like:
        - xs, sm, md, lg, xl for size-based naming
        - base, small, large for relative naming

        Args:
            library: Library with tokens to annotate

        Returns:
            Updated library with role suggestions
        """
        if not library.tokens:
            return library

        # Sort by value
        sorted_tokens = sorted(library.tokens, key=lambda t: t.value_px)
        num_tokens = len(sorted_tokens)

        # Assign roles based on position in scale
        if num_tokens == 1:
            sorted_tokens[0].role = "base"
        elif num_tokens == 2:
            sorted_tokens[0].role = "small"
            sorted_tokens[1].role = "large"
        elif num_tokens == 3:
            sorted_tokens[0].role = "small"
            sorted_tokens[1].role = "base"
            sorted_tokens[2].role = "large"
        elif num_tokens <= 5:
            roles = ["xs", "sm", "md", "lg", "xl"]
            for i, token in enumerate(sorted_tokens):
                token.role = roles[i] if i < len(roles) else f"size-{i}"
        else:
            # Use numeric scale positions
            roles = ["2xs", "xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl"]
            mid = num_tokens // 2

            for i, token in enumerate(sorted_tokens):
                if i < mid - 2:
                    token.role = roles[max(0, i)]
                elif i == mid - 2:
                    token.role = "sm"
                elif i == mid - 1:
                    token.role = "md"
                elif i == mid:
                    token.role = "lg"
                else:
                    idx = min(i - mid + 5, len(roles) - 1)
                    token.role = roles[idx]

        return library
