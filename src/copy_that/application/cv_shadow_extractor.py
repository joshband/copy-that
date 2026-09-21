"""Legacy shim — prefer ``copy_that.extractors.shadow.cv_extractor``.

Default: classical shadowlab → CSS tokens. Dark-blob opt-in via
``ENABLE_DARK_BLOB_SHADOW_CV=1``. See docs/architecture/CURRENT_ARCHITECTURE_STATE.md (dual-CV note).
"""

from __future__ import annotations

from copy_that.extractors.shadow.cv_extractor import (
    CVShadowExtractor,
    ExtractedShadowToken,
    ShadowExtractionResult,
)

__all__ = ["CVShadowExtractor", "ExtractedShadowToken", "ShadowExtractionResult"]
