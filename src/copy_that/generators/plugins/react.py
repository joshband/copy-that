"""React generator producing a deterministic TypeScript theme module."""

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
    number_css_value,
    opacity_css_value,
    shadow_css_value,
    slug,
    spacing_css_vars,
    stroke_style_css_value,
    theme_key,
    transition_css_value,
    typography_css_props,
)


def _emit_object(name: str, entries: dict[str, str], indent: int = 2) -> list[str]:
    pad = " " * indent
    lines = [f"{pad}{name}: {{"]
    for key in sorted(entries.keys()):
        lines.append(f"{pad}  {js_string(key)}: {js_string(entries[key])},")
    lines.append(f"{pad}}},")
    return lines


def _colors(section: Mapping[str, Any], css_vars: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        value = css_color_value(token)
        if value:
            out[theme_key(token_id, "color")] = value
            css_vars[f"--{slug(token_id)}"] = value
    return out


def _spacing(section: Mapping[str, Any], css_vars: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        for var_name, css_value in spacing_css_vars(token_id, token):
            key = var_name
            if key.startswith("spacing-") and len(key) > len("spacing-"):
                key = key[len("spacing-") :]
            out[key] = css_value
            css_vars[f"--{var_name}"] = css_value
    return out


def _typography(section: Mapping[str, Any], css_vars: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        val = token.get("$value")
        base = theme_key(token_id, "typography")
        if isinstance(val, Mapping):
            for suffix, css_value in typography_css_props(val):
                # suffix is like "-font-weight"; key becomes "body-font-weight"
                key = f"{base}{suffix}"
                out[key] = css_value
                css_vars[f"--{slug(token_id)}{suffix}"] = css_value
        elif val is not None:
            out[base] = str(val)
            css_vars[f"--{slug(token_id)}"] = str(val)
    return out


def _shadows(section: Mapping[str, Any], css_vars: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        value = shadow_css_value(token)
        if value:
            out[theme_key(token_id, "shadow")] = value
            css_vars[f"--{slug(token_id)}"] = value
    return out


def _layout(section: Mapping[str, Any], css_vars: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        base = theme_key(token_id, "layout")
        for suffix, css_value in layout_css_values(token):
            out[f"{base}{suffix}"] = css_value
            css_vars[f"--{slug(token_id)}{suffix}"] = css_value
    return out


def _simple_section(
    section: Mapping[str, Any],
    formatter: TokenFormatter,
    css_vars: dict[str, str],
    *section_names: str,
) -> dict[str, str]:
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        value = formatter(token)
        if value is not None:
            out[theme_key(token_id, *section_names)] = value
            css_vars[f"--{slug(token_id)}"] = value
    return out


class ReactGenerator(BaseGenerator):
    """Generate a TypeScript theme module from a W3C/DTCG token map."""

    id = "react"
    label = "React Theme"
    description = "Deterministic TypeScript theme object plus ThemeProvider / useTheme."

    def generate(self) -> str:
        tokens_endpoint = "/api/v1/design-tokens/export/w3c"
        css_vars: dict[str, str] = {}

        colors = _colors(self.tokens.get("color") or {}, css_vars)
        spacing = _spacing(self.tokens.get("spacing") or {}, css_vars)
        typography = _typography(self.tokens.get("typography") or {}, css_vars)
        shadows = _shadows(self.tokens.get("shadow") or {}, css_vars)
        layout = _layout(self.tokens.get("layout") or {}, css_vars)
        opacity = _simple_section(
            self.tokens.get("opacity") or {}, opacity_css_value, css_vars, "opacity"
        )
        gradient = _simple_section(
            self.tokens.get("gradient") or {}, css_gradient_value, css_vars, "gradient"
        )
        duration = _simple_section(
            self.tokens.get("duration") or {}, duration_css_value, css_vars, "duration"
        )
        cubic_bezier = _simple_section(
            self.tokens.get("cubicBezier") or {},
            cubic_bezier_css_value,
            css_vars,
            "cubicBezier",
            "easing",
        )
        font_family = _simple_section(
            self.tokens.get("fontFamily") or {},
            font_family_css_value,
            css_vars,
            "fontFamily",
            "font",
        )
        font_weight = _simple_section(
            self.tokens.get("fontWeight") or {},
            font_weight_css_value,
            css_vars,
            "fontWeight",
            "font",
        )
        stroke_style = _simple_section(
            self.tokens.get("strokeStyle") or {},
            stroke_style_css_value,
            css_vars,
            "strokeStyle",
            "stroke",
        )
        border = _simple_section(
            self.tokens.get("border") or {}, border_css_value, css_vars, "border"
        )
        transition = _simple_section(
            self.tokens.get("transition") or {},
            transition_css_value,
            css_vars,
            "transition",
        )
        dimension = _simple_section(
            self.tokens.get("dimension") or {},
            lambda t: format_dimension_css(t.get("$value") if "$value" in t else t.get("value")),
            css_vars,
            "dimension",
        )
        number = _simple_section(
            self.tokens.get("number") or {}, number_css_value, css_vars, "number"
        )

        lines: list[str] = [
            "// Generated from TokenGraph (deterministic TypeScript theme)",
        ]
        from copy_that.generators.plugins.guide_meta import guide_pack_ts_comment_block

        lines.extend(guide_pack_ts_comment_block(self.component_meta))
        lines.extend(
            [
                "import {",
                "  createContext,",
                "  createElement,",
                "  useContext,",
                "  useEffect,",
                "} from 'react';",
                "import type { ReactNode } from 'react';",
                "",
                "export const theme = {",
            ]
        )
        # Brand role aliases when GuidePack supplied
        brand = (
            self.component_meta.get("brand")
            if isinstance(self.component_meta, Mapping)
            else None
        )
        role_map = brand.get("roles") if isinstance(brand, Mapping) else None
        if isinstance(role_map, Mapping) and role_map:
            brand_entries: dict[str, str] = {}
            for role, token_id in role_map.items():
                key = theme_key(str(token_id), "color")
                if key in colors:
                    brand_entries[str(role)] = colors[key]
                elif str(token_id) in colors:
                    brand_entries[str(role)] = colors[str(token_id)]
            if brand_entries:
                lines.extend(_emit_object("brand", brand_entries))

        lines.extend(_emit_object("colors", colors))
        lines.extend(_emit_object("spacing", spacing))
        lines.extend(_emit_object("typography", typography))
        lines.extend(_emit_object("shadows", shadows))
        lines.extend(_emit_object("layout", layout))
        lines.extend(_emit_object("opacity", opacity))
        lines.extend(_emit_object("gradient", gradient))
        lines.extend(_emit_object("duration", duration))
        lines.extend(_emit_object("cubicBezier", cubic_bezier))
        lines.extend(_emit_object("fontFamily", font_family))
        lines.extend(_emit_object("fontWeight", font_weight))
        lines.extend(_emit_object("dimension", dimension))
        lines.extend(_emit_object("number", number))
        lines.extend(_emit_object("strokeStyle", stroke_style))
        lines.extend(_emit_object("border", border))
        lines.extend(_emit_object("transition", transition))
        lines.append("} as const;")
        lines.append("")
        lines.append("export const tokens = theme;")
        lines.append("")
        lines.append("/** Flat CSS custom properties (aligned with CSS export naming). */")
        lines.append("export const cssVars: Record<string, string> = {")
        for var_name in sorted(css_vars.keys()):
            lines.append(f"  {js_string(var_name)}: {js_string(css_vars[var_name])},")
        lines.append("};")
        lines.append("")
        lines.append("export type Theme = typeof theme;")
        lines.append("")
        lines.append("const ThemeContext = createContext<Theme>(theme);")
        lines.append("")
        lines.append("export type ThemeProviderProps = {")
        lines.append("  children: ReactNode;")
        lines.append("  /** Element that receives CSS variables; defaults to documentElement. */")
        lines.append("  target?: HTMLElement | null;")
        lines.append("};")
        lines.append("")
        lines.append("/** Injects cssVars onto the target element and provides theme context. */")
        lines.append("export function ThemeProvider({ children, target }: ThemeProviderProps) {")
        lines.append("  useEffect(() => {")
        lines.append(
            "    const el = target ?? (typeof document === 'object' && document"
            " ? document.documentElement : null);"
        )
        lines.append("    if (!el) return;")
        lines.append("    for (const [name, value] of Object.entries(cssVars)) {")
        lines.append("      el.style.setProperty(name, value);")
        lines.append("    }")
        lines.append("    return () => {")
        lines.append("      for (const name of Object.keys(cssVars)) {")
        lines.append("        el.style.removeProperty(name);")
        lines.append("      }")
        lines.append("    };")
        lines.append("  }, [target]);")
        lines.append("  return createElement(ThemeContext.Provider, { value: theme }, children);")
        lines.append("}")
        lines.append("")
        lines.append("export function useTheme(): Theme {")
        lines.append("  return useContext(ThemeContext);")
        lines.append("}")
        lines.append("")

        # Optional component slot scaffolding
        raw_slots = (
            self.component_meta.get("slots") if isinstance(self.component_meta, Mapping) else []
        )
        slots = raw_slots if isinstance(raw_slots, list) else []
        if slots:
            component_name = str(self.component_meta.get("component", "Component"))
            lines.append("type SlotStyles = Record<string, Record<string, string>>;")
            lines.append("export const slotStyles: SlotStyles = {")
            for slot in slots:
                slot_name = slot.get("name", "slot")
                bindings = slot.get("tokens", [])
                lines.append(f"  {js_string(str(slot_name))}: {{")
                for binding in bindings:
                    prop = binding.get("property")
                    token_id = binding.get("token")
                    if prop and token_id:
                        lines.append(f"    {js_string(str(prop))}: `var(--{slug(str(token_id))})`,")
                lines.append("  },")
            lines.append("};")
            lines.append("")
            lines.append(f"export const componentName = {js_string(component_name)};")
            lines.append("")

        lines.extend(
            [
                "/** Optional runtime fetch of the W3C token graph. */",
                "export async function loadTokens() {",
                f"  const res = await fetch({js_string(tokens_endpoint)});",
                "  if (!res.ok) throw new Error(`Failed to load tokens (${res.status})`);",
                "  return (await res.json()) as Record<string, unknown>;",
                "}",
            ]
        )

        return "\n".join(lines)
