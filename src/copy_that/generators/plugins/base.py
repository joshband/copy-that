"""Base interface for deterministic token generators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any


class BaseGenerator(ABC):
    """Abstract base class for generator plugins."""

    #: Unique identifier for the generator (e.g., "react", "css")
    id: str = "base"
    #: Human-friendly label
    label: str = "Base Generator"
    #: Short description of what the generator produces
    description: str = ""

    def __init__(
        self, tokens: Mapping[str, Any], component_meta: Mapping[str, Any] | None = None
    ) -> None:
        # Tokens are expected to be a W3C/DTCG-style section map (already flattened for HTTP use).
        self.tokens = tokens
        # Component semantics/anatomy metadata supplied by the caller (optional).
        self.component_meta = component_meta or {}

    @abstractmethod
    def generate(self) -> str:
        """Produce a deterministic string representation from the provided tokens + metadata."""
        raise NotImplementedError
