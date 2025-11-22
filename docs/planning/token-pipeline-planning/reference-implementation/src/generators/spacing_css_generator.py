"""
REFERENCE IMPLEMENTATION - CSS Custom Properties Generator for Spacing

This is REFERENCE CODE for planning purposes. It demonstrates how to evolve
the existing BaseGenerator pattern for CSS custom properties output.

NOTE: This code is not production-ready. It serves as a blueprint for
implementing CSS generation in the actual codebase.

TODO: Integrate with existing copy_that.generators module structure
TODO: Add support for CSS-in-JS output (styled-components, emotion)
TODO: Add SCSS/LESS variable output options
"""

# TODO: Update imports when integrated into main codebase
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from aggregators.spacing_aggregator import SpacingTokenLibrary


class BaseGenerator:
    """
    Abstract base class for token format generators.

    Follows the pattern from copy_that.generators.base_generator.
    """

    def __init__(self, library: SpacingTokenLibrary):
        """
        Initialize generator with a token library.

        Args:
            library: SpacingTokenLibrary containing aggregated tokens
        """
        self.library = library

    def generate(self) -> str:
        """
        Generate output in the specific format.

        Returns:
            String containing the formatted token output
        """
        raise NotImplementedError


class SpacingCSSGenerator(BaseGenerator):
    """
    Generate CSS custom properties for spacing tokens.

    Outputs CSS variables that can be used directly in stylesheets.

    Example output:
    :root {
      /* Spacing Scale - 8pt grid system */
      --spacing-xs: 4px;
      --spacing-sm: 8px;
      --spacing-md: 16px;
      --spacing-lg: 24px;
      --spacing-xl: 32px;
    }
    """

    def __init__(
        self,
        library: SpacingTokenLibrary,
        prefix: str = "spacing",
        unit: str = "px",
        include_rem: bool = True,
        include_comments: bool = True,
        selector: str = ":root",
    ):
        """
        Initialize the CSS generator.

        Args:
            library: SpacingTokenLibrary to generate from
            prefix: Prefix for CSS variable names
            unit: Primary unit ('px' or 'rem')
            include_rem: Include rem variants as separate variables
            include_comments: Include comments with metadata
            selector: CSS selector to scope variables
        """
        super().__init__(library)
        self.prefix = prefix
        self.unit = unit
        self.include_rem = include_rem
        self.include_comments = include_comments
        self.selector = selector

    def generate(self) -> str:
        """
        Generate CSS custom properties.

        Returns:
            CSS string with custom properties
        """
        lines = []

        # Opening
        lines.append(f"{self.selector} {{")

        # Header comment
        if self.include_comments:
            stats = self.library.statistics
            scale_system = stats.get("scale_system", "custom")
            base_unit = stats.get("base_unit", 8)
            count = stats.get("spacing_count", 0)

            lines.append(f"  /* Spacing Scale - {scale_system} ({count} values) */")
            lines.append(f"  /* Base unit: {base_unit}px */")
            lines.append("")

        # Generate variables for each token
        for token in self.library.tokens:
            var_name = self._get_variable_name(token)

            # Add comment with metadata
            if self.include_comments:
                comment_parts = []
                if token.semantic_role:
                    comment_parts.append(token.semantic_role)
                if token.confidence:
                    comment_parts.append(f"confidence: {token.confidence:.2f}")
                if comment_parts:
                    lines.append(f"  /* {' | '.join(comment_parts)} */")

            # Primary variable
            if self.unit == "rem":
                lines.append(f"  --{var_name}: {token.value_rem}rem;")
            else:
                lines.append(f"  --{var_name}: {token.value_px}px;")

            # Rem variant
            if self.include_rem and self.unit == "px":
                lines.append(f"  --{var_name}-rem: {token.value_rem}rem;")

            lines.append("")

        # Closing
        lines.append("}")

        return "\n".join(lines)

    def generate_with_breakpoints(self) -> str:
        """
        Generate CSS with responsive breakpoint overrides.

        Returns:
            CSS string with media queries for responsive spacing

        Example output:
        :root {
          --spacing-md: 16px;
        }

        @media (max-width: 576px) {
          :root {
            --spacing-md: 12px;
          }
        }
        """
        lines = []

        # Base values
        lines.append(f"{self.selector} {{")
        if self.include_comments:
            lines.append("  /* Base spacing values */")
            lines.append("")

        for token in self.library.tokens:
            var_name = self._get_variable_name(token)
            lines.append(f"  --{var_name}: {token.value_px}px;")

        lines.append("}")
        lines.append("")

        # Breakpoint overrides
        breakpoints = {
            "sm": "576px",
            "md": "768px",
            "lg": "992px",
            "xl": "1200px",
        }

        # Generate media queries for each breakpoint
        for bp_name, bp_value in breakpoints.items():
            has_overrides = False
            bp_lines = []

            for token in self.library.tokens:
                if token.responsive_scales and bp_name in token.responsive_scales:
                    if not has_overrides:
                        bp_lines.append(f"@media (min-width: {bp_value}) {{")
                        bp_lines.append(f"  {self.selector} {{")
                        has_overrides = True

                    var_name = self._get_variable_name(token)
                    bp_value_px = token.responsive_scales[bp_name]
                    bp_lines.append(f"    --{var_name}: {bp_value_px}px;")

            if has_overrides:
                bp_lines.append("  }")
                bp_lines.append("}")
                bp_lines.append("")
                lines.extend(bp_lines)

        return "\n".join(lines)

    def generate_utility_classes(self) -> str:
        """
        Generate Tailwind-style utility classes for spacing.

        Returns:
            CSS string with utility classes

        Example output:
        .p-xs { padding: var(--spacing-xs); }
        .m-sm { margin: var(--spacing-sm); }
        .gap-md { gap: var(--spacing-md); }
        """
        lines = []

        # Header
        if self.include_comments:
            lines.append("/* Spacing Utility Classes */")
            lines.append("")

        for token in self.library.tokens:
            var_name = self._get_variable_name(token)
            suffix = token.role or str(token.value_px)

            # Padding utilities
            lines.append(f".p-{suffix} {{ padding: var(--{var_name}); }}")
            lines.append(
                f".px-{suffix} {{ padding-left: var(--{var_name}); padding-right: var(--{var_name}); }}"
            )
            lines.append(
                f".py-{suffix} {{ padding-top: var(--{var_name}); padding-bottom: var(--{var_name}); }}"
            )

            # Margin utilities
            lines.append(f".m-{suffix} {{ margin: var(--{var_name}); }}")
            lines.append(
                f".mx-{suffix} {{ margin-left: var(--{var_name}); margin-right: var(--{var_name}); }}"
            )
            lines.append(
                f".my-{suffix} {{ margin-top: var(--{var_name}); margin-bottom: var(--{var_name}); }}"
            )

            # Gap utilities
            lines.append(f".gap-{suffix} {{ gap: var(--{var_name}); }}")

            lines.append("")

        return "\n".join(lines)

    def _get_variable_name(self, token) -> str:
        """
        Generate CSS variable name for a token.

        Args:
            token: AggregatedSpacingToken

        Returns:
            CSS variable name (without --)
        """
        # Use role if assigned, otherwise use name
        if token.role:
            suffix = token.role
        elif token.name:
            # Extract suffix from name like "spacing-md" -> "md"
            suffix = token.name.replace("spacing-", "").replace("space-", "")
        else:
            suffix = str(token.value_px)

        # Sanitize
        suffix = suffix.lower().replace(" ", "-")

        return f"{self.prefix}-{suffix}"


