"""Protect the live color cache and metadata contracts in the canonical extractor."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from copy_that.extractors.color import extractor as color_extractor
from copy_that.infrastructure.cache.extraction_cache import ExtractionCache, InMemoryBackend
from copy_that.services.colors_service import color_token_responses


@pytest.fixture
def extraction(monkeypatch: pytest.MonkeyPatch):
    cache = ExtractionCache(InMemoryBackend())
    # Use the real cache and parser; replace only the paid provider boundary.
    monkeypatch.setattr(color_extractor, "get_extraction_cache", lambda: cache, raising=False)
    service = color_extractor.AIColorExtractor(api_key="test-key")
    create = Mock(
        return_value=SimpleNamespace(
            content=[SimpleNamespace(type="text", text="Primary blue #2171B5 confidence: 0.9")]
        )
    )
    monkeypatch.setattr(service.client.messages, "create", create)
    return service, cache, create


def test_repeated_input_uses_cache_without_another_paid_call(extraction) -> None:
    service, _, create = extraction
    first = service.extract_colors_from_base64("aW1hZ2U=", "image/png", max_colors=3)
    second = service.extract_colors_from_base64("aW1hZ2U=", "image/png", max_colors=3)
    assert first.colors[0].hex == "#2171B5"
    assert second.model_dump() == first.model_dump()
    assert create.call_count == 1


def test_cache_isolates_projects_and_extraction_parameters(extraction) -> None:
    service, _, create = extraction
    args = ("aW1hZ2U=", "image/png")
    service.extract_colors_from_base64(*args, max_colors=3, cache_namespace="project-a")
    service.extract_colors_from_base64(*args, max_colors=3, cache_namespace="project-b")
    service.extract_colors_from_base64(*args, max_colors=4, cache_namespace="project-a")
    service.extract_colors_from_base64(*args, max_colors=3, cache_namespace="project-a")
    assert create.call_count == 3


def test_caller_hash_restores_accessibility_metadata_in_response(extraction) -> None:
    service, cache, create = extraction
    contrast_targets = [{"background": "#FFFFFF", "contrast": 4.8, "aa_normal": True}]
    role_scores = {"text": 0.8, "accent": 0.7}
    cache.set(
        "color.full",
        "caller-hash",
        "project-a",
        {
            "colors": [
                {
                    "hex": "#2171B5",
                    "rgb": "rgb(33, 113, 181)",
                    "name": "Blue",
                    "confidence": 0.9,
                    "contrast_targets": contrast_targets,
                    "role_scores": role_scores,
                }
            ],
            "dominant_colors": ["#2171B5"],
            "color_palette": "Blue",
            "extraction_confidence": 0.9,
        },
    )
    result = service.extract_colors_from_base64(
        "aW1hZ2U=", "image/png", cache_namespace="project-a", input_hash="caller-hash"
    )
    response = color_token_responses(result.colors)
    assert response[0]["contrast_targets"] == contrast_targets
    assert response[0]["role_scores"] == role_scores
    create.assert_not_called()
