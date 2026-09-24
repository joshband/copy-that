"""
Mood Board Generator - AI-curated aesthetic boards

Text providers:
- Anthropic Claude (default when MOOD_BOARD_TEXT_BASE_URL is unset)
- OpenAI-compatible chat (LM Studio / local) when MOOD_BOARD_TEXT_BASE_URL is set

Image providers (policy router):
- flux_fast: MOOD_BOARD_FLUX_BASE_URL or non-local MOOD_BOARD_IMAGE_BASE_URL
- local_mflux: localhost MOOD_BOARD_IMAGE_BASE_URL shim
- dalle: OPENAI_API_KEY
- token_collage: deterministic SVG last resort
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Any

from anthropic import Anthropic
from openai import OpenAI

from copy_that.services.mood_board_images.protocol import RoutingPolicy
from copy_that.services.mood_board_images.registry import build_router

logger = logging.getLogger(__name__)

DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_DALLE_MODEL = "dall-e-3"
DEFAULT_LOCAL_TEXT_API_KEY = "lm-studio"
DEFAULT_LOCAL_IMAGE_API_KEY = "local"
DEFAULT_ROUTING_POLICY: RoutingPolicy = "balanced"


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
            Policy router over flux_fast / local_mflux / dalle / token_collage.
            Legacy image_client retained for unit tests that inspect providers.
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

        # --- Image router + legacy client for tests ---
        cloud_openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.image_router = build_router(
            image_base_url=resolved_image_base or None,
            image_api_key=image_api_key,
            image_model=image_model,
            openai_api_key=cloud_openai_key,
        )
        primary = next(
            (b for b in self.image_router.backends if b.id != "token_collage"),
            None,
        )
        if primary is not None:
            self.image_provider = primary.id
            self.image_model = getattr(primary, "model", primary.id)
            self.dalle_model = self.image_model
            # Prefer a real OpenAI client when available for legacy _call_images_generate
            if resolved_image_base:
                self.image_client = OpenAI(
                    base_url=resolved_image_base,
                    api_key=image_api_key
                    or os.getenv("MOOD_BOARD_IMAGE_API_KEY")
                    or DEFAULT_LOCAL_IMAGE_API_KEY,
                )
                self.openai = self.image_client
            elif cloud_openai_key:
                self.image_client = OpenAI(api_key=cloud_openai_key)
                self.openai = self.image_client
            else:
                self.image_client = None
                self.openai = None
        else:
            self.image_provider = "token_collage"
            self.image_model = "token_collage"
            self.dalle_model = "token_collage"
            self.image_client = None
            self.openai = None

        self._image_size = os.getenv("MOOD_BOARD_IMAGE_SIZE", "1024x1024")
        policy_env = (os.getenv("MOOD_BOARD_ROUTING_POLICY") or DEFAULT_ROUTING_POLICY).strip()
        self.default_policy: RoutingPolicy = (
            policy_env  # type: ignore[assignment]
            if policy_env in {"balanced", "fast", "cheap", "private", "quality"}
            else DEFAULT_ROUTING_POLICY
        )

    async def generate(
        self,
        colors: list[Any],
        num_variants: int = 2,
        include_images: bool = True,
        num_images_per_variant: int = 4,
        focus_type: str = "material",
        image_slots: list[Any] | None = None,
        on_progress: Any | None = None,
        policy: RoutingPolicy | None = None,
        allow_cloud: bool = True,
        max_latency_ms: float | None = None,
    ) -> dict:
        """Generate mood board variants.

        Args:
            colors: List of ColorInput objects with hex, name, temperature, etc.
            num_variants: Number of mood board variants to generate (1-3)
            include_images: Whether to generate images (skipped if no backend)
            num_images_per_variant: Number of images per variant (1-6) when
                ``image_slots`` is omitted
            focus_type: Theme focus — "material", "typography", or "mixed"
            image_slots: Optional list of ``{focus_type}`` dicts for per-image
                focus (e.g. material, material, typography)
            on_progress: Optional async ``(progress: float, message: str) -> None``
                callback for job status updates (themes vs long local image gens).

        Returns:
            MoodBoardResponse dict with variants, timing, and models used
        """
        start_time = time.time()

        async def _report(progress: float, message: str) -> None:
            if on_progress is not None:
                await on_progress(progress, message)

        slots = self._resolve_image_slots(
            image_slots, num_images_per_variant, focus_type
        )
        theme_focus = self._theme_focus_from_slots(slots, focus_type)

        await _report(0.2, "generating_themes")
        themes = await self._generate_themes(colors, num_variants, theme_focus)

        resolved_policy: RoutingPolicy = policy or self.default_policy
        image_model_used = "none"
        providers_used: list[str] = []
        if include_images:
            non_collage = [
                b for b in self.image_router.backends if b.id != "token_collage"
            ]
            if not non_collage and resolved_policy == "private":
                logger.info(
                    "include_images=True but only collage available under private policy"
                )
            image_model_used = self.image_model
            total = max(len(themes), 1)
            deadline = None
            if max_latency_ms is not None and max_latency_ms > 0:
                deadline = time.monotonic() + (max_latency_ms / 1000.0)
            for index, theme in enumerate(themes):
                await _report(
                    0.45 + 0.45 * (index / total),
                    f"rendering_images ({index + 1}/{total})",
                )
                images = await self._generate_images(
                    theme=theme["theme"],
                    num_images=len(slots),
                    focus_type=theme_focus,
                    image_slots=slots,
                    policy=resolved_policy,
                    allow_cloud=allow_cloud,
                    deadline_monotonic=deadline,
                )
                theme["theme"]["generated_images"] = images
                for img in images:
                    sel = img.get("selection") or {}
                    provider = sel.get("provider") or img.get("provider")
                    if isinstance(provider, str) and provider not in providers_used:
                        providers_used.append(provider)
            await _report(0.95, "rendering_images")
            if providers_used:
                image_model_used = ",".join(providers_used)

        generation_time_ms = (time.time() - start_time) * 1000

        return {
            "variants": themes,
            "generation_time_ms": round(generation_time_ms, 2),
            "models_used": {
                "content_generation": self.text_model,
                "image_generation": image_model_used,
                "text_provider": self.text_provider,
                "image_provider": (
                    ",".join(providers_used)
                    if providers_used
                    else (self.image_provider if include_images else "none")
                ),
                "routing_policy": resolved_policy if include_images else "none",
            },
            "focus_type": theme_focus,
        }

    @staticmethod
    def _resolve_image_slots(
        image_slots: list[Any] | None,
        num_images: int,
        focus_type: str,
    ) -> list[dict[str, str]]:
        """Normalize image slot plan to ``[{focus_type, role}, ...]``."""
        if image_slots:
            resolved: list[dict[str, str]] = []
            for slot in image_slots:
                if isinstance(slot, dict):
                    ft = str(slot.get("focus_type") or "material")
                else:
                    ft = str(getattr(slot, "focus_type", None) or "material")
                if ft not in {"material", "typography"}:
                    ft = "material"
                resolved.append({"focus_type": ft, "role": ft})
            return resolved[:6]
        # Single-focus fallback when slots omitted
        ft = focus_type if focus_type in {"material", "typography"} else "material"
        count = max(1, min(int(num_images), 6))
        return [{"focus_type": ft, "role": ft} for _ in range(count)]

    @staticmethod
    def _theme_focus_from_slots(
        slots: list[dict[str, str]], fallback: str
    ) -> str:
        focuses = {s.get("focus_type", "material") for s in slots}
        if len(focuses) > 1:
            return "mixed"
        if len(focuses) == 1:
            return next(iter(focuses))
        return fallback if fallback in {"material", "typography", "mixed"} else "material"

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
        self,
        theme: dict,
        num_images: int,
        focus_type: str = "material",
        image_slots: list[dict[str, str]] | None = None,
        policy: RoutingPolicy = "balanced",
        allow_cloud: bool = True,
        deadline_monotonic: float | None = None,
    ) -> list[dict]:
        """Generate images via policy router (parallel when cloud-friendly)."""
        theme_name = theme.get("name", "Design Theme")
        tags = ", ".join(theme.get("tags", [])[:3])
        color_palette = ", ".join(theme.get("color_palette", [])[:3])
        base_prompt = (
            f"A mood board aesthetic image representing {theme_name}. "
            f"Style: {tags}. Color palette: {color_palette}. "
            "High quality, artistic, inspirational."
        )
        slots = image_slots or self._resolve_image_slots(
            None, num_images, focus_type if focus_type != "mixed" else "material"
        )

        # Per-focus variation index so two material slots get distinct prompts
        focus_counters: dict[str, int] = {}
        prompt_jobs: list[tuple[str, str, str]] = []
        for slot in slots:
            ft = slot.get("focus_type", "material")
            role = slot.get("role", ft)
            variations = self._get_dalle_variations(ft)
            idx = focus_counters.get(ft, 0)
            focus_counters[ft] = idx + 1
            variation = variations[idx % len(variations)]
            prompt_jobs.append((f"{base_prompt} {variation}", ft, role))

        parallel = policy != "private" and allow_cloud

        async def _one(prompt: str, slot_focus: str, role: str) -> dict | None:
            result = await asyncio.to_thread(
                self.image_router.generate_one,
                prompt=prompt,
                size=self._image_size,
                policy=policy,
                allow_cloud=allow_cloud,
                focus_type=slot_focus,
                deadline_monotonic=deadline_monotonic,
            )
            if result is None:
                return None
            return {
                "url": result.url,
                "prompt": result.prompt,
                "revised_prompt": result.revised_prompt,
                "provider": result.provider,
                "selection": result.selection,
                "focus_type": slot_focus,
                "role": role,
            }

        if parallel and len(prompt_jobs) > 1:
            gathered = await asyncio.gather(
                *[_one(p, ft, role) for p, ft, role in prompt_jobs]
            )
            return [img for img in gathered if img is not None]

        images: list[dict] = []
        for prompt, ft, role in prompt_jobs:
            img = await _one(prompt, ft, role)
            if img is not None:
                images.append(img)
        return images

    async def _generate_images_with_dalle(
        self, theme: dict, num_images: int, focus_type: str = "material"
    ) -> list[dict]:
        """Legacy path — delegates to router for backwards-compatible tests."""
        return await self._generate_images(
            theme=theme,
            num_images=num_images,
            focus_type=focus_type,
            policy=self.default_policy,
            allow_cloud=True,
        )

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
        elif focus_type == "mixed":
            return """**MIXED FOCUS GUIDANCE (material + typography/grid):**
- Each theme must cover BOTH tactile material language AND typographic/grid language
- Include at least one visual element about materials/surfaces and one about type/grid
- References may span industrial design and graphic/type movements
- Keep a coherent aesthetic that bridges physical texture and graphic systems

Example visual elements:
  * "Brushed aluminum surfaces with circular grain texture"
  * "Soft polymer bezels with matte tactile finish"
  * "Modular grid system with visible baseline"
  * "Bold geometric sans-serif technical labels"
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
