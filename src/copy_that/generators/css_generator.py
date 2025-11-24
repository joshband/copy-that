"""
CSS custom properties generator

Generates tokens as CSS custom properties (:root variables)
"""

import logging

from .base_generator import BaseGenerator

logger = logging.getLogger(__name__)


class CSSTokenGenerator(BaseGenerator):
    """Generate tokens as CSS custom properties"""

    def generate(self) -> str:
        """
        Generate CSS custom properties format

        Returns:
            CSS string with :root variables
        """
        lines = [
            "/* Generated color tokens */",
            ":root {",
        ]

        if self.library.tokens:
            # Group by role or use flat structure
            tokens_by_role = {}
            for token in self.library.tokens:
                role = token.role or "default"
                if role not in tokens_by_role:
                    tokens_by_role[role] = []
                tokens_by_role[role].append(token)

            # Generate CSS variables
            for role in sorted(tokens_by_role.keys()):
                tokens = tokens_by_role[role]

                if role != "default":
                    lines.append(f"\n  /* {role.title()} colors */")

                for token in tokens:
                    var_name = self._to_css_variable_name(token.name, role)
                    comment = f"/* {token.confidence:.0%} confidence, {len(token.provenance)} source(s) */"
                    lines.append(f"  {var_name}: {token.hex}; {comment}")
        else:
            lines.append("  /* No colors available */")

        # Add statistics as comments
        if self.library.statistics:
            lines.append("\n  /* Statistics */")
            stats = self.library.statistics
            lines.append(f"  /* Total colors: {stats.get('color_count', 0)} */")
            lines.append(f"  /* Average confidence: {stats.get('avg_confidence', 0):.1%} */")

        lines.append("}")

        return "\n".join(lines)

    @staticmethod
    def _to_css_variable_name(name: str, role: str = "") -> str:
        """
        Convert token name to valid CSS variable name

        Args:
            name: Token name
            role: Optional role prefix

        Returns:
            Valid CSS custom property name (--color-...)
        """
        # Sanitize name: remove special chars, convert to kebab-case
        sanitized = name.replace(" ", "-").replace("&", "and")
        sanitized = sanitized.replace("(", "").replace(")", "")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c == "-")
        sanitized = sanitized.lower()

        # Remove multiple consecutive dashes
        while "--" in sanitized:
            sanitized = sanitized.replace("--", "-")

        # Build variable name
        if role and role != "default":
            if sanitized == role:
                var_name = f"--color-{role}"
            else:
                var_name = f"--color-{role}-{sanitized}"
        else:
            var_name = f"--color-{sanitized}"

        return var_name
