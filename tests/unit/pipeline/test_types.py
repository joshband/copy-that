"""Tests for pipeline types module

Tests for TokenType enum and Pydantic models: TokenResult, PipelineTask, ProcessedImage
"""

from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from copy_that.pipeline.types import (
    PipelineTask,
    ProcessedImage,
    TokenResult,
    TokenType,
)


class TestTokenType:
    """Test TokenType enum"""

    def test_token_type_color(self):
        """Test color token type exists"""
        assert TokenType.COLOR == "color"
        assert TokenType.COLOR.value == "color"

    def test_token_type_spacing(self):
        """Test spacing token type exists"""
        assert TokenType.SPACING == "spacing"
        assert TokenType.SPACING.value == "spacing"

    def test_token_type_typography(self):
        """Test typography token type exists"""
        assert TokenType.TYPOGRAPHY == "typography"
        assert TokenType.TYPOGRAPHY.value == "typography"

    def test_token_type_shadow(self):
        """Test shadow token type exists"""
        assert TokenType.SHADOW == "shadow"
        assert TokenType.SHADOW.value == "shadow"

    def test_token_type_gradient(self):
        """Test gradient token type exists"""
        assert TokenType.GRADIENT == "gradient"
        assert TokenType.GRADIENT.value == "gradient"

    def test_token_type_all_values(self):
        """Test all token types are accounted for"""
        expected = {"color", "spacing", "typography", "shadow", "gradient"}
        actual = {t.value for t in TokenType}
        assert actual == expected

    def test_token_type_from_string(self):
        """Test creating TokenType from string value"""
        assert TokenType("color") == TokenType.COLOR
        assert TokenType("spacing") == TokenType.SPACING

    def test_token_type_invalid_value(self):
        """Test invalid token type raises ValueError"""
        with pytest.raises(ValueError):
            TokenType("invalid")


class TestTokenResult:
    """Test TokenResult Pydantic model"""

    def test_token_result_creation(self):
        """Test basic TokenResult creation"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="primary-blue",
            value="#0066CC",
            confidence=0.95,
        )
        assert result.token_type == TokenType.COLOR
        assert result.name == "primary-blue"
        assert result.value == "#0066CC"
        assert result.confidence == 0.95

    def test_token_result_with_metadata(self):
        """Test TokenResult with metadata"""
        result = TokenResult(
            token_type=TokenType.TYPOGRAPHY,
            name="heading-font",
            value="Inter",
            confidence=0.88,
            metadata={"weight": "bold", "size": "24px"},
        )
        assert result.metadata == {"weight": "bold", "size": "24px"}

    def test_token_result_default_metadata(self):
        """Test TokenResult default metadata is None"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="accent",
            value="#FF5733",
            confidence=0.9,
        )
        assert result.metadata is None

    def test_token_result_confidence_bounds(self):
        """Test TokenResult confidence must be between 0 and 1"""
        # Valid confidence values
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="test",
            value="#000",
            confidence=0.0,
        )
        assert result.confidence == 0.0

        result = TokenResult(
            token_type=TokenType.COLOR,
            name="test",
            value="#000",
            confidence=1.0,
        )
        assert result.confidence == 1.0

    def test_token_result_invalid_confidence_too_low(self):
        """Test TokenResult rejects confidence below 0"""
        with pytest.raises(ValidationError):
            TokenResult(
                token_type=TokenType.COLOR,
                name="test",
                value="#000",
                confidence=-0.1,
            )

    def test_token_result_invalid_confidence_too_high(self):
        """Test TokenResult rejects confidence above 1"""
        with pytest.raises(ValidationError):
            TokenResult(
                token_type=TokenType.COLOR,
                name="test",
                value="#000",
                confidence=1.1,
            )

    def test_token_result_required_fields(self):
        """Test TokenResult requires all mandatory fields"""
        with pytest.raises(ValidationError):
            TokenResult(
                token_type=TokenType.COLOR,
                name="test",
                # missing value and confidence
            )

    def test_token_result_string_token_type(self):
        """Test TokenResult accepts string for token_type"""
        result = TokenResult(
            token_type="color",
            name="test",
            value="#000",
            confidence=0.5,
        )
        assert result.token_type == TokenType.COLOR

    def test_token_result_serialization(self):
        """Test TokenResult serializes to dict"""
        result = TokenResult(
            token_type=TokenType.SPACING,
            name="margin-small",
            value="8px",
            confidence=0.92,
            metadata={"unit": "px"},
        )
        data = result.model_dump()
        assert data["token_type"] == "spacing"
        assert data["name"] == "margin-small"
        assert data["value"] == "8px"
        assert data["confidence"] == 0.92
        assert data["metadata"] == {"unit": "px"}


