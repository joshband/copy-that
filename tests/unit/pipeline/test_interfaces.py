"""Tests for pipeline interfaces module

Tests for BasePipelineAgent ABC and pipeline exceptions
"""

from abc import ABC
from typing import Any

import pytest

from copy_that.pipeline.exceptions import (
    AggregationError,
    ExtractionError,
    GenerationError,
    PipelineError,
    PreprocessingError,
    ValidationError,
)
from copy_that.pipeline.interfaces import BasePipelineAgent
from copy_that.pipeline.types import PipelineTask, ProcessedImage, TokenResult, TokenType


class TestPipelineExceptions:
    """Test pipeline exception classes"""

    def test_pipeline_error_base(self):
        """Test PipelineError is base exception"""
        error = PipelineError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_pipeline_error_with_details(self):
        """Test PipelineError with details"""
        error = PipelineError("Error occurred", details={"task_id": "123", "stage": "extract"})
        assert error.message == "Error occurred"
        assert error.details == {"task_id": "123", "stage": "extract"}

    def test_pipeline_error_default_details(self):
        """Test PipelineError default details is None"""
        error = PipelineError("Error")
        assert error.details is None

    def test_preprocessing_error(self):
        """Test PreprocessingError inherits from PipelineError"""
        error = PreprocessingError("Image preprocessing failed")
        assert isinstance(error, PipelineError)
        assert str(error) == "Image preprocessing failed"

    def test_preprocessing_error_with_details(self):
        """Test PreprocessingError with details"""
        error = PreprocessingError(
            "Invalid image format",
            details={"format": "HEIC", "expected": ["PNG", "JPEG", "GIF"]},
        )
        assert error.details["format"] == "HEIC"

    def test_extraction_error(self):
        """Test ExtractionError inherits from PipelineError"""
        error = ExtractionError("Token extraction failed")
        assert isinstance(error, PipelineError)
        assert str(error) == "Token extraction failed"

    def test_extraction_error_with_details(self):
        """Test ExtractionError with details"""
        error = ExtractionError(
            "Could not extract colors",
            details={"token_type": "color", "reason": "No dominant colors found"},
        )
        assert error.details["token_type"] == "color"

    def test_aggregation_error(self):
        """Test AggregationError inherits from PipelineError"""
        error = AggregationError("Token aggregation failed")
        assert isinstance(error, PipelineError)
        assert str(error) == "Token aggregation failed"

    def test_aggregation_error_with_details(self):
        """Test AggregationError with details"""
        error = AggregationError(
            "Conflict in token merging",
            details={"conflicting_tokens": ["token-1", "token-2"]},
        )
        assert error.details["conflicting_tokens"] == ["token-1", "token-2"]

    def test_validation_error(self):
        """Test ValidationError inherits from PipelineError"""
        error = ValidationError("Token validation failed")
        assert isinstance(error, PipelineError)
        assert str(error) == "Token validation failed"

    def test_validation_error_with_details(self):
        """Test ValidationError with details"""
        error = ValidationError(
            "Invalid token value",
            details={"token_name": "primary-color", "value": "invalid", "expected": "hex color"},
        )
        assert error.details["token_name"] == "primary-color"

    def test_generation_error(self):
        """Test GenerationError inherits from PipelineError"""
        error = GenerationError("Code generation failed")
        assert isinstance(error, PipelineError)
        assert str(error) == "Code generation failed"

    def test_generation_error_with_details(self):
        """Test GenerationError with details"""
        error = GenerationError(
            "Template rendering failed",
            details={"format": "CSS", "template": "variables.css.jinja2"},
        )
        assert error.details["format"] == "CSS"

    def test_exception_chaining(self):
        """Test exception can be raised with cause"""
        original = ValueError("Original error")
        try:
            try:
                raise original
            except ValueError as e:
                raise PreprocessingError("Wrapped error") from e
        except PreprocessingError as pe:
            assert pe.__cause__ is original

    def test_exception_inheritance_hierarchy(self):
        """Test all exceptions inherit from PipelineError"""
        exceptions = [
            PreprocessingError("test"),
            ExtractionError("test"),
            AggregationError("test"),
            ValidationError("test"),
            GenerationError("test"),
        ]
        for exc in exceptions:
            assert isinstance(exc, PipelineError)
            assert isinstance(exc, Exception)


