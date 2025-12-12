"""
Mood Board Generator - AI-curated aesthetic boards using Claude + DALL-E

Uses:
- Anthropic Claude Sonnet 4.5 for content generation (themes, descriptions, references)
- OpenAI DALL-E 3 for visual image generation
"""

import json
import logging
import os
import time
from typing import Any

from anthropic import Anthropic
from openai import OpenAI

logger = logging.getLogger(__name__)


class MoodBoardGenerator:
    """Generate AI-curated mood boards from color tokens"""

    def __init__(self, anthropic_api_key: str | None = None, openai_api_key: str | None = None):
        """Initialize the mood board generator

        Args:
            anthropic_api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            openai_api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.anthropic = Anthropic(api_key=anthropic_api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.openai = OpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"))
        self.claude_model = "claude-sonnet-4-5-20250929"
        self.dalle_model = "dall-e-3"

    async def generate(
        self,
        colors: list[Any],
        num_variants: int = 2,
        include_images: bool = True,
        num_images_per_variant: int = 4,
        focus_type: str = "material",
    ) -> dict:
        """Generate mood board variants

        Args:
            colors: List of ColorInput objects with hex, name, temperature, etc.
            num_variants: Number of mood board variants to generate (1-3)
            include_images: Whether to generate DALL-E images
            num_images_per_variant: Number of images per variant (1-6)
            focus_type: Type of mood board focus - "material" or "typography"

        Returns:
            MoodBoardResponse dict with variants, timing, and models used
        """
        start_time = time.time()

        # Step 1: Use Claude to analyze colors and generate mood board themes
        themes = await self._generate_themes_with_claude(colors, num_variants, focus_type)

        # Step 2: Generate images with DALL-E for each theme (if requested)
        if include_images:
            for theme in themes:
                theme["theme"]["generated_images"] = await self._generate_images_with_dalle(
                    theme=theme["theme"],
                    num_images=num_images_per_variant,
                    focus_type=focus_type,
                )

        generation_time_ms = (time.time() - start_time) * 1000

        return {
            "variants": themes,
            "generation_time_ms": round(generation_time_ms, 2),
            "models_used": {
                "content_generation": self.claude_model,
                "image_generation": self.dalle_model if include_images else "none",
            },
            "focus_type": focus_type,
        }

    async def _generate_themes_with_claude(
        self, colors: list[Any], num_variants: int, focus_type: str = "material"
    ) -> list[dict]:
        """Use Claude to generate mood board themes based on colors"""

        # Prepare color data for Claude
        color_summary = self._summarize_colors(colors)
        focus_guidance = self._get_focus_guidance(focus_type)

        prompt = f"""You are an expert design curator and art historian. Analyze these extracted color tokens and generate {num_variants} distinct mood board themes.

**Focus Type: {focus_type.upper()}**
{focus_guidance}

**Color Data:**
{color_summary}

**Your Task:**
Generate {num_variants} mood board variants, each with a unique aesthetic interpretation. For each variant, provide:

1. **Theme Name** - A compelling, evocative name (e.g., "Retro-Futurism", "Bauhaus Geometry", "Synth-Wave Dreams")
2. **Subtitle** - A one-line description capturing the essence (e.g., "Playful tactile controls meet Yves Klein blue")
3. **Tags** - 4-6 descriptive tags (e.g., "retro-futurism", "tactile", "analog", "mid-century")
4. **Visual Elements** - 3-4 descriptions of visual characteristics:
   - Type: texture, shape, pattern, object, or composition
   - Description: What this element looks like
   - Prominence: primary, secondary, or accent
5. **Aesthetic References** - 2-3 cultural/artistic movements or artists that relate:
   - Movement name
   - Artist (optional)
   - Period
   - 2-3 key characteristics
6. **Dominant Colors** - Select 3-4 hex colors from the palette that best represent this variant
7. **Vibe** - One word capturing the overall feeling

**Important Guidelines:**
- Make each variant DISTINCT from the others (different aesthetic movements, eras, or styles)
- Reference real art movements, artists, and design periods
- Be specific and evocative in descriptions
- Connect colors to cultural/historical aesthetics authentically

