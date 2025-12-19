"""Generator registry for TokenGraph exports."""

from __future__ import annotations

from collections.abc import Iterable

from copy_that.generators.plugins.base import BaseGenerator


class GeneratorRegistry:
    """Simple registry mapping generator IDs to their implementations."""

    def __init__(self) -> None:
        self._registry: dict[str, type[BaseGenerator]] = {}

    def register(self, generator_cls: type[BaseGenerator]) -> None:
        """Register a generator class."""
        self._registry[generator_cls.id] = generator_cls

    def get(self, generator_id: str) -> type[BaseGenerator] | None:
        """Retrieve a generator class by id."""
        return self._registry.get(generator_id)

    def available(self) -> Iterable[str]:
        """List registered generator IDs."""
        return self._registry.keys()


generator_registry = GeneratorRegistry()