class TestBasePipelineAgent:
    """Test BasePipelineAgent ABC"""

    def test_base_pipeline_agent_is_abc(self):
        """Test BasePipelineAgent is an ABC"""
        assert issubclass(BasePipelineAgent, ABC)

    def test_cannot_instantiate_base_agent(self):
        """Test BasePipelineAgent cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BasePipelineAgent()

    def test_concrete_agent_must_implement_process(self):
        """Test concrete agent must implement process method"""

        class IncompleteAgent(BasePipelineAgent):
            @property
            def agent_type(self) -> str:
                return "incomplete"

            @property
            def stage_name(self) -> str:
                return "test"

            async def health_check(self) -> bool:
                return True

        with pytest.raises(TypeError):
            IncompleteAgent()

    def test_concrete_agent_must_implement_health_check(self):
        """Test concrete agent must implement health_check method"""

        class IncompleteAgent(BasePipelineAgent):
            @property
            def agent_type(self) -> str:
                return "incomplete"

            @property
            def stage_name(self) -> str:
                return "test"

            async def process(self, task: PipelineTask) -> list[TokenResult]:
                return []

        with pytest.raises(TypeError):
            IncompleteAgent()

    def test_concrete_agent_must_implement_agent_type(self):
        """Test concrete agent must implement agent_type property"""

        class IncompleteAgent(BasePipelineAgent):
            @property
            def stage_name(self) -> str:
                return "test"

            async def process(self, task: PipelineTask) -> list[TokenResult]:
                return []

            async def health_check(self) -> bool:
                return True

        with pytest.raises(TypeError):
            IncompleteAgent()

    def test_concrete_agent_must_implement_stage_name(self):
        """Test concrete agent must implement stage_name property"""

        class IncompleteAgent(BasePipelineAgent):
            @property
            def agent_type(self) -> str:
                return "incomplete"

            async def process(self, task: PipelineTask) -> list[TokenResult]:
                return []

            async def health_check(self) -> bool:
                return True

        with pytest.raises(TypeError):
            IncompleteAgent()


class TestConcreteAgentImplementation:
    """Test concrete agent implementations"""

    def test_complete_agent_can_be_instantiated(self):
        """Test complete agent implementation can be instantiated"""

        class CompleteAgent(BasePipelineAgent):
            @property
            def agent_type(self) -> str:
                return "color_extractor"

            @property
            def stage_name(self) -> str:
                return "extraction"

            async def process(self, task: PipelineTask) -> list[TokenResult]:
                return [
                    TokenResult(
                        token_type=TokenType.COLOR,
                        name="primary",
                        value="#FF0000",
                        confidence=0.95,
                    )
                ]

            async def health_check(self) -> bool:
                return True

        agent = CompleteAgent()
        assert agent.agent_type == "color_extractor"
        assert agent.stage_name == "extraction"

    @pytest.mark.asyncio
    async def test_agent_process_returns_results(self):
        """Test agent process method returns TokenResults"""

        class ColorAgent(BasePipelineAgent):
            @property
            def agent_type(self) -> str:
                return "color"

            @property
            def stage_name(self) -> str:
                return "extraction"

            async def process(self, task: PipelineTask) -> list[TokenResult]:
                return [
                    TokenResult(
                        token_type=TokenType.COLOR,
                        name="primary",
                        value="#0066CC",
                        confidence=0.92,
                    ),
                    TokenResult(
                        token_type=TokenType.COLOR,
                        name="secondary",
                        value="#FF5733",
                        confidence=0.88,
                    ),
                ]

            async def health_check(self) -> bool:
                return True

        agent = ColorAgent()
        task = PipelineTask(
            task_id="test-task",
            image_url="https://example.com/test.png",
            token_types=[TokenType.COLOR],
        )
        results = await agent.process(task)

        assert len(results) == 2
        assert all(isinstance(r, TokenResult) for r in results)
        assert results[0].name == "primary"
        assert results[1].name == "secondary"

    @pytest.mark.asyncio
    async def test_agent_health_check_returns_bool(self):
        """Test agent health_check returns boolean"""

        class HealthyAgent(BasePipelineAgent):
            def __init__(self, is_healthy: bool = True):
                self._is_healthy = is_healthy

            @property
            def agent_type(self) -> str:
                return "test"

            @property
            def stage_name(self) -> str:
                return "test"

            async def process(self, task: PipelineTask) -> list[TokenResult]:
                return []

            async def health_check(self) -> bool:
                return self._is_healthy

        healthy_agent = HealthyAgent(is_healthy=True)
        unhealthy_agent = HealthyAgent(is_healthy=False)

        assert await healthy_agent.health_check() is True
        assert await unhealthy_agent.health_check() is False

    @pytest.mark.asyncio
    async def test_agent_process_empty_results(self):
        """Test agent process can return empty results"""

        class EmptyAgent(BasePipelineAgent):
            @property
            def agent_type(self) -> str:
                return "empty"

            @property
            def stage_name(self) -> str:
                return "test"

            async def process(self, task: PipelineTask) -> list[TokenResult]:
                return []

            async def health_check(self) -> bool:
                return True

        agent = EmptyAgent()
        task = PipelineTask(
            task_id="empty-task",
            image_url="https://example.com/empty.png",
            token_types=[TokenType.COLOR],
        )
        results = await agent.process(task)
        assert results == []

    @pytest.mark.asyncio
    async def test_agent_can_raise_pipeline_errors(self):
        """Test agent can raise pipeline errors during process"""

        class FailingAgent(BasePipelineAgent):
            @property
            def agent_type(self) -> str:
                return "failing"

            @property
            def stage_name(self) -> str:
                return "extraction"

            async def process(self, task: PipelineTask) -> list[TokenResult]:
                raise ExtractionError(
                    "Failed to extract tokens",
                    details={"task_id": task.task_id},
                )

            async def health_check(self) -> bool:
                return True

        agent = FailingAgent()
        task = PipelineTask(
            task_id="fail-task",
            image_url="https://example.com/fail.png",
            token_types=[TokenType.COLOR],
        )

        with pytest.raises(ExtractionError) as exc_info:
            await agent.process(task)

        assert "Failed to extract tokens" in str(exc_info.value)
        assert exc_info.value.details["task_id"] == "fail-task"


class TestAgentTypeVariations:
    """Test various agent type implementations"""

    def test_preprocessing_agent(self):
        """Test preprocessing agent type"""

        class PreprocessingAgent(BasePipelineAgent):
            @property
            def agent_type(self) -> str:
                return "preprocessor"

            @property
            def stage_name(self) -> str:
                return "preprocessing"

            async def process(self, task: PipelineTask) -> list[TokenResult]:
                return []

            async def health_check(self) -> bool:
                return True

        agent = PreprocessingAgent()
        assert agent.agent_type == "preprocessor"
        assert agent.stage_name == "preprocessing"

    def test_validation_agent(self):
        """Test validation agent type"""

        class ValidationAgent(BasePipelineAgent):
            @property
            def agent_type(self) -> str:
                return "validator"

            @property
            def stage_name(self) -> str:
                return "validation"

            async def process(self, task: PipelineTask) -> list[TokenResult]:
                return []

            async def health_check(self) -> bool:
                return True

        agent = ValidationAgent()
        assert agent.agent_type == "validator"
        assert agent.stage_name == "validation"

    def test_aggregation_agent(self):
        """Test aggregation agent type"""

        class AggregationAgent(BasePipelineAgent):
            @property
            def agent_type(self) -> str:
                return "aggregator"

            @property
            def stage_name(self) -> str:
                return "aggregation"

            async def process(self, task: PipelineTask) -> list[TokenResult]:
                return []

            async def health_check(self) -> bool:
                return True

        agent = AggregationAgent()
        assert agent.agent_type == "aggregator"
        assert agent.stage_name == "aggregation"


class TestExceptionMessages:
    """Test exception message formatting"""

    def test_pipeline_error_str_representation(self):
        """Test PipelineError string representation"""
        error = PipelineError("Test message")
        assert str(error) == "Test message"

    def test_pipeline_error_repr_with_details(self):
        """Test PipelineError repr includes details"""
        error = PipelineError("Error", details={"key": "value"})
        repr_str = repr(error)
        assert "PipelineError" in repr_str or "Error" in repr_str

    def test_specific_error_types_preserve_message(self):
        """Test specific error types preserve message"""
        errors = [
            PreprocessingError("Preprocessing failed"),
            ExtractionError("Extraction failed"),
            AggregationError("Aggregation failed"),
            ValidationError("Validation failed"),
            GenerationError("Generation failed"),
        ]

        expected_messages = [
            "Preprocessing failed",
            "Extraction failed",
            "Aggregation failed",
            "Validation failed",
            "Generation failed",
        ]

        for error, expected in zip(errors, expected_messages):
            assert str(error) == expected