class TestPipelineTask:
    """Test PipelineTask Pydantic model"""

    def test_pipeline_task_creation(self):
        """Test basic PipelineTask creation"""
        task = PipelineTask(
            task_id="task-123",
            image_url="https://example.com/image.png",
            token_types=[TokenType.COLOR],
        )
        assert task.task_id == "task-123"
        assert task.image_url == "https://example.com/image.png"
        assert task.token_types == [TokenType.COLOR]

    def test_pipeline_task_multiple_token_types(self):
        """Test PipelineTask with multiple token types"""
        task = PipelineTask(
            task_id="task-456",
            image_url="https://example.com/image.jpg",
            token_types=[TokenType.COLOR, TokenType.TYPOGRAPHY, TokenType.SPACING],
        )
        assert len(task.token_types) == 3
        assert TokenType.COLOR in task.token_types
        assert TokenType.TYPOGRAPHY in task.token_types
        assert TokenType.SPACING in task.token_types

    def test_pipeline_task_with_priority(self):
        """Test PipelineTask with priority"""
        task = PipelineTask(
            task_id="urgent-task",
            image_url="https://example.com/urgent.png",
            token_types=[TokenType.COLOR],
            priority=10,
        )
        assert task.priority == 10

    def test_pipeline_task_default_priority(self):
        """Test PipelineTask default priority is 0"""
        task = PipelineTask(
            task_id="task",
            image_url="https://example.com/img.png",
            token_types=[TokenType.COLOR],
        )
        assert task.priority == 0

    def test_pipeline_task_with_context(self):
        """Test PipelineTask with context"""
        task = PipelineTask(
            task_id="task-ctx",
            image_url="https://example.com/brand.png",
            token_types=[TokenType.COLOR],
            context={"project_id": 123, "session_id": 456},
        )
        assert task.context == {"project_id": 123, "session_id": 456}

    def test_pipeline_task_default_context(self):
        """Test PipelineTask default context is None"""
        task = PipelineTask(
            task_id="task",
            image_url="https://example.com/img.png",
            token_types=[TokenType.COLOR],
        )
        assert task.context is None

    def test_pipeline_task_created_at_auto(self):
        """Test PipelineTask auto-generates created_at"""
        task = PipelineTask(
            task_id="task",
            image_url="https://example.com/img.png",
            token_types=[TokenType.COLOR],
        )
        assert task.created_at is not None
        assert isinstance(task.created_at, datetime)

    def test_pipeline_task_empty_token_types_invalid(self):
        """Test PipelineTask requires at least one token type"""
        with pytest.raises(ValidationError):
            PipelineTask(
                task_id="task",
                image_url="https://example.com/img.png",
                token_types=[],
            )

    def test_pipeline_task_string_token_types(self):
        """Test PipelineTask accepts string token types"""
        task = PipelineTask(
            task_id="task",
            image_url="https://example.com/img.png",
            token_types=["color", "spacing"],
        )
        assert task.token_types == [TokenType.COLOR, TokenType.SPACING]

    def test_pipeline_task_serialization(self):
        """Test PipelineTask serializes to dict"""
        task = PipelineTask(
            task_id="task-ser",
            image_url="https://example.com/test.png",
            token_types=[TokenType.COLOR, TokenType.SHADOW],
            priority=5,
            context={"key": "value"},
        )
        data = task.model_dump()
        assert data["task_id"] == "task-ser"
        assert data["image_url"] == "https://example.com/test.png"
        assert "color" in data["token_types"]
        assert "shadow" in data["token_types"]
        assert data["priority"] == 5
        assert data["context"] == {"key": "value"}


