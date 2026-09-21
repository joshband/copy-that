"""Shadow token extraction modules."""

from .adapters import AIShadowExtractorAdapter, CVShadowExtractorAdapter
from .base import ExtractionResult, ShadowExtractorProtocol
from .extractor import ShadowExtractor, ShadowStyle
from .orchestrator import ShadowAggregator, ShadowExtractionOrchestrator
from .token_bridge import extracted_to_shadow_style, shadow_style_to_api_dict

__all__ = [
    "AIShadowExtractorAdapter",
    "CVShadowExtractorAdapter",
    "ExtractionResult",
    "ShadowAggregator",
    "ShadowExtractionOrchestrator",
    "ShadowExtractor",
    "ShadowExtractorProtocol",
    "ShadowStyle",
    "extracted_to_shadow_style",
    "shadow_style_to_api_dict",
]
