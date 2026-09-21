"""Validators for API requests, including image validation."""

import base64
import binascii
import io
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Configuration
MAX_IMAGE_SIZE_MB = 10
MAX_IMAGE_DIMENSION = 4096
MIN_IMAGE_DIMENSION = 16


def validate_image_size(data: str, max_mb: int = MAX_IMAGE_SIZE_MB) -> bytes:
    """Validate base64 image size doesn't exceed limit.

    Args:
        data: Base64 encoded image data
        max_mb: Maximum allowed size in megabytes

    Returns:
        Decoded image bytes

    Raises:
        ValueError: If image exceeds size limit or is invalid base64
    """
    try:
        decoded = base64.b64decode(data)
    except binascii.Error as e:
        raise ValueError("Invalid base64 image data") from e

    size_mb = len(decoded) / (1024 * 1024)
    if size_mb > max_mb:
        raise ValueError(f"Image exceeds {max_mb}MB limit ({size_mb:.1f}MB provided)")

    return decoded


def validate_image_dimensions(
    image_bytes: bytes,
    max_dim: int = MAX_IMAGE_DIMENSION,
    min_dim: int = MIN_IMAGE_DIMENSION,
) -> None:
    """Validate image dimensions are within allowed bounds.

    Args:
        image_bytes: Raw image data (bytes)
        max_dim: Maximum allowed width/height in pixels
        min_dim: Minimum allowed width/height in pixels

    Raises:
        ValueError: If dimensions are invalid
    """
    try:
        from PIL import Image
    except ImportError:
        logger.warning("PIL not available; skipping dimension validation")
        return

    try:
        img = Image.open(io.BytesIO(image_bytes))
    except OSError as e:
        raise ValueError("Unable to decode image - may be corrupted") from e

    width, height = img.size

    if width < min_dim or height < min_dim:
        raise ValueError(
            f"Image dimensions too small (minimum {min_dim}x{min_dim}, got {width}x{height})"
        )

    if width > max_dim or height > max_dim:
        raise ValueError(
            f"Image dimensions too large (maximum {max_dim}x{max_dim}, got {width}x{height})"
        )


def validate_base64_image(
    data: str,
    max_mb: int = MAX_IMAGE_SIZE_MB,
    max_dim: int = MAX_IMAGE_DIMENSION,
    min_dim: int = MIN_IMAGE_DIMENSION,
) -> bytes:
    """Validate base64 image comprehensively (size, dimensions, format).

    This is the main validation function to use before processing images.

    Args:
        data: Base64 encoded image data
        max_mb: Maximum allowed size in megabytes
        max_dim: Maximum allowed width/height in pixels
        min_dim: Minimum allowed width/height in pixels

    Returns:
        Decoded image bytes (validated)

    Raises:
        ValueError: If image fails any validation
    """
    # Validate size first (cheaper operation)
    decoded = validate_image_size(data, max_mb=max_mb)

    # Then validate dimensions (requires PIL)
    validate_image_dimensions(decoded, max_dim=max_dim, min_dim=min_dim)

    return decoded


def validate_project_id(project_id: Any) -> None:
    """Validate that project_id is a valid positive integer.

    Args:
        project_id: Value to validate

    Raises:
        ValueError: If project_id is invalid
    """
    if project_id is None:
        raise ValueError("project_id is required")

    try:
        project_int = int(project_id)
        if project_int <= 0:
            raise ValueError("project_id must be positive")
    except (ValueError, TypeError) as e:
        raise ValueError("project_id must be a valid positive integer") from e


def validate_max_colors(max_colors: int, min_val: int = 1, max_val: int = 50) -> None:
    """Validate max_colors parameter.

    Args:
        max_colors: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Raises:
        ValueError: If max_colors is out of range
    """
    try:
        colors_int = int(max_colors)
        if colors_int < min_val or colors_int > max_val:
            raise ValueError(f"max_colors must be between {min_val} and {max_val}")
    except (ValueError, TypeError) as e:
        raise ValueError(f"max_colors must be an integer between {min_val} and {max_val}") from e
