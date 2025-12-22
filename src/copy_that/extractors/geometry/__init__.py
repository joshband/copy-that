"""Geometry extractors (depth + normals)."""

from .depth_normals import extract_depth_and_normals
from .profile import GeometryProfile

__all__ = ["GeometryProfile", "extract_depth_and_normals"]
