"""
Design Token Generator - Generates industry-standard design tokens from Visual DNA.

This module creates reusable design tokens (colors, spacing, typography, effects)
that can be used across platforms (web, iOS, Android, etc.).
"""

from typing import Dict, List, Any, Optional
import json
from pathlib import Path
import colorsys


class DesignTokenGenerator:
    """
    Generates design tokens following the Design Tokens Community Group specification.

    Creates both primitive tokens (raw values) and semantic tokens (contextual usage).
    """

    def __init__(self):
        """Initialize the design token generator."""
        self.tokens = {
            'primitive': {},
            'semantic': {}
        }

    def generate_tokens(self, visual_dna: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete design token system from Visual DNA.

        Args:
            visual_dna: Visual DNA extracted from reference image

        Returns:
            Complete design token system
        """
        print("Generating design tokens...")

        # Generate primitive tokens
        self.tokens['primitive'] = {
            'color': self._generate_color_tokens(visual_dna['color_genome']),
            'spacing': self._generate_spacing_tokens(visual_dna['spatial_rhythm']),
            'borderRadius': self._generate_radius_tokens(visual_dna['corner_style']),
            'shadow': self._generate_shadow_tokens(visual_dna['elevation_model']),
            'typography': self._generate_typography_tokens(),
        }

        # Generate semantic tokens
        self.tokens['semantic'] = {
            'color': self._generate_semantic_colors(self.tokens['primitive']['color']),
            'spacing': self._generate_semantic_spacing(self.tokens['primitive']['spacing']),
            'component': self._generate_component_tokens(visual_dna)
        }

        return self.tokens

    def _generate_color_tokens(self, color_genome: Dict[str, Any]) -> Dict[str, Any]:
        """Generate primitive color tokens."""
        print("  - Generating color tokens...")

        palette = color_genome['palette']

        # Extract key colors
        primary_hex = color_genome['primary_color']
        secondary_hex = color_genome['secondary_color']
        accent_hex = color_genome['accent_color']

        # Generate color scales (50-900)
        tokens = {
            'primary': self._generate_color_scale(primary_hex),
            'secondary': self._generate_color_scale(secondary_hex),
            'accent': self._generate_color_scale(accent_hex),
        }

        # Add grayscale
        tokens['gray'] = {
            '50': '#fafafa',
            '100': '#f5f5f5',
            '200': '#e5e5e5',
            '300': '#d4d4d4',
            '400': '#a3a3a3',
            '500': '#737373',
            '600': '#525252',
            '700': '#404040',
            '800': '#262626',
            '900': '#171717',
        }

        # Add semantic colors
        tokens['white'] = '#ffffff'
        tokens['black'] = '#000000'
        tokens['success'] = {'500': '#10b981'}
        tokens['warning'] = {'500': '#f59e0b'}
        tokens['error'] = {'500': '#ef4444'}
        tokens['info'] = {'500': '#3b82f6'}

        return tokens

    def _generate_color_scale(self, hex_color: str) -> Dict[str, str]:
        """Generate a color scale from a base color (50-900)."""
        # Convert hex to RGB
        rgb = self._hex_to_rgb(hex_color)
        h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)

        scale = {}

        # Generate lighter shades (50-400)
        for i, value in enumerate([50, 100, 200, 300, 400]):
            # Increase lightness
            factor = 1 + (9 - i * 2) * 0.08
            new_v = min(v * factor, 1.0)
            new_s = max(s * (1 - (9 - i * 2) * 0.08), 0.1)

            r, g, b = colorsys.hsv_to_rgb(h, new_s, new_v)
            scale[str(value)] = self._rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))

        # Base color (500)
        scale['500'] = hex_color

        # Generate darker shades (600-900)
        for i, value in enumerate([600, 700, 800, 900]):
            # Decrease lightness
            factor = 1 - (i + 1) * 0.15
            new_v = max(v * factor, 0.1)
            new_s = min(s * (1 + (i + 1) * 0.1), 1.0)

            r, g, b = colorsys.hsv_to_rgb(h, new_s, new_v)
            scale[str(value)] = self._rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))

        return scale

    def _generate_spacing_tokens(self, spatial_rhythm: Dict[str, Any]) -> Dict[str, str]:
        """Generate spacing tokens."""
        print("  - Generating spacing tokens...")

        base_unit = spatial_rhythm.get('base_unit', 8)

        # Generate spacing scale based on base unit
        spacing = {
            '0': '0px',
            '1': f'{base_unit // 2}px',  # 4px if base is 8
            '2': f'{base_unit}px',  # 8px
            '3': f'{base_unit + base_unit // 2}px',  # 12px
            '4': f'{base_unit * 2}px',  # 16px
            '5': f'{base_unit * 2 + base_unit // 2}px',  # 20px
            '6': f'{base_unit * 3}px',  # 24px
            '8': f'{base_unit * 4}px',  # 32px
            '10': f'{base_unit * 5}px',  # 40px
            '12': f'{base_unit * 6}px',  # 48px
            '16': f'{base_unit * 8}px',  # 64px
            '20': f'{base_unit * 10}px',  # 80px
            '24': f'{base_unit * 12}px',  # 96px
        }

        return spacing

    def _generate_radius_tokens(self, corner_style: Dict[str, Any]) -> Dict[str, str]:
        """Generate border radius tokens."""
        print("  - Generating border radius tokens...")

        base_radius = corner_style.get('estimated_radius', 8)

        if corner_style['corner_style'] == 'sharp':
            return {
                'none': '0px',
                'sm': '2px',
                'md': '4px',
                'lg': '6px',
                'xl': '8px',
                'full': '9999px'
            }
        elif corner_style['corner_style'] == 'slightly_rounded':
            return {
                'none': '0px',
                'sm': '4px',
                'md': '6px',
                'lg': '8px',
                'xl': '12px',
                'full': '9999px'
            }
        elif corner_style['corner_style'] == 'rounded':
            return {
                'none': '0px',
                'sm': '6px',
                'md': '8px',
                'lg': '12px',
                'xl': '16px',
                'full': '9999px'
            }
        else:  # heavily_rounded
            return {
                'none': '0px',
                'sm': '8px',
                'md': '12px',
                'lg': '16px',
                'xl': '24px',
                'full': '9999px'
            }

    def _generate_shadow_tokens(self, elevation_model: Dict[str, Any]) -> Dict[str, str]:
        """Generate shadow tokens for elevation."""
        print("  - Generating shadow tokens...")

        style = elevation_model.get('elevation_style', 'subtle')

        if style == 'flat':
            return {
                'none': 'none',
                'sm': '0 1px 2px rgba(0, 0, 0, 0.03)',
                'md': '0 2px 4px rgba(0, 0, 0, 0.05)',
                'lg': '0 4px 6px rgba(0, 0, 0, 0.07)',
                'xl': '0 8px 12px rgba(0, 0, 0, 0.10)',
            }
        elif style == 'subtle':
            return {
                'none': 'none',
                'sm': '0 1px 2px rgba(0, 0, 0, 0.05)',
                'md': '0 4px 6px rgba(0, 0, 0, 0.1)',
                'lg': '0 10px 15px rgba(0, 0, 0, 0.1)',
                'xl': '0 20px 25px rgba(0, 0, 0, 0.15)',
            }
        elif style == 'moderate':
            return {
                'none': 'none',
                'sm': '0 2px 4px rgba(0, 0, 0, 0.1)',
                'md': '0 4px 8px rgba(0, 0, 0, 0.15)',
                'lg': '0 12px 20px rgba(0, 0, 0, 0.2)',
                'xl': '0 24px 32px rgba(0, 0, 0, 0.25)',
            }
        else:  # dramatic
            return {
                'none': 'none',
                'sm': '0 4px 6px rgba(0, 0, 0, 0.15)',
                'md': '0 8px 12px rgba(0, 0, 0, 0.2)',
                'lg': '0 16px 24px rgba(0, 0, 0, 0.25)',
                'xl': '0 32px 48px rgba(0, 0, 0, 0.3)',
            }

    def _generate_typography_tokens(self) -> Dict[str, Any]:
        """Generate typography tokens."""
        print("  - Generating typography tokens...")

        return {
            'fontFamily': {
                'sans': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                'serif': 'Georgia, Cambria, "Times New Roman", Times, serif',
                'mono': 'Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace'
            },
            'fontSize': {
                'xs': '12px',
                'sm': '14px',
                'base': '16px',
                'lg': '18px',
                'xl': '20px',
                '2xl': '24px',
                '3xl': '30px',
                '4xl': '36px',
                '5xl': '48px',
            },
            'fontWeight': {
                'light': '300',
                'normal': '400',
                'medium': '500',
                'semibold': '600',
                'bold': '700',
            },
            'lineHeight': {
                'tight': '1.25',
                'normal': '1.5',
                'relaxed': '1.75',
            },
            'letterSpacing': {
                'tight': '-0.05em',
                'normal': '0',
                'wide': '0.05em',
            }
        }

    def _generate_semantic_colors(self, primitive_colors: Dict[str, Any]) -> Dict[str, Any]:
        """Generate semantic color tokens."""
        print("  - Generating semantic color tokens...")

        return {
            'background': {
                'primary': '{color.white}',
                'secondary': '{color.gray.50}',
                'tertiary': '{color.gray.100}',
                'elevated': '{color.white}',
                'overlay': 'rgba(0, 0, 0, 0.5)',
            },
            'text': {
                'primary': '{color.gray.900}',
                'secondary': '{color.gray.600}',
                'tertiary': '{color.gray.500}',
                'inverse': '{color.white}',
                'disabled': '{color.gray.400}',
            },
            'border': {
                'default': '{color.gray.300}',
                'hover': '{color.gray.400}',
                'focus': '{color.primary.500}',
                'error': '{color.error.500}',
            },
            'action': {
                'primary': '{color.primary.500}',
                'primaryHover': '{color.primary.600}',
                'primaryActive': '{color.primary.700}',
                'secondary': '{color.secondary.500}',
                'secondaryHover': '{color.secondary.600}',
                'danger': '{color.error.500}',
                'dangerHover': '{color.error.600}',
            },
            'status': {
                'success': '{color.success.500}',
                'warning': '{color.warning.500}',
                'error': '{color.error.500}',
                'info': '{color.info.500}',
            }
        }

    def _generate_semantic_spacing(self, primitive_spacing: Dict[str, str]) -> Dict[str, Any]:
        """Generate semantic spacing tokens."""
        return {
            'component': {
                'paddingX': '{spacing.4}',
                'paddingY': '{spacing.2}',
                'gap': '{spacing.2}',
            },
            'layout': {
                'containerPadding': '{spacing.6}',
                'sectionGap': '{spacing.12}',
                'itemGap': '{spacing.4}',
            }
        }

    def _generate_component_tokens(self, visual_dna: Dict[str, Any]) -> Dict[str, Any]:
        """Generate component-specific tokens."""
        return {
            'button': {
                'paddingX': '{spacing.component.paddingX}',
                'paddingY': '{spacing.component.paddingY}',
                'borderRadius': '{borderRadius.md}',
                'fontSize': '{typography.fontSize.base}',
                'fontWeight': '{typography.fontWeight.medium}',
                'minWidth': '88px',
                'minHeight': '36px',
            },
            'input': {
                'paddingX': '{spacing.3}',
                'paddingY': '{spacing.2}',
                'borderRadius': '{borderRadius.md}',
                'borderWidth': '1px',
                'fontSize': '{typography.fontSize.base}',
                'minHeight': '40px',
            },
            'card': {
                'padding': '{spacing.6}',
                'borderRadius': '{borderRadius.lg}',
                'shadow': '{shadow.md}',
                'gap': '{spacing.4}',
            }
        }

    def export_css(self) -> str:
        """Export tokens as CSS variables."""
        css_lines = [':root {']

        # Colors
        if 'color' in self.tokens['primitive']:
            for color_name, color_value in self.tokens['primitive']['color'].items():
                if isinstance(color_value, dict):
                    for shade, hex_val in color_value.items():
                        css_lines.append(f'  --color-{color_name}-{shade}: {hex_val};')
                else:
                    css_lines.append(f'  --color-{color_name}: {color_value};')

        # Spacing
        if 'spacing' in self.tokens['primitive']:
            for key, value in self.tokens['primitive']['spacing'].items():
                css_lines.append(f'  --spacing-{key}: {value};')

        # Border radius
        if 'borderRadius' in self.tokens['primitive']:
            for key, value in self.tokens['primitive']['borderRadius'].items():
                css_lines.append(f'  --radius-{key}: {value};')

        # Shadows
        if 'shadow' in self.tokens['primitive']:
            for key, value in self.tokens['primitive']['shadow'].items():
                css_lines.append(f'  --shadow-{key}: {value};')

        # Typography
        if 'typography' in self.tokens['primitive']:
            typo = self.tokens['primitive']['typography']
            if 'fontSize' in typo:
                for key, value in typo['fontSize'].items():
                    css_lines.append(f'  --font-size-{key}: {value};')
            if 'fontWeight' in typo:
                for key, value in typo['fontWeight'].items():
                    css_lines.append(f'  --font-weight-{key}: {value};')

        css_lines.append('}')
        return '\n'.join(css_lines)

    def export_json(self) -> str:
        """Export tokens as JSON."""
        return json.dumps(self.tokens, indent=2)

    def export_tailwind_config(self) -> str:
        """Export as Tailwind config."""
        config = {
            'theme': {
                'extend': {
                    'colors': {},
                    'spacing': {},
                    'borderRadius': {},
                    'boxShadow': {}
                }
            }
        }

        # Add colors
        if 'color' in self.tokens['primitive']:
            for color_name, color_value in self.tokens['primitive']['color'].items():
                if isinstance(color_value, dict):
                    config['theme']['extend']['colors'][color_name] = color_value
                else:
                    config['theme']['extend']['colors'][color_name] = color_value

        # Add spacing
        if 'spacing' in self.tokens['primitive']:
            config['theme']['extend']['spacing'] = self.tokens['primitive']['spacing']

        # Add border radius
        if 'borderRadius' in self.tokens['primitive']:
            config['theme']['extend']['borderRadius'] = self.tokens['primitive']['borderRadius']

        # Add shadows
        if 'shadow' in self.tokens['primitive']:
            config['theme']['extend']['boxShadow'] = self.tokens['primitive']['shadow']

        return f"module.exports = {json.dumps(config, indent=2)}"

    # Helper methods

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, r: int, g: int, b: int) -> str:
        """Convert RGB to hex color."""
        return f'#{r:02x}{g:02x}{b:02x}'
