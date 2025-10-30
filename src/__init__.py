"""
Copy That - Generative UI Design System Engine

This package provides tools for analyzing reference images and generating
complete design systems with parametric component generation.
"""

__version__ = "0.1.0"
__author__ = "Copy That Team"

from . import visual_dna
from . import pattern_detector
from . import style_rules

__all__ = ["visual_dna", "pattern_detector", "style_rules"]