Return your response as valid JSON matching this structure:
{{
  "variants": [
    {{
      "id": "primary",
      "title": "Theme Name",
      "subtitle": "One-line description",
      "theme": {{
        "name": "Theme Name",
        "description": "Brief description",
        "tags": ["tag1", "tag2", "tag3"],
        "visual_elements": [
          {{
            "type": "texture",
            "description": "Description of visual element",
            "prominence": "primary"
          }}
        ],
        "color_palette": ["#hex1", "#hex2"],
        "references": [
          {{
            "movement": "Movement Name",
            "artist": "Artist Name",
            "period": "1960s",
            "characteristics": ["char1", "char2"]
          }}
        ]
      }},
      "dominant_colors": ["#hex1", "#hex2", "#hex3"],
      "vibe": "expressive"
    }}
  ]
}}"""

        try:
            response = self.anthropic.messages.create(
                model=self.claude_model,
                max_tokens=4096,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract JSON from response
            content = response.content[0].text

            # Try to parse JSON
            # Claude sometimes wraps JSON in ```json blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            return result.get("variants", [])

        except Exception as e:
            logger.error(f"Error generating themes with Claude: {e}")
            # Return fallback themes
            return self._generate_fallback_themes(colors, num_variants)

    async def _generate_images_with_dalle(
        self, theme: dict, num_images: int, focus_type: str = "material"
    ) -> list[dict]:
        """Generate images with DALL-E based on theme"""

        images = []
        theme_name = theme.get("name", "Design Theme")
        tags = ", ".join(theme.get("tags", [])[:3])
        color_palette = ", ".join(theme.get("color_palette", [])[:3])

        # Generate prompts for each image
        base_prompt = f"A mood board aesthetic image representing {theme_name}. Style: {tags}. Color palette: {color_palette}. High quality, artistic, inspirational."

        # Get focus-specific variations
        variations = self._get_dalle_variations(focus_type)

        for i in range(num_images):
            try:
                variation = variations[i % len(variations)]
                full_prompt = f"{base_prompt} {variation}"

                response = self.openai.images.generate(
                    model=self.dalle_model,
                    prompt=full_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )

                if response.data and len(response.data) > 0:
                    images.append(
                        {
                            "url": response.data[0].url,
                            "prompt": full_prompt,
                            "revised_prompt": response.data[0].revised_prompt,
                        }
                    )

            except Exception as e:
                logger.warning(f"Failed to generate image {i + 1} for theme {theme_name}: {e}")
                continue

        return images

    def _summarize_colors(self, colors: list[Any]) -> str:
        """Create a readable summary of colors for Claude"""
        lines = ["Colors in this palette:"]
        for i, color in enumerate(colors[:10], 1):  # Limit to 10 colors
            hex_val = color.hex if hasattr(color, "hex") else color.get("hex", "#000000")
            name = color.name if hasattr(color, "name") else color.get("name", "Unnamed")
            temp = (
                color.temperature
                if hasattr(color, "temperature")
                else color.get("temperature", "neutral")
            )
            sat = (
                color.saturation_level
                if hasattr(color, "saturation_level")
                else color.get("saturation_level", "balanced")
            )

            lines.append(f"  {i}. {hex_val} ({name}) - {temp}, {sat}")

        return "\n".join(lines)

    def _generate_fallback_themes(self, colors: list[Any], num_variants: int) -> list[dict]:
        """Generate fallback themes if Claude fails"""
        # Simple fallback based on color analysis
        dominant_colors = [
            c.hex if hasattr(c, "hex") else c.get("hex", "#000000") for c in colors[:4]
        ]

        theme_templates = [
            {
                "id": "primary",
                "title": "Modern Minimalism",
                "subtitle": "Clean, contemporary design language",
                "theme": {
                    "name": "Modern Minimalism",
                    "description": "A refined palette emphasizing clarity and simplicity",
                    "tags": ["modern", "minimal", "clean", "contemporary"],
                    "visual_elements": [
                        {
                            "type": "shape",
                            "description": "Simple geometric forms",
                            "prominence": "primary",
                        }
                    ],
                    "color_palette": dominant_colors[:3],
                    "references": [
                        {
                            "movement": "Minimalism",
                            "period": "1960s-present",
                            "characteristics": ["reduction", "essential elements"],
                        }
                    ],
                },
                "dominant_colors": dominant_colors[:3],
                "vibe": "refined",
            },
            {
                "id": "secondary",
                "title": "Expressive Modernism",
                "subtitle": "Bold color meets structured design",
                "theme": {
                    "name": "Expressive Modernism",
                    "description": "Dynamic palette with contemporary energy",
                    "tags": ["modern", "expressive", "bold", "dynamic"],
                    "visual_elements": [
                        {
                            "type": "composition",
                            "description": "Dynamic arrangements",
                            "prominence": "primary",
                        }
                    ],
                    "color_palette": dominant_colors[:3],
                    "references": [
                        {
                            "movement": "Modernism",
                            "period": "20th century",
                            "characteristics": ["functional", "progressive"],
                        }
                    ],
                },
                "dominant_colors": dominant_colors[:3],
                "vibe": "dynamic",
            },
        ]

        return theme_templates[:num_variants]

    def _get_focus_guidance(self, focus_type: str) -> str:
        """Get focus-specific guidance for Claude prompt"""
        if focus_type == "material":
            return """**MATERIAL FOCUS GUIDANCE:**
