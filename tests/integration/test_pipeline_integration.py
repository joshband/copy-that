"""Integration tests for pipeline module.

Tests that pipeline module exports are accessible and types work correctly
in a realistic context.
"""

from datetime import datetime

import pytest

from copy_that.pipeline import (
    AggregationError,
    BasePipelineAgent,
    ExtractionError,
    GenerationError,
    PipelineError,
    PipelineTask,
    PreprocessingError,
    ProcessedImage,
    TokenResult,
    TokenType,
    ValidationError,
    W3CTokenType,
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

    def test_all_exceptions_importable(self) -> None:
        """Verify all exceptions can be imported."""
        assert PipelineError is not None
        assert PreprocessingError is not None
        assert ExtractionError is not None
        assert AggregationError is not None
        assert ValidationError is not None
        assert GenerationError is not None

    def test_base_interface_importable(self) -> None:
        """Verify base interface can be imported."""
        assert BasePipelineAgent is not None


class TestPipelineIntegration:
    """Integration tests for pipeline types working together."""

    def test_create_pipeline_task(self) -> None:
        """Test creating a pipeline task."""
        task = PipelineTask(
            task_id="test-task-123",
            image_url="https://example.com/image.png",
            token_types=[TokenType.COLOR, TokenType.SPACING],
            priority=5,
            context={"source": "integration_test"},
        )

        assert task.task_id == "test-task-123"
        assert len(task.token_types) == 2
        assert task.priority == 5
        assert isinstance(task.created_at, datetime)

    def test_create_processed_image(self) -> None:
        """Test creating a processed image metadata."""
        image = ProcessedImage(
            image_id="img-456",
            original_url="https://example.com/image.png",
            processed_path="/tmp/processed.webp",
            width=800,
            height=600,
            format="webp",
            file_size=50000,
        )

        assert image.image_id == "img-456"
        assert image.width == 800
        assert image.format == "webp"

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
        # Create token that references another
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
            PreprocessingError("preprocessing failed"),
            ExtractionError("extraction failed"),
            AggregationError("aggregation failed"),
            ValidationError("validation failed"),
            GenerationError("generation failed"),
        ]

        for error in errors:
            assert isinstance(error, PipelineError)
            with pytest.raises(PipelineError):
                raise error

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

    def test_pipeline_task_token_type_conversion(self) -> None:
        """Test pipeline task converts string token types."""
        task = PipelineTask(
            task_id="test-123",
            image_url="https://example.com/image.png",
            token_types=["color", "spacing"],  # type: ignore
        )

        # Should convert strings to TokenType enums
        assert task.token_types[0] == TokenType.COLOR
        assert task.token_types[1] == TokenType.SPACING


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

    def test_all_w3c_token_types(self) -> None:
        """Test all W3C token type enum values."""
        expected_types = [
            "color",
            "dimension",
            "fontFamily",
            "fontWeight",
            "duration",
            "cubicBezier",
            "number",
            "strokeStyle",
            "border",
            "transition",
            "shadow",
            "gradient",
            "typography",
            "composition",
        ]
        actual_types = [t.value for t in W3CTokenType]
        assert sorted(actual_types) == sorted(expected_types)
