"""
Parametric Component Generator - Generates complete UI component libraries.

This module creates entire families of UI components with multiple variants,
sizes, states, and themes based on extracted visual DNA and design tokens.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from .svg_generator import SVGGenerator


class ComponentLibrary:
    """Represents a complete UI component library."""

    def __init__(self, name: str, version: str = "1.0.0"):
        """
        Initialize a component library.

        Args:
            name: Library name
            version: Semantic version
        """
        self.name = name
        self.version = version
        self.components = {}
        self.metadata = {
            'name': name,
            'version': version,
            'generated_at': datetime.now().isoformat(),
            'component_count': 0
        }

    def add_component(self, component_type: str, component_data: Dict[str, Any]) -> None:
        """Add a component family to the library."""
        self.components[component_type] = component_data
        self.metadata['component_count'] = len(self.components)

    def to_dict(self) -> Dict[str, Any]:
        """Convert library to dictionary format."""
        return {
            'metadata': self.metadata,
            'components': self.components
        }

    def save(self, output_dir: Path) -> None:
        """Save the library to disk."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata
        metadata_file = output_dir / 'library.json'
        with open(metadata_file, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


class ParametricComponentGenerator:
    """
    Creates UI components using parametric generation based on design rules.

    Instead of extracting existing components, this generates new ones that
    follow the extracted visual style.
    """

    def __init__(
        self,
        visual_dna: Dict[str, Any],
        design_tokens: Dict[str, Any]
    ):
        """
        Initialize the parametric component generator.

        Args:
            visual_dna: Extracted visual DNA
            design_tokens: Generated design tokens
        """
        self.visual_dna = visual_dna
        self.design_tokens = design_tokens
        self.design_rules = visual_dna.get('design_rules', {})
        self.svg_generator = SVGGenerator(design_tokens)

        # Component configurations
        self.size_variants = {
            'sm': {'scale': 0.875},
            'md': {'scale': 1.0},
            'lg': {'scale': 1.25},
            'xl': {'scale': 1.5}
        }

        self.state_variants = ['default', 'hover', 'active', 'disabled', 'focus']
        self.theme_variants = ['light', 'dark']

    def generate_library(self, output_dir: Optional[Path] = None) -> ComponentLibrary:
        """
        Generate a complete UI component library.

        Args:
            output_dir: Optional directory to save components

        Returns:
            ComponentLibrary object
        """
        print("Generating complete component library...")

        library = ComponentLibrary("Generated Design System")

        # Generate component families
        library.add_component('button', self.generate_button_family())
        library.add_component('input', self.generate_input_family())
        library.add_component('card', self.generate_card_family())
        library.add_component('badge', self.generate_badge_family())
        library.add_component('switch', self.generate_switch_family())

        # Save if output directory provided
        if output_dir:
            self._save_library(library, output_dir)

        return library

    def generate_button_family(self) -> Dict[str, Any]:
        """Generate a complete button component family."""
        print("  - Generating button family...")

        family = {
            'type': 'atom',
            'description': 'Interactive button component',
            'variants': {},
            'metadata': self._create_component_metadata('button')
        }

        type_variants = ['primary', 'secondary', 'ghost', 'danger']

        for button_type in type_variants:
            for size_name, size_config in self.size_variants.items():
                for state in self.state_variants:
                    if state == 'focus':  # Focus is mainly for inputs
                        continue

                    # Calculate dimensions
                    base_width = 120
                    base_height = 40
                    width = int(base_width * size_config['scale'])
                    height = int(base_height * size_config['scale'])

                    # Generate SVG
                    svg = self.svg_generator.generate_button(
                        width=width,
                        height=height,
                        variant=button_type,
                        state=state,
                        label='Button'
                    )

                    # Create variant key
                    variant_key = f'{button_type}-{size_name}-{state}'
                    family['variants'][variant_key] = {
                        'svg': svg,
                        'type': button_type,
                        'size': size_name,
                        'state': state,
                        'dimensions': {'width': width, 'height': height}
                    }

        return family

    def generate_input_family(self) -> Dict[str, Any]:
        """Generate a complete input component family."""
        print("  - Generating input family...")

        family = {
            'type': 'atom',
            'description': 'Text input component',
            'variants': {},
            'metadata': self._create_component_metadata('input')
        }

        input_states = ['default', 'focus', 'error', 'disabled']

        for size_name, size_config in self.size_variants.items():
            for state in input_states:
                for has_icon in [False, True]:
                    # Calculate dimensions
                    base_width = 280
                    base_height = 40
                    width = int(base_width * size_config['scale'])
                    height = int(base_height * size_config['scale'])

                    # Generate SVG
                    svg = self.svg_generator.generate_input(
                        width=width,
                        height=height,
                        state=state,
                        placeholder='Enter text...',
                        has_icon=has_icon
                    )

                    # Create variant key
                    icon_suffix = '-with-icon' if has_icon else ''
                    variant_key = f'text-{size_name}-{state}{icon_suffix}'
                    family['variants'][variant_key] = {
                        'svg': svg,
                        'size': size_name,
                        'state': state,
                        'has_icon': has_icon,
                        'dimensions': {'width': width, 'height': height}
                    }

        return family

    def generate_card_family(self) -> Dict[str, Any]:
        """Generate a complete card component family."""
        print("  - Generating card family...")

        family = {
            'type': 'organism',
            'description': 'Card container component',
            'variants': {},
            'metadata': self._create_component_metadata('card')
        }

        card_configs = [
            {'has_header': True, 'has_footer': False, 'elevation': 'sm'},
            {'has_header': True, 'has_footer': False, 'elevation': 'md'},
            {'has_header': True, 'has_footer': False, 'elevation': 'lg'},
            {'has_header': True, 'has_footer': True, 'elevation': 'md'},
            {'has_header': False, 'has_footer': False, 'elevation': 'md'},
        ]

        for size_name, size_config in self.size_variants.items():
            for config in card_configs:
                # Calculate dimensions
                base_width = 320
                base_height = 240
                width = int(base_width * size_config['scale'])
                height = int(base_height * size_config['scale'])

                # Generate SVG
                svg = self.svg_generator.generate_card(
                    width=width,
                    height=height,
                    has_header=config['has_header'],
                    has_footer=config['has_footer'],
                    elevation=config['elevation']
                )

                # Create variant key
                header_suffix = '-header' if config['has_header'] else ''
                footer_suffix = '-footer' if config['has_footer'] else ''
                variant_key = f'{size_name}-{config["elevation"]}{header_suffix}{footer_suffix}'

                family['variants'][variant_key] = {
                    'svg': svg,
                    'size': size_name,
                    'elevation': config['elevation'],
                    'has_header': config['has_header'],
                    'has_footer': config['has_footer'],
                    'dimensions': {'width': width, 'height': height}
                }

        return family

    def generate_badge_family(self) -> Dict[str, Any]:
        """Generate a complete badge component family."""
        print("  - Generating badge family...")

        family = {
            'type': 'atom',
            'description': 'Badge label component',
            'variants': {},
            'metadata': self._create_component_metadata('badge')
        }

        badge_variants = ['primary', 'success', 'warning', 'error', 'info']
        badge_sizes = ['sm', 'md', 'lg']

        for variant in badge_variants:
            for size in badge_sizes:
                # Generate SVG
                svg = self.svg_generator.generate_badge(
                    label=variant.capitalize(),
                    variant=variant,
                    size=size
                )

                variant_key = f'{variant}-{size}'
                family['variants'][variant_key] = {
                    'svg': svg,
                    'variant': variant,
                    'size': size
                }

        return family

    def generate_switch_family(self) -> Dict[str, Any]:
        """Generate a complete switch/toggle component family."""
        print("  - Generating switch family...")

        family = {
            'type': 'atom',
            'description': 'Toggle switch component',
            'variants': {},
            'metadata': self._create_component_metadata('switch')
        }

        switch_sizes = {
            'sm': {'width': 36, 'height': 20},
            'md': {'width': 44, 'height': 24},
            'lg': {'width': 52, 'height': 28}
        }

        for size_name, dimensions in switch_sizes.items():
            for checked in [False, True]:
                # Generate SVG
                svg = self.svg_generator.generate_switch(
                    width=dimensions['width'],
                    height=dimensions['height'],
                    checked=checked
                )

                state = 'checked' if checked else 'unchecked'
                variant_key = f'{size_name}-{state}'

                family['variants'][variant_key] = {
                    'svg': svg,
                    'size': size_name,
                    'checked': checked,
                    'dimensions': dimensions
                }

        return family

    def generate_custom_component(
        self,
        component_type: str,
        **kwargs
    ) -> str:
        """
        Generate a custom component with specific parameters.

        Args:
            component_type: Type of component (button, input, card, etc.)
            **kwargs: Component-specific parameters

        Returns:
            SVG string
        """
        generators = {
            'button': self.svg_generator.generate_button,
            'input': self.svg_generator.generate_input,
            'card': self.svg_generator.generate_card,
            'badge': self.svg_generator.generate_badge,
            'switch': self.svg_generator.generate_switch
        }

        generator = generators.get(component_type)
        if not generator:
            raise ValueError(f"Unknown component type: {component_type}")

        return generator(**kwargs)

    def _create_component_metadata(self, component_name: str) -> Dict[str, Any]:
        """Create metadata for a component."""
        return {
            'component': component_name,
            'generated_at': datetime.now().isoformat(),
            'visual_dna_source': {
                'corner_style': self.visual_dna.get('corner_style', {}).get('corner_style'),
                'color_harmony': self.visual_dna.get('color_genome', {}).get('harmony_type'),
                'elevation_style': self.visual_dna.get('elevation_model', {}).get('elevation_style')
            },
            'design_tokens_used': {
                'colors': list(self.design_tokens.get('primitive', {}).get('color', {}).keys()),
                'spacing_base': self.design_tokens.get('primitive', {}).get('spacing', {}).get('2'),
                'radius_base': self.design_tokens.get('primitive', {}).get('borderRadius', {}).get('md')
            }
        }

    def _save_library(self, library: ComponentLibrary, output_dir: Path) -> None:
        """Save component library to disk."""
        print(f"Saving component library to {output_dir}...")

        # Create output directory structure
        components_dir = output_dir / 'components'
        components_dir.mkdir(parents=True, exist_ok=True)

        # Save each component family
        for component_type, component_data in library.components.items():
            component_dir = components_dir / component_type
            component_dir.mkdir(exist_ok=True)

            # Save component metadata
            metadata_file = component_dir / f'{component_type}.metadata.json'
            with open(metadata_file, 'w') as f:
                metadata = {
                    'type': component_data.get('type'),
                    'description': component_data.get('description'),
                    'variant_count': len(component_data.get('variants', {})),
                    'metadata': component_data.get('metadata')
                }
                json.dump(metadata, f, indent=2)

            # Save SVG files for each variant
            variants_dir = component_dir / 'variants'
            variants_dir.mkdir(exist_ok=True)

            for variant_key, variant_data in component_data.get('variants', {}).items():
                svg_file = variants_dir / f'{component_type}-{variant_key}.svg'
                with open(svg_file, 'w') as f:
                    f.write(variant_data['svg'])

        # Save library metadata
        library.save(output_dir)

        print(f"  ✓ Saved {library.metadata['component_count']} component families")
        print(f"  ✓ Total variants: {sum(len(c.get('variants', {})) for c in library.components.values())}")


class VariationEngine:
    """
    Creates systematic variations of components.

    Handles size variations, state variations, color variations, and theme variations.
    """

    def __init__(self, design_tokens: Dict[str, Any]):
        """
        Initialize the variation engine.

        Args:
            design_tokens: Design token system
        """
        self.design_tokens = design_tokens

    def create_size_variations(
        self,
        base_component: Dict[str, Any],
        sizes: List[str] = ['sm', 'md', 'lg', 'xl']
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create size variations of a component.

        Args:
            base_component: Base component data
            sizes: List of size variants to generate

        Returns:
            Dictionary of size variations
        """
        scale_factors = {
            'xs': 0.75,
            'sm': 0.875,
            'md': 1.0,
            'lg': 1.25,
            'xl': 1.5,
            '2xl': 2.0
        }

        variations = {}
        base_width = base_component.get('width', 100)
        base_height = base_component.get('height', 40)

        for size in sizes:
            scale = scale_factors.get(size, 1.0)
            variations[size] = {
                **base_component,
                'width': int(base_width * scale),
                'height': int(base_height * scale),
                'size': size
            }

        return variations

    def create_theme_variations(
        self,
        component: Dict[str, Any],
        themes: List[str] = ['light', 'dark']
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create theme variations of a component.

        Args:
            component: Component data
            themes: List of themes to generate

        Returns:
            Dictionary of theme variations
        """
        # This would typically modify colors based on theme
        # For now, simplified implementation
        variations = {}

        for theme in themes:
            variations[theme] = {
                **component,
                'theme': theme
            }

        return variations
