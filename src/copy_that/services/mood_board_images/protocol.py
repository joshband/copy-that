"""Image backend protocol for mood board tiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable

RoutingPolicy = Literal["balanced", "fast", "cheap", "private", "quality"]


@dataclass(frozen=True)
class Availability:
    """Provider readiness for routing."""

    available: bool
    reason: str | None = None
    estimated_latency_ms: float = 15_000.0
    cost_per_image_usd: float = 0.02
    quality: float = 0.7  # 0–1 prior


@dataclass
class ImageResult:
    """Single generated (or collage) tile."""

    url: str
    prompt: str
    revised_prompt: str | None = None
    provider: str = "unknown"
    selection: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class ImageBackend(Protocol):
    """OpenAI-Images-shaped backend used by the policy router."""

    id: str
    kind: Literal["cloud", "local", "collage"]

    def health(self) -> Availability:
        """Return current availability (no heavy network required)."""

    def generate(self, *, prompt: str, size: str, n: int = 1) -> list[ImageResult]:
        """Synchronously generate ``n`` images (call via to_thread when parallel)."""
