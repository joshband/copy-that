"""
Mood Board Generator - AI-curated aesthetic boards

Text providers:
- Anthropic Claude (default when MOOD_BOARD_TEXT_BASE_URL is unset)
- OpenAI-compatible chat (LM Studio / local) when MOOD_BOARD_TEXT_BASE_URL is set

Image providers:
- OpenAI DALL·E 3 (default when OPENAI_API_KEY is set and IMAGE_BASE_URL unset)
- OpenAI-compatible images.generate when MOOD_BOARD_IMAGE_BASE_URL is set
- Graceful skip when include_images=False or no image backend is configured
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

from anthropic import Anthropic
from openai import OpenAI

logger = logging.getLogger(__name__)

DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_DALLE_MODEL = "dall-e-3"
DEFAULT_LOCAL_TEXT_API_KEY = "lm-studio"
DEFAULT_LOCAL_IMAGE_API_KEY = "local"


def _strip_json_fence(content: str) -> str:
    """Remove optional markdown code fences around JSON."""
    if "```json" in content:
        return content.split("```json", 1)[1].split("```", 1)[0].strip()
    if "```" in content:
        return content.split("```", 1)[1].split("```", 1)[0].strip()
    return content.strip()


class MoodBoardGenerator:
    """Generate AI-curated mood boards from color tokens."""

    def __init__(
        self,
        anthropic_api_key: str | None = None,
        openai_api_key: str | None = None,
        text_base_url: str | None = None,
        text_api_key: str | None = None,
        text_model: str | None = None,
        image_base_url: str | None = None,
        image_api_key: str | None = None,
        image_model: str | None = None,
    ):
        """Initialize providers from explicit args or environment.

        Text (themes):
            MOOD_BOARD_TEXT_BASE_URL + MOOD_BOARD_TEXT_API_KEY + MOOD_BOARD_TEXT_MODEL
            → OpenAI-compatible chat. When TEXT_BASE_URL unset → Anthropic Claude.

        Images:
            MOOD_BOARD_IMAGE_BASE_URL + MOOD_BOARD_IMAGE_API_KEY + MOOD_BOARD_IMAGE_MODEL
            → OpenAI-compatible images.generate. When unset and OPENAI_API_KEY present
            → DALL·E 3. Otherwise image generation is unavailable (graceful skip).
        """
        resolved_text_base = (text_base_url or os.getenv("MOOD_BOARD_TEXT_BASE_URL") or "").rstrip(
            "/"
        )
        resolved_image_base = (
            image_base_url or os.getenv("MOOD_BOARD_IMAGE_BASE_URL") or ""
        ).rstrip("/")

        self.text_client: OpenAI | None
        self.image_client: OpenAI | None
        self.openai: OpenAI | None
        self.anthropic: Anthropic | None

        # --- Text provider ---
        if resolved_text_base:
            self.text_provider = "openai_compatible"
            self.text_model = text_model or os.getenv("MOOD_BOARD_TEXT_MODEL") or "local-model"
            self.text_client = OpenAI(
                base_url=resolved_text_base,
                api_key=text_api_key
                or os.getenv("MOOD_BOARD_TEXT_API_KEY")
                or DEFAULT_LOCAL_TEXT_API_KEY,
            )
            self.anthropic = None
            # Back-compat attribute used by older tests
            self.claude_model = self.text_model
        else:
            self.text_provider = "anthropic"
            self.text_model = DEFAULT_CLAUDE_MODEL
            self.claude_model = self.text_model
            self.text_client = None
            self.anthropic = Anthropic(api_key=anthropic_api_key or os.getenv("ANTHROPIC_API_KEY"))

        # --- Image provider ---
        cloud_openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if resolved_image_base:
            self.image_provider = "openai_compatible"
            self.image_model = image_model or os.getenv("MOOD_BOARD_IMAGE_MODEL") or "local-sd"
            self.image_client = OpenAI(
                base_url=resolved_image_base,
                api_key=image_api_key
                or os.getenv("MOOD_BOARD_IMAGE_API_KEY")
                or DEFAULT_LOCAL_IMAGE_API_KEY,
            )
            self.dalle_model = self.image_model
            # Keep legacy attribute for cloud-only call sites / tests
            self.openai = self.image_client
        elif cloud_openai_key:
            self.image_provider = "openai"
            self.image_model = DEFAULT_DALLE_MODEL
            self.dalle_model = self.image_model
            self.image_client = OpenAI(api_key=cloud_openai_key)
            self.openai = self.image_client
        else:
            self.image_provider = "none"
            self.image_model = "none"
            self.dalle_model = "none"
            self.image_client = None
            self.openai = None

        self._image_size = os.getenv("MOOD_BOARD_IMAGE_SIZE", "1024x1024")

    async def generate(
        self,
        colors: list[Any],
        num_variants: int = 2,
        include_images: bool = True,
        num_images_per_variant: int = 4,
        focus_type: str = "material",
        on_progress: Any | None = None,
    ) -> dict:
        """Generate mood board variants.

        Args:
            colors: List of ColorInput objects with hex, name, temperature, etc.
            num_variants: Number of mood board variants to generate (1-3)
            include_images: Whether to generate images (skipped if no backend)
            num_images_per_variant: Number of images per variant (1-6)
            focus_type: Type of mood board focus - "material" or "typography"
            on_progress: Optional async ``(progress: float, message: str) -> None``
                callback for job status updates (themes vs long local image gens).

        Returns:
            MoodBoardResponse dict with variants, timing, and models used
        """
        start_time = time.time()

        async def _report(progress: float, message: str) -> None:
            if on_progress is not None:
                await on_progress(progress, message)

        await _report(0.2, "generating_themes")
        themes = await self._generate_themes(colors, num_variants, focus_type)

        image_model_used = "none"
        if include_images:
            if self.image_client is None:
                logger.info(
                    "include_images=True but no image backend configured "
                    "(set MOOD_BOARD_IMAGE_BASE_URL or OPENAI_API_KEY); skipping images"
                )
            else:
                image_model_used = self.image_model
                total = max(len(themes), 1)
                for index, theme in enumerate(themes):
                    await _report(
                        0.45 + 0.45 * (index / total),
                        f"rendering_images ({index + 1}/{total})",
                    )
                    theme["theme"]["generated_images"] = await self._generate_images(
                        theme=theme["theme"],
                        num_images=num_images_per_variant,
                        focus_type=focus_type,
                    )
                await _report(0.95, "rendering_images")

        generation_time_ms = (time.time() - start_time) * 1000

        return {
            "variants": themes,
            "generation_time_ms": round(generation_time_ms, 2),
            "models_used": {
                "content_generation": self.text_model,
                "image_generation": image_model_used,
                "text_provider": self.text_provider,
                "image_provider": self.image_provider if include_images else "none",
            },
            "focus_type": focus_type,
        }

    async def _generate_themes(
        self, colors: list[Any], num_variants: int, focus_type: str = "material"
    ) -> list[dict]:
        """Generate mood board themes via configured text provider."""
        if self.text_provider == "openai_compatible":
            return await self._generate_themes_openai_compatible(colors, num_variants, focus_type)
        return await self._generate_themes_with_claude(colors, num_variants, focus_type)

    def _build_theme_prompt(self, colors: list[Any], num_variants: int, focus_type: str) -> str:
        color_summary = self._summarize_colors(colors)
        focus_guidance = self._get_focus_guidance(focus_type)
        return f"""You are an expert design curator and art historian. Analyze these extracted color tokens and generate {num_variants} distinct mood board themes.

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

    def _parse_theme_response(self, content: str) -> list[dict]:
        result = json.loads(_strip_json_fence(content))
        return result.get("variants", [])

    async def _generate_themes_with_claude(
        self, colors: list[Any], num_variants: int, focus_type: str = "material"
    ) -> list[dict]:
        """Use Anthropic Claude to generate mood board themes."""
        if self.anthropic is None:
            logger.error("Anthropic client not configured")
            return self._generate_fallback_themes(colors, num_variants)

        prompt = self._build_theme_prompt(colors, num_variants, focus_type)

        try:
            response = self.anthropic.messages.create(
                model=self.text_model,
                max_tokens=4096,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0].text
            return self._parse_theme_response(content)
        except Exception as e:
            logger.error(f"Error generating themes with Claude: {e}")
            return self._generate_fallback_themes(colors, num_variants)

    async def _generate_themes_openai_compatible(
        self, colors: list[Any], num_variants: int, focus_type: str = "material"
    ) -> list[dict]:
        """Use OpenAI-compatible chat (e.g. LM Studio) for theme JSON."""
        if self.text_client is None:
            logger.error("OpenAI-compatible text client not configured")
            return self._generate_fallback_themes(colors, num_variants)

        prompt = self._build_theme_prompt(colors, num_variants, focus_type)

        try:
            response = self.text_client.chat.completions.create(
                model=self.text_model,
                max_tokens=4096,
                temperature=0.7,
                timeout=180.0,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a design curator. Respond with valid JSON only — "
                            "no markdown fences unless necessary."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            message = response.choices[0].message
            content = (message.content or "").strip()
            # Some LM Studio reasoning models put the answer in reasoning_content.
            if not content:
                content = (getattr(message, "reasoning_content", None) or "").strip()
            if not content:
                raise ValueError("Empty content from text model")
            return self._parse_theme_response(content)
        except Exception as e:
            logger.error(f"Error generating themes with OpenAI-compatible text API: {e}")
            return self._generate_fallback_themes(colors, num_variants)

    async def _generate_images(
        self, theme: dict, num_images: int, focus_type: str = "material"
    ) -> list[dict]:
        """Generate images via configured image backend (DALL·E or local compatible)."""
        return await self._generate_images_with_dalle(theme, num_images, focus_type)

    async def _generate_images_with_dalle(
        self, theme: dict, num_images: int, focus_type: str = "material"
    ) -> list[dict]:
        """Generate images with OpenAI images.generate (cloud DALL·E or local proxy)."""
        if self.image_client is None:
            return []

        images: list[dict] = []
        theme_name = theme.get("name", "Design Theme")
        tags = ", ".join(theme.get("tags", [])[:3])
        color_palette = ", ".join(theme.get("color_palette", [])[:3])

        base_prompt = (
            f"A mood board aesthetic image representing {theme_name}. "
            f"Style: {tags}. Color palette: {color_palette}. "
            "High quality, artistic, inspirational."
        )
        variations = self._get_dalle_variations(focus_type)

        for i in range(num_images):
            try:
                variation = variations[i % len(variations)]
                full_prompt = f"{base_prompt} {variation}"
                response = self._call_images_generate(full_prompt)

                if response.data and len(response.data) > 0:
                    item = response.data[0]
                    url = getattr(item, "url", None)
                    b64 = getattr(item, "b64_json", None)
                    if not url and b64:
                        url = f"data:image/png;base64,{b64}"
                    if url:
                        images.append(
                            {
                                "url": url,
                                "prompt": full_prompt,
                                "revised_prompt": getattr(item, "revised_prompt", None),
                            }
                        )
            except Exception as e:
                logger.warning(
                    "Failed to generate image %s for theme %s: %s",
                    i + 1,
                    theme_name,
                    e,
                )
                continue

        return images

    def _call_images_generate(self, prompt: str) -> Any:
        """Call images.generate with cloud vs local parameter differences."""
        assert self.image_client is not None
        kwargs: dict[str, Any] = {
            "model": self.image_model,
            "prompt": prompt,
            "n": 1,
            "size": self._image_size,
        }
        # DALL·E 3 supports quality; many local proxies reject unknown fields.
        if self.image_provider == "openai":
            kwargs["quality"] = "standard"
        return self.image_client.images.generate(**kwargs)

    def _summarize_colors(self, colors: list[Any]) -> str:
        """Create a readable summary of colors for the text model."""
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
        """Generate fallback themes if the text provider fails."""
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
        """Get focus-specific guidance for the text prompt."""
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
        """Get focus-specific prompt variations for image generation."""
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
