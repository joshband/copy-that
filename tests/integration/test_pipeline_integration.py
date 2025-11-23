"""Integration tests for pipeline module.

Tests that pipeline module exports are accessible and types work correctly
in a realistic context.
"""

from datetime import datetime
from uuid import UUID

import pytest

from copy_that.pipeline import (
    BasePipelineAgent,
    PipelineError,
    PipelineTask,
    PipelineTaskStatus,
    PipelineTimeoutError,
    PipelineValidationError,
    ProcessedImage,
    TokenResult,
    TokenType,
    W3CTokenType,
)
from copy_that.pipeline.exceptions import (
    PipelineConfigurationError,
    PipelineConnectionError,
    PipelineRateLimitError,
    PipelineRetryableError,
)


class TestPipelineModuleExports:
    """Test that all pipeline exports are accessible."""

    def test_all_types_importable(self) -> None:
        """Verify all public types can be imported."""
        assert TokenType is not None
        assert W3CTokenType is not None
        assert TokenResult is not None
        assert PipelineTask is not None
        assert ProcessedImage is not None
        assert PipelineTaskStatus is not None

    def test_all_exceptions_importable(self) -> None:
        """Verify all exceptions can be imported."""
        assert PipelineError is not None
        assert PipelineValidationError is not None
        assert PipelineTimeoutError is not None
        assert PipelineConfigurationError is not None
        assert PipelineConnectionError is not None
        assert PipelineRateLimitError is not None
        assert PipelineRetryableError is not None

    def test_base_interface_importable(self) -> None:
        """Verify base interface can be imported."""
        assert BasePipelineAgent is not None


class TestPipelineIntegration:
    """Integration tests for pipeline types working together."""

    def test_create_pipeline_task_with_images(self) -> None:
        """Test creating a pipeline task with processed images."""
        # Create processed images
        image1 = ProcessedImage(
            original_url="https://example.com/image1.png",
            processed_path="/tmp/processed1.webp",
            width=800,
            height=600,
            format="webp",
            file_size=50000,
        )
        image2 = ProcessedImage(
            original_url="https://example.com/image2.jpg",
            processed_path="/tmp/processed2.webp",
            width=1200,
            height=900,
            format="webp",
            file_size=75000,
        )

        # Create pipeline task
        task = PipelineTask(
            task_id=UUID("12345678-1234-5678-1234-567812345678"),
            token_type=TokenType.COLOR,
            images=[image1, image2],
            config={"min_confidence": 0.7},
        )

        assert task.status == PipelineTaskStatus.PENDING
        assert len(task.images) == 2
        assert task.token_type == TokenType.COLOR

    def test_create_token_results_with_w3c_format(self) -> None:
        """Test creating token results with W3C format output."""
        # Create color token
        color_token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            path=["color", "brand"],
            w3c_type=W3CTokenType.COLOR,
            value="#3498db",
            confidence=0.95,
            description="Primary brand color",
            metadata={"source": "logo"},
        )

        # Verify W3C output
        w3c_dict = color_token.to_w3c_dict()
        assert w3c_dict["$value"] == "#3498db"
        assert w3c_dict["$type"] == "color"
        assert w3c_dict["$description"] == "Primary brand color"
        assert w3c_dict["$extensions"]["com.copythat"]["confidence"] == 0.95

        # Verify full path
        assert color_token.full_path == "color.brand.primary"

    def test_token_reference_system(self) -> None:
        """Test creating tokens with references to other tokens."""
        # Create base token
        base_token = TokenResult(
            token_type=TokenType.COLOR,
            name="blue-500",
            path=["color", "primitive"],
            w3c_type=W3CTokenType.COLOR,
            value="#3498db",
            confidence=1.0,
        )

        # Create token that references base
        semantic_token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            path=["color", "semantic"],
            w3c_type=W3CTokenType.COLOR,
            value="#3498db",
            reference="{color.primitive.blue-500}",
            confidence=1.0,
        )

        # Verify reference output
        w3c_dict = semantic_token.to_w3c_dict()
        assert w3c_dict["$value"] == "{color.primitive.blue-500}"

    def test_exception_hierarchy(self) -> None:
        """Test that exception hierarchy works correctly."""
        # All specific errors should be catchable as PipelineError
        errors = [
            PipelineValidationError("validation failed"),
            PipelineTimeoutError("timeout"),
            PipelineConfigurationError("bad config"),
            PipelineConnectionError("connection failed"),
            PipelineRateLimitError("rate limited", retry_after=60.0),
        ]

        for error in errors:
            assert isinstance(error, PipelineError)
            with pytest.raises(PipelineError):
                raise error

    def test_retryable_error_detection(self) -> None:
        """Test that retryable errors can be identified."""
        retryable_errors = [
            PipelineConnectionError("connection failed"),
            PipelineTimeoutError("timeout"),
            PipelineRateLimitError("rate limited"),
        ]

        for error in retryable_errors:
            assert isinstance(error, PipelineRetryableError)

    def test_composite_token_value(self) -> None:
        """Test creating tokens with composite values."""
        shadow_token = TokenResult(
            token_type=TokenType.SHADOW,
            name="elevation-1",
            path=["effect", "shadow"],
            w3c_type=W3CTokenType.SHADOW,
            value={
                "color": "#00000033",
                "offsetX": "0px",
                "offsetY": "2px",
                "blur": "4px",
                "spread": "0px",
            },
            confidence=0.88,
        )

        w3c_dict = shadow_token.to_w3c_dict()
        assert isinstance(w3c_dict["$value"], dict)
        assert w3c_dict["$value"]["blur"] == "4px"

    def test_pipeline_task_lifecycle(self) -> None:
        """Test pipeline task status transitions."""
        task = PipelineTask(
            task_id=UUID("12345678-1234-5678-1234-567812345678"),
            token_type=TokenType.COLOR,
            images=[],
        )

        # Initial state
        assert task.status == PipelineTaskStatus.PENDING

        # Simulate lifecycle transitions
        task.status = PipelineTaskStatus.PROCESSING
        task.started_at = datetime.now()
        assert task.status == PipelineTaskStatus.PROCESSING

        task.status = PipelineTaskStatus.COMPLETED
        task.completed_at = datetime.now()
        assert task.status == PipelineTaskStatus.COMPLETED


class TestW3CTokenTypeMapping:
    """Test W3C token type mappings for different token types."""

    def test_color_token_types(self) -> None:
        """Test color tokens use correct W3C type."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="test",
            value="#ff0000",
            w3c_type=W3CTokenType.COLOR,
            confidence=0.9,
        )
        assert token.to_w3c_dict()["$type"] == "color"

    def test_spacing_as_dimension(self) -> None:
        """Test spacing tokens use dimension W3C type."""
        token = TokenResult(
            token_type=TokenType.SPACING,
            name="md",
            value="16px",
            w3c_type=W3CTokenType.DIMENSION,
            confidence=0.9,
        )
        assert token.to_w3c_dict()["$type"] == "dimension"

    def test_typography_composite(self) -> None:
        """Test typography tokens use typography W3C type."""
        token = TokenResult(
            token_type=TokenType.TYPOGRAPHY,
            name="heading-1",
            value={
                "fontFamily": "Inter",
                "fontSize": "32px",
                "fontWeight": 700,
                "lineHeight": 1.2,
            },
            w3c_type=W3CTokenType.TYPOGRAPHY,
            confidence=0.85,
        )
        w3c = token.to_w3c_dict()
        assert w3c["$type"] == "typography"
        assert w3c["$value"]["fontFamily"] == "Inter"
