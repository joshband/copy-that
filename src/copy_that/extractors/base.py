"""Base class for all token extractors."""

from abc import ABC, abstractmethod
from typing import Any


class BaseExtractor(ABC):
    """Abstract base class for all token extractors.

    Defines the interface that all extractors must implement.
    """

    token_type: str = "unknown"

    @abstractmethod
    async def extract(self, input_data: str | bytes) -> list[dict[str, Any]]:
        """Extract tokens from input data.

        Args:
            input_data: The input data to extract tokens from (image bytes, text, etc.)

        Returns:
            List of extracted tokens as dictionaries
        """
        pass

    async def preprocess(self, data: str | bytes) -> str | bytes:
        """Optional preprocessing hook.

        Can be overridden by subclasses for custom preprocessing.

        Args:
            data: The input data

        Returns:
            Preprocessed data
        """
        return data

    async def postprocess(self, tokens: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Optional postprocessing hook.

        Can be overridden by subclasses for custom postprocessing.

        Args:
            tokens: The extracted tokens

        Returns:
            Postprocessed tokens
        """
        return tokens
