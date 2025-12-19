"""CSS generator that renders :root variables and slot-oriented class stubs."""

from __future__ import annotations

import json
from collections.abc import Mapping

from copy_that.generators.plugins.base import BaseGenerator


def _slug(value: str) -> str:
    return value.lower().replace(" ", "-").replace("/", "-")


class CSSGenerator(BaseGenerator):
    """Generate CSS custom properties from a W3C/DTCG token map."""

    id = "css"
    label = "CSS Variables"
    description = "Outputs :root custom properties plus optional component slot scaffolding."

    def generate(self) -> str:
        lines: list[str] = [
            "/* Generated from TokenGraph (deterministic) */",
            ":root {",
        ]

        color_section = self.tokens.get("color") or {}
        spacing_section = self.tokens.get("spacing") or {}
        shadow_section = self.tokens.get("shadow") or {}
        typography_section = self.tokens.get("typography") or {}

        # Colors
        if color_section:
            lines.append("  /* Colors */")
            for token_id in sorted(color_section.keys()):
                token = color_section[token_id]
                value = token.get("$value") or token.get("value")
                if value:
                    lines.append(f"  --{_slug(token_id)}: {value};")

        # Spacing
        if spacing_section:
            lines.append("")
            lines.append("  /* Spacing */")
            for token_id in sorted(spacing_section.keys()):
                token = spacing_section[token_id]
                val = token.get("$value") or token.get("value")
                if isinstance(val, Mapping):
                    px = val.get("value") if val.get("unit") == "px" else val.get("px")
                    if px is not None:
                        lines.append(f"  --{_slug(token_id)}: {px}px;")
                elif val is not None:
                    lines.append(f"  --{_slug(token_id)}: {val};")

        # Typography
        if typography_section:
            lines.append("")
            lines.append("  /* Typography */")
            for token_id in sorted(typography_section.keys()):
                token = typography_section[token_id]
                val = token.get("$value")
                if isinstance(val, Mapping):
                    font_family = val.get("fontFamily")
                    font_size = val.get("fontSize")
                    if font_family:
                        if isinstance(font_family, list):
                            ff = ", ".join(font_family)
                        else:
                            ff = str(font_family)
                        lines.append(f"  --{_slug(token_id)}-font-family: {ff};")
                    if (
                        isinstance(font_size, Mapping)
                        and font_size.get("unit")
                        and font_size.get("value") is not None
                    ):
                        lines.append(
                            f"  --{_slug(token_id)}-font-size: {font_size.get('value')}{font_size.get('unit')};"
                        )
                elif val is not None:
                    lines.append(f"  --{_slug(token_id)}: {val};")

        # Shadows
        if shadow_section:
            lines.append("")
            lines.append("  /* Shadows */")
            for token_id in sorted(shadow_section.keys()):
                token = shadow_section[token_id]
                val = token.get("$value") or token.get("value")
                if isinstance(val, list) and val:
                    # deterministically render the first layer as CSS
                    layer = val[0]
                    shadow_css = [
                        f"{layer.get('x') or 0}px",
                        f"{layer.get('y') or 0}px",
                        f"{layer.get('blur') or 0}px",
                        f"{layer.get('spread') or 0}px",
                        str(layer.get("color") or "rgba(0,0,0,0.2)"),
                    ]
                    lines.append(f"  --{_slug(token_id)}: {' '.join(shadow_css)};")
                elif isinstance(val, Mapping):
                    layer = val
                    shadow_css = [
                        f"{layer.get('x') or 0}px",
                        f"{layer.get('y') or 0}px",
                        f"{layer.get('blur') or 0}px",
                        f"{layer.get('spread') or 0}px",
                        str(layer.get("color") or "rgba(0,0,0,0.2)"),
                    ]
                    lines.append(f"  --{_slug(token_id)}: {' '.join(shadow_css)};")

        lines.append("}")

        # Optional component slot scaffolding
        slots = self.component_meta.get("slots") if isinstance(self.component_meta, Mapping) else []
        if slots:
            component_name = _slug(str(self.component_meta.get("component", "component")))
            lines.append("")
            lines.append(f"/* Component anatomy scaffolding for {component_name} */")
            for slot in slots:
                slot_name = _slug(str(slot.get("name", "slot")))
                lines.append(f".{component_name}__{slot_name} {{")
                for binding in slot.get("tokens", []):
                    prop = binding.get("property")
                    token_id = binding.get("token")
                    if prop and token_id:
                        lines.append(f"  {prop}: var(--{_slug(token_id)});")
                lines.append("}")

        # Append JSON of tokens for reference (deterministic ordering)
        lines.append("")
        lines.append("/* Token snapshot (flattened W3C) */")
        lines.append(json.dumps(self.tokens, indent=2, sort_keys=True))

        return "\n".join(lines)
