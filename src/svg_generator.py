"""
SVG Component Generator - Generates SVG UI components based on design tokens.

This module creates vector UI components (buttons, inputs, cards, etc.) as SVG files
that match the extracted visual style.
"""

from typing import Dict, List, Any, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom


class SVGGenerator:
    """
    Generates SVG UI components using design tokens and style rules.
    """

    def __init__(self, design_tokens: Dict[str, Any]):
        """
        Initialize the SVG generator with design tokens.

        Args:
            design_tokens: Design token system (primitive + semantic)
        """
        self.tokens = design_tokens
        self.primitive = design_tokens.get('primitive', {})
        self.semantic = design_tokens.get('semantic', {})

    def generate_button(
        self,
        width: int,
        height: int,
        variant: str = 'primary',
        state: str = 'default',
        label: str = 'Button',
        corner_radius: Optional[int] = None
    ) -> str:
        """
        Generate a button component as SVG.

        Args:
            width: Button width in pixels
            height: Button height in pixels
            variant: Button variant (primary, secondary, ghost, danger)
            state: Button state (default, hover, active, disabled)
            label: Button text
            corner_radius: Optional custom corner radius

        Returns:
            SVG string
        """
        # Get style properties
        radius = corner_radius or self._parse_px(self.primitive.get('borderRadius', {}).get('md', '8px'))
        shadow = self._get_shadow(variant, state)
        bg_color = self._get_button_color(variant, state)
        text_color = self._get_button_text_color(variant)
        border_color = self._get_button_border_color(variant, state)

        # Create SVG
        svg = ET.Element('svg', {
            'width': str(width),
            'height': str(height),
            'viewBox': f'0 0 {width} {height}',
            'xmlns': 'http://www.w3.org/2000/svg'
        })

        # Add defs for shadows and gradients
        defs = ET.SubElement(svg, 'defs')
        if shadow:
            self._add_shadow_filter(defs, 'buttonShadow', shadow)

        # Add background rectangle
        rect_attrs = {
            'x': '0',
            'y': '0',
            'width': str(width),
            'height': str(height),
            'rx': str(radius),
            'fill': bg_color,
        }

        if border_color:
            rect_attrs['stroke'] = border_color
            rect_attrs['stroke-width'] = '1'

        if shadow:
            rect_attrs['filter'] = 'url(#buttonShadow)'

        ET.SubElement(svg, 'rect', rect_attrs)

        # Add text
        text_attrs = {
            'x': str(width / 2),
            'y': str(height / 2),
            'text-anchor': 'middle',
            'dominant-baseline': 'middle',
            'fill': text_color,
            'font-family': 'system-ui, -apple-system, sans-serif',
            'font-size': '14',
            'font-weight': '500'
        }

        text_elem = ET.SubElement(svg, 'text', text_attrs)
        text_elem.text = label

        return self._prettify_svg(svg)

    def generate_input(
        self,
        width: int,
        height: int = 40,
        state: str = 'default',
        placeholder: str = 'Enter text...',
        has_icon: bool = False
    ) -> str:
        """
        Generate an input field component as SVG.

        Args:
            width: Input width in pixels
            height: Input height in pixels
            state: Input state (default, focus, error, disabled)
            placeholder: Placeholder text
            has_icon: Whether to include an icon

        Returns:
            SVG string
        """
        radius = self._parse_px(self.primitive.get('borderRadius', {}).get('md', '8px'))
        border_color = self._get_input_border_color(state)
        bg_color = self._get_input_bg_color(state)
        text_color = '#a0a0a0'  # Placeholder color

        svg = ET.Element('svg', {
            'width': str(width),
            'height': str(height),
            'viewBox': f'0 0 {width} {height}',
            'xmlns': 'http://www.w3.org/2000/svg'
        })

        # Add background
        rect_attrs = {
            'x': '0',
            'y': '0',
            'width': str(width),
            'height': str(height),
            'rx': str(radius),
            'fill': bg_color,
            'stroke': border_color,
            'stroke-width': '2' if state == 'focus' else '1'
        }

        ET.SubElement(svg, 'rect', rect_attrs)

        # Add placeholder text
        padding = 12
        text_x = padding if not has_icon else padding + 24

        text_attrs = {
            'x': str(text_x),
            'y': str(height / 2),
            'dominant-baseline': 'middle',
            'fill': text_color,
            'font-family': 'system-ui, -apple-system, sans-serif',
            'font-size': '14'
        }

        text_elem = ET.SubElement(svg, 'text', text_attrs)
        text_elem.text = placeholder

        # Add icon if requested
        if has_icon:
            self._add_search_icon(svg, padding, height / 2 - 8)

        return self._prettify_svg(svg)

    def generate_card(
        self,
        width: int,
        height: int,
        has_header: bool = True,
        has_footer: bool = False,
        elevation: str = 'md'
    ) -> str:
        """
        Generate a card component as SVG.

        Args:
            width: Card width in pixels
            height: Card height in pixels
            has_header: Whether to include a header section
            has_footer: Whether to include a footer section
            elevation: Shadow elevation (sm, md, lg)

        Returns:
            SVG string
        """
        radius = self._parse_px(self.primitive.get('borderRadius', {}).get('lg', '12px'))
        shadow = self.primitive.get('shadow', {}).get(elevation, '')
        bg_color = '#ffffff'

        svg = ET.Element('svg', {
            'width': str(width),
            'height': str(height),
            'viewBox': f'0 0 {width} {height}',
            'xmlns': 'http://www.w3.org/2000/svg'
        })

        # Add defs for shadow
        defs = ET.SubElement(svg, 'defs')
        self._add_shadow_filter(defs, 'cardShadow', shadow)

        # Main card background
        rect_attrs = {
            'x': '0',
            'y': '0',
            'width': str(width),
            'height': str(height),
            'rx': str(radius),
            'fill': bg_color,
            'filter': 'url(#cardShadow)'
        }

        ET.SubElement(svg, 'rect', rect_attrs)

        # Add header section if requested
        if has_header:
            header_height = 60
            # Header divider line
            line_attrs = {
                'x1': '0',
                'y1': str(header_height),
                'x2': str(width),
                'y2': str(header_height),
                'stroke': '#e5e5e5',
                'stroke-width': '1'
            }
            ET.SubElement(svg, 'line', line_attrs)

            # Header text
            text_attrs = {
                'x': '20',
                'y': '30',
                'fill': '#171717',
                'font-family': 'system-ui, -apple-system, sans-serif',
                'font-size': '18',
                'font-weight': '600'
            }
            text_elem = ET.SubElement(svg, 'text', text_attrs)
            text_elem.text = 'Card Title'

        # Add footer if requested
        if has_footer:
            footer_y = height - 60
            # Footer divider line
            line_attrs = {
                'x1': '0',
                'y1': str(footer_y),
                'x2': str(width),
                'y2': str(footer_y),
                'stroke': '#e5e5e5',
                'stroke-width': '1'
            }
            ET.SubElement(svg, 'line', line_attrs)

        return self._prettify_svg(svg)

    def generate_badge(
        self,
        label: str,
        variant: str = 'primary',
        size: str = 'md'
    ) -> str:
        """
        Generate a badge component as SVG.

        Args:
            label: Badge text
            variant: Badge variant (primary, success, warning, error, info)
            size: Badge size (sm, md, lg)

        Returns:
            SVG string
        """
        # Size mappings
        sizes = {
            'sm': {'height': 20, 'padding': 8, 'font-size': '11'},
            'md': {'height': 24, 'padding': 10, 'font-size': '12'},
            'lg': {'height': 28, 'padding': 12, 'font-size': '14'}
        }

        size_config = sizes.get(size, sizes['md'])

        # Estimate width based on text length
        char_width = 7 if size == 'sm' else 8
        width = len(label) * char_width + size_config['padding'] * 2
        height = size_config['height']

        radius = height // 2
        bg_color = self._get_badge_color(variant)
        text_color = '#ffffff'

        svg = ET.Element('svg', {
            'width': str(width),
            'height': str(height),
            'viewBox': f'0 0 {width} {height}',
            'xmlns': 'http://www.w3.org/2000/svg'
        })

        # Background
        rect_attrs = {
            'x': '0',
            'y': '0',
            'width': str(width),
            'height': str(height),
            'rx': str(radius),
            'fill': bg_color
        }

        ET.SubElement(svg, 'rect', rect_attrs)

        # Text
        text_attrs = {
            'x': str(width / 2),
            'y': str(height / 2),
            'text-anchor': 'middle',
            'dominant-baseline': 'middle',
            'fill': text_color,
            'font-family': 'system-ui, -apple-system, sans-serif',
            'font-size': size_config['font-size'],
            'font-weight': '500'
        }

        text_elem = ET.SubElement(svg, 'text', text_attrs)
        text_elem.text = label

        return self._prettify_svg(svg)

    def generate_switch(
        self,
        width: int = 44,
        height: int = 24,
        checked: bool = False
    ) -> str:
        """
        Generate a toggle switch component as SVG.

        Args:
            width: Switch width in pixels
            height: Switch height in pixels
            checked: Whether switch is in checked state

        Returns:
            SVG string
        """
        radius = height // 2
        knob_size = height - 4
        knob_x = width - knob_size - 2 if checked else 2

        bg_color = self._resolve_token('{color.primary.500}') if checked else '#d4d4d4'

        svg = ET.Element('svg', {
            'width': str(width),
            'height': str(height),
            'viewBox': f'0 0 {width} {height}',
            'xmlns': 'http://www.w3.org/2000/svg'
        })

        # Track background
        track_attrs = {
            'x': '0',
            'y': '0',
            'width': str(width),
            'height': str(height),
            'rx': str(radius),
            'fill': bg_color
        }

        ET.SubElement(svg, 'rect', track_attrs)

        # Knob
        knob_attrs = {
            'cx': str(knob_x + knob_size / 2),
            'cy': str(height / 2),
            'r': str(knob_size / 2),
            'fill': '#ffffff'
        }

        ET.SubElement(svg, 'circle', knob_attrs)

        return self._prettify_svg(svg)

    # Helper methods

    def _get_button_color(self, variant: str, state: str) -> str:
        """Get button background color based on variant and state."""
        color_map = {
            'primary': {
                'default': self._resolve_token('{color.primary.500}'),
                'hover': self._resolve_token('{color.primary.600}'),
                'active': self._resolve_token('{color.primary.700}'),
                'disabled': '#d4d4d4'
            },
            'secondary': {
                'default': self._resolve_token('{color.secondary.500}'),
                'hover': self._resolve_token('{color.secondary.600}'),
                'active': self._resolve_token('{color.secondary.700}'),
                'disabled': '#d4d4d4'
            },
            'ghost': {
                'default': 'transparent',
                'hover': '#f5f5f5',
                'active': '#e5e5e5',
                'disabled': 'transparent'
            },
            'danger': {
                'default': '#ef4444',
                'hover': '#dc2626',
                'active': '#b91c1c',
                'disabled': '#d4d4d4'
            }
        }

        return color_map.get(variant, color_map['primary']).get(state, color_map['primary']['default'])

    def _get_button_text_color(self, variant: str) -> str:
        """Get button text color based on variant."""
        if variant == 'ghost':
            return '#171717'
        return '#ffffff'

    def _get_button_border_color(self, variant: str, state: str) -> Optional[str]:
        """Get button border color if needed."""
        if variant == 'ghost':
            return '#d4d4d4' if state != 'hover' else '#a3a3a3'
        return None

    def _get_input_border_color(self, state: str) -> str:
        """Get input border color based on state."""
        state_map = {
            'default': '#d4d4d4',
            'focus': self._resolve_token('{color.primary.500}'),
            'error': '#ef4444',
            'disabled': '#e5e5e5'
        }
        return state_map.get(state, state_map['default'])

    def _get_input_bg_color(self, state: str) -> str:
        """Get input background color based on state."""
        return '#fafafa' if state == 'disabled' else '#ffffff'

    def _get_badge_color(self, variant: str) -> str:
        """Get badge background color based on variant."""
        color_map = {
            'primary': self._resolve_token('{color.primary.500}'),
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'info': '#3b82f6'
        }
        return color_map.get(variant, color_map['primary'])

    def _get_shadow(self, variant: str, state: str) -> Optional[str]:
        """Get shadow value for component."""
        if variant == 'ghost' or state == 'disabled':
            return None
        return self.primitive.get('shadow', {}).get('sm', '')

    def _add_shadow_filter(self, defs: ET.Element, filter_id: str, shadow: str) -> None:
        """Add shadow filter to SVG defs."""
        if not shadow or shadow == 'none':
            return

        # Simple shadow filter
        filter_elem = ET.SubElement(defs, 'filter', {'id': filter_id})

        # Gaussian blur
        ET.SubElement(filter_elem, 'feGaussianBlur', {
            'in': 'SourceAlpha',
            'stdDeviation': '2'
        })

        # Offset
        ET.SubElement(filter_elem, 'feOffset', {
            'dx': '0',
            'dy': '2',
            'result': 'offsetblur'
        })

        # Merge
        merge = ET.SubElement(filter_elem, 'feMerge')
        ET.SubElement(merge, 'feMergeNode')
        ET.SubElement(merge, 'feMergeNode', {'in': 'SourceGraphic'})

    def _add_search_icon(self, svg: ET.Element, x: float, y: float) -> None:
        """Add a simple search icon to SVG."""
        # Circle
        circle_attrs = {
            'cx': str(x + 8),
            'cy': str(y + 8),
            'r': '6',
            'stroke': '#737373',
            'stroke-width': '2',
            'fill': 'none'
        }
        ET.SubElement(svg, 'circle', circle_attrs)

        # Handle
        line_attrs = {
            'x1': str(x + 13),
            'y1': str(y + 13),
            'x2': str(x + 16),
            'y2': str(y + 16),
            'stroke': '#737373',
            'stroke-width': '2',
            'stroke-linecap': 'round'
        }
        ET.SubElement(svg, 'line', line_attrs)

    def _resolve_token(self, token_ref: str) -> str:
        """Resolve token reference like {color.primary.500} to actual value."""
        if not token_ref.startswith('{') or not token_ref.endswith('}'):
            return token_ref

        # Remove braces
        path = token_ref[1:-1].split('.')

        # Navigate token structure
        value = self.primitive
        for key in path:
            if isinstance(value, dict):
                value = value.get(key, token_ref)
            else:
                return token_ref

        return value if isinstance(value, str) else token_ref

    def _parse_px(self, value: str) -> int:
        """Parse pixel value from string like '8px'."""
        if isinstance(value, int):
            return value
        try:
            return int(value.replace('px', ''))
        except (ValueError, AttributeError):
            return 8

    def _prettify_svg(self, elem: ET.Element) -> str:
        """Convert ET.Element to pretty-printed SVG string."""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='  ').split('\n', 1)[1]  # Remove XML declaration
