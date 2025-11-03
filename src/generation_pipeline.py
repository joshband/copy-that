"""
Generation Pipeline - Main orchestrator for the generative UI system.

This module ties together all components: analysis, token generation,
component generation, and export.
"""

from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json
import cv2
import numpy as np

from .visual_dna import VisualDNAExtractor
from .design_tokens import DesignTokenGenerator
from .component_generator import ParametricComponentGenerator, ComponentLibrary
from .image_processor import EnhancedImageProcessor


class GenerativeUISystem:
    """
    Complete generative UI system that analyzes reference images and
    generates production-ready design systems.
    """

    def __init__(self, use_openai: bool = True, api_key: Optional[str] = None):
        """
        Initialize the generative UI system.

        Args:
            use_openai: Whether to use OpenAI for enhanced analysis
            api_key: Optional OpenAI API key
        """
        self.use_openai = use_openai
        self.api_key = api_key

        # Initialize components
        self.visual_dna_extractor = VisualDNAExtractor()
        self.token_generator = DesignTokenGenerator()
        self.image_processor = EnhancedImageProcessor(use_openai=use_openai, api_key=api_key)

        # Storage for analysis results
        self.visual_dna = None
        self.design_tokens = None
        self.ai_analysis = None
        self.component_library = None

    def analyze_reference(
        self,
        image_path: Union[str, Path],
        include_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a reference image to extract visual DNA.

        Args:
            image_path: Path to reference image
            include_ai: Whether to include AI-powered analysis

        Returns:
            Visual DNA profile
        """
        print(f"\n{'='*60}")
        print("ANALYZING REFERENCE IMAGE")
        print(f"{'='*60}\n")

        # Load image
        image = self.image_processor.load_image(image_path)

        # Extract visual DNA
        self.visual_dna = self.visual_dna_extractor.extract_visual_dna(image)

        # Optionally get AI insights
        if include_ai and self.use_openai:
            print("\nRunning AI-enhanced analysis...")
            try:
                self.ai_analysis = self.image_processor.openai_analyzer.comprehensive_analysis(image_path)
                # Merge AI insights into visual DNA
                self._merge_ai_insights(self.ai_analysis)
            except Exception as e:
                print(f"Warning: AI analysis failed: {e}")
                self.ai_analysis = None

        return self.visual_dna

    def generate_design_system(
        self,
        visual_dna: Optional[Dict[str, Any]] = None,
        components: Optional[List[str]] = None,
        output_dir: Optional[Path] = None
    ) -> ComponentLibrary:
        """
        Generate a complete design system from visual DNA.

        Args:
            visual_dna: Optional visual DNA (uses stored if not provided)
            components: Optional list of components to generate
            output_dir: Optional directory to save output

        Returns:
            Generated component library
        """
        print(f"\n{'='*60}")
        print("GENERATING DESIGN SYSTEM")
        print(f"{'='*60}\n")

        # Use provided or stored visual DNA
        if visual_dna is None:
            visual_dna = self.visual_dna

        if visual_dna is None:
            raise ValueError("No visual DNA available. Run analyze_reference() first.")

        # Generate design tokens
        print("Step 1: Generating Design Tokens...")
        self.design_tokens = self.token_generator.generate_tokens(visual_dna)

        # Generate components
        print("\nStep 2: Generating UI Components...")
        component_gen = ParametricComponentGenerator(visual_dna, self.design_tokens)
        self.component_library = component_gen.generate_library(output_dir=output_dir)

        print(f"\n{'='*60}")
        print("GENERATION COMPLETE")
        print(f"{'='*60}")
        print(f"Components: {self.component_library.metadata['component_count']}")
        total_variants = sum(
            len(c.get('variants', {}))
            for c in self.component_library.components.values()
        )
        print(f"Total variants: {total_variants}")

        return self.component_library

    def export_design_system(
        self,
        output_dir: Path,
        formats: Optional[List[str]] = None
    ) -> Dict[str, Path]:
        """
        Export design system in various formats.

        Args:
            output_dir: Output directory
            formats: List of formats (css, json, tailwind, figma)

        Returns:
            Dictionary mapping format to output path
        """
        if formats is None:
            formats = ['css', 'json', 'tailwind']

        if self.design_tokens is None:
            raise ValueError("No design tokens available. Run generate_design_system() first.")

        print(f"\n{'='*60}")
        print("EXPORTING DESIGN SYSTEM")
        print(f"{'='*60}\n")

        output_dir = Path(output_dir)
        tokens_dir = output_dir / 'tokens'
        tokens_dir.mkdir(parents=True, exist_ok=True)

        exported = {}

        if 'css' in formats:
            css_file = tokens_dir / 'tokens.css'
            css_content = self.token_generator.export_css()
            css_file.write_text(css_content)
            exported['css'] = css_file
            print(f"  ✓ Exported CSS tokens: {css_file}")

        if 'json' in formats:
            json_file = tokens_dir / 'tokens.json'
            json_content = self.token_generator.export_json()
            json_file.write_text(json_content)
            exported['json'] = json_file
            print(f"  ✓ Exported JSON tokens: {json_file}")

        if 'tailwind' in formats:
            tailwind_file = tokens_dir / 'tailwind.config.js'
            tailwind_content = self.token_generator.export_tailwind_config()
            tailwind_file.write_text(tailwind_content)
            exported['tailwind'] = tailwind_file
            print(f"  ✓ Exported Tailwind config: {tailwind_file}")

        # Export visual DNA
        dna_file = output_dir / 'analysis' / 'visual-dna.json'
        dna_file.parent.mkdir(parents=True, exist_ok=True)
        with open(dna_file, 'w') as f:
            json.dump(self.visual_dna, f, indent=2)
        exported['visual_dna'] = dna_file
        print(f"  ✓ Exported Visual DNA: {dna_file}")

        # Export AI analysis if available
        if self.ai_analysis:
            ai_file = output_dir / 'analysis' / 'ai-analysis.json'
            with open(ai_file, 'w') as f:
                json.dump(self.ai_analysis, f, indent=2)
            exported['ai_analysis'] = ai_file
            print(f"  ✓ Exported AI analysis: {ai_file}")

        return exported

    def generate_component_code(
        self,
        component_type: str,
        framework: str = 'react'
    ) -> str:
        """
        Generate code for a specific component.

        Args:
            component_type: Type of component (button, input, etc.)
            framework: Target framework (react, vue, svelte)

        Returns:
            Component code as string
        """
        if self.component_library is None:
            raise ValueError("No component library available. Run generate_design_system() first.")

        component_data = self.component_library.components.get(component_type)
        if not component_data:
            raise ValueError(f"Component '{component_type}' not found in library")

        if framework == 'react':
            return self._generate_react_component(component_type, component_data)
        elif framework == 'vue':
            return self._generate_vue_component(component_type, component_data)
        else:
            raise ValueError(f"Unsupported framework: {framework}")

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the generated design system.

        Returns:
            Summary dictionary
        """
        summary = {
            'has_visual_dna': self.visual_dna is not None,
            'has_design_tokens': self.design_tokens is not None,
            'has_components': self.component_library is not None,
            'has_ai_analysis': self.ai_analysis is not None
        }

        if self.visual_dna:
            summary['visual_style'] = {
                'corner_style': self.visual_dna.get('corner_style', {}).get('corner_style'),
                'color_harmony': self.visual_dna.get('color_genome', {}).get('harmony_type'),
                'elevation_style': self.visual_dna.get('elevation_model', {}).get('elevation_style'),
                'grid_type': self.visual_dna.get('spatial_rhythm', {}).get('grid_type')
            }

        if self.design_tokens:
            summary['design_tokens'] = {
                'color_scales': len(self.design_tokens.get('primitive', {}).get('color', {})),
                'spacing_values': len(self.design_tokens.get('primitive', {}).get('spacing', {})),
                'has_typography': 'typography' in self.design_tokens.get('primitive', {})
            }

        if self.component_library:
            summary['components'] = {
                'count': self.component_library.metadata['component_count'],
                'types': list(self.component_library.components.keys()),
                'total_variants': sum(
                    len(c.get('variants', {}))
                    for c in self.component_library.components.values()
                )
            }

        return summary

    # Helper methods

    def _merge_ai_insights(self, ai_analysis: Dict[str, Any]) -> None:
        """Merge AI analysis insights into visual DNA."""
        if not ai_analysis:
            return

        # Add AI insights to visual DNA
        self.visual_dna['ai_insights'] = {
            'style_analysis': ai_analysis.get('style_analysis', {}),
            'components_detected': ai_analysis.get('components', {}),
            'tokens_suggested': ai_analysis.get('design_tokens', {})
        }

    def _generate_react_component(
        self,
        component_type: str,
        component_data: Dict[str, Any]
    ) -> str:
        """Generate React component code."""
        component_name = component_type.capitalize()

        code = f"""import React from 'react';
import './styles.css';

interface {component_name}Props {{
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  disabled?: boolean;
  children?: React.ReactNode;
}}

export const {component_name}: React.FC<{component_name}Props> = ({{
  variant = 'primary',
  size = 'md',
  disabled = false,
  children,
  ...props
}}) => {{
  const className = `{component_type} {component_type}-${{variant}} {component_type}-${{size}} ${{disabled ? '{component_type}-disabled' : ''}}`;

  return (
    <{component_type} className={{className}} disabled={{disabled}} {{...props}}>
      {{children}}
    </{component_type}>
  );
}};
"""

        return code

    def _generate_vue_component(
        self,
        component_type: str,
        component_data: Dict[str, Any]
    ) -> str:
        """Generate Vue component code."""
        component_name = component_type.capitalize()

        code = f"""<template>
  <{component_type}
    :class="componentClass"
    :disabled="disabled"
  >
    <slot />
  </{component_type}>
</template>

<script lang="ts">
import {{ defineComponent, computed }} from 'vue';

export default defineComponent({{
  name: '{component_name}',
  props: {{
    variant: {{
      type: String,
      default: 'primary',
      validator: (value: string) => ['primary', 'secondary', 'ghost', 'danger'].includes(value)
    }},
    size: {{
      type: String,
      default: 'md',
      validator: (value: string) => ['sm', 'md', 'lg', 'xl'].includes(value)
    }},
    disabled: {{
      type: Boolean,
      default: false
    }}
  }},
  setup(props) {{
    const componentClass = computed(() => {{
      return [
        '{component_type}',
        `{component_type}-${{props.variant}}`,
        `{component_type}-${{props.size}}`,
        {{ '{component_type}-disabled': props.disabled }}
      ];
    }});

    return {{ componentClass }};
  }}
}});
</script>

<style scoped>
@import './styles.css';
</style>
"""

        return code


# Convenience function for quick generation
def generate_from_image(
    image_path: Union[str, Path],
    output_dir: Union[str, Path],
    use_openai: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to generate a complete design system from a single image.

    Args:
        image_path: Path to reference image
        output_dir: Output directory
        use_openai: Whether to use OpenAI for enhanced analysis

    Returns:
        Summary of generated system
    """
    system = GenerativeUISystem(use_openai=use_openai)

    # Analyze
    system.analyze_reference(image_path, include_ai=use_openai)

    # Generate
    output_path = Path(output_dir)
    system.generate_design_system(output_dir=output_path)

    # Export
    system.export_design_system(output_path, formats=['css', 'json', 'tailwind'])

    return system.get_summary()
