"""CSS generator that renders :root variables and slot-oriented class stubs."""

from __future__ import annotations

from collections.abc import Mapping

from copy_that.generators.plugins.base import BaseGenerator
from copy_that.generators.plugins.format_utils import (
    border_css_value,
    css_color_value,
    css_gradient_value,
    cubic_bezier_css_value,
    dimension_px,
    duration_css_value,
    font_family_css_value,
    font_weight_css_value,
    format_dimension_css,
    layout_css_values,
    number_css_value,
    opacity_css_value,
    shadow_css_value,
    slug,
    spacing_css_vars,
    stroke_style_css_value,
    transition_css_value,
    typography_css_props,
)

# Re-export helpers previously defined here so existing imports keep working.
_slug = slug
_css_color_value = css_color_value
_dimension_px = dimension_px
_layout_css_values = layout_css_values
_css_gradient_value = css_gradient_value


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
        layout_section = self.tokens.get("layout") or {}
        opacity_section = self.tokens.get("opacity") or {}
        gradient_section = self.tokens.get("gradient") or {}
        duration_section = self.tokens.get("duration") or {}
        cubic_bezier_section = self.tokens.get("cubicBezier") or {}
        font_family_section = self.tokens.get("fontFamily") or {}
        font_weight_section = self.tokens.get("fontWeight") or {}
        stroke_style_section = self.tokens.get("strokeStyle") or {}
        border_section = self.tokens.get("border") or {}
        transition_section = self.tokens.get("transition") or {}
        dimension_section = self.tokens.get("dimension") or {}
        number_section = self.tokens.get("number") or {}

        if color_section:
            lines.append("  /* Colors */")
            for token_id in sorted(color_section.keys()):
                token = color_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                css_value = css_color_value(token)
                if css_value:
                    lines.append(f"  --{slug(token_id)}: {css_value};")

        if spacing_section:
            lines.append("")
            lines.append("  /* Spacing */")
            for token_id in sorted(spacing_section.keys()):
                token = spacing_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                for var_name, css_value in spacing_css_vars(token_id, token):
                    lines.append(f"  --{var_name}: {css_value};")

        if typography_section:
            lines.append("")
            lines.append("  /* Typography */")
            for token_id in sorted(typography_section.keys()):
                token = typography_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                val = token.get("$value")
                if isinstance(val, Mapping):
                    for suffix, css_value in typography_css_props(val):
                        lines.append(f"  --{slug(token_id)}{suffix}: {css_value};")
                elif val is not None:
                    lines.append(f"  --{slug(token_id)}: {val};")

        if shadow_section:
            lines.append("")
            lines.append("  /* Shadows */")
            for token_id in sorted(shadow_section.keys()):
                token = shadow_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                css_value = shadow_css_value(token)
                if css_value:
                    lines.append(f"  --{slug(token_id)}: {css_value};")

        if layout_section:
            lines.append("")
            lines.append("  /* Layout / shape */")
            for token_id in sorted(layout_section.keys()):
                token = layout_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                for var_suffix, css_value in layout_css_values(token):
                    lines.append(f"  --{slug(token_id)}{var_suffix}: {css_value};")

        if opacity_section:
            lines.append("")
            lines.append("  /* Opacity */")
            for token_id in sorted(opacity_section.keys()):
                token = opacity_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                css_value = opacity_css_value(token)
                if css_value is not None:
                    lines.append(f"  --{slug(token_id)}: {css_value};")

        if gradient_section:
            lines.append("")
            lines.append("  /* Gradients */")
            for token_id in sorted(gradient_section.keys()):
                token = gradient_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                css_value = css_gradient_value(token)
                if css_value:
                    lines.append(f"  --{slug(token_id)}: {css_value};")

        if duration_section:
            lines.append("")
            lines.append("  /* Duration */")
            for token_id in sorted(duration_section.keys()):
                token = duration_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                css_value = duration_css_value(token)
                if css_value:
                    lines.append(f"  --{slug(token_id)}: {css_value};")

        if cubic_bezier_section:
            lines.append("")
            lines.append("  /* Easing */")
            for token_id in sorted(cubic_bezier_section.keys()):
                token = cubic_bezier_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                css_value = cubic_bezier_css_value(token)
                if css_value:
                    lines.append(f"  --{slug(token_id)}: {css_value};")

        if font_family_section:
            lines.append("")
            lines.append("  /* Font family */")
            for token_id in sorted(font_family_section.keys()):
                token = font_family_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                css_value = font_family_css_value(token)
                if css_value:
                    lines.append(f"  --{slug(token_id)}: {css_value};")

        if font_weight_section:
            lines.append("")
            lines.append("  /* Font weight */")
            for token_id in sorted(font_weight_section.keys()):
                token = font_weight_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                css_value = font_weight_css_value(token)
                if css_value:
                    lines.append(f"  --{slug(token_id)}: {css_value};")

        if dimension_section:
            lines.append("")
            lines.append("  /* Dimension */")
            for token_id in sorted(dimension_section.keys()):
                token = dimension_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                raw = token.get("$value") if "$value" in token else token.get("value")
                css_value = format_dimension_css(raw)
                if css_value:
                    lines.append(f"  --{slug(token_id)}: {css_value};")

        if number_section:
            lines.append("")
            lines.append("  /* Number */")
            for token_id in sorted(number_section.keys()):
                token = number_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                css_value = number_css_value(token)
                if css_value is not None:
                    lines.append(f"  --{slug(token_id)}: {css_value};")

        if stroke_style_section:
            lines.append("")
            lines.append("  /* Stroke style */")
            for token_id in sorted(stroke_style_section.keys()):
                token = stroke_style_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                css_value = stroke_style_css_value(token)
                if css_value:
                    lines.append(f"  --{slug(token_id)}: {css_value};")

        if border_section:
            lines.append("")
            lines.append("  /* Border */")
            for token_id in sorted(border_section.keys()):
                token = border_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                css_value = border_css_value(token)
                if css_value:
                    lines.append(f"  --{slug(token_id)}: {css_value};")

        if transition_section:
            lines.append("")
            lines.append("  /* Transition */")
            for token_id in sorted(transition_section.keys()):
                token = transition_section[token_id]
                if not isinstance(token, Mapping):
                    continue
                css_value = transition_css_value(token)
                if css_value:
                    lines.append(f"  --{slug(token_id)}: {css_value};")

        lines.append("}")

        slots = self.component_meta.get("slots") if isinstance(self.component_meta, Mapping) else []
        if slots:
            component_name = slug(str(self.component_meta.get("component", "component")))
            lines.append("")
            lines.append(f"/* Component anatomy scaffolding for {component_name} */")
            for slot in slots:
                slot_name = slug(str(slot.get("name", "slot")))
                lines.append(f".{component_name}__{slot_name} {{")
                for binding in slot.get("tokens", []):
                    prop = binding.get("property")
                    token_id = binding.get("token")
                    if prop and token_id:
                        lines.append(f"  {prop}: var(--{slug(token_id)});")
                lines.append("}")

        return "\n".join(lines)
