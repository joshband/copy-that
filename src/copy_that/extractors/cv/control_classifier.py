"""Heuristic control classifier with a model-ready interface."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, cast

from .primitives import Circle, Rectangle


class ControlType(str, Enum):
    KNOB = "knob"
    BUTTON = "button"
    SWITCH = "switch"
    FADER = "fader"
    INDICATOR = "indicator"
    DECORATIVE = "decorative"


@dataclass(slots=True)
class ControlCandidate:
    primitive: Any
    bbox: tuple[int, int, int, int]


@dataclass(slots=True)
class ControlInstance:
    control_type: ControlType
    bbox: tuple[int, int, int, int]
    metadata: dict[str, Any]


class ControlClassifier:
    """Classify knobs/buttons/switches; placeholder for future ML model."""

    def __init__(self, model: Any | None = None) -> None:
        self.model = model

    def classify(
        self, candidates: list[ControlCandidate], image: Any | None = None
    ) -> list[ControlInstance]:
        if self.model:
            return cast(list[ControlInstance], self.model.classify(candidates, image))
        return [self._heuristic_classify(candidate) for candidate in candidates]

    def _heuristic_classify(self, candidate: ControlCandidate) -> ControlInstance:
        primitive = candidate.primitive
        bbox = candidate.bbox
        metadata: dict[str, Any]
        if isinstance(primitive, Circle):
            control_type = ControlType.KNOB
            metadata = {"radius": primitive.radius}
        elif isinstance(primitive, Rectangle):
            aspect_ratio = primitive.width / max(primitive.height, 1)
            if aspect_ratio > 3:
                control_type = ControlType.FADER
            elif aspect_ratio < 0.5:
                control_type = ControlType.SWITCH
            else:
                control_type = ControlType.BUTTON
            metadata = {"aspect_ratio": aspect_ratio}
        else:
            control_type = ControlType.DECORATIVE
            metadata = {}
        return ControlInstance(control_type=control_type, bbox=bbox, metadata=metadata)
