"""Lazy boundary for geometry's optional deep-CV runtime."""

from __future__ import annotations

from typing import Any, cast

from .geometry_models import OptionalDependencyError
from .profile import GeometryProfile


def extract_depth_and_normals(
    image: Any, *, profile: GeometryProfile = GeometryProfile.AUTO
) -> dict[str, Any]:
    """Load geometry only on demand and report missing extras without breaking core imports."""
    try:
        from .depth_normals import extract_depth_and_normals as extract
    except ImportError as exc:
        raise OptionalDependencyError(
            "Geometry requires optional CV dependencies; install copy-that[cv-deep]."
        ) from exc
    return cast(dict[str, Any], extract(image, profile=profile))
