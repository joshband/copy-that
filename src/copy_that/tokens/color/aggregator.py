"""
ColorAggregator - Batch color aggregation and deduplication

Core logic for:
- De-duplicating colors from multiple image extractions using Delta-E
- Tracking provenance (which images contributed each color)
- Generating library statistics
"""

import logging
from collections.abc import Iterator
from dataclasses import dataclass, field

from copy_that.application.color_extractor import ExtractedColorToken
from copy_that.application.color_utils import calculate_delta_e
from copy_that.constants import DEFAULT_DELTA_E_THRESHOLD

logger = logging.getLogger(__name__)


@dataclass
class AggregatedColorToken:
    """A color token with provenance and aggregation metadata"""

    # Original color properties
    hex: str
    rgb: str
    name: str
    confidence: float

    # Optional color properties
    harmony: str | None = None
    temperature: str | None = None
    saturation_level: str | None = None
    lightness_level: str | None = None
    semantic_names: dict | None = None

    # Aggregation metadata
    provenance: dict[str, float] = field(default_factory=dict)  # {"image_0": 0.95, "image_1": 0.88}
    role: str | None = None  # Set during curation: 'primary', 'secondary', etc.

    def add_provenance(self, image_id: str, confidence: float) -> None:
        """Track that this color was found in an image with given confidence"""
        self.provenance[image_id] = confidence

    def merge_provenance(self, other: "AggregatedColorToken") -> None:
        """Merge provenance from another token (during deduplication)"""
        self.provenance.update(other.provenance)

    def update_from_source(self, source: ExtractedColorToken, image_id: str) -> None:
        """Update token properties from a source extraction"""
        # Update to highest confidence version
        if source.confidence > self.confidence:
            self.confidence = source.confidence
            self.hex = source.hex
            self.rgb = source.rgb
            self.name = source.name
            if source.harmony:
                self.harmony = source.harmony
            if source.temperature:
                self.temperature = source.temperature

        # Always track provenance
        self.add_provenance(image_id, source.confidence)


@dataclass
class TokenLibrary:
    """Aggregated, deduplicated token set from an extraction session"""

    tokens: list[AggregatedColorToken] = field(default_factory=list)
    statistics: dict = field(default_factory=dict)
    token_type: str = "color"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "tokens": [
                {
                    "hex": t.hex,
                    "rgb": t.rgb,
                    "name": t.name,
                    "confidence": t.confidence,
                    "role": t.role,
                    "provenance": t.provenance,
                }
                for t in self.tokens
            ],
            "statistics": self.statistics,
            "token_type": self.token_type,
        }


