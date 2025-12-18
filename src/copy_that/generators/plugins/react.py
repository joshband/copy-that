"""React generator producing deterministic TSX snippets from TokenGraph + component metadata."""

from __future__ import annotations

import json
from collections.abc import Mapping

from copy_that.generators.plugins.base import BaseGenerator


def _slug(value: str) -> str:
    return value.lower().replace(" ", "-").replace("/", "-")


class ReactGenerator(BaseGenerator):
    """Generate a TSX snippet that binds tokens to component anatomy."""

    id = "react"
    label = "React TSX"
    description = "Deterministic TSX using token refs + componentMeta anatomy."

    def generate(self) -> str:
        component_name = self.component_meta.get("component", "Component")
        slots = self.component_meta.get("slots") if isinstance(self.component_meta, Mapping) else []

        lines: list[str] = [
            "// Generated from TokenGraph (deterministic, no JSX parsing)",
            "// Tokens are provided as flattened W3C JSON",
            f"const tokens = {json.dumps(self.tokens, indent=2, sort_keys=True)} as const;",
            "",
            "type SlotStyles = Record<string, Record<string, string>>;",
            "const slotStyles: SlotStyles = {",
        ]

        for slot in slots:
            slot_name = slot.get("name", "slot")
            bindings = slot.get("tokens", [])
            lines.append(f"  '{slot_name}': {{")
            for binding in bindings:
                prop = binding.get("property")
                token_id = binding.get("token")
                if prop and token_id:
                    lines.append(f"    '{prop}': `var(--{_slug(token_id)})`,")
            lines.append("  },")
        lines.append("};")
        lines.append("")

        lines.extend(
            [
                "export function renderComponent(children?: React.ReactNode) {",
                f"  const component = '{component_name}';",
                "  return (",
                "    <div data-component={component}>",
            ]
        )

        if slots:
            for slot in slots:
                slot_name = slot.get("name", "slot")
                slot_key = _slug(str(slot_name))
                slot_styles_expr = f"slotStyles['{slot_name}'] ?? {{}}"
                lines.append(f'      <div data-slot="{slot_key}" style={{{slot_styles_expr}}}>')
                lines.append("        {children}")
                lines.append("      </div>")
            lines.append("    </div>")
            lines.append("  );")
            lines.append("}")
        else:
            lines.append("      {children}")
            lines.append("    </div>")
            lines.append("  );")
            lines.append("}")

        lines.append("")
        lines.append("// Export raw tokens for downstream generators")
        lines.append("export const designTokens = tokens;")

        return "\n".join(lines)
