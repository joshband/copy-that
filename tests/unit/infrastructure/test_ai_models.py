"""Model IDs come from copy_that.infrastructure.ai_models only (AGENTS.md hard rule)."""

import re
from pathlib import Path

import pytest

from copy_that.infrastructure import ai_models

SRC = Path(__file__).resolve().parents[3] / "src"
MODEL_ID_LITERAL = re.compile(
    r"""["'](claude-(?:opus|sonnet|haiku)-[0-9][\w.-]*|gpt-[0-9][\w.-]*|dall-e-[0-9])["']"""
)


def test_getters_return_defaults_without_env():
    assert ai_models.claude_vision_model() == ai_models.CLAUDE_VISION_DEFAULT
    assert ai_models.claude_shadow_model() == ai_models.CLAUDE_SHADOW_DEFAULT
    assert ai_models.openai_vision_model() == ai_models.OPENAI_VISION_DEFAULT
    assert ai_models.openai_vision_model(ai_models.OPENAI_FAST_DEFAULT) == "gpt-4o-mini"
    assert ai_models.openai_image_model() == ai_models.OPENAI_IMAGE_DEFAULT


@pytest.mark.parametrize(
    ("env", "getter"),
    [
        ("CLAUDE_MODEL", ai_models.claude_vision_model),
        ("CLAUDE_SHADOW_MODEL", ai_models.claude_shadow_model),
        ("OPENAI_MODEL", ai_models.openai_vision_model),
        ("OPENAI_IMAGE_MODEL", ai_models.openai_image_model),
    ],
)
def test_env_overrides_default_at_call_time(monkeypatch, env, getter):
    monkeypatch.setenv(env, "override-model")
    assert getter() == "override-model"
    monkeypatch.setenv(env, "")
    assert getter() != "override-model"


def test_no_inline_model_ids_outside_ai_models():
    offenders = [
        f"{path.relative_to(SRC)}:{lineno}: {match.group(1)}"
        for path in SRC.rglob("*.py")
        if path.name != "ai_models.py"
        for lineno, line in enumerate(path.read_text().splitlines(), 1)
        for match in MODEL_ID_LITERAL.finditer(line)
    ]
    assert not offenders, "Move these model IDs into infrastructure/ai_models.py:\n" + "\n".join(
        offenders
    )
