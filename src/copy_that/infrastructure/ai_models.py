"""AI model IDs — the only place Copy That defines them.

Each getter reads its env var at call time (so `.env` loaded after import still applies) and
falls back to the default constant. Changing a default changes cost and output: do it
deliberately, and update `docs/configuration/ENVIRONMENT_VARIABLES.md`.
"""

from __future__ import annotations

import os

CLAUDE_VISION_DEFAULT = "claude-sonnet-4-5-20250929"
CLAUDE_SHADOW_DEFAULT = "claude-opus-4-1-20250805"
OPENAI_VISION_DEFAULT = "gpt-4o"
OPENAI_FAST_DEFAULT = "gpt-4o-mini"
OPENAI_PREMIUM_DEFAULT = "gpt-4.1"
OPENAI_IMAGE_DEFAULT = "dall-e-3"


def _env(name: str, default: str) -> str:
    return os.getenv(name) or default


def claude_vision_model() -> str:
    """Claude model for color/typography extraction, qualitative metrics, mood-board copy."""
    return _env("CLAUDE_MODEL", CLAUDE_VISION_DEFAULT)


def claude_shadow_model() -> str:
    """Claude model for AI shadow extraction."""
    return _env("CLAUDE_SHADOW_MODEL", CLAUDE_SHADOW_DEFAULT)


def openai_vision_model(default: str = OPENAI_VISION_DEFAULT) -> str:
    """OpenAI vision model; `OPENAI_MODEL` overrides every OpenAI vision call site."""
    return _env("OPENAI_MODEL", default)


def openai_image_model() -> str:
    """OpenAI image-generation model for the DALL·E mood-board backend."""
    return _env("OPENAI_IMAGE_MODEL", OPENAI_IMAGE_DEFAULT)