class ColorAggregator:
    """Batch color aggregation using Delta-E deduplication"""

    # Use centralized constant for JND (Just Noticeable Difference)

    def __init__(self, delta_e_threshold: float = DEFAULT_DELTA_E_THRESHOLD) -> None:
        """Initialize with a configurable Delta-E threshold."""
        self.delta_e_threshold = delta_e_threshold

    def deduplicate(self, tokens: list[AggregatedColorToken]) -> list[AggregatedColorToken]:
        """Deduplicate a list of aggregated color tokens using Delta-E matching."""
        deduped: list[AggregatedColorToken] = []

        for token in tokens:
            match = next(
                (
                    existing
                    for existing in deduped
                    if calculate_delta_e(token.hex, existing.hex) < self.delta_e_threshold
                ),
                None,
            )

            if match:
                # Prefer higher-confidence attributes
                if token.confidence > match.confidence:
                    match.confidence = token.confidence
                    match.hex = token.hex
                    match.rgb = token.rgb
                    match.name = token.name
                    match.harmony = token.harmony or match.harmony
                    match.temperature = token.temperature or match.temperature
                    match.saturation_level = token.saturation_level or match.saturation_level
                    match.lightness_level = token.lightness_level or match.lightness_level

                # Track all provenance contributions
                match.merge_provenance(token)
                continue

            deduped.append(
                AggregatedColorToken(
                    hex=token.hex,
                    rgb=token.rgb,
                    name=token.name,
                    confidence=token.confidence,
                    harmony=token.harmony,
                    temperature=token.temperature,
                    saturation_level=token.saturation_level,
                    lightness_level=token.lightness_level,
                    semantic_names=token.semantic_names,
                    provenance=dict(token.provenance),
                    role=token.role,
                )
            )

        return deduped

    @staticmethod
    def aggregate_batch(
        colors_batch: list[list[ExtractedColorToken]],
        delta_e_threshold: float = DEFAULT_DELTA_E_THRESHOLD,
    ) -> TokenLibrary:
        """
        Aggregate colors from multiple image extractions

        Args:
            colors_batch: List of color lists, one per image
            delta_e_threshold: Delta-E threshold for deduplication (lower = stricter)

        Returns:
            TokenLibrary with deduplicated tokens and statistics
        """
        library = TokenLibrary()

        if not colors_batch or all(not colors for colors in colors_batch):
            # Empty batch
            library.statistics = {
                "color_count": 0,
                "image_count": len(colors_batch),
                "avg_confidence": 0.0,
                "min_confidence": 0.0,
                "max_confidence": 0.0,
                "dominant_colors": [],
            }
            return library

        # Flatten and index colors by image
        image_count = len(colors_batch)
        image_index = 0
        for image_colors in colors_batch:
            image_id = f"image_{image_index}"

            for source_color in image_colors:
                # Try to find existing color to merge
                existing_token = ColorAggregator._find_matching_token(
                    source_color,
                    library.tokens,
                    delta_e_threshold,
                )

                if existing_token:
                    # Merge with existing token
                    existing_token.update_from_source(source_color, image_id)
                else:
                    # Create new token
                    new_token = AggregatedColorToken(
                        hex=source_color.hex,
                        rgb=source_color.rgb,
                        name=source_color.name,
                        confidence=source_color.confidence,
                        harmony=source_color.harmony,
                        temperature=source_color.temperature,
                        saturation_level=getattr(source_color, "saturation_level", None),
                        lightness_level=getattr(source_color, "lightness_level", None),
                        semantic_names=getattr(source_color, "semantic_names", None),
                    )
                    new_token.add_provenance(image_id, source_color.confidence)
                    library.tokens.append(new_token)

            image_index += 1

        # Generate statistics
        library.statistics = ColorAggregator._generate_statistics(library.tokens, image_count)

        logger.info(
            f"Aggregated {len(colors_batch)} images into {len(library.tokens)} unique colors"
        )

        return library

    @staticmethod
    def _find_matching_token(
        source: ExtractedColorToken,
        existing_tokens: list[AggregatedColorToken],
        delta_e_threshold: float,
    ) -> AggregatedColorToken | None:
        """
        Find existing token matching source color using Delta-E

        Args:
            source: Source color to match
            existing_tokens: List of existing tokens
            delta_e_threshold: Delta-E threshold for match

        Returns:
            Matching token or None
        """
        for existing in existing_tokens:
            # Calculate Delta-E between source and existing
            delta_e = calculate_delta_e(source.hex, existing.hex)

            if delta_e < delta_e_threshold:
                return existing

        return None

    @staticmethod
    def _generate_statistics(tokens: list[AggregatedColorToken], image_count: int) -> dict:
        """
        Generate library statistics

        Args:
            tokens: Aggregated tokens
            image_count: Number of images in batch

        Returns:
            Statistics dictionary
        """
        if not tokens:
            return {
                "color_count": 0,
                "image_count": image_count,
                "avg_confidence": 0.0,
                "min_confidence": 0.0,
                "max_confidence": 0.0,
                "dominant_colors": [],
            }

        confidences = [t.confidence for t in tokens]
        avg_confidence = sum(confidences) / len(confidences)

        # Find dominant colors (highest confidence)
        sorted_tokens = sorted(tokens, key=lambda t: t.confidence, reverse=True)
        dominant_count = min(5, len(tokens))  # Top 5 colors
        dominant_colors = [t.hex for t in sorted_tokens[:dominant_count]]

        return {
            "color_count": len(tokens),
            "image_count": image_count,
            "avg_confidence": round(avg_confidence, 4),
            "min_confidence": round(min(confidences), 4),
            "max_confidence": round(max(confidences), 4),
            "dominant_colors": dominant_colors,
            "multi_image_colors": len([t for t in tokens if len(t.provenance) > 1]),
        }


class ColorTokenLibrary(TokenLibrary):
    """Aggregated token library specialized for colors."""

    def add_token(self, token: AggregatedColorToken) -> None:
        self.tokens.append(token)

    def __len__(self) -> int:  # pragma: no cover - simple proxy
        return len(self.tokens)

    def __iter__(self) -> Iterator[AggregatedColorToken]:  # pragma: no cover - simple proxy
        return iter(self.tokens)
