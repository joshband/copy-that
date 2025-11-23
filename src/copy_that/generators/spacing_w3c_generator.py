"""
W3C Design Tokens Generator for Spacing

Generates spacing tokens in W3C Design Tokens Community Group format.
Follows the pattern of w3c_generator.py for color tokens.
"""

import json

from copy_that.tokens.spacing.aggregator import SpacingTokenLibrary

from .base_generator import BaseGenerator


class SpacingW3CGenerator(BaseGenerator):
    """
    Generate W3C Design Tokens format for spacing tokens.

    Outputs JSON following the W3C Design Tokens Community Group specification.

    Example output:
    {
      "spacing": {
        "$description": "Spacing tokens for consistent layout",
        "xs": {
          "$value": "4px",
          "$type": "dimension",
          "$description": "Extra small spacing"
        },
        "sm": {
          "$value": "8px",
          "$type": "dimension"
        },
        ...
      }
    }
    """

    def __init__(
        self,
        library: SpacingTokenLibrary,
        include_rem: bool = True,
        include_metadata: bool = True,
        namespace: str = "spacing",
    ):
        """
        Initialize the W3C generator.

        Args:
            library: SpacingTokenLibrary to generate from
            include_rem: Include rem values as $extensions
            include_metadata: Include provenance and confidence as $extensions
            namespace: Top-level namespace for tokens
        """
        self.library = library
        self.include_rem = include_rem
        self.include_metadata = include_metadata
        self.namespace = namespace

    def generate(self) -> str:
        """
        Generate W3C Design Tokens JSON format.

        Returns:
            JSON string with W3C-compliant token structure
        """
        tokens_dict = self._build_token_structure()
        return json.dumps(tokens_dict, indent=2)

    def _build_token_structure(self) -> dict:
        """
        Build the W3C token structure.

        Returns:
            Dictionary with W3C-compliant structure
        """
        # Root structure
        output = {
            self.namespace: {
                "$description": f"Spacing tokens ({self.library.statistics.get('spacing_count', 0)} values)",
                "$type": "dimension",
            }
        }

        # Add scale system info as extension
        if self.include_metadata:
            output[self.namespace]["$extensions"] = {
                "com.copythat.metadata": {
                    "scale_system": self.library.statistics.get("scale_system", "custom"),
                    "base_unit": self.library.statistics.get("base_unit", 8),
                    "grid_compliance": self.library.statistics.get("grid_compliance", 0),
                }
            }

        # Add each token
        for token in self.library.tokens:
            token_name = self._get_token_name(token)

            token_entry = {
                "$value": f"{token.value_px}px",
                "$type": "dimension",
            }

            # Add description if we have semantic role
            if token.semantic_role:
                token_entry["$description"] = f"{token.semantic_role.title()} spacing"

            # Add extensions
            extensions = {}

            if self.include_rem:
                extensions["rem"] = f"{token.value_rem}rem"

            if self.include_metadata:
                if token.confidence:
                    extensions["confidence"] = round(token.confidence, 3)
                if token.provenance:
                    extensions["provenance"] = token.provenance
                if token.grid_aligned is not None:
                    extensions["grid_aligned"] = token.grid_aligned
                if token.merged_values and len(token.merged_values) > 1:
                    extensions["merged_from"] = token.merged_values

            if extensions:
                token_entry["$extensions"] = {"com.copythat.spacing": extensions}

            output[self.namespace][token_name] = token_entry

        return output

    def _get_token_name(self, token) -> str:
        """
        Generate a safe token name.

        Args:
            token: AggregatedSpacingToken

        Returns:
            Safe string for use as token key
        """
        # Prefer role if assigned
        if token.role:
            return token.role

        # Use sanitized name
        name = token.name or f"spacing-{token.value_px}"
        # Remove invalid characters
        safe_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in name)
        return safe_name.lower().strip("-")

    def generate_nested(self) -> str:
        """
        Generate W3C format with nested structure for responsive variants.

        Returns:
            JSON string with nested breakpoint variants

        Example output:
        {
          "spacing": {
            "md": {
              "$value": "16px",
              "responsive": {
                "sm": { "$value": "12px" },
                "lg": { "$value": "20px" }
              }
            }
          }
        }
        """
        output = {
            self.namespace: {
                "$description": "Spacing tokens with responsive variants",
                "$type": "dimension",
            }
        }

        for token in self.library.tokens:
            token_name = self._get_token_name(token)

            token_entry = {
                "$value": f"{token.value_px}px",
                "$type": "dimension",
            }

            # Add responsive variants if available
            if token.responsive_scales:
                token_entry["responsive"] = {}
                for breakpoint, value in token.responsive_scales.items():
                    if breakpoint != "md":  # Skip base value
                        token_entry["responsive"][breakpoint] = {
                            "$value": f"{value}px",
                            "$type": "dimension",
                        }

            output[self.namespace][token_name] = token_entry

        return json.dumps(output, indent=2)


class SpacingW3CMultiFormatGenerator(SpacingW3CGenerator):
    """
    Extended W3C generator that outputs multiple unit formats.

    Generates tokens with px, rem, and em variants in the same structure.

    Example output:
    {
      "spacing": {
        "md": {
          "px": { "$value": "16px" },
          "rem": { "$value": "1rem" },
          "em": { "$value": "1em" }
        }
      }
    }
    """

    def generate(self) -> str:
        """
        Generate W3C format with multiple unit variants.

        Returns:
            JSON string with px/rem/em variants
        """
        output = {
            self.namespace: {
                "$description": "Spacing tokens in multiple units",
            }
        }

        for token in self.library.tokens:
            token_name = self._get_token_name(token)

            output[self.namespace][token_name] = {
                "px": {
                    "$value": f"{token.value_px}px",
                    "$type": "dimension",
                },
                "rem": {
                    "$value": f"{token.value_rem}rem",
                    "$type": "dimension",
                },
                "em": {
                    "$value": f"{token.value_rem}em",  # Same as rem for base context
                    "$type": "dimension",
                },
            }

        return json.dumps(output, indent=2)
