"""
W3C Design Tokens format generator

Generates tokens in the W3C Design Tokens Community Group standard format
https://design-tokens.github.io/community-group/format/
"""

import json
import logging
from copy_that.tokens.color.aggregator import TokenLibrary
from .base_generator import BaseGenerator

logger = logging.getLogger(__name__)


class W3CTokenGenerator(BaseGenerator):
    """Generate tokens in W3C Design Tokens JSON format"""

    def generate(self) -> str:
        """
        Generate W3C Design Tokens format JSON

        Returns:
            JSON string with W3C Design Tokens structure
        """
        output = {
            "$schema": "https://tokens.figma.com/schema/tokens.json",
            "$tokens": {},
        }

        if not self.library.tokens:
            return json.dumps(output, indent=2)

        # Organize tokens by role or create a flat structure
        for token in self.library.tokens:
            role = token.role or "default"

            if role not in output["$tokens"]:
                output["$tokens"][role] = {}

            # Create semantic name from token name
            semantic_name = self._sanitize_name(token.name)

            # W3C token structure
            token_data = {
                "$value": token.hex,
                "$type": "color",
                "description": f"Color extracted with {token.confidence:.1%} confidence",
                "metadata": {
                    "name": token.name,
                    "rgb": token.rgb,
                    "confidence": token.confidence,
                    "harmony": token.harmony,
                    "temperature": token.temperature,
                    "provenance": token.provenance,
                    "sources": len(token.provenance),
                },
            }

            output["$tokens"][role][semantic_name] = token_data

        # Add library statistics as metadata
        output["$metadata"] = {
            "library_statistics": self.library.statistics,
            "generated_at": "2025-11-20",
            "token_count": len(self.library.tokens),
        }

        return json.dumps(output, indent=2)

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """
        Sanitize token name for W3C compliance

        Removes special characters, converts to kebab-case

        Args:
            name: Original token name

        Returns:
            Sanitized name suitable for token keys
        """
        # Remove special characters
        sanitized = name.replace(" ", "-").replace("&", "and").replace("(", "").replace(")", "")
        # Convert to lowercase
        sanitized = sanitized.lower()
        # Remove any remaining invalid characters
        sanitized = "".join(c for c in sanitized if c.isalnum() or c in "-_")
        return sanitized