- Emphasize physical surfaces, textures, and tactile qualities
- Reference materials: anodized aluminum, resin, glass, metal finishes, polymers
- Consider light interaction, reflections, depth, and dimensionality
- Think about physical controls and three-dimensional objects
- Visual elements should describe MATERIALS and SURFACES

Example visual elements:
  * "Brushed aluminum surfaces with circular grain texture"
  * "Resin swirls with fluid gradient transitions"
  * "Glass spheres with internal phosphor glow"
  * "Tactile polymer buttons with matte finish"
  * "Anodized metal knobs with radial machining"
  * "CRT oscilloscope screen with phosphor traces"
"""
        elif focus_type == "typography":
            return """**TYPOGRAPHY FOCUS GUIDANCE:**
- Emphasize typographic systems, grids, and letterforms
- Reference design movements: Swiss Design, Bauhaus, International Style
- Consider grid systems, baseline alignment, modular rhythm
- Think about technical labels, control glyphs, measurement scales
- Visual elements should describe TYPE SYSTEMS and GRAPHIC LANGUAGE

Example visual elements:
  * "Bold geometric sans-serif with tight letter spacing"
  * "Industrial panel labels with technical numerics"
  * "Modular grid system with visible baseline"
  * "Icon set with play/stop/pause glyphs"
  * "Swiss typography with asymmetric composition"
  * "Technical measurement scales and frequency markings"
"""
        else:
            return "Focus on the aesthetic and visual qualities of the color palette."

    def _get_dalle_variations(self, focus_type: str) -> list[str]:
        """Get focus-specific prompt variations for DALL-E"""
        if focus_type == "material":
            return [
                "Show anodized aluminum surface with brushed metal texture",
                "Show resin and enamel fluid patterns with swirling colors",
                "Show glass globe with internal glow and light refraction",
                "Show tactile control panel with physical knobs and buttons",
                "Show CRT oscilloscope with phosphor glow effect",
                "Show metallic surfaces with gradient reflections",
            ]
        elif focus_type == "typography":
            return [
                "Show Swiss grid system with bold sans-serif typography",
                "Show industrial control panel with frequency markings and technical labels",
                "Show modular typographic composition with visible baseline grid",
                "Show geometric letterforms on technical background",
                "Show technical signage with control glyphs and measurement scales",
                "Show asymmetric layout with bold typography and icon system",
            ]
        else:
            return [
                "focusing on texture and material",
                "emphasizing geometric patterns",
                "showcasing objects and composition",
                "highlighting color relationships",
            ]
