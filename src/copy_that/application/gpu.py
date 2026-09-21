"""GPU capability detection helpers."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def gpu_enabled() -> bool:
    """Return True if GPU use is allowed (env gate)."""
    return os.getenv("ENABLE_GPU", "").lower() in {"1", "true", "yes"}


def choose_device(prefer_gpu: bool = True) -> str:
    """Choose device string for torch usage."""
    if not prefer_gpu or not gpu_enabled():
        return "cpu"
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda:0"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
    except Exception as exc:  # noqa: BLE001
        logger.info("GPU detection failed, falling back to CPU: %s", exc)
    return "cpu"