class SpacingSCSSGenerator(SpacingCSSGenerator):
    """
    Generate SCSS variables and mixins for spacing.

    Example output:
    // Spacing Scale
    $spacing-xs: 4px;
    $spacing-sm: 8px;
    $spacing-md: 16px;

    // Spacing map
    $spacing-scale: (
      'xs': $spacing-xs,
      'sm': $spacing-sm,
      'md': $spacing-md
    );

    @mixin spacing($property, $size) {
      #{$property}: map-get($spacing-scale, $size);
    }
    """

    def generate(self) -> str:
        """
        Generate SCSS variables and map.

        Returns:
            SCSS string with variables, map, and mixin
        """
        lines = []

        # Header
        if self.include_comments:
            stats = self.library.statistics
            lines.append(f"// Spacing Scale - {stats.get('scale_system', 'custom')}")
            lines.append(f"// {stats.get('spacing_count', 0)} values")
            lines.append("")

        # Generate variables
        var_names = []
        for token in self.library.tokens:
            var_name = self._get_variable_name(token)
            var_names.append(var_name)

            if self.unit == "rem":
                lines.append(f"${var_name}: {token.value_rem}rem;")
            else:
                lines.append(f"${var_name}: {token.value_px}px;")

        lines.append("")

        # Generate map
        lines.append("// Spacing map for programmatic access")
        lines.append("$spacing-scale: (")
        for i, token in enumerate(self.library.tokens):
            var_name = self._get_variable_name(token)
            key = token.role or var_name.split("-")[-1]
            comma = "," if i < len(self.library.tokens) - 1 else ""
            lines.append(f"  '{key}': ${var_name}{comma}")
        lines.append(");")
        lines.append("")

        # Generate mixin
        lines.append("// Utility mixin")
        lines.append("@mixin spacing($property, $size) {")
        lines.append("  #{$property}: map-get($spacing-scale, $size);")
        lines.append("}")

        return "\n".join(lines)


class SpacingTailwindConfigGenerator(BaseGenerator):
    """
    Generate Tailwind CSS config for spacing.

    Example output:
    module.exports = {
      theme: {
        extend: {
          spacing: {
            'xs': '4px',
            'sm': '8px',
            'md': '16px',
          }
        }
      }
    }
    """

    def __init__(self, library: SpacingTokenLibrary, use_rem: bool = False):
        """
        Initialize Tailwind config generator.

        Args:
            library: SpacingTokenLibrary
            use_rem: Use rem units instead of px
        """
        super().__init__(library)
        self.use_rem = use_rem

    def generate(self) -> str:
        """
        Generate Tailwind config snippet.

        Returns:
            JavaScript module.exports string
        """
        lines = []

        lines.append("module.exports = {")
        lines.append("  theme: {")
        lines.append("    extend: {")
        lines.append("      spacing: {")

        for i, token in enumerate(self.library.tokens):
            # Use role or generate key
            key = token.role or str(token.value_px)

            # Format value
            if self.use_rem:
                value = f"{token.value_rem}rem"
            else:
                value = f"{token.value_px}px"

            comma = "," if i < len(self.library.tokens) - 1 else ""
            lines.append(f"        '{key}': '{value}'{comma}")

        lines.append("      }")
        lines.append("    }")
        lines.append("  }")
        lines.append("}")

        return "\n".join(lines)
