"""Shared formatting helpers for CSS / React / Tailwind generators."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

TokenFormatter = Callable[[Mapping[str, Any]], str | None]


def slug(value: str) -> str:
    return value.lower().replace(" ", "-").replace("/", "-").replace(".", "-")


def theme_key(token_id: str, *section_names: str) -> str:
    """Slug for theme object keys; strips redundant section prefixes.

    CSS custom properties keep the full ``slug(token_id)`` for cross-section
    uniqueness. Nested theme maps (React ``theme.colors``, Tailwind ``colors``)
    drop a leading ``color-`` / ``spacing-`` / etc. so consumers get
    ``theme.colors.primary`` / ``bg-primary`` instead of ``color-primary``.
    """
    key = slug(token_id)
    for name in section_names:
        prefix = f"{slug(name)}-"
        if key.startswith(prefix) and len(key) > len(prefix):
            return key[len(prefix) :]
    return key


def is_brace_ref(value: object) -> bool:
    return isinstance(value, str) and value.startswith("{")


def resolve_plain_string(value: object) -> str | None:
    """Return a usable string, skipping DTCG `{alias}` refs."""
    if isinstance(value, str):
        if not value or is_brace_ref(value):
            return None
        return value
    if isinstance(value, list):
        parts = [p for p in (resolve_plain_string(item) for item in value) if p]
        return ", ".join(parts) if parts else None
    return None


def css_color_value(token: Mapping) -> str | None:
    """Prefer a browser-usable color string (hex / oklch() / rgb())."""
    hex_value = token.get("hex")
    if isinstance(hex_value, str) and hex_value.startswith("#"):
        return hex_value

    value = token.get("$value") or token.get("value")
    if isinstance(value, str):
        if value.startswith("{"):
            return None
        return value
    if isinstance(value, Mapping):
        space = str(value.get("space") or value.get("colorSpace") or "").lower()
        if space == "oklch" and value.get("l") is not None:
            l_ = value.get("l")
            c = value.get("c", 0)
            h = value.get("h", 0)
            alpha = value.get("alpha", 1.0)
            if alpha is not None and float(alpha) < 1.0:
                return f"oklch({l_} {c} {h} / {alpha})"
            return f"oklch({l_} {c} {h})"
        if "r" in value and "g" in value and "b" in value:
            return f"rgb({value['r']}, {value['g']}, {value['b']})"
    return None


def dimension_px(raw: object) -> float | None:
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, Mapping):
        if raw.get("value") is not None:
            return float(raw["value"])
        if raw.get("px") is not None:
            return float(raw["px"])
        if raw.get("width") is not None:
            return dimension_px(raw["width"])
    return None


def format_px(num: float) -> str:
    if float(num).is_integer():
        return f"{int(num)}px"
    return f"{num}px"


def format_dimension_css(raw: object) -> str | None:
    """Format a dimension token value as CSS (respects unit when present)."""
    if isinstance(raw, (int, float)):
        return format_px(float(raw))
    if isinstance(raw, Mapping):
        if raw.get("value") is not None and raw.get("unit"):
            unit = str(raw["unit"])
            val = raw["value"]
            try:
                num = float(val)
                if unit == "px" and num.is_integer():
                    return f"{int(num)}{unit}"
                return f"{val}{unit}"
            except (TypeError, ValueError):
                return f"{val}{unit}"
        mapped = dimension_px(raw)
        if mapped is None:
            return None
        return format_px(mapped)
    if isinstance(raw, str) and not is_brace_ref(raw):
        return raw
    return None


def typography_css_props(val: Mapping) -> list[tuple[str, str]]:
    """Return (css-suffix, css-value) pairs for typography composite fields."""
    results: list[tuple[str, str]] = []

    font_family = resolve_plain_string(val.get("fontFamily"))
    if font_family:
        results.append(("-font-family", font_family))

    font_size = format_dimension_css(val.get("fontSize"))
    if font_size:
        results.append(("-font-size", font_size))

    if val.get("fontWeight") is not None and not is_brace_ref(val.get("fontWeight")):
        results.append(("-font-weight", str(val["fontWeight"])))

    font_style = resolve_plain_string(val.get("fontStyle"))
    if font_style:
        results.append(("-font-style", font_style))

    line_height = format_dimension_css(val.get("lineHeight"))
    if line_height:
        results.append(("-line-height", line_height))

    letter_spacing = format_dimension_css(val.get("letterSpacing"))
    if letter_spacing:
        results.append(("-letter-spacing", letter_spacing))

    text_align = resolve_plain_string(val.get("textAlign"))
    if text_align:
        results.append(("-text-align", text_align))

    return results


def spacing_css_vars(token_id: str, token: Mapping) -> list[tuple[str, str]]:
    """Return (var-name, css-value) pairs for a spacing token (incl. rem companion)."""
    name = slug(token_id)
    results: list[tuple[str, str]] = []
    val = token.get("$value") or token.get("value")
    attrs = token if isinstance(token, Mapping) else {}

    rem_from_attrs = attrs.get("value_rem")
    if rem_from_attrs is None:
        rem_from_attrs = attrs.get("rem")

    if isinstance(val, Mapping):
        unit = str(val.get("unit") or "").lower()
        raw_value = val.get("value")
        px = val.get("px") if val.get("px") is not None else (raw_value if unit == "px" else None)
        rem = val.get("rem") if val.get("rem") is not None else (raw_value if unit == "rem" else None)

        if unit == "rem" and rem is not None:
            results.append((name, f"{rem}rem"))
        elif px is not None:
            results.append((name, f"{px}px"))
            companion = rem if rem is not None else rem_from_attrs
            if companion is not None:
                results.append((f"{name}-rem", f"{companion}rem"))
        elif rem is not None:
            results.append((name, f"{rem}rem"))
        else:
            css = format_dimension_css(val)
            if css:
                results.append((name, css))
                if rem_from_attrs is not None and unit != "rem":
                    results.append((f"{name}-rem", f"{rem_from_attrs}rem"))
    elif val is not None and not is_brace_ref(val):
        results.append((name, str(val)))
        if rem_from_attrs is not None:
            results.append((f"{name}-rem", f"{rem_from_attrs}rem"))

    return results


def shadow_layer_css(layer: Mapping) -> str:
    """Render one shadow layer as a CSS box-shadow fragment."""
    parts: list[str] = []
    if layer.get("inset") is True:
        parts.append("inset")

    for key in ("x", "y", "blur", "spread"):
        num = dimension_px(layer.get(key))
        parts.append(format_px(num if num is not None else 0.0))

    color = layer.get("color")
    if isinstance(color, str) and color.startswith("{"):
        parts.append("rgba(0,0,0,0.2)")
    elif isinstance(color, str) and color:
        parts.append(color)
    else:
        parts.append("rgba(0,0,0,0.2)")

    return " ".join(parts)


def shadow_css_value(token: Mapping) -> str | None:
    val = token.get("$value") or token.get("value")
    if isinstance(val, list) and val:
        layers = [shadow_layer_css(layer) for layer in val if isinstance(layer, Mapping)]
        return ", ".join(layers) if layers else None
    if isinstance(val, Mapping):
        return shadow_layer_css(val)
    return None


def layout_css_values(token: Mapping) -> list[tuple[str, str]]:
    """Extract (css-suffix, css-value) pairs from a layout W3C entry."""
    val = token.get("$value") or token.get("value")
    role = str(token.get("role") or "")
    results: list[tuple[str, str]] = []

    def _px(raw: object) -> str | None:
        num = dimension_px(raw)
        if num is None:
            return None
        return format_px(num)

    if isinstance(val, Mapping):
        if "radius" in val:
            css = _px(val["radius"])
            if css:
                results.append(("-radius", css))
        if "border" in val:
            css = _px(val["border"])
            if css:
                results.append(("-border-width", css))
        if "gutter" in val:
            css = _px(val["gutter"])
            if css:
                results.append(("-gutter", css))
        if "margin" in val:
            margin = val["margin"]
            if isinstance(margin, Mapping) and "value" not in margin and "px" not in margin:
                for side, side_val in margin.items():
                    css = _px(side_val)
                    if css:
                        results.append((f"-margin-{side}", css))
            else:
                css = _px(margin)
                if css:
                    results.append(("-margin", css))
        if "columns" in val and val["columns"] is not None:
            results.append(("-columns", str(int(val["columns"]))))
        if not results:
            css = _px(val)
            if css:
                suffix = ""
                if role == "corner_radius":
                    suffix = "-radius"
                elif role == "border_width":
                    suffix = "-border-width"
                results.append((suffix, css))
    elif isinstance(val, (int, float)):
        suffix = ""
        if role == "corner_radius":
            suffix = "-radius"
        elif role == "border_width":
            suffix = "-border-width"
        results.append((suffix, format_px(float(val))))

    return results


def css_gradient_value(token: Mapping) -> str | None:
    """Render a simple linear-gradient() from a DTCG-ish gradient token."""
    val = token.get("$value") if "$value" in token else token.get("value")
    if not isinstance(val, Mapping):
        return None
    stops = val.get("stops")
    if not isinstance(stops, list) or len(stops) < 2:
        return None
    colors: list[str] = []
    for stop in stops:
        if not isinstance(stop, Mapping):
            continue
        color = stop.get("color")
        if isinstance(color, str) and color and not color.startswith("{"):
            colors.append(color)
    if len(colors) < 2:
        return None
    angle = val.get("angle", 90)
    try:
        angle_num = float(angle)
        angle_css = f"{int(angle_num)}deg" if angle_num.is_integer() else f"{angle_num}deg"
    except (TypeError, ValueError):
        angle_css = "90deg"
    return f"linear-gradient({angle_css}, {', '.join(colors)})"


def duration_css_value(token: Mapping) -> str | None:
    val = token.get("$value") if "$value" in token else token.get("value")
    if isinstance(val, Mapping) and val.get("value") is not None:
        unit = val.get("unit") or "ms"
        return f"{val['value']}{unit}"
    if val is not None and not is_brace_ref(val):
        return str(val)
    return None


def cubic_bezier_css_value(token: Mapping) -> str | None:
    val = token.get("$value") if "$value" in token else token.get("value")
    if isinstance(val, list) and len(val) == 4:
        return f"cubic-bezier({val[0]}, {val[1]}, {val[2]}, {val[3]})"
    return None


def opacity_css_value(token: Mapping) -> str | None:
    val = token.get("$value") if "$value" in token else token.get("value")
    if val is not None and not is_brace_ref(val):
        return str(val)
    return None


def font_family_css_value(token: Mapping) -> str | None:
    val = token.get("$value") if "$value" in token else token.get("value")
    return resolve_plain_string(val)


def font_weight_css_value(token: Mapping) -> str | None:
    val = token.get("$value") if "$value" in token else token.get("value")
    if isinstance(val, (int, float)):
        return str(int(val) if float(val).is_integer() else val)
    return resolve_plain_string(val)


def stroke_style_css_value(token: Mapping) -> str | None:
    val = token.get("$value") if "$value" in token else token.get("value")
    if isinstance(val, str) and not is_brace_ref(val):
        return val
    if isinstance(val, Mapping):
        # DTCG dash-array object — approximate as dashed
        return "dashed"
    return None


def border_css_value(token: Mapping) -> str | None:
    """Shorthand border: width style color (skips brace refs for color/style)."""
    val = token.get("$value") if "$value" in token else token.get("value")
    if not isinstance(val, Mapping):
        return None
    width = format_dimension_css(val.get("width"))
    style = val.get("style")
    style_css = style if isinstance(style, str) and not is_brace_ref(style) else "solid"
    color = val.get("color")
    color_css = color if isinstance(color, str) and not is_brace_ref(color) else "currentColor"
    if width is None:
        return None
    return f"{width} {style_css} {color_css}"


def transition_css_value(token: Mapping) -> str | None:
    """CSS transition shorthand; unresolved refs fall back to defaults."""
    val = token.get("$value") if "$value" in token else token.get("value")
    if not isinstance(val, Mapping):
        return None
    duration = val.get("duration")
    if isinstance(duration, Mapping) and duration.get("value") is not None:
        unit = duration.get("unit") or "ms"
        dur_css = f"{duration['value']}{unit}"
    elif isinstance(duration, str) and not is_brace_ref(duration):
        dur_css = duration
    else:
        dur_css = "200ms"
    delay = val.get("delay")
    if isinstance(delay, Mapping) and delay.get("value") is not None:
        unit = delay.get("unit") or "ms"
        delay_css = f"{delay['value']}{unit}"
    else:
        delay_css = "0ms"
    timing = val.get("timingFunction")
    if isinstance(timing, list) and len(timing) == 4:
        ease_css = f"cubic-bezier({timing[0]}, {timing[1]}, {timing[2]}, {timing[3]})"
    elif isinstance(timing, str) and not is_brace_ref(timing):
        ease_css = timing
    else:
        ease_css = "ease"
    return f"{dur_css} {ease_css} {delay_css}"


def number_css_value(token: Mapping) -> str | None:
    val = token.get("$value") if "$value" in token else token.get("value")
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str) and not is_brace_ref(val):
        return val
    return None


def js_string(value: str) -> str:
    """Quote a string for JS/TS source."""
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def section_map_strings(section: Mapping[str, Any], formatter: TokenFormatter) -> dict[str, str]:
    """Build slug→formatted-string map from a W3C section using ``formatter(token)``."""
    out: dict[str, str] = {}
    for token_id in sorted(section.keys()):
        token = section[token_id]
        if not isinstance(token, Mapping):
            continue
        formatted = formatter(token)
        if formatted:
            out[slug(token_id)] = formatted
    return out
