"""Transport-neutral extraction artifact data models."""

import math
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ArtifactImage(BaseModel):
    """Base64-encoded image artifact from a pipeline stage."""

    type: str = Field(..., description="Artifact type label (overlay, mask, etc.)")
    mime: str = Field("image/png", description="Image MIME type")
    base64: str = Field(..., description="Base64 image payload, no data URL prefix")
    confidence: float | None = Field(None, ge=0, le=1, description="Confidence score")
    stage: str | None = Field(None, description="Pipeline stage identifier")
    description: str | None = Field(None, description="Human-readable description")

    model_config = ConfigDict(from_attributes=True)


class ArtifactJson(BaseModel):
    """Structured JSON artifact from a pipeline stage."""

    type: str = Field(..., description="Artifact type label (histogram, matrix, etc.)")
    payload: dict[str, Any] = Field(..., description="Structured artifact payload")
    confidence: float | None = Field(None, ge=0, le=1, description="Confidence score")
    stage: str | None = Field(None, description="Pipeline stage identifier")

    model_config = ConfigDict(from_attributes=True)


class ArtifactBundle(BaseModel):
    """Unified artifact bundle for API responses and SSE events."""

    images: list[ArtifactImage] = Field(default_factory=list, description="Image artifacts")
    json_: list[ArtifactJson] = Field(
        default_factory=list,
        alias="json",
        description="JSON artifacts",
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


def sanitize_json_value(value: Any) -> Any:
    """Replace NaN/Inf floats for JSON serialization.

    Recursively processes dictionaries and lists to ensure all float values
    are valid for JSON encoding (replaces NaN and Inf with None).

    Args:
        value: Any value to sanitize

    Returns:
        Sanitized value with NaN/Inf replaced by None
    """
    if isinstance(value, dict):
        return {k: sanitize_json_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_json_value(v) for v in value]
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def sanitize_numbers(obj: Any) -> Any:
    """Recursively replace NaN/inf with None so JSON is valid.

    Similar to sanitize_json_value but with explicit isfinite check.
    Processes floats, dicts, and lists recursively.

    Args:
        obj: Any value to sanitize

    Returns:
        Sanitized value with non-finite floats replaced by None
    """
    if isinstance(obj, float):
        if not math.isfinite(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: sanitize_numbers(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_numbers(v) for v in obj]
    return obj
