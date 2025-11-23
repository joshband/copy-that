"""Tests for pipeline types module

Tests for TokenType enum and Pydantic models: TokenResult, PipelineTask, ProcessedImage
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from copy_that.pipeline.types import (
    PipelineTask,
    ProcessedImage,
    TokenResult,
    TokenType,
    W3CTokenType,
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


class TestW3CTokenType:
    """Test W3CTokenType enum"""

    def test_w3c_token_type_color(self):
        """Test color W3C token type"""
        assert W3CTokenType.COLOR == "color"
        assert W3CTokenType.COLOR.value == "color"

    def test_w3c_token_type_dimension(self):
        """Test dimension W3C token type"""
        assert W3CTokenType.DIMENSION == "dimension"
        assert W3CTokenType.DIMENSION.value == "dimension"

    def test_w3c_token_type_font_family(self):
        """Test fontFamily W3C token type"""
        assert W3CTokenType.FONT_FAMILY == "fontFamily"
        assert W3CTokenType.FONT_FAMILY.value == "fontFamily"

    def test_w3c_token_type_typography(self):
        """Test typography W3C token type"""
        assert W3CTokenType.TYPOGRAPHY == "typography"
        assert W3CTokenType.TYPOGRAPHY.value == "typography"

    def test_w3c_token_type_all_values(self):
        """Test all W3C token types are accounted for"""
        expected = {
            "color", "dimension", "fontFamily", "fontWeight",
            "duration", "cubicBezier", "number", "strokeStyle",
            "border", "transition", "shadow", "gradient",
            "typography", "composition"
        }
        actual = {t.value for t in W3CTokenType}
        assert actual == expected

    def test_w3c_token_type_from_string(self):
        """Test creating W3CTokenType from string value"""
        assert W3CTokenType("color") == W3CTokenType.COLOR
        assert W3CTokenType("dimension") == W3CTokenType.DIMENSION
        assert W3CTokenType("fontFamily") == W3CTokenType.FONT_FAMILY


class TestTokenResultW3C:
    """Test TokenResult W3C features"""

    def test_token_result_with_path(self):
        """Test TokenResult with W3C path hierarchy"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            path=["color", "brand"],
            value="#FF6B35",
            confidence=0.95,
        )
        assert result.path == ["color", "brand"]
        assert result.name == "primary"

    def test_token_result_full_path_property(self):
        """Test full_path property returns dot-separated path"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            path=["color", "brand"],
            value="#FF6B35",
            confidence=0.95,
        )
        assert result.full_path == "color.brand.primary"

    def test_token_result_full_path_no_hierarchy(self):
        """Test full_path with no path returns just name"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="accent",
            value="#FF5733",
            confidence=0.9,
        )
        assert result.full_path == "accent"

    def test_token_result_with_w3c_type(self):
        """Test TokenResult with W3C type specification"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            w3c_type=W3CTokenType.COLOR,
            value="#FF6B35",
            confidence=0.95,
        )
        assert result.w3c_type == W3CTokenType.COLOR

    def test_token_result_with_description(self):
        """Test TokenResult with W3C description"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
            description="Primary brand color - vibrant orange",
        )
        assert result.description == "Primary brand color - vibrant orange"

    def test_token_result_with_reference(self):
        """Test TokenResult with token reference"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="primaryHover",
            value="",
            reference="{color.brand.primary}",
            confidence=1.0,
        )
        assert result.reference == "{color.brand.primary}"

    def test_token_result_with_extensions(self):
        """Test TokenResult with W3C extensions"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
            extensions={
                "com.figma": {"variableId": "VariableID:123"}
            },
        )
        assert result.extensions["com.figma"]["variableId"] == "VariableID:123"

    def test_token_result_composite_value(self):
        """Test TokenResult with composite dict value"""
        result = TokenResult(
            token_type=TokenType.TYPOGRAPHY,
            name="heading-1",
            w3c_type=W3CTokenType.TYPOGRAPHY,
            value={
                "fontFamily": "Inter",
                "fontSize": "32px",
                "fontWeight": 700,
                "lineHeight": 1.2,
            },
            confidence=0.88,
        )
        assert result.value["fontFamily"] == "Inter"
        assert result.value["fontSize"] == "32px"
        assert result.value["fontWeight"] == 700

    def test_token_result_numeric_value(self):
        """Test TokenResult with numeric value"""
        result = TokenResult(
            token_type=TokenType.SPACING,
            name="base",
            w3c_type=W3CTokenType.NUMBER,
            value=8,
            confidence=1.0,
        )
        assert result.value == 8

    def test_token_result_to_w3c_dict_basic(self):
        """Test to_w3c_dict with basic token"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            w3c_type=W3CTokenType.COLOR,
            value="#FF6B35",
            confidence=0.95,
        )
        w3c = result.to_w3c_dict()
        assert w3c["$value"] == "#FF6B35"
        assert w3c["$type"] == "color"
        assert "com.copythat" in w3c["$extensions"]
        assert w3c["$extensions"]["com.copythat"]["confidence"] == 0.95

    def test_token_result_to_w3c_dict_with_description(self):
        """Test to_w3c_dict includes description"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            w3c_type=W3CTokenType.COLOR,
            value="#FF6B35",
            confidence=0.95,
            description="Primary brand color",
        )
        w3c = result.to_w3c_dict()
        assert w3c["$description"] == "Primary brand color"

    def test_token_result_to_w3c_dict_with_reference(self):
        """Test to_w3c_dict uses reference as value"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="primaryHover",
            value="",
            reference="{color.brand.primary}",
            confidence=1.0,
        )
        w3c = result.to_w3c_dict()
        assert w3c["$value"] == "{color.brand.primary}"

    def test_token_result_to_w3c_dict_with_extensions(self):
        """Test to_w3c_dict merges custom extensions"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            w3c_type=W3CTokenType.COLOR,
            value="#FF6B35",
            confidence=0.95,
            extensions={
                "com.figma": {"variableId": "123"}
            },
        )
        w3c = result.to_w3c_dict()
        assert w3c["$extensions"]["com.figma"]["variableId"] == "123"
        assert w3c["$extensions"]["com.copythat"]["confidence"] == 0.95

    def test_token_result_to_w3c_dict_composite(self):
        """Test to_w3c_dict with composite value"""
        result = TokenResult(
            token_type=TokenType.TYPOGRAPHY,
            name="heading",
            w3c_type=W3CTokenType.TYPOGRAPHY,
            value={
                "fontFamily": "Inter",
                "fontSize": "24px",
            },
            confidence=0.9,
        )
        w3c = result.to_w3c_dict()
        assert w3c["$value"]["fontFamily"] == "Inter"
        assert w3c["$type"] == "typography"

    def test_token_result_serialization_with_w3c_fields(self):
        """Test TokenResult serialization includes W3C fields"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            path=["color", "brand"],
            w3c_type=W3CTokenType.COLOR,
            value="#FF6B35",
            confidence=0.95,
            description="Primary color",
            extensions={"key": "value"},
        )
        data = result.model_dump()
        assert data["path"] == ["color", "brand"]
        assert data["w3c_type"] == "color"
        assert data["description"] == "Primary color"
        assert data["extensions"] == {"key": "value"}

    def test_token_result_default_w3c_fields(self):
        """Test TokenResult W3C fields have correct defaults"""
        result = TokenResult(
            token_type=TokenType.COLOR,
            name="test",
            value="#000",
            confidence=0.5,
        )
        assert result.path == []
        assert result.w3c_type is None
        assert result.description is None
        assert result.reference is None
        assert result.extensions is None

    def test_token_result_spacing_dimension(self):
        """Test spacing token with dimension type"""
        result = TokenResult(
            token_type=TokenType.SPACING,
            name="md",
            path=["spacing"],
            w3c_type=W3CTokenType.DIMENSION,
            value="16px",
            confidence=0.92,
            description="Medium spacing",
        )
        w3c = result.to_w3c_dict()
        assert w3c["$value"] == "16px"
        assert w3c["$type"] == "dimension"

    def test_token_result_shadow_composite(self):
        """Test shadow token with composite value"""
        result = TokenResult(
            token_type=TokenType.SHADOW,
            name="card",
            path=["shadow"],
            w3c_type=W3CTokenType.SHADOW,
            value={
                "offsetX": "0px",
                "offsetY": "4px",
                "blur": "6px",
                "spread": "0px",
                "color": "rgba(0,0,0,0.1)",
            },
            confidence=0.85,
        )
        assert result.value["blur"] == "6px"
        w3c = result.to_w3c_dict()
        assert w3c["$type"] == "shadow"

    def test_token_result_gradient_composite(self):
        """Test gradient token with composite value"""
        result = TokenResult(
            token_type=TokenType.GRADIENT,
            name="primary",
            path=["gradient"],
            w3c_type=W3CTokenType.GRADIENT,
            value={
                "type": "linear",
                "angle": 90,
                "stops": [
                    {"color": "#FF6B35", "position": 0},
                    {"color": "#FF9966", "position": 100},
                ],
            },
            confidence=0.8,
        )
        assert result.value["type"] == "linear"
        assert len(result.value["stops"]) == 2
