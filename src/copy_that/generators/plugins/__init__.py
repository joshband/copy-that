"""Lightweight generator plugin registry for TokenGraph-based exports."""

from copy_that.generators.plugins.base import BaseGenerator
from copy_that.generators.plugins.css import CSSGenerator
from copy_that.generators.plugins.react import ReactGenerator
from copy_that.generators.plugins.registry import generator_registry

# Register built-in generators
generator_registry.register(CSSGenerator)
generator_registry.register(ReactGenerator)

__all__ = ["BaseGenerator", "CSSGenerator", "ReactGenerator", "generator_registry"]
