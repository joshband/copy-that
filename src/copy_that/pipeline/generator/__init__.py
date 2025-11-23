"""
Generator module for token output generation.

This module provides the GeneratorAgent for transforming TokenResults
into various output formats including W3C Design Tokens JSON, CSS
Custom Properties, React theme objects, and Tailwind configuration.

Supported Formats:
- w3c: W3C Design Tokens JSON format
- css: CSS Custom Properties
- scss: SCSS variables
- react: React/TypeScript theme object
- tailwind: Tailwind CSS configuration

Components:
- GeneratorAgent: Main agent for multi-format output generation
- OutputFormat: Enum of supported output formats
"""

from copy_that.pipeline.generator.agent import GeneratorAgent, OutputFormat

__all__ = [
    "GeneratorAgent",
    "OutputFormat",
]
