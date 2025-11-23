"""Preprocessing pipeline module.

This module provides image preprocessing capabilities for the pipeline:
- URL validation with SSRF protection
- Async image downloading with retry
- Image enhancement (resize, contrast, format conversion)
- Image caching

Usage:
    from copy_that.pipeline.preprocessing import PreprocessingAgent

    async with PreprocessingAgent() as agent:
        result = await agent.process(task)
"""

from .agent import PreprocessingAgent
from .downloader import (
    DownloadError,
    DownloadResult,
    ImageDownloader,
    RetryExhaustedError,
    TimeoutError,
)
from .enhancer import EnhancementError, ImageEnhancer
from .validator import (
    FileSizeError,
    ImageValidator,
    InvalidImageError,
    SSRFError,
    ValidationError,
)

__all__ = [
    # Main agent
    "PreprocessingAgent",
    # Validator
    "ImageValidator",
    "ValidationError",
    "SSRFError",
    "InvalidImageError",
    "FileSizeError",
    # Downloader
    "ImageDownloader",
    "DownloadResult",
    "DownloadError",
    "TimeoutError",
    "RetryExhaustedError",
    # Enhancer
    "ImageEnhancer",
    "EnhancementError",
]
