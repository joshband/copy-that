"""Shared utilities for API routers."""

import math
from typing import Any


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
