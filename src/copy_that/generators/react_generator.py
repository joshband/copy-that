"""
React/TypeScript token generator

Generates tokens as TypeScript/JavaScript exports for React applications
"""

import logging

from .base_generator import BaseGenerator

logger = logging.getLogger(__name__)


class ReactTokenGenerator(BaseGenerator):
    """Generate tokens as TypeScript/JavaScript exports"""

    def generate(self) -> str:
        """
        Generate TypeScript/JavaScript export format

        Returns:
            TypeScript string with token exports
        """
        lines = [
            "/**",
            " * Generated color tokens",
            " * Do not edit manually - regenerate from token library",
            " */",
            "",
        ]

        if self.library.tokens:
            # Group by role
            tokens_by_role = {}
            for token in self.library.tokens:
                role = token.role or "default"
                if role not in tokens_by_role:
                    tokens_by_role[role] = []
                tokens_by_role[role].append(token)

            # Generate type definitions
            lines.append("// Token structure")
            lines.append("export interface ColorToken {")
            lines.append("  hex: string;")
            lines.append("  rgb: string;")
            lines.append("  name: string;")
            lines.append("  confidence: number;")
            lines.append("}")
            lines.append("")

            # Generate color exports
            lines.append("export const colors = {")

            for role in sorted(tokens_by_role.keys()):
                tokens = tokens_by_role[role]

                if role != "default":
                    lines.append(f"  // {role.capitalize()} colors")

                role_key = self._to_js_identifier(role)
                lines.append(f"  {role_key}: {{")

                for token in tokens:
                    token_key = self._to_js_identifier(token.name)
                    lines.append(f"    {token_key}: {{")
                    lines.append(f"      hex: '{token.hex}',")
                    lines.append(f"      rgb: '{token.rgb}',")
                    lines.append(f"      name: '{token.name}',")
                    lines.append(f"      confidence: {token.confidence},")
                    lines.append("    },")

                lines.append("  },")

            lines.append("} as const;")
            lines.append("")

            # Generate type from const
            lines.append("export type Colors = typeof colors;")
            lines.append("")

            # Generate utility type for accessing nested colors
            lines.append("// Helper type for accessing nested color tokens")
            lines.append("export type ColorValue = string;")
            lines.append("")

            # Generate factory function
            lines.append(
                "export const getColor = (role: string, name: string): ColorToken | undefined => {"
            )
            lines.append("  const roleColors = colors[role as keyof Colors];")
            lines.append("  if (!roleColors) return undefined;")
            lines.append("  return roleColors[name as keyof typeof roleColors];")
            lines.append("};")

        else:
            lines.append("// No colors available")
            lines.append("export const colors = {} as const;")

        # Add metadata comment
        stats = self.library.statistics
        lines.append("")
        lines.append("/**")
        lines.append(" * Library Statistics:")
        lines.append(f" * - Total colors: {stats.get('color_count', 0)}")
        lines.append(f" * - Average confidence: {stats.get('avg_confidence', 0):.1%}")
        lines.append(f" * - Images analyzed: {stats.get('image_count', 0)}")
        lines.append(" */")

        return "\n".join(lines)

    @staticmethod
    def _to_js_identifier(name: str) -> str:
        """
        Convert token name to valid JavaScript identifier

        Args:
            name: Token name

        Returns:
            Valid JavaScript variable name
        """
        # Convert to camelCase
        parts = name.split(" ")
        if len(parts) == 1:
            # Remove non-alphanumeric characters
            sanitized = "".join(c for c in name if c.isalnum())
        else:
            # First part lowercase, rest title case
            sanitized = parts[0].lower().replace("-", "")
            for part in parts[1:]:
                sanitized += part.capitalize().replace("-", "")

        # Ensure it starts with letter or underscore
        if sanitized and not sanitized[0].isalpha() and sanitized[0] != "_":
            sanitized = "_" + sanitized

        return sanitized or "color"
