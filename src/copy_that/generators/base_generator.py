"""
Abstract base class for token generators

Defines the interface that all generators must implement
"""

from abc import ABC, abstractmethod

from copy_that.tokens.color.aggregator import TokenLibrary


class BaseGenerator(ABC):
    """Abstract base class for token format generators"""

    def __init__(self, library: TokenLibrary):
        """
        Initialize generator with a token library

        Args:
            library: TokenLibrary containing aggregated tokens
        """
        self.library = library

    @abstractmethod
    def generate(self) -> str:
        """
        Generate output in the specific format

        Returns:
            String containing the formatted token output
        """
        pass
