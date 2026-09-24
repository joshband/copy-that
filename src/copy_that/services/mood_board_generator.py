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

from copy_that.application.color_utils import normalize_hex
from copy_that.services.mood_board_images.protocol import RoutingPolicy
from copy_that.services.mood_board_images.registry import build_router

logger = logging.getLogger(__name__)

DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_DALLE_MODEL = "dall-e-3"
DEFAULT_LOCAL_TEXT_API_KEY = "lm-studio"
DEFAULT_LOCAL_IMAGE_API_KEY = "local"
DEFAULT_ROUTING_POLICY: RoutingPolicy = "balanced"
# MoodBoardRequest allows 20 colors. The image prompt uses that full list.
IMAGE_PALETTE_LIMIT = 20


def _strip_json_fence(content: str) -> str:
    """Remove optional markdown code fences around JSON."""
    if "```json" in content:
        return content.split("```json", 1)[1].split("```", 1)[0].strip()
    if "```" in content:
        return content.split("```", 1)[1].split("```", 1)[0].strip()
    return content.strip()


def _color_attr(color: Any, key: str) -> Any:
    if isinstance(color, dict):
        return color.get(key)
    return getattr(color, key, None)


def _usable_color_name(name: Any) -> str:
    if not isinstance(name, str):
        return ""
    label = name.strip()
    if not label or label.lower() in {"unnamed", "none"} or label.startswith("#"):
        return ""
    return label


def _role_bucket(color: Any) -> str:
    """Map a color onto ground, secondary, accent, or trace.

    Measured share wins over extract labels. A color tagged "background" that
    covers under 2% of the photo is a trace, not the ground.
    """
    prominence = _color_attr(color, "prominence_percentage")
    if isinstance(prominence, (int, float)):
        share = float(prominence)
        if share >= 20:
            return "background"
        if share >= 8:
            return "secondary"
        if share >= 2:
            return "accent"
        return "other"

    intent = str(_color_attr(color, "design_intent") or "").strip().lower()
    usage_raw = _color_attr(color, "usage") or []
    usage = [str(item).strip().lower() for item in usage_raw if str(item).strip()]
    background_role = str(_color_attr(color, "background_role") or "").strip().lower()
    is_accent = _color_attr(color, "is_accent") is True

    if intent in {"background", "ground", "surface"} or any("background" in item for item in usage):
        return "background"
    if background_role in {"primary", "secondary"} and not is_accent:
        return "background"
    if intent == "primary":
        return "primary"
    if intent == "secondary":
        return "secondary"
    accent_usage = ("button", "accent", "highlight", "alert", "detail")
    if (
        is_accent
        or intent in {"accent", "highlight", "alert", "detail"}
        or any(any(token in item for token in accent_usage) for item in usage)
    ):
        return "accent"
    return "other"


def measure_palette_shares(colors: list[Any], image_b64: str) -> list[dict[str, Any]]:
    """Set ``prominence_percentage`` from how much of the source each hex covers.

    Pixels farther than CIEDE2000 18 from every palette color are left unmatched.
    The resized photo may still be sent later as a reference to every image backend.
    """
    import base64
    from io import BytesIO

    from coloraide import Color
    from PIL import Image

    raw = image_b64.strip()
    if raw.startswith("data:") and "," in raw:
        raw = raw.split(",", 1)[1]
    sample = Image.open(BytesIO(base64.b64decode(raw))).convert("RGB")
    sample = sample.resize((96, 96), Image.Resampling.BOX)
    pixels = list(sample.getdata())

    refs: list[tuple[str, Color]] = []
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for color in colors:
        if isinstance(color, dict):
            item = dict(color)
        elif hasattr(color, "model_dump"):
            item = color.model_dump()
        else:
            item = {
                "hex": getattr(color, "hex", None),
                "name": getattr(color, "name", None),
                "usage": getattr(color, "usage", None),
                "design_intent": getattr(color, "design_intent", None),
                "prominence_percentage": getattr(color, "prominence_percentage", None),
            }
        hx_raw = item.get("hex")
        if not hx_raw:
            normalized.append(item)
            continue
        hx = normalize_hex(str(hx_raw))
        item["hex"] = hx
        normalized.append(item)
        if hx not in seen:
            seen.add(hx)
            refs.append((hx, Color(hx).convert("srgb")))

    counts = {hx: 0 for hx, _ref in refs}
    for red, green, blue in pixels:
        pix = Color(f"rgb({int(red)} {int(green)} {int(blue)})")
        best_hx: str | None = None
        best_de = 1e9
        for hx, ref in refs:
            de = pix.delta_e(ref, method="2000")
            if de < best_de:
                best_hx, best_de = hx, de
        if best_hx is not None and best_de <= 18:
            counts[best_hx] += 1

    total = max(len(pixels), 1)
    for item in normalized:
        hx = item.get("hex")
        if isinstance(hx, str) and hx in counts:
            item["prominence_percentage"] = round(100 * counts[hx] / total, 2)
    return normalized