class TestProcessedImage:
    """Test ProcessedImage Pydantic model"""

    def test_processed_image_creation(self):
        """Test basic ProcessedImage creation"""
        image = ProcessedImage(
            image_id="img-123",
            source_url="https://example.com/original.png",
            width=1920,
            height=1080,
        )
        assert image.image_id == "img-123"
        assert image.source_url == "https://example.com/original.png"
        assert image.width == 1920
        assert image.height == 1080

    def test_processed_image_with_format(self):
        """Test ProcessedImage with format"""
        image = ProcessedImage(
            image_id="img-456",
            source_url="https://example.com/photo.jpg",
            width=800,
            height=600,
            format="JPEG",
        )
        assert image.format == "JPEG"

    def test_processed_image_default_format(self):
        """Test ProcessedImage default format is None"""
        image = ProcessedImage(
            image_id="img",
            source_url="https://example.com/img.png",
            width=100,
            height=100,
        )
        assert image.format is None

    def test_processed_image_with_file_size(self):
        """Test ProcessedImage with file_size"""
        image = ProcessedImage(
            image_id="img-789",
            source_url="https://example.com/large.png",
            width=4000,
            height=3000,
            file_size=5242880,  # 5MB
        )
        assert image.file_size == 5242880

    def test_processed_image_with_preprocessed_data(self):
        """Test ProcessedImage with preprocessed_data"""
        image = ProcessedImage(
            image_id="img-pre",
            source_url="https://example.com/img.png",
            width=500,
            height=500,
            preprocessed_data={"histogram": [0.1, 0.2, 0.3], "dominant_color": "#FF0000"},
        )
        assert image.preprocessed_data["histogram"] == [0.1, 0.2, 0.3]
        assert image.preprocessed_data["dominant_color"] == "#FF0000"

    def test_processed_image_processed_at_auto(self):
        """Test ProcessedImage auto-generates processed_at"""
        image = ProcessedImage(
            image_id="img",
            source_url="https://example.com/img.png",
            width=100,
            height=100,
        )
        assert image.processed_at is not None
        assert isinstance(image.processed_at, datetime)

    def test_processed_image_positive_dimensions(self):
        """Test ProcessedImage requires positive dimensions"""
        with pytest.raises(ValidationError):
            ProcessedImage(
                image_id="img",
                source_url="https://example.com/img.png",
                width=0,
                height=100,
            )

        with pytest.raises(ValidationError):
            ProcessedImage(
                image_id="img",
                source_url="https://example.com/img.png",
                width=100,
                height=-1,
            )

    def test_processed_image_serialization(self):
        """Test ProcessedImage serializes to dict"""
        image = ProcessedImage(
            image_id="img-ser",
            source_url="https://example.com/ser.png",
            width=1280,
            height=720,
            format="PNG",
            file_size=1024000,
            preprocessed_data={"key": "value"},
        )
        data = image.model_dump()
        assert data["image_id"] == "img-ser"
        assert data["source_url"] == "https://example.com/ser.png"
        assert data["width"] == 1280
        assert data["height"] == 720
        assert data["format"] == "PNG"
        assert data["file_size"] == 1024000
        assert data["preprocessed_data"] == {"key": "value"}
        assert "processed_at" in data


class TestTokenResultEdgeCases:
    """Edge case tests for TokenResult"""

    def test_token_result_complex_metadata(self):
        """Test TokenResult with complex nested metadata"""
        result = TokenResult(
            token_type=TokenType.SHADOW,
            name="card-shadow",
            value="0 4px 6px rgba(0,0,0,0.1)",
            confidence=0.85,
            metadata={
                "offset_x": 0,
                "offset_y": 4,
                "blur": 6,
                "spread": 0,
                "color": {"r": 0, "g": 0, "b": 0, "a": 0.1},
            },
        )
        assert result.metadata["color"]["a"] == 0.1

    def test_token_result_empty_name(self):
        """Test TokenResult with empty name"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="",
            value="#000",
            confidence=0.5,
        )
        assert result.name == ""


class TestPipelineTaskEdgeCases:
    """Edge case tests for PipelineTask"""

    def test_pipeline_task_all_token_types(self):
        """Test PipelineTask with all token types"""
        task = PipelineTask(
            task_id="comprehensive-task",
            image_url="https://example.com/all.png",
            token_types=[
                TokenType.COLOR,
                TokenType.SPACING,
                TokenType.TYPOGRAPHY,
                TokenType.SHADOW,
                TokenType.GRADIENT,
            ],
        )
        assert len(task.token_types) == 5

    def test_pipeline_task_negative_priority(self):
        """Test PipelineTask with negative priority (low priority)"""
        task = PipelineTask(
            task_id="low-priority",
            image_url="https://example.com/low.png",
            token_types=[TokenType.COLOR],
            priority=-10,
        )
        assert task.priority == -10


class TestProcessedImageEdgeCases:
    """Edge case tests for ProcessedImage"""

    def test_processed_image_large_dimensions(self):
        """Test ProcessedImage with very large dimensions"""
        image = ProcessedImage(
            image_id="huge",
            source_url="https://example.com/huge.tiff",
            width=10000,
            height=10000,
        )
        assert image.width == 10000
        assert image.height == 10000

    def test_processed_image_zero_file_size(self):
        """Test ProcessedImage rejects zero file size"""
        with pytest.raises(ValidationError):
            ProcessedImage(
                image_id="img",
                source_url="https://example.com/img.png",
                width=100,
                height=100,
                file_size=0,
            )
