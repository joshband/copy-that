"""Shared utilities for API routers."""

import base64
import math
import os
from typing import Any

from fastapi import HTTPException, status


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


def enforce_payload_size(
    image_base64: str | None, *, max_bytes: int | None = None, field_name: str = "image_base64"
) -> None:
    """
    Enforce a maximum payload size for base64 inputs to prevent OOM.

    Args:
        image_base64: The base64 string (with or without data URL prefix)
        max_bytes: Maximum allowed raw bytes (after decoding). Defaults from env or 5MB.
        field_name: Field name for error context
    """
    if not image_base64:
        return

    max_bytes = max_bytes or int(os.getenv("EXTRACTION_MAX_IMAGE_BYTES", "5242880"))  # 5MB default

    # Strip data URL prefix if present
    b64 = image_base64.split(",", 1)[1] if "," in image_base64 else image_base64
    try:
        decoded_len = len(base64.b64decode(b64, validate=True))
    except Exception:
        decoded_len = len(b64) * 3 // 4  # fallback estimation

    if decoded_len > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"{field_name} exceeds maximum size of {max_bytes} bytes",
        )
