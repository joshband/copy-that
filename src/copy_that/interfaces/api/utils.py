"""Shared utilities for API routers."""

import base64
import os

from fastapi import HTTPException, status

from copy_that.services.artifact_models import (
    sanitize_json_value as sanitize_json_value,
)
from copy_that.services.artifact_models import (
    sanitize_numbers as sanitize_numbers,
)


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