def resize_reference_jpeg(image_b64: str, long_edge: int = 768) -> str:
    """Return a raw base64 JPEG whose long edge is at most ``long_edge``."""
    import base64
    from io import BytesIO

    from PIL import Image

    raw = image_b64.strip()
    if raw.startswith("data:") and "," in raw:
        raw = raw.split(",", 1)[1]
    img = Image.open(BytesIO(base64.b64decode(raw))).convert("RGB")
    img.thumbnail((long_edge, long_edge), Image.Resampling.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode("ascii")


FALLBACK_DESIGN_BRIEF: dict[str, Any] = {
    "subject": "the photographed object",
    "materials": "the surfaces visible in the source",
    "lighting": "the lighting in the source",
    "lettering": "",
    "look_and_feel": "the visual character of the source",
    "finish": "the surface finish visible in the source",
    "ground": "a neutral board background",
    "ui_elements": "the controls and components visible in the source",
    "influences": "only references the visible form suggests",
    "do_not_invent": "a new object, scene, or palette",
    "has_readable_type": False,
}

# Unused by the style endpoint. Kept so callers can still order the slots.
SLOT_STRENGTH = {"material": 0.08, "ui": 0.06, "typography": 0.04}


def parse_design_brief(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize a vision-model JSON object into the design-brief shape."""
    data = payload or {}
    lettering = str(data.get("lettering") or "").strip()
    has_type = data.get("has_readable_type")
    if not isinstance(has_type, bool):
        has_type = bool(lettering)
    return {
        "subject": str(data.get("subject") or FALLBACK_DESIGN_BRIEF["subject"]).strip(),
        "materials": str(data.get("materials") or FALLBACK_DESIGN_BRIEF["materials"]).strip(),
        "lighting": str(data.get("lighting") or FALLBACK_DESIGN_BRIEF["lighting"]).strip(),
        "lettering": lettering,
        "look_and_feel": str(
            data.get("look_and_feel") or FALLBACK_DESIGN_BRIEF["look_and_feel"]
        ).strip(),
        "finish": str(data.get("finish") or FALLBACK_DESIGN_BRIEF["finish"]).strip(),
        "ground": str(data.get("ground") or FALLBACK_DESIGN_BRIEF["ground"]).strip(),
        "ui_elements": str(
            data.get("ui_elements") or FALLBACK_DESIGN_BRIEF["ui_elements"]
        ).strip(),
        "influences": str(
            data.get("influences") or FALLBACK_DESIGN_BRIEF["influences"]
        ).strip(),
        "do_not_invent": str(
            data.get("do_not_invent") or FALLBACK_DESIGN_BRIEF["do_not_invent"]
        ).strip(),
        "has_readable_type": has_type,
    }


def design_brief_instruction() -> str:
    return """Look at this source photograph and describe only what is visible.
Influences must be references the visible form suggests, not a new art movement.
Return JSON only:
{
  "subject": "what the object is",
  "materials": "surfaces and finishes actually visible",
  "lighting": "light, shadow, and geometry",
  "lettering": "any readable words, labels, or grid; empty string if none",
  "look_and_feel": "the visual character a designer would name",
  "finish": "matte enamel, neon glow, painted texture, or the finish actually visible",
  "ground": "the board background the source implies",
  "ui_elements": "controls and components actually visible",
  "influences": "short references the visible form suggests",
  "do_not_invent": "what a later image must not add",
  "has_readable_type": false
}"""


def _display_words(text: str, limit: int = 3) -> str:
    words = [word for word in text.replace(",", " ").split() if word]
    return " ".join(words[:limit])


def _compact_palette(palette_text: str) -> str:
    """Hex phrases without the fill-the-frame role essay."""
    import re

    phrases = re.findall(r"(#[0-9A-Fa-f]{6}[^.;]*)", palette_text or "")
    cleaned = [phrase.strip() for phrase in phrases[:8]]
    if not cleaned:
        return ""
    return "Colors: " + "; ".join(cleaned) + "."


def slot_image_request(
    brief: dict[str, Any],
    focus_type: str,
    index: int,
    palette_text: str,
) -> tuple[str, float]:
    """Prompt and unused strength for one style-locked design board."""
    del index
    materials = brief.get("materials") or FALLBACK_DESIGN_BRIEF["materials"]
    lighting = brief.get("lighting") or FALLBACK_DESIGN_BRIEF["lighting"]
    lettering = str(brief.get("lettering") or "").strip()
    look = brief.get("look_and_feel") or FALLBACK_DESIGN_BRIEF["look_and_feel"]
    finish = brief.get("finish") or FALLBACK_DESIGN_BRIEF["finish"]
    ground = brief.get("ground") or FALLBACK_DESIGN_BRIEF["ground"]
    ui_elements = brief.get("ui_elements") or FALLBACK_DESIGN_BRIEF["ui_elements"]
    avoid = brief.get("do_not_invent") or FALLBACK_DESIGN_BRIEF["do_not_invent"]
    has_type = bool(brief.get("has_readable_type")) and bool(lettering)
    focus = focus_type if focus_type in SLOT_STRENGTH else "material"
    strength = SLOT_STRENGTH[focus]
    colors = _compact_palette(palette_text)
    if focus == "typography":
        display = _display_words(lettering if has_type else str(look))
        study = (
            "Typography poster. A flat poster grid on the source palette and surface. "
            f"Spell this display word exactly: {display}. "
            "Spell Aa in a large size. Include a small geometric grid and a few simple "
            "interface marks. No assembled device."
        )
    elif focus == "ui":
        sections = _display_words(str(ui_elements), limit=4)
        study = (
            "UI component system. A flat orthographic sheet. "
            f"Title, spelled exactly: {_display_words(str(look), limit=2)}. "
            f"Sections only for these controls: {sections}. "
            "Each section shows the words DEFAULT and ACTIVE. "
            f"Finish: {finish}. Neon stays glowing and enamel stays matte. "
            "Not a photograph of the original device."
        )
    else:
        study = (
            "Material collage. Even gutters between separate cells: one finish close-up, "
            "one texture, one hardware piece, one small interface fragment, and one palette strip. "
            f"Surfaces: {materials}. Finish: {finish}. Lighting: {lighting}. "
            "The product does not fill the frame."
        )
    prompt = (
        f"{study} Ground: {ground}. Do not invent {avoid}. "
        "Use only short real English words from this prompt. "
        f"{colors}"
    )
    return prompt, strength


def _palette_entry(color: Any) -> tuple[str, str, str, float | None] | None:
    """Return hex, prompt phrase, role bucket, and prominence for one color."""
    raw = _color_attr(color, "hex")
    if not raw:
        return None
    try:
        hx = normalize_hex(str(raw))
    except Exception:
        logger.debug("Skipping unreadable palette color %r", raw)
        return None

    details: list[str] = []
    name = _usable_color_name(_color_attr(color, "name"))
    if name:
        details.append(name)
    usage_raw = _color_attr(color, "usage") or []
    usage = [str(item).strip() for item in usage_raw if str(item).strip()]
    if usage:
        details.append(", ".join(usage[:3]))
    prominence = _color_attr(color, "prominence_percentage")
    share: float | None = None
    if isinstance(prominence, (int, float)):
        share = float(prominence)
        details.append(f"about {share:g}% of the source")
    elif _color_attr(color, "design_intent"):
        details.append(str(_color_attr(color, "design_intent")).strip())

    phrase = f"{hx} ({'; '.join(details)})" if details else hx
    return hx, phrase, _role_bucket(color), share


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
        source_image_base64: str | None = None,
        design_brief: dict[str, Any] | None = None,
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
        reference_b64 = None
        if source_image_base64:
            reference_b64 = resize_reference_jpeg(source_image_base64)
            colors = measure_palette_shares(colors, reference_b64)
        brief = design_brief or (
            self._load_design_brief(reference_b64) if reference_b64 else dict(FALLBACK_DESIGN_BRIEF)
        )

        await _report(0.15, "reading_source")
        await _report(0.2, "generating_themes")
        themes = await self._generate_themes(colors, num_variants, theme_focus, brief)

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
                    colors=colors,
                    design_brief=brief,
                    source_image_b64=reference_b64,
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
            "design_brief": brief,
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
                if ft not in {"material", "ui", "typography"}:
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
        self,
        colors: list[Any],
        num_variants: int,
        focus_type: str = "material",
        design_brief: dict[str, Any] | None = None,
    ) -> list[dict]:
        """Generate mood board themes via configured text provider."""
        if self.text_provider == "openai_compatible":
            return await self._generate_themes_openai_compatible(
                colors, num_variants, focus_type, design_brief
            )
        return await self._generate_themes_with_claude(
            colors, num_variants, focus_type, design_brief
        )

    def _build_theme_prompt(
        self,
        colors: list[Any],
        num_variants: int,
        focus_type: str,
        design_brief: dict[str, Any] | None = None,
    ) -> str:
        color_summary = self._summarize_colors(colors)
        focus_guidance = self._get_focus_guidance(focus_type, design_brief)
        brief = design_brief or FALLBACK_DESIGN_BRIEF
        source_block = (
            f"**Source photograph:** {brief.get('subject')}\n"
            f"Look and feel: {brief.get('look_and_feel')}\n"
            f"Finish: {brief.get('finish')}\n"
            f"Ground: {brief.get('ground')}\n"
            f"Materials: {brief.get('materials')}\n"
            f"UI elements: {brief.get('ui_elements')}\n"
            f"Lighting: {brief.get('lighting')}\n"
            f"Lettering: {brief.get('lettering') or 'none visible'}\n"
            f"Influences: {brief.get('influences')}\n"
            f"Do not invent: {brief.get('do_not_invent')}\n"
        )
        return f"""You are describing the source photograph, not inventing a new art movement. Generate {num_variants} mood board themes that name and describe that subject.

{source_block}
**Focus Type: {focus_type.upper()}**
{focus_guidance}

**Color Data:**
{color_summary}

**Your Task:**
Generate {num_variants} mood board variants, each with a unique aesthetic interpretation. For each variant, provide:

1. **Theme Name** - A name for this source subject, not a different scene
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
6. **Source color roles** - In color_palette, repeat source hex colors and keep their roles (background, primary, secondary, accent). Include every background color and the main accents. Do not invent hexes that are not in the color data, and do not reduce the source to three unrelated colors.
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
        self,
        colors: list[Any],
        num_variants: int,
        focus_type: str = "material",
        design_brief: dict[str, Any] | None = None,
    ) -> list[dict]:
        """Use Anthropic Claude to generate mood board themes."""
        if self.anthropic is None:
            logger.error("Anthropic client not configured")
            return self._generate_fallback_themes(colors, num_variants)

        prompt = self._build_theme_prompt(colors, num_variants, focus_type, design_brief)

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
        self,
        colors: list[Any],
        num_variants: int,
        focus_type: str = "material",
        design_brief: dict[str, Any] | None = None,
    ) -> list[dict]:
        """Use OpenAI-compatible chat (e.g. LM Studio) for theme JSON."""
        if self.text_client is None:
            logger.error("OpenAI-compatible text client not configured")
            return self._generate_fallback_themes(colors, num_variants)

        prompt = self._build_theme_prompt(colors, num_variants, focus_type, design_brief)

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
        colors: list[Any] | None = None,
        design_brief: dict[str, Any] | None = None,
        source_image_b64: str | None = None,
    ) -> list[dict]:
        """Generate images via policy router (parallel when cloud-friendly)."""
        color_palette = self._format_image_palette(colors, theme)
        brief = design_brief or FALLBACK_DESIGN_BRIEF
        slots = image_slots or self._resolve_image_slots(
            None, num_images, focus_type if focus_type != "mixed" else "material"
        )

        focus_counters: dict[str, int] = {}
        prompt_jobs: list[tuple[str, str, str, float]] = []
        for slot in slots:
            ft = slot.get("focus_type", "material")
            role = slot.get("role", ft)
            idx = focus_counters.get(ft, 0)
            focus_counters[ft] = idx + 1
            prompt, strength = slot_image_request(brief, ft, idx, color_palette)
            prompt_jobs.append((prompt, ft, role, strength))

        parallel = policy != "private" and allow_cloud

        async def _one(prompt: str, slot_focus: str, role: str, strength: float) -> dict | None:
            result = await asyncio.to_thread(
                self.image_router.generate_one,
                prompt=prompt,
                size=self._image_size,
                policy=policy,
                allow_cloud=allow_cloud,
                focus_type=slot_focus,
                deadline_monotonic=deadline_monotonic,
                image_b64=source_image_b64,
                strength=strength,
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
                *[_one(p, ft, role, strength) for p, ft, role, strength in prompt_jobs]
            )
            return [img for img in gathered if img is not None]

        images: list[dict] = []
        for prompt, ft, role, strength in prompt_jobs:
            img = await _one(prompt, ft, role, strength)
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

    def _format_image_palette(self, colors: list[Any] | None, theme: dict) -> str:
        """Source-structured palette for image prompts.

        Prefer the extracted color list. Group by role and, when the extract
        recorded it, how much of the source image each color covers.
        """
        source: list[Any]
        if colors:
            source = list(colors)
        else:
            source = [{"hex": hx} for hx in (theme.get("color_palette") or [])]

        buckets: dict[str, list[tuple[float, str]]] = {
            "background": [],
            "primary": [],
            "secondary": [],
            "accent": [],
            "other": [],
        }
        seen: set[str] = set()
        kept = 0
        for color in source:
            if kept >= IMAGE_PALETTE_LIMIT:
                break
            entry = _palette_entry(color)
            if entry is None or entry[0] in seen:
                continue
            hx, phrase, bucket, prominence = entry
            seen.add(hx)
            kept += 1
            buckets[bucket].append((-(prominence if prominence is not None else -1.0), phrase))

        labels = {
            "background": "Largest areas, fill most of the frame with these",
            "primary": "Primary colors",
            "secondary": "Secondary areas",
            "accent": "Small accents only, do not let these take over",
            "other": "Trace colors, keep them tiny and do not expand them",
        }
        sentences: list[str] = []
        for key, label in labels.items():
            phrases = [phrase for _rank, phrase in sorted(buckets[key])]
            if phrases:
                sentences.append(f"{label}: {'; '.join(phrases)}.")
        if not sentences:
            return "Use only the colors extracted from the source image."
        return " ".join(sentences)

    def _summarize_colors(self, colors: list[Any]) -> str:
        """Create a readable summary of colors for the text model."""
        lines = ["Colors in this source image:"]
        index = 0
        for color in colors[:IMAGE_PALETTE_LIMIT]:
            entry = _palette_entry(color)
            if entry is None:
                continue
            index += 1
            _hx, phrase, bucket, _prominence = entry
            lines.append(f"  {index}. {phrase} — {bucket}")
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

    def _load_design_brief(self, image_b64: str) -> dict[str, Any]:
        """Vision brief of the source. Falls back when no vision model answers."""
        client, model = self._vision_client()
        if client is None or not model:
            return dict(FALLBACK_DESIGN_BRIEF)
        try:
            response = client.chat.completions.create(
                model=model,
                max_tokens=800,
                temperature=0.2,
                timeout=60.0,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": design_brief_instruction()},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                            },
                        ],
                    }
                ],
            )
            content = (response.choices[0].message.content or "").strip()
            return parse_design_brief(json.loads(_strip_json_fence(content)))
        except Exception:
            logger.warning("Design brief vision pass failed", exc_info=True)
            return dict(FALLBACK_DESIGN_BRIEF)

    def _vision_client(self) -> tuple[Any, str | None]:
        """Color-extract vision model when configured, else the mood-board text model."""
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            return OpenAI(api_key=openai_key), os.getenv("OPENAI_MODEL", "gpt-4o")
        if self.text_client is not None:
            return self.text_client, self.text_model
        return None, None

    def _get_focus_guidance(
        self, focus_type: str, design_brief: dict[str, Any] | None = None
    ) -> str:
        """Focus guidance grounded in the source brief, for every theme mode."""
        brief = design_brief or FALLBACK_DESIGN_BRIEF
        subject = brief.get("subject") or FALLBACK_DESIGN_BRIEF["subject"]
        materials = brief.get("materials") or FALLBACK_DESIGN_BRIEF["materials"]
        ui_elements = brief.get("ui_elements") or FALLBACK_DESIGN_BRIEF["ui_elements"]
        look = brief.get("look_and_feel") or FALLBACK_DESIGN_BRIEF["look_and_feel"]
        finish = brief.get("finish") or FALLBACK_DESIGN_BRIEF["finish"]
        ground = brief.get("ground") or FALLBACK_DESIGN_BRIEF["ground"]
        influences = brief.get("influences") or FALLBACK_DESIGN_BRIEF["influences"]
        lettering = brief.get("lettering") or "none visible"
        if focus_type == "material":
            return f"""**MATERIAL FOCUS GUIDANCE:**
- Describe a guttered material collage for {subject}, not a product photo
- Materials: {materials}
- Finish: {finish}. Ground: {ground}
- Look and feel: {look}
"""
        if focus_type == "ui":
            return f"""**UI ELEMENTS FOCUS GUIDANCE:**
- Describe a flat component system for {subject}, with DEFAULT and ACTIVE states
- Controls: {ui_elements}
- Finish: {finish}. Ground: {ground}
- Look and feel: {look}
"""
        if focus_type == "typography":
            if brief.get("has_readable_type"):
                type_line = f"Describe this lettering as a type specimen: {lettering}"
            else:
                type_line = (
                    "The photo has no readable type. Describe a geometric label "
                    "system in the source colors. Do not invent a lifestyle scene."
                )
            return f"""**TYPOGRAPHY FOCUS GUIDANCE:**
- {type_line}
- A poster with a large Aa and a small grid, not a device
- Finish: {finish}. Ground: {ground}
- Stay with {subject}
"""
        if focus_type == "mixed":
            return f"""**MIXED FOCUS GUIDANCE (materials, UI elements, typography):**
- A material collage, a component system, and a type poster for {subject}
- Materials: {materials}
- UI elements: {ui_elements}
- Lettering: {lettering}
- Finish: {finish}. Ground: {ground}
- Influences, only if the form suggests them: {influences}
- Do not describe a redraw of the whole product
"""
        return "Focus on the aesthetic and visual qualities of the source photograph."

    def _get_dalle_variations(self, focus_type: str) -> list[str]:
        """Slot lines for tests. Live generation uses ``slot_image_request``."""
        brief = FALLBACK_DESIGN_BRIEF
        if focus_type == "material":
            return [
                slot_image_request(brief, "material", 0, "")[0],
                slot_image_request(brief, "material", 1, "")[0],
            ]
        if focus_type == "typography":
            return [slot_image_request(brief, "typography", 0, "")[0]]
        return [slot_image_request(brief, "material", 0, "")[0]]
