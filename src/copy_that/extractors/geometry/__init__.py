"""Geometry extractors (depth + normals)."""

from .optional_runtime import extract_depth_and_normals
from .profile import GeometryProfile

__all__ = ["GeometryProfile", "extract_depth_and_normals"]
