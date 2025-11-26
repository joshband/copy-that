"""Shared generator data models decoupled from legacy token stubs."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AggregatedColorToken:
    hex: str
    rgb: str
    name: str
    confidence: float
    harmony: str | None = None
    temperature: str | None = None
    saturation_level: str | None = None
    lightness_level: str | None = None
    semantic_names: dict | None = None
    provenance: dict[str, float] = field(default_factory=dict)
    role: str | None = None

    def add_provenance(self, image_id: str, confidence: float) -> None:
        self.provenance[image_id] = confidence

    def merge_provenance(self, other: "AggregatedColorToken") -> None:
        self.provenance.update(other.provenance)

    def update_from_source(self, source: Any, image_id: str) -> None:
        if getattr(source, "confidence", 0) > self.confidence:
            self.confidence = source.confidence
            self.hex = source.hex
            self.rgb = source.rgb
            self.name = source.name
        self.add_provenance(image_id, getattr(source, "confidence", self.confidence))


@dataclass
class TokenLibrary:
    tokens: list[AggregatedColorToken] = field(default_factory=list)
    statistics: dict = field(default_factory=dict)
    token_type: str = "color"

    def add_token(self, token: AggregatedColorToken) -> None:
        self.tokens.append(token)

    @property
    def stats(self) -> dict:
        """Backward-compatible accessor used by legacy tests."""
        return self.statistics

    def to_dict(self) -> dict:
        return {
            "tokens": [vars(t) for t in self.tokens],
            "statistics": self.statistics,
            "token_type": self.token_type,
        }


@dataclass
class AggregatedSpacingToken:
    value_px: int
    name: str
    confidence: float
    semantic_role: str | None = None
    spacing_type: str | None = None
    scale_position: int | None = None
    base_unit: int | None = None
    grid_aligned: bool | None = None
    responsive_scales: dict[str, int] | None = None
    provenance: dict[str, float] = field(default_factory=dict)
    role: str | None = None
    merged_values: list[int] = field(default_factory=list)

    def add_provenance(self, image_id: str, confidence: float) -> None:
        self.provenance[image_id] = confidence

    def merge_provenance(self, other: "AggregatedSpacingToken") -> None:
        self.provenance.update(other.provenance)

    def update_from_source(self, source: Any, image_id: str) -> None:
        if getattr(source, "value_px", self.value_px) not in self.merged_values:
            self.merged_values.append(getattr(source, "value_px", self.value_px))
        if getattr(source, "confidence", 0) > self.confidence:
            self.confidence = getattr(source, "confidence", self.confidence)
            self.value_px = getattr(source, "value_px", self.value_px)
            self.name = getattr(source, "name", self.name)
        self.add_provenance(image_id, getattr(source, "confidence", self.confidence))

    @property
    def value_rem(self) -> float:
        return round(self.value_px / 16, 4)


@dataclass
class SpacingTokenLibrary:
    tokens: list[AggregatedSpacingToken] = field(default_factory=list)
    statistics: dict = field(default_factory=dict)
    token_type: str = "spacing"

    def to_dict(self) -> dict:
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
