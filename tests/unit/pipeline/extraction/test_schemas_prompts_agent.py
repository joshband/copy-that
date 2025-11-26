import pytest
from jsonschema import ValidationError

from copy_that.pipeline import TokenType
from copy_that.pipeline.extraction.agent import ExtractionAgent, ExtractionError
from copy_that.pipeline.extraction.prompts import (
    get_extraction_prompt,
    get_system_prompt,
)
from copy_that.pipeline.extraction.schemas import (
    get_tool_schema,
    validate_extraction_result,
)
from copy_that.pipeline.types import PipelineTask


class DummyContent:
    def __init__(self, input_data, content_type="tool_use"):
        self.input = input_data
        self.type = content_type


class DummyResponse:
    def __init__(self, contents, stop_reason="stop"):
        self.content = contents
        self.stop_reason = stop_reason


class DummyPreprocessed:
    def __init__(self, data: str, fmt: str = "png"):
        self.preprocessed_data = {"base64": data}
        self.format = fmt


@pytest.mark.parametrize("token_type", ["color", "spacing"])
def test_get_tool_schema_invalid_token_type(token_type: str):
    with pytest.raises(ValueError):
        get_tool_schema(token_type + "-invalid")


def test_validate_color_schema_success():
    color_payload = {
        "colors": [
            {
                "name": "brand-primary",
                "hex_value": "#112233",
                "confidence": 0.9,
                "rgb": {"r": 17, "g": 34, "b": 51},
                "hsl": {"h": 220, "s": 45, "l": 13},
                "usage": "background",
                "category": "brand",
            }
        ]
    }
    assert validate_extraction_result(TokenType.COLOR, color_payload) is True


def test_validate_spacing_schema_missing_required_field():
    spacing_payload = {
        "spacing": [
            {
                "name": "space-sm",
                "value": 8,
                "confidence": 0.8,
                # 'unit' missing should trigger ValidationError
            }
        ]
    }
    with pytest.raises(ValidationError):
        validate_extraction_result(TokenType.SPACING, spacing_payload)


def test_get_extraction_prompt_registry():
    prompt = get_extraction_prompt(TokenType.COLOR)
    assert "Brand Colors" in prompt
    assert get_system_prompt().startswith("You are an expert")
    with pytest.raises(ValueError):
        get_extraction_prompt("unknown")


def test_parse_response_success():
    agent = ExtractionAgent(TokenType.COLOR)
    payload = {"colors": [{"name": "primary", "hex_value": "#ffffff", "confidence": 1.0}]}
    fake_response = DummyResponse([DummyContent(payload)])
    parsed = agent._parse_response(fake_response)
    assert parsed == payload


def test_parse_response_missing_tool_use():
    agent = ExtractionAgent(TokenType.COLOR)
    fake_response = DummyResponse([DummyContent({}, content_type="text")], stop_reason="none")
    with pytest.raises(ExtractionError) as exc:
        agent._parse_response(fake_response)
    assert "No tool use" in str(exc.value)


@pytest.mark.asyncio
async def test_get_image_data_from_preprocessed_context():
    agent = ExtractionAgent(TokenType.COLOR)
    preprocessed = DummyPreprocessed("ZGVtbw==", fmt="webp")
    task = PipelineTask(
        task_id="task-1",
        image_url="https://example.com/image.png",
        token_types=[TokenType.COLOR],
        context={"preprocessed_image": preprocessed},
    )
    result = await agent._get_image_data(task)
    assert result["type"] == "base64"
    assert result["media_type"] == "image/webp"
    assert result["data"] == "ZGVtbw=="


def test_convert_to_token_results_color_metadata():
    agent = ExtractionAgent(TokenType.COLOR)
    payload = {
        "colors": [{"name": "cta", "hex_value": "#0000ff", "confidence": 0.7, "category": "accent"}]
    }
    results = agent._convert_to_token_results(payload)
    assert len(results) == 1
    token = results[0]
    assert token.value == "#0000ff"
    assert token.metadata["category"] == "accent"
    assert token.full_path.startswith("color")


def test_spacing_value_and_metadata():
    agent = ExtractionAgent(TokenType.SPACING)
    payload = {
        "spacing": [
            {"name": "space-lg", "value": 24, "unit": "px", "confidence": 0.6, "scale_position": 3}
        ]
    }
    results = agent._convert_to_token_results(payload)
    assert results[0].value == "24px"
    assert results[0].metadata["scale_position"] == 3


def test_format_dimension_unitless():
    agent = ExtractionAgent(TokenType.SHADOW)
    assert agent._format_dimension({"value": 5, "unit": "unitless"}) == "5"


def test_get_items_from_result_map():
    agent = ExtractionAgent(TokenType.GRADIENT)
    payload = {"gradients": [{"name": "glow", "type": "linear", "stops": [], "confidence": 0.8}]}
    items = agent._get_items_from_result(payload)
    assert len(items) == 1
