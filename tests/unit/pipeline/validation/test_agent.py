import pytest

from copy_that.pipeline import PipelineTask, TokenResult, TokenType
from copy_that.pipeline.exceptions import ValidationError
from copy_that.pipeline.validation.agent import ValidationAgent, ValidationConfig


def _token(name: str, value: str, confidence: float = 0.9) -> TokenResult:
    return TokenResult(
        token_type=TokenType.COLOR,
        name=name,
        value=value,
        confidence=confidence,
        w3c_type="color",
        path=["color"],
    )


def _task(tokens=None, strict=False):
    context = {"tokens": tokens} if tokens is not None else {}
    if strict:
        config = ValidationConfig(strict_mode=True, min_confidence=0.85)
        agent = ValidationAgent(config)
    else:
        agent = ValidationAgent()
    if tokens is None:
        context = None
    return agent, PipelineTask(
        task_id="vind",
        image_url="http://example.com/x.png",
        token_types=[TokenType.COLOR],
        context=context,
    )


@pytest.mark.asyncio
async def test_process_missing_context():
    agent, task = _task(tokens=None)
    task.context = None
    with pytest.raises(ValidationError):
        await agent.process(task)


@pytest.mark.asyncio
async def test_process_empty_tokens():
    agent, task = _task(tokens=[])
    with pytest.raises(ValidationError):
        await agent.process(task)


@pytest.mark.asyncio
async def test_strict_mode_filters_low_confidence():
    low = _token("low", "#010101", confidence=0.2)
    high = _token("high", "#FFFFFF", confidence=0.9)
    agent, task = _task(tokens=[low, high], strict=True)

    result = await agent.process(task)
    assert result == [high]


@pytest.mark.asyncio
async def test_lenient_mode_returns_all():
    token = _token("primary", "#000000")
    agent, task = _task(tokens=[token])
    result = await agent.process(task)
    assert result == [token]


@pytest.mark.asyncio
async def test_validate_schema_reports_invalid_color():
    agent = ValidationAgent()
    token = _token("bad", "not-a-color")
    errors = agent.validate_schema(token)
    assert any("Invalid color format" in err for err in errors)


@pytest.mark.asyncio
async def test_validate_token_adds_custom_rule_messages():
    def rule(token):
        yield "custom rule triggered"

    config = ValidationConfig(custom_rules=[rule])
    agent = ValidationAgent(config)
    token = _token("custom", "#00FF00")

    validated = agent.validate_token(token)
    assert "custom rule triggered" in validated.validation_errors
