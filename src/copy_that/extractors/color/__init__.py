"""Color token extraction modules."""

# ColorExtractor is defined in extractor.py (Claude Sonnet-based extraction)
# OpenAIColorExtractor is defined in openai_extractor.py (GPT-4 Vision-based extraction)
from .openai_extractor import OpenAIColorExtractor

__all__ = ["OpenAIColorExtractor"]
