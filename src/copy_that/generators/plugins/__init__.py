"""Lightweight generator plugin registry for TokenGraph-based exports."""

from copy_that.generators.plugins.base import BaseGenerator
from copy_that.generators.plugins.css import CSSGenerator
from copy_that.generators.plugins.react import ReactGenerator
from copy_that.generators.plugins.registry import generator_registry
from copy_that.generators.plugins.tailwind import TailwindGenerator

# Register built-in generators
generator_registry.register(CSSGenerator)
generator_registry.register(ReactGenerator)
generator_registry.register(TailwindGenerator)

__all__ = [
    "BaseGenerator",
    "CSSGenerator",
    "ReactGenerator",
    "TailwindGenerator",
    "generator_registry",
]
