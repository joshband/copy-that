"""Temporary shim to keep legacy imports alive while migrating to token graph."""

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
        # minimal update logic; prefer token graph for new code
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

    def to_dict(self) -> dict:
        return {
            "tokens": [vars(t) for t in self.tokens],
            "statistics": self.statistics,
            "token_type": self.token_type,
        }


class ColorAggregator:
    """Legacy aggregator stub; replace with token graph utilities."""

    @staticmethod
    def aggregate_colors(tokens: list[Any], delta_e_threshold: float = 3.0) -> TokenLibrary:  # noqa: ARG004
        # Minimal pass-through; real dedupe should live in token graph.
        agg_tokens = []
        for tok in tokens:
            agg_tokens.append(
                AggregatedColorToken(
                    hex=getattr(tok, "hex", ""),
                    rgb=getattr(tok, "rgb", ""),
                    name=getattr(tok, "name", ""),
                    confidence=getattr(tok, "confidence", 0.0),
                )
            )
        return TokenLibrary(tokens=agg_tokens, statistics={"count": len(agg_tokens)})
