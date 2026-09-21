"""Tailwind generator producing a theme.extend config snippet."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from copy_that.generators.plugins.base import BaseGenerator
from copy_that.generators.plugins.format_utils import (
    TokenFormatter,
    border_css_value,
    css_color_value,
    css_gradient_value,
    cubic_bezier_css_value,
    duration_css_value,
    font_family_css_value,
    font_weight_css_value,
    format_dimension_css,
    js_string,
    layout_css_values,
    opacity_css_value,
    resolve_plain_string,
    shadow_css_value,
    slug,
    spacing_css_vars,
    stroke_style_css_value,
    theme_key,
)


def _emit_js_object(name: str, entries: dict[str, str], indent: int = 4) -> list[str]:
    pad = " " * indent
    lines = [f"{pad}{name}: {{"]
    for key in sorted(entries.keys()):
        lines.append(f"{pad}  {js_string(key)}: {js_string(entries[key])},")
    lines.append(f"{pad}}},")
    return lines


def _colors(section: Mapping[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        value = css_color_value(token)
        if value:
            out[theme_key(token_id, "color")] = value
    return out


def _spacing(section: Mapping[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        for var_name, css_value in spacing_css_vars(token_id, token):
            # Prefer primary (non -rem companion) keys for Tailwind spacing
            if var_name.endswith("-rem"):
                continue
            key = var_name
            if key.startswith("spacing-") and len(key) > len("spacing-"):
                key = key[len("spacing-") :]
            out[key] = css_value
    return out


def _border_radius(section: Mapping[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        for suffix, css_value in layout_css_values(token):
            if suffix == "-radius" or suffix.endswith("-radius"):
                key = theme_key(token_id, "layout", "border", "radius")
                if suffix and suffix != "-radius":
                    key = f"{key}{suffix}"
                out[key] = css_value
            elif "radius" in slug(token_id) and suffix == "":
                out[theme_key(token_id, "layout", "border", "radius")] = css_value
    return out


def _box_shadows(section: Mapping[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        value = shadow_css_value(token)
        if value:
            out[theme_key(token_id, "shadow")] = value
    return out


def _background_images(section: Mapping[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        value = css_gradient_value(token)
        if value:
            out[theme_key(token_id, "gradient")] = value
    return out


def _font_sizes(section: Mapping[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        val = token.get("$value")
        if not isinstance(val, Mapping):
            continue
        size = format_dimension_css(val.get("fontSize"))
        if size:
            out[theme_key(token_id, "typography")] = size
    return out


def _font_families_from_typography(section: Mapping[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        val = token.get("$value")
        if not isinstance(val, Mapping):
            continue
        family = resolve_plain_string(val.get("fontFamily"))
        if family:
            out[theme_key(token_id, "typography")] = family
    return out


def _durations(section: Mapping[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        value = duration_css_value(token)
        if value:
            out[theme_key(token_id, "duration")] = value
    return out


def _easings(section: Mapping[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        value = cubic_bezier_css_value(token)
        if value:
            out[theme_key(token_id, "cubicBezier", "easing")] = value
    return out


def _simple(
    section: Mapping[str, Any],
    formatter: TokenFormatter,
    *section_names: str,
) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        value = formatter(token)
        if value:
            out[theme_key(token_id, *section_names)] = value
    return out


class TailwindGenerator(BaseGenerator):
    """Generate a Tailwind ``theme.extend`` config snippet from W3C tokens."""

    id = "tailwind"
    label = "Tailwind Theme"
    description = "Outputs a tailwind.config theme.extend snippet from the token graph."

    def generate(self) -> str:
        colors = _colors(self.tokens.get("color") or {})
        spacing = _spacing(self.tokens.get("spacing") or {})
        border_radius = _border_radius(self.tokens.get("layout") or {})
        box_shadow = _box_shadows(self.tokens.get("shadow") or {})
        background_image = _background_images(self.tokens.get("gradient") or {})
        font_size = _font_sizes(self.tokens.get("typography") or {})
        durations = _durations(self.tokens.get("duration") or {})
        easings = _easings(self.tokens.get("cubicBezier") or {})
        font_family = _simple(self.tokens.get("fontFamily") or {}, font_family_css_value, "fontFamily", "font")
        # Prefer atomic fontFamily tokens; fill gaps from typography composites.
        for key, value in _font_families_from_typography(self.tokens.get("typography") or {}).items():
            font_family.setdefault(key, value)
        font_weight = _simple(self.tokens.get("fontWeight") or {}, font_weight_css_value, "fontWeight", "font")
        border_width = _simple(self.tokens.get("border") or {}, border_css_value, "border")
        stroke = _simple(self.tokens.get("strokeStyle") or {}, stroke_style_css_value, "strokeStyle", "stroke")
        opacity = _simple(self.tokens.get("opacity") or {}, opacity_css_value, "opacity")

        lines: list[str] = [
            "// Generated from TokenGraph (deterministic Tailwind theme.extend)",
            "// Paste under module.exports / export default as theme.extend (or merge).",
            "module.exports = {",
            "  theme: {",
            "    extend: {",
        ]
        lines.extend(_emit_js_object("colors", colors))
        lines.extend(_emit_js_object("spacing", spacing))
        lines.extend(_emit_js_object("borderRadius", border_radius))
        lines.extend(_emit_js_object("borderWidth", border_width))
        lines.extend(_emit_js_object("boxShadow", box_shadow))
        lines.extend(_emit_js_object("backgroundImage", background_image))
        lines.extend(_emit_js_object("fontFamily", font_family))
        lines.extend(_emit_js_object("fontSize", font_size))
        lines.extend(_emit_js_object("fontWeight", font_weight))
        lines.extend(_emit_js_object("opacity", opacity))
        lines.extend(_emit_js_object("borderStyle", stroke))
        lines.extend(_emit_js_object("transitionDuration", durations))
        lines.extend(_emit_js_object("transitionTimingFunction", easings))
        lines.append("    },")
        lines.append("  },")
        lines.append("};")
        return "\n".join(lines)
