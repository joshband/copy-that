"""
Color deduplication using Delta-E 2000 perceptual color comparison.

This module provides the ColorDeduplicator class for merging similar colors
based on perceptual similarity using the CIEDE2000 color difference formula.
"""

from typing import Any

from coloraide import Color

from copy_that.pipeline import TokenResult, TokenType


class ColorDeduplicator:
    """
    Deduplicates color tokens based on Delta-E 2000 perceptual color difference.

    Uses ColorAide library to calculate Delta-E 2000 (CIEDE2000) between colors
    and merges colors that are within the specified JND (Just Noticeable Difference)
    threshold.

    Example:
        >>> deduplicator = ColorDeduplicator(threshold=2.0)
        >>> tokens = [
        ...     TokenResult(token_type=TokenType.COLOR, name="red1", value="#FF0000", confidence=0.9),
        ...     TokenResult(token_type=TokenType.COLOR, name="red2", value="#FF0001", confidence=0.8),
        ... ]
        >>> result = deduplicator.deduplicate(tokens)
        >>> len(result)  # Similar colors merged
        1
    """

    def __init__(self, threshold: float = 2.0) -> None:
        """
        Initialize with Delta-E threshold.

        Args:
            threshold: Maximum Delta-E 2000 value for colors to be considered
                      similar enough to merge. Default is 2.0 JND (Just Noticeable
                      Difference), meaning colors within this threshold are
                      perceptually almost indistinguishable.
        """
        self.threshold = threshold

    def deduplicate(self, tokens: list[TokenResult]) -> list[TokenResult]:
        """
        Deduplicate color tokens based on Delta-E 2000 similarity.

        Process:
        1. Separate color tokens from non-color tokens
        2. Parse colors and group similar ones using Delta-E 2000
        3. Merge each group into a single token (keeping highest confidence)
        4. Combine deduplicated colors with unchanged non-color tokens

        Args:
            tokens: List of TokenResult objects to deduplicate

        Returns:
            List of deduplicated TokenResult objects with similar colors merged.
            Non-color tokens pass through unchanged. Invalid color formats are
            preserved in the output.
        """
        if not tokens:
            return []

        # Separate color and non-color tokens
        color_tokens: list[TokenResult] = []
        non_color_tokens: list[TokenResult] = []

        for token in tokens:
            if token.token_type == TokenType.COLOR:
                color_tokens.append(token)
            else:
                non_color_tokens.append(token)

        if not color_tokens:
            return list(tokens)

        # Parse colors and track which can be parsed
        parsed_colors: list[tuple[int, Color]] = []  # (index, Color)
        unparseable_tokens: list[TokenResult] = []

        for i, token in enumerate(color_tokens):
            color = self._parse_color(str(token.value))
            if color is not None:
                parsed_colors.append((i, color))
            else:
                # Keep unparseable tokens in output
                unparseable_tokens.append(token)

        if not parsed_colors:
            # No valid colors to deduplicate
            return list(tokens)

        # Group similar colors
        groups: list[list[int]] = []
        used_indices: set[int] = set()

        for i, (token_idx, color1) in enumerate(parsed_colors):
            if token_idx in used_indices:
                continue

            # Start a new group with this color
            group = [token_idx]
            used_indices.add(token_idx)

            # Find all similar colors
            for j in range(i + 1, len(parsed_colors)):
                other_idx, color2 = parsed_colors[j]
                if other_idx in used_indices:
                    continue

                delta_e = self._calculate_delta_e(color1, color2)
                if delta_e <= self.threshold:
                    group.append(other_idx)
                    used_indices.add(other_idx)

            groups.append(group)

        # Merge each group
        deduplicated_colors: list[TokenResult] = []
        for group in groups:
            group_tokens = [color_tokens[idx] for idx in group]
            merged = self._merge_tokens(group_tokens)
            deduplicated_colors.append(merged)

        # Sort deduplicated colors by confidence (highest first)
        deduplicated_colors.sort(key=lambda t: t.confidence, reverse=True)

        # Combine results: deduplicated colors + unparseable + non-color tokens
        result = deduplicated_colors + unparseable_tokens + non_color_tokens

        return result

    def _parse_color(self, value: str) -> Color | None:
        """
        Parse color value string to ColorAide Color object.

        Handles various CSS color formats:
        - Hex: #RGB, #RRGGBB, #RRGGBBAA
        - RGB/RGBA: rgb(r, g, b), rgba(r, g, b, a)
        - HSL/HSLA: hsl(h, s%, l%), hsla(h, s%, l%, a)
        - Named colors: red, blue, etc.

        Args:
            value: Color value string to parse

        Returns:
            ColorAide Color object, or None if parsing fails
        """
        try:
            return Color(value)
        except Exception:
            return None

    def _calculate_delta_e(self, color1: Color, color2: Color) -> float:
        """
        Calculate Delta-E 2000 between two colors.

        Uses the CIEDE2000 formula which is the most perceptually accurate
        standard for measuring color difference.

        Args:
            color1: First color
            color2: Second color

        Returns:
            Delta-E 2000 value (0 = identical, higher = more different)
        """
        return color1.delta_e(color2, method="2000")

    def _merge_tokens(self, tokens: list[TokenResult]) -> TokenResult:
        """
        Merge similar tokens, keeping the one with highest confidence.

        Process:
        1. Find token with highest confidence (the "best" token)
        2. Preserve all W3C fields from the best token
        3. Merge provenance metadata from all tokens

        Args:
            tokens: List of similar TokenResult objects to merge

        Returns:
            Single merged TokenResult with highest confidence token's data
            and combined provenance metadata
        """
        if len(tokens) == 1:
            return tokens[0]

        # Find the token with highest confidence
        best_token = max(tokens, key=lambda t: t.confidence)

        # Collect provenance information from all merged tokens
        merged_sources: list[dict[str, Any]] = []
        for token in tokens:
            source_info: dict[str, Any] = {
                "name": token.name,
                "value": token.value,
                "confidence": token.confidence,
            }
            if token.metadata:
                # Include relevant metadata from each source
                if "source" in token.metadata:
                    source_info["source"] = token.metadata["source"]
                if "region" in token.metadata:
                    source_info["region"] = token.metadata["region"]
            merged_sources.append(source_info)

        # Build merged metadata
        merged_metadata: dict[str, Any] = {}

        # Copy metadata from best token
        if best_token.metadata:
            merged_metadata = dict(best_token.metadata)

        # Add provenance information about merged sources
        if len(tokens) > 1:
            merged_metadata["merged_sources"] = merged_sources
            merged_metadata["merge_count"] = len(tokens)

        # Create the merged token with all W3C fields preserved
        merged_token = TokenResult(
            token_type=best_token.token_type,
            name=best_token.name,
            path=best_token.path,
            w3c_type=best_token.w3c_type,
            value=best_token.value,
            description=best_token.description,
            reference=best_token.reference,
            confidence=best_token.confidence,
            extensions=best_token.extensions,
            metadata=merged_metadata if merged_metadata else None,
        )

        return merged_token
