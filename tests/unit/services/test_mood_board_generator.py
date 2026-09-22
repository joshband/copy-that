"""Unit tests for MoodBoardGenerator (mocked providers — no network)."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from copy_that.services.mood_board_generator import MoodBoardGenerator


@pytest.fixture
def generator(monkeypatch: pytest.MonkeyPatch) -> MoodBoardGenerator:
    monkeypatch.delenv("MOOD_BOARD_TEXT_BASE_URL", raising=False)
    monkeypatch.delenv("MOOD_BOARD_IMAGE_BASE_URL", raising=False)
    with (
        patch("copy_that.services.mood_board_generator.Anthropic"),
        patch("copy_that.services.mood_board_generator.OpenAI"),
    ):
        return MoodBoardGenerator(anthropic_api_key="test", openai_api_key="test")


@pytest.fixture
def local_generator(monkeypatch: pytest.MonkeyPatch) -> MoodBoardGenerator:
    monkeypatch.setenv("MOOD_BOARD_TEXT_BASE_URL", "http://127.0.0.1:1234/v1")
    monkeypatch.setenv("MOOD_BOARD_TEXT_MODEL", "local-llama")
    monkeypatch.setenv("MOOD_BOARD_IMAGE_BASE_URL", "http://127.0.0.1:8765/v1")
    monkeypatch.setenv("MOOD_BOARD_IMAGE_MODEL", "local-sd")
    with patch("copy_that.services.mood_board_generator.OpenAI") as openai_cls:
        client = MagicMock()
        openai_cls.return_value = client
        gen = MoodBoardGenerator()
        gen._mock_openai_cls = openai_cls  # type: ignore[attr-defined]
        return gen


def test_summarize_colors_supports_dicts_and_objects(generator: MoodBoardGenerator) -> None:
    colors = [
        {"hex": "#FF0000", "name": "Red", "temperature": "warm", "saturation_level": "vibrant"},
        SimpleNamespace(hex="#00FF00", name="Green", temperature="cool", saturation_level="muted"),
    ]
    text = generator._summarize_colors(colors)
    assert "#FF0000" in text and "Red" in text
    assert "#00FF00" in text and "Green" in text


def test_focus_guidance_material_vs_typography(generator: MoodBoardGenerator) -> None:
    material = generator._get_focus_guidance("material")
    typography = generator._get_focus_guidance("typography")
    assert "MATERIAL" in material.upper() or "anodized" in material.lower()
    assert "TYPOGRAPHY" in typography.upper() or "Swiss" in typography
    assert generator._get_focus_guidance("other").startswith("Focus on")


def test_dalle_variations_by_focus(generator: MoodBoardGenerator) -> None:
    assert any("aluminum" in v.lower() for v in generator._get_dalle_variations("material"))
    assert any(
        "swiss" in v.lower() or "typograph" in v.lower()
        for v in generator._get_dalle_variations("typography")
    )


def test_fallback_themes_respect_num_variants(generator: MoodBoardGenerator) -> None:
    colors = [{"hex": "#112233", "name": "Navy"}]
    themes = generator._generate_fallback_themes(colors, num_variants=1)
    assert len(themes) == 1
    assert themes[0]["dominant_colors"][0] == "#112233"


def test_cloud_defaults_use_anthropic_and_dalle(generator: MoodBoardGenerator) -> None:
    assert generator.text_provider == "anthropic"
    assert generator.image_provider == "dalle"
    assert generator.text_model == "claude-sonnet-4-5-20250929"
    assert generator.image_model == "dall-e-3"


def test_local_env_selects_openai_compatible_providers(
    local_generator: MoodBoardGenerator,
) -> None:
    assert local_generator.text_provider == "openai_compatible"
    assert local_generator.image_provider == "local_mflux"
    assert local_generator.text_model == "local-llama"
    assert local_generator.image_model == "local-sd"
    assert local_generator.anthropic is None


@pytest.mark.asyncio
async def test_generate_skips_images_when_disabled(generator: MoodBoardGenerator) -> None:
    fake_variants = [
        {
            "id": "primary",
            "title": "T",
            "subtitle": "S",
            "theme": {"name": "T", "tags": [], "color_palette": ["#112233"]},
            "dominant_colors": ["#112233"],
            "vibe": "cool",
        }
    ]
    with (
        patch.object(generator, "_generate_themes", return_value=fake_variants),
        patch.object(generator, "_generate_images") as gen_images,
    ):
        result = await generator.generate(
            colors=[{"hex": "#112233"}],
            include_images=False,
            num_variants=1,
            focus_type="material",
        )
    gen_images.assert_not_called()
    assert result["models_used"]["image_generation"] == "none"
    assert result["models_used"]["content_generation"] == generator.text_model
    assert result["models_used"]["text_provider"] == "anthropic"
    assert result["focus_type"] == "material"
    assert len(result["variants"]) == 1


@pytest.mark.asyncio
async def test_generate_uses_collage_when_no_cloud_backend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MOOD_BOARD_TEXT_BASE_URL", raising=False)
    monkeypatch.delenv("MOOD_BOARD_IMAGE_BASE_URL", raising=False)
    monkeypatch.delenv("MOOD_BOARD_FLUX_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with patch("copy_that.services.mood_board_generator.Anthropic"):
        gen = MoodBoardGenerator(anthropic_api_key="test", openai_api_key=None)

    fake_variants = [
        {
            "id": "primary",
            "title": "T",
            "subtitle": "S",
            "theme": {"name": "T", "tags": [], "color_palette": ["#112233"]},
            "dominant_colors": ["#112233"],
            "vibe": "cool",
        }
    ]
    with patch.object(gen, "_generate_themes", return_value=fake_variants):
        result = await gen.generate(
            colors=[{"hex": "#112233"}],
            include_images=True,
            num_variants=1,
            num_images_per_variant=1,
        )
    assert gen.image_provider == "token_collage"
    images = result["variants"][0]["theme"]["generated_images"]
    assert len(images) == 1
    assert images[0]["url"].startswith("data:image/svg+xml")
    assert images[0]["selection"]["provider"] == "token_collage"


@pytest.mark.asyncio
async def test_generate_calls_router_per_variant_when_enabled(
    generator: MoodBoardGenerator,
) -> None:
    fake_variants = [
        {
            "id": "primary",
            "title": "T",
            "subtitle": "S",
            "theme": {"name": "T", "tags": ["a"], "color_palette": ["#112233"]},
            "dominant_colors": ["#112233"],
            "vibe": "cool",
        }
    ]
    with (
        patch.object(generator, "_generate_themes", return_value=fake_variants),
        patch.object(
            generator,
            "_generate_images",
            return_value=[
                {
                    "url": "https://example.com/x.png",
                    "prompt": "p",
                    "provider": "dalle",
                    "selection": {"provider": "dalle", "policy": "balanced"},
                }
            ],
        ) as gen_images,
    ):
        result = await generator.generate(
            colors=[{"hex": "#112233"}],
            include_images=True,
            num_images_per_variant=1,
            num_variants=1,
            focus_type="typography",
        )
    gen_images.assert_called_once()
    assert "dalle" in result["models_used"]["image_generation"]
    assert result["variants"][0]["theme"]["generated_images"][0]["url"].startswith("https://")


@pytest.mark.asyncio
async def test_claude_json_fence_parse(generator: MoodBoardGenerator) -> None:
    payload = {
        "variants": [
            {
                "id": "primary",
                "title": "Parsed",
                "subtitle": "from fence",
                "theme": {
                    "name": "Parsed",
                    "description": "d",
                    "tags": ["t"],
                    "visual_elements": [],
                    "color_palette": ["#ABCDEF"],
                    "references": [],
                },
                "dominant_colors": ["#ABCDEF"],
                "vibe": "cool",
            }
        ]
    }
    fenced = f"```json\n{json.dumps(payload)}\n```"
    mock_response = SimpleNamespace(
        content=[SimpleNamespace(text=fenced)],
    )
    generator.anthropic.messages.create = MagicMock(return_value=mock_response)

    variants = await generator._generate_themes_with_claude(
        [{"hex": "#ABCDEF", "name": "Sky"}],
        num_variants=1,
        focus_type="material",
    )
    assert len(variants) == 1
    assert variants[0]["title"] == "Parsed"


@pytest.mark.asyncio
async def test_local_text_uses_chat_completions(
    local_generator: MoodBoardGenerator,
) -> None:
    payload = {
        "variants": [
            {
                "id": "primary",
                "title": "Local Theme",
                "subtitle": "from lm studio",
                "theme": {
                    "name": "Local Theme",
                    "description": "d",
                    "tags": ["local"],
                    "visual_elements": [],
                    "color_palette": ["#112233"],
                    "references": [],
                },
                "dominant_colors": ["#112233"],
                "vibe": "local",
            }
        ]
    }
    local_generator.text_client.chat.completions.create = MagicMock(
        return_value=SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))]
        )
    )

    variants = await local_generator._generate_themes(
        [{"hex": "#112233", "name": "Navy"}],
        num_variants=1,
        focus_type="material",
    )
    assert variants[0]["title"] == "Local Theme"
    local_generator.text_client.chat.completions.create.assert_called_once()
    call_kwargs = local_generator.text_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "local-llama"


@pytest.mark.asyncio
async def test_local_images_use_images_generate_without_quality(
    local_generator: MoodBoardGenerator,
) -> None:
    local_backend = next(b for b in local_generator.image_router.backends if b.id == "local_mflux")
    local_backend._client.images.generate = MagicMock(  # type: ignore[attr-defined]
        return_value=SimpleNamespace(
            data=[
                SimpleNamespace(
                    url=None,
                    b64_json="aaaabbbb",
                    revised_prompt=None,
                )
            ]
        )
    )

    images = await local_generator._generate_images(
        theme={"name": "T", "tags": ["a"], "color_palette": ["#112233"]},
        num_images=1,
        focus_type="material",
        policy="private",
    )
    assert len(images) == 1
    assert images[0]["url"].startswith("data:image/png;base64,")
    kwargs = local_backend._client.images.generate.call_args.kwargs  # type: ignore[attr-defined]
    assert kwargs["model"] == "local-sd"
    assert "quality" not in kwargs


@pytest.mark.asyncio
async def test_cloud_images_pass_quality(generator: MoodBoardGenerator) -> None:
    dalle = next(b for b in generator.image_router.backends if b.id == "dalle")
    dalle._client.images.generate = MagicMock(  # type: ignore[attr-defined]
        return_value=SimpleNamespace(
            data=[
                SimpleNamespace(
                    url="https://cdn.example/img.png",
                    b64_json=None,
                    revised_prompt="revised",
                )
            ]
        )
    )
    images = await generator._generate_images(
        theme={"name": "T", "tags": ["a"], "color_palette": ["#112233"]},
        num_images=1,
        focus_type="material",
        policy="quality",
    )
    assert images[0]["url"] == "https://cdn.example/img.png"
    assert dalle._client.images.generate.call_args.kwargs["quality"] == "standard"  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_generate_records_local_models_used(
    local_generator: MoodBoardGenerator,
) -> None:
    fake_variants = [
        {
            "id": "primary",
            "title": "T",
            "subtitle": "S",
            "theme": {"name": "T", "tags": [], "color_palette": ["#112233"]},
            "dominant_colors": ["#112233"],
            "vibe": "cool",
        }
    ]
    with (
        patch.object(local_generator, "_generate_themes", return_value=fake_variants),
        patch.object(
            local_generator,
            "_generate_images",
            return_value=[
                {
                    "url": "data:image/png;base64,xx",
                    "prompt": "p",
                    "provider": "local_mflux",
                    "selection": {"provider": "local_mflux"},
                }
            ],
        ),
    ):
        result = await local_generator.generate(
            colors=[{"hex": "#112233"}],
            include_images=True,
            num_variants=1,
            num_images_per_variant=1,
        )
    assert result["models_used"]["content_generation"] == "local-llama"
    assert "local_mflux" in result["models_used"]["image_generation"]
    assert result["models_used"]["text_provider"] == "openai_compatible"
    assert result["models_used"]["routing_policy"] == local_generator.default_policy
