"""Tests for ValidationAgent

Comprehensive test suite for the ValidationAgent including:
- Schema validation
- Token validation with accessibility and quality scoring
- Batch validation
- Pipeline processing
- Configuration options
- Edge cases
"""

from unittest.mock import MagicMock, patch

import pytest

from copy_that.pipeline import (
    PipelineTask,
    TokenResult,
    TokenType,
    W3CTokenType,
)
from copy_that.pipeline.exceptions import ValidationError
from copy_that.pipeline.validation.agent import (
    ValidatedToken,
    ValidationAgent,
    ValidationConfig,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def default_config() -> ValidationConfig:
    """Default validation configuration."""
    return ValidationConfig()


@pytest.fixture
def strict_config() -> ValidationConfig:
    """Strict mode validation configuration."""
    return ValidationConfig(strict_mode=True, min_confidence=0.7)


@pytest.fixture
def valid_color_token() -> TokenResult:
    """Valid color token for testing."""
    return TokenResult(
        token_type=TokenType.COLOR,
        name="primary",
        path=["color", "brand"],
        w3c_type=W3CTokenType.COLOR,
        value="#FF6B35",
        confidence=0.95,
        description="Primary brand color",
    )


@pytest.fixture
def valid_spacing_token() -> TokenResult:
    """Valid spacing token for testing."""
    return TokenResult(
        token_type=TokenType.SPACING,
        name="medium",
        path=["spacing"],
        w3c_type=W3CTokenType.DIMENSION,
        value=16,
        confidence=0.85,
        description="Medium spacing value",
    )


@pytest.fixture
def invalid_hex_token() -> TokenResult:
    """Token with invalid hex color format."""
    return TokenResult(
        token_type=TokenType.COLOR,
        name="invalid-color",
        value="FF6B35",  # Missing #
        confidence=0.8,
    )


@pytest.fixture
def invalid_spacing_token() -> TokenResult:
    """Token with invalid (negative) spacing value."""
    return TokenResult(
        token_type=TokenType.SPACING,
        name="negative",
        value=-10,
        confidence=0.7,
    )


@pytest.fixture
def low_confidence_token() -> TokenResult:
    """Token with low confidence score."""
    return TokenResult(
        token_type=TokenType.COLOR,
        name="low-conf",
        value="#AABBCC",
        confidence=0.3,
    )


@pytest.fixture
def agent(default_config: ValidationConfig) -> ValidationAgent:
    """ValidationAgent with default configuration."""
    return ValidationAgent(config=default_config)


@pytest.fixture
def strict_agent(strict_config: ValidationConfig) -> ValidationAgent:
    """ValidationAgent with strict configuration."""
    return ValidationAgent(config=strict_config)


@pytest.fixture
def pipeline_task(valid_color_token: TokenResult, valid_spacing_token: TokenResult) -> PipelineTask:
    """Pipeline task with tokens in context."""
    return PipelineTask(
        task_id="test-task-001",
        image_url="https://example.com/image.png",
        token_types=[TokenType.COLOR, TokenType.SPACING],
        context={"tokens": [valid_color_token, valid_spacing_token]},
    )


# =============================================================================
# Test ValidationConfig
# =============================================================================


class TestValidationConfig:
    """Tests for ValidationConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ValidationConfig()
        assert config.min_confidence == 0.5
        assert config.strict_mode is False
        assert config.check_accessibility is True
        assert config.check_quality is True
        assert config.background_color == "#FFFFFF"

    def test_custom_config(self):
        """Test custom configuration values."""
        config = ValidationConfig(
            min_confidence=0.8,
            strict_mode=True,
            check_accessibility=False,
            check_quality=False,
            background_color="#000000",
        )
        assert config.min_confidence == 0.8
        assert config.strict_mode is True
        assert config.check_accessibility is False
        assert config.check_quality is False
        assert config.background_color == "#000000"

    def test_min_confidence_bounds(self):
        """Test min_confidence validation bounds."""
        # Valid bounds
        ValidationConfig(min_confidence=0.0)
        ValidationConfig(min_confidence=1.0)

        # Invalid bounds
        with pytest.raises(ValueError):
            ValidationConfig(min_confidence=-0.1)
        with pytest.raises(ValueError):
            ValidationConfig(min_confidence=1.1)


# =============================================================================
# Test ValidatedToken
# =============================================================================


class TestValidatedToken:
    """Tests for ValidatedToken model."""

    def test_default_values(self, valid_color_token: TokenResult):
        """Test default ValidatedToken values."""
        validated = ValidatedToken(token=valid_color_token)
        assert validated.is_valid is True
        assert validated.validation_errors == []
        assert validated.accessibility_score == 1.0
        assert validated.quality_score == 1.0
        assert validated.overall_score == 1.0

    def test_with_errors(self, valid_color_token: TokenResult):
        """Test ValidatedToken with validation errors."""
        validated = ValidatedToken(
            token=valid_color_token,
            is_valid=False,
            validation_errors=["Invalid format"],
            accessibility_score=0.5,
            quality_score=0.6,
            overall_score=0.54,
        )
        assert validated.is_valid is False
        assert len(validated.validation_errors) == 1
        assert validated.accessibility_score == 0.5


# =============================================================================
# Test Schema Validation
# =============================================================================


class TestSchemaValidation:
    """Tests for schema validation rules."""

    def test_valid_hex_color_6_digit(self, agent: ValidationAgent):
        """Test valid 6-digit hex color passes validation."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert errors == []

    def test_valid_hex_color_3_digit(self, agent: ValidationAgent):
        """Test valid 3-digit hex color passes validation."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="short",
            value="#F63",
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert errors == []

    def test_valid_hex_color_8_digit_alpha(self, agent: ValidationAgent):
        """Test valid 8-digit hex color with alpha passes validation."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="transparent",
            value="#FF6B35AA",
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert errors == []

    def test_valid_hex_color_lowercase(self, agent: ValidationAgent):
        """Test lowercase hex color passes validation."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="lower",
            value="#ff6b35",
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert errors == []

    def test_invalid_hex_missing_hash(self, agent: ValidationAgent):
        """Test hex color without # fails validation."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="no-hash",
            value="FF6B35",
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert len(errors) == 1
        assert "Invalid hex color format" in errors[0]

    def test_invalid_hex_wrong_length(self, agent: ValidationAgent):
        """Test hex color with wrong length fails validation."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="wrong-len",
            value="#FF6B3",  # 5 characters
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert len(errors) == 1
        assert "Invalid hex color format" in errors[0]

    def test_invalid_hex_invalid_chars(self, agent: ValidationAgent):
        """Test hex color with invalid characters fails validation."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="invalid-chars",
            value="#GG6B35",  # G is not valid hex
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert len(errors) == 1
        assert "Invalid hex color format" in errors[0]

    def test_valid_positive_spacing(self, agent: ValidationAgent):
        """Test positive spacing value passes validation."""
        token = TokenResult(
            token_type=TokenType.SPACING,
            name="medium",
            value=16,
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert errors == []

    def test_invalid_negative_spacing(self, agent: ValidationAgent):
        """Test negative spacing value fails validation."""
        token = TokenResult(
            token_type=TokenType.SPACING,
            name="negative",
            value=-10,
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert len(errors) == 1
        assert "Spacing value must be positive" in errors[0]

    def test_invalid_zero_spacing(self, agent: ValidationAgent):
        """Test zero spacing value fails validation."""
        token = TokenResult(
            token_type=TokenType.SPACING,
            name="zero",
            value=0,
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert len(errors) == 1
        assert "Spacing value must be positive" in errors[0]

    def test_valid_float_spacing(self, agent: ValidationAgent):
        """Test positive float spacing value passes validation."""
        token = TokenResult(
            token_type=TokenType.SPACING,
            name="float-space",
            value=16.5,
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert errors == []

    def test_empty_name_fails(self, agent: ValidationAgent):
        """Test empty token name fails validation."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="",
            value="#FF6B35",
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert len(errors) == 1
        assert "Token name is required" in errors[0]

    def test_whitespace_name_fails(self, agent: ValidationAgent):
        """Test whitespace-only token name fails validation."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="   ",
            value="#FF6B35",
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert len(errors) == 1
        assert "Token name is required" in errors[0]

    def test_multiple_validation_errors(self, agent: ValidationAgent):
        """Test token with multiple validation errors."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="",
            value="invalid-color",
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert len(errors) == 2
        assert any("Invalid hex color format" in e for e in errors)
        assert any("Token name is required" in e for e in errors)

    def test_non_string_color_value_skips_hex_check(self, agent: ValidationAgent):
        """Test that non-string color values don't trigger hex validation."""
        # Color token with dict value (like gradient stops)
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="gradient",
            value={"stops": [{"color": "#FF0000", "position": 0}]},
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert errors == []

    def test_non_numeric_spacing_value_skips_positive_check(self, agent: ValidationAgent):
        """Test that non-numeric spacing values don't trigger positive check."""
        # Spacing token with string value
        token = TokenResult(
            token_type=TokenType.SPACING,
            name="custom",
            value="auto",
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert errors == []

    def test_typography_token_no_special_validation(self, agent: ValidationAgent):
        """Test typography token with no special validation rules."""
        token = TokenResult(
            token_type=TokenType.TYPOGRAPHY,
            name="body",
            value={"fontFamily": "Arial", "fontSize": 16},
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert errors == []


# =============================================================================
# Test validate_token Method
# =============================================================================


class TestValidateToken:
    """Tests for single token validation."""

    def test_valid_token_returns_valid_result(
        self, agent: ValidationAgent, valid_color_token: TokenResult
    ):
        """Test that valid token returns valid result."""
        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.9
            ),
            patch.object(agent.quality_scorer, "calculate_quality_score", return_value=0.85),
        ):
            result = agent.validate_token(valid_color_token)

        assert result.is_valid is True
        assert result.validation_errors == []
        assert result.token == valid_color_token

    def test_invalid_token_returns_errors(
        self, agent: ValidationAgent, invalid_hex_token: TokenResult
    ):
        """Test that invalid token returns validation errors."""
        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.5
            ),
            patch.object(agent.quality_scorer, "calculate_quality_score", return_value=0.6),
        ):
            result = agent.validate_token(invalid_hex_token)

        assert result.is_valid is False
        assert len(result.validation_errors) > 0
        assert "Invalid hex color format" in result.validation_errors[0]

    def test_accessibility_score_integration(
        self, agent: ValidationAgent, valid_color_token: TokenResult
    ):
        """Test that accessibility score is calculated."""
        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.75
            ) as mock_calc,
            patch.object(agent.quality_scorer, "calculate_quality_score", return_value=0.8),
        ):
            result = agent.validate_token(valid_color_token)

        assert result.accessibility_score == 0.75
        mock_calc.assert_called_once()

    def test_quality_score_integration(
        self, agent: ValidationAgent, valid_color_token: TokenResult
    ):
        """Test that quality score is calculated."""
        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.8
            ),
            patch.object(
                agent.quality_scorer, "calculate_quality_score", return_value=0.65
            ) as mock_scorer,
        ):
            result = agent.validate_token(valid_color_token)

        assert result.quality_score == 0.65
        mock_scorer.assert_called_once()

    def test_overall_score_calculation_no_errors(
        self, agent: ValidationAgent, valid_color_token: TokenResult
    ):
        """Test overall score calculation for valid token."""
        # overall = accessibility * 0.4 + quality * 0.4 + (1.0) * 0.2
        # = 0.8 * 0.4 + 0.7 * 0.4 + 1.0 * 0.2
        # = 0.32 + 0.28 + 0.2 = 0.8
        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.8
            ),
            patch.object(agent.quality_scorer, "calculate_quality_score", return_value=0.7),
        ):
            result = agent.validate_token(valid_color_token)

        expected = 0.8 * 0.4 + 0.7 * 0.4 + 1.0 * 0.2
        assert abs(result.overall_score - expected) < 0.001

    def test_overall_score_calculation_with_errors(
        self, agent: ValidationAgent, invalid_hex_token: TokenResult
    ):
        """Test overall score calculation for token with errors."""
        # overall = accessibility * 0.4 + quality * 0.4 + (0.5) * 0.2
        # = 0.8 * 0.4 + 0.7 * 0.4 + 0.5 * 0.2
        # = 0.32 + 0.28 + 0.1 = 0.7
        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.8
            ),
            patch.object(agent.quality_scorer, "calculate_quality_score", return_value=0.7),
        ):
            result = agent.validate_token(invalid_hex_token)

        expected = 0.8 * 0.4 + 0.7 * 0.4 + 0.5 * 0.2
        assert abs(result.overall_score - expected) < 0.001

    def test_accessibility_check_disabled(self, valid_color_token: TokenResult):
        """Test that accessibility check can be disabled."""
        config = ValidationConfig(check_accessibility=False)
        agent = ValidationAgent(config=config)

        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score"
            ) as mock_calc,
            patch.object(agent.quality_scorer, "calculate_quality_score", return_value=0.8),
        ):
            result = agent.validate_token(valid_color_token)

        mock_calc.assert_not_called()
        assert result.accessibility_score == 1.0

    def test_quality_check_disabled(self, valid_color_token: TokenResult):
        """Test that quality check can be disabled."""
        config = ValidationConfig(check_quality=False)
        agent = ValidationAgent(config=config)

        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.8
            ),
            patch.object(agent.quality_scorer, "calculate_quality_score") as mock_scorer,
        ):
            result = agent.validate_token(valid_color_token)

        mock_scorer.assert_not_called()
        assert result.quality_score == 1.0

    def test_background_color_passed_to_accessibility(self, valid_color_token: TokenResult):
        """Test that background color is passed to accessibility calculator."""
        config = ValidationConfig(background_color="#000000")
        agent = ValidationAgent(config=config)

        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.8
            ) as mock_calc,
            patch.object(agent.quality_scorer, "calculate_quality_score", return_value=0.8),
        ):
            agent.validate_token(valid_color_token)

        # Check that calculate_accessibility_score was called with background color
        mock_calc.assert_called_once()
        call_kwargs = mock_calc.call_args
        assert "#000000" in str(call_kwargs) or call_kwargs[1].get("background_color") == "#000000"


# =============================================================================
# Test validate_tokens Method (Batch Validation)
# =============================================================================


class TestValidateTokensBatch:
    """Tests for batch token validation."""

    def test_batch_validation_multiple_tokens(
        self,
        agent: ValidationAgent,
        valid_color_token: TokenResult,
        valid_spacing_token: TokenResult,
    ):
        """Test batch validation with multiple valid tokens."""
        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.9
            ),
            patch.object(agent.quality_scorer, "calculate_quality_score", return_value=0.85),
        ):
            results = agent.validate_tokens([valid_color_token, valid_spacing_token])

        assert len(results) == 2
        assert all(r.is_valid for r in results)

    def test_batch_validation_empty_list(self, agent: ValidationAgent):
        """Test batch validation with empty list."""
        results = agent.validate_tokens([])
        assert results == []

    def test_batch_validation_mixed_valid_invalid(
        self, agent: ValidationAgent, valid_color_token: TokenResult, invalid_hex_token: TokenResult
    ):
        """Test batch validation with mixed valid and invalid tokens."""
        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.8
            ),
            patch.object(agent.quality_scorer, "calculate_quality_score", return_value=0.7),
        ):
            results = agent.validate_tokens([valid_color_token, invalid_hex_token])

        assert len(results) == 2
        assert results[0].is_valid is True
        assert results[1].is_valid is False

    def test_batch_validation_preserves_order(
        self,
        agent: ValidationAgent,
        valid_color_token: TokenResult,
        valid_spacing_token: TokenResult,
    ):
        """Test that batch validation preserves token order."""
        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.9
            ),
            patch.object(agent.quality_scorer, "calculate_quality_score", return_value=0.85),
        ):
            results = agent.validate_tokens([valid_color_token, valid_spacing_token])

        assert results[0].token == valid_color_token
        assert results[1].token == valid_spacing_token

    def test_batch_validation_all_invalid(
        self,
        agent: ValidationAgent,
        invalid_hex_token: TokenResult,
        invalid_spacing_token: TokenResult,
    ):
        """Test batch validation when all tokens are invalid."""
        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.5
            ),
            patch.object(agent.quality_scorer, "calculate_quality_score", return_value=0.5),
        ):
            results = agent.validate_tokens([invalid_hex_token, invalid_spacing_token])

        assert len(results) == 2
        assert all(not r.is_valid for r in results)


# =============================================================================
# Test process Method (Pipeline Integration)
# =============================================================================


class TestProcessPipeline:
    """Tests for pipeline task processing."""

    @pytest.mark.asyncio
    async def test_process_returns_validated_tokens(
        self, agent: ValidationAgent, pipeline_task: PipelineTask
    ):
        """Test that process returns validated TokenResult objects."""
        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.9
            ),
            patch.object(agent.quality_scorer, "calculate_quality_score", return_value=0.85),
        ):
            results = await agent.process(pipeline_task)

        assert len(results) == 2
        assert all(isinstance(r, TokenResult) for r in results)

    @pytest.mark.asyncio
    async def test_process_strict_mode_filters_invalid(
        self,
        strict_agent: ValidationAgent,
        valid_color_token: TokenResult,
        invalid_hex_token: TokenResult,
    ):
        """Test that strict mode filters out invalid tokens."""
        task = PipelineTask(
            task_id="test-strict",
            image_url="https://example.com/image.png",
            token_types=[TokenType.COLOR],
            context={"tokens": [valid_color_token, invalid_hex_token]},
        )

        with (
            patch.object(
                strict_agent.accessibility_calculator,
                "calculate_accessibility_score",
                return_value=0.9,
            ),
            patch.object(strict_agent.quality_scorer, "calculate_quality_score", return_value=0.85),
        ):
            results = await strict_agent.process(task)

        # Should only return the valid token
        assert len(results) == 1
        assert results[0].name == "primary"

    @pytest.mark.asyncio
    async def test_process_strict_mode_filters_low_confidence(
        self,
        strict_agent: ValidationAgent,
        valid_color_token: TokenResult,
        low_confidence_token: TokenResult,
    ):
        """Test that strict mode filters tokens below min_confidence."""
        task = PipelineTask(
            task_id="test-conf",
            image_url="https://example.com/image.png",
            token_types=[TokenType.COLOR],
            context={"tokens": [valid_color_token, low_confidence_token]},
        )

        with (
            patch.object(
                strict_agent.accessibility_calculator,
                "calculate_accessibility_score",
                return_value=0.9,
            ),
            patch.object(strict_agent.quality_scorer, "calculate_quality_score", return_value=0.85),
        ):
            results = await strict_agent.process(task)

        # Low confidence token (0.3) should be filtered out (min_confidence = 0.7)
        assert len(results) == 1
        assert results[0].name == "primary"

    @pytest.mark.asyncio
    async def test_process_lenient_mode_keeps_invalid(
        self, agent: ValidationAgent, valid_color_token: TokenResult, invalid_hex_token: TokenResult
    ):
        """Test that lenient mode keeps invalid tokens."""
        task = PipelineTask(
            task_id="test-lenient",
            image_url="https://example.com/image.png",
            token_types=[TokenType.COLOR],
            context={"tokens": [valid_color_token, invalid_hex_token]},
        )

        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.9
            ),
            patch.object(agent.quality_scorer, "calculate_quality_score", return_value=0.85),
        ):
            results = await agent.process(task)

        # Should keep both tokens in lenient mode
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_process_missing_tokens_in_context(self, agent: ValidationAgent):
        """Test process with missing tokens in context raises error."""
        task = PipelineTask(
            task_id="test-missing",
            image_url="https://example.com/image.png",
            token_types=[TokenType.COLOR],
            context={},  # No tokens
        )

        with pytest.raises(ValidationError) as exc_info:
            await agent.process(task)

        assert "No tokens" in str(exc_info.value) or "tokens" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_process_none_context(self, agent: ValidationAgent):
        """Test process with None context raises error."""
        task = PipelineTask(
            task_id="test-none",
            image_url="https://example.com/image.png",
            token_types=[TokenType.COLOR],
            context=None,
        )

        with pytest.raises(ValidationError) as exc_info:
            await agent.process(task)

        assert "No tokens" in str(exc_info.value) or "context" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_process_all_tokens_fail_raises_error(
        self,
        strict_agent: ValidationAgent,
        invalid_hex_token: TokenResult,
        invalid_spacing_token: TokenResult,
    ):
        """Test that all tokens failing in strict mode raises ValidationError."""
        task = PipelineTask(
            task_id="test-all-fail",
            image_url="https://example.com/image.png",
            token_types=[TokenType.COLOR, TokenType.SPACING],
            context={"tokens": [invalid_hex_token, invalid_spacing_token]},
        )

        with (
            patch.object(
                strict_agent.accessibility_calculator,
                "calculate_accessibility_score",
                return_value=0.5,
            ),
            patch.object(strict_agent.quality_scorer, "calculate_quality_score", return_value=0.5),
            pytest.raises(ValidationError) as exc_info,
        ):
            await strict_agent.process(task)

        assert "all" in str(exc_info.value).lower() or "no valid" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_process_empty_tokens_list(self, agent: ValidationAgent):
        """Test process with empty tokens list."""
        task = PipelineTask(
            task_id="test-empty",
            image_url="https://example.com/image.png",
            token_types=[TokenType.COLOR],
            context={"tokens": []},
        )

        with pytest.raises(ValidationError) as exc_info:
            await agent.process(task)

        assert "No tokens" in str(exc_info.value) or "empty" in str(exc_info.value).lower()


# =============================================================================
# Test health_check Method
# =============================================================================


class TestHealthCheck:
    """Tests for health check functionality."""

    @pytest.mark.asyncio
    async def test_health_check_returns_true(self, agent: ValidationAgent):
        """Test that health check returns True when healthy."""
        result = await agent.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_type(self, agent: ValidationAgent):
        """Test that health check returns boolean."""
        result = await agent.health_check()
        assert isinstance(result, bool)


# =============================================================================
# Test Agent Properties
# =============================================================================


class TestAgentProperties:
    """Tests for agent type and stage properties."""

    def test_agent_type_property(self, agent: ValidationAgent):
        """Test agent_type property returns correct value."""
        assert agent.agent_type == "validation"

    def test_stage_name_property(self, agent: ValidationAgent):
        """Test stage_name property returns correct value."""
        assert agent.stage_name == "validation"


# =============================================================================
# Test Configuration Options
# =============================================================================


class TestConfigurationOptions:
    """Tests for configuration options."""

    def test_min_confidence_filtering(self):
        """Test that min_confidence affects quality score calculation."""
        config = ValidationConfig(min_confidence=0.8, strict_mode=True)
        agent = ValidationAgent(config=config)

        high_conf = TokenResult(
            token_type=TokenType.COLOR,
            name="high",
            value="#FF0000",
            confidence=0.9,
        )
        low_conf = TokenResult(
            token_type=TokenType.COLOR,
            name="low",
            value="#00FF00",
            confidence=0.6,
        )

        # Use side_effect to return different quality scores based on confidence
        def quality_score_by_confidence(token):
            return token.confidence * 0.8  # Scale confidence to quality

        with (
            patch.object(
                agent.accessibility_calculator, "calculate_accessibility_score", return_value=0.9
            ),
            patch.object(
                agent.quality_scorer, "calculate_quality_score", side_effect=quality_score_by_confidence
            ),
        ):
            results = agent.validate_tokens([high_conf, low_conf])

        # Low confidence token should have lower overall score
        assert results[0].overall_score > results[1].overall_score

    def test_agent_initialization_with_none_config(self):
        """Test agent can be initialized with None config."""
        agent = ValidationAgent(config=None)
        assert agent.config.min_confidence == 0.5
        assert agent.config.strict_mode is False


# =============================================================================
# Test get_quality_report Method
# =============================================================================


class TestGetQualityReport:
    """Tests for quality report generation."""

    def test_get_quality_report_calls_scorer(
        self,
        agent: ValidationAgent,
        valid_color_token: TokenResult,
        valid_spacing_token: TokenResult,
    ):
        """Test that get_quality_report calls the quality scorer."""
        mock_report = MagicMock()
        with patch.object(
            agent.quality_scorer, "generate_quality_report", return_value=mock_report
        ) as mock_gen:
            result = agent.get_quality_report([valid_color_token, valid_spacing_token])

        mock_gen.assert_called_once_with([valid_color_token, valid_spacing_token])
        assert result == mock_report


# =============================================================================
# Test Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_token_with_max_confidence(self, agent: ValidationAgent):
        """Test token with maximum confidence score."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="max-conf",
            value="#FF6B35",
            confidence=1.0,
        )
        errors = agent.validate_schema(token)
        assert errors == []

    def test_token_with_min_confidence(self, agent: ValidationAgent):
        """Test token with minimum confidence score."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="min-conf",
            value="#FF6B35",
            confidence=0.0,
        )
        errors = agent.validate_schema(token)
        assert errors == []

    def test_shadow_token_type(self, agent: ValidationAgent):
        """Test shadow token type validation."""
        token = TokenResult(
            token_type=TokenType.SHADOW,
            name="elevation-1",
            value={"offsetX": 0, "offsetY": 2, "blur": 4, "color": "#00000033"},
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert errors == []

    def test_gradient_token_type(self, agent: ValidationAgent):
        """Test gradient token type validation."""
        token = TokenResult(
            token_type=TokenType.GRADIENT,
            name="brand-gradient",
            value={"type": "linear", "stops": []},
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert errors == []

    def test_unicode_token_name(self, agent: ValidationAgent):
        """Test token with unicode name."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert errors == []

    def test_very_long_token_name(self, agent: ValidationAgent):
        """Test token with very long name."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="a" * 1000,
            value="#FF6B35",
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert errors == []

    def test_special_characters_in_name(self, agent: ValidationAgent):
        """Test token with special characters in name."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="color-primary_v2.0",
            value="#FF6B35",
            confidence=0.9,
        )
        errors = agent.validate_schema(token)
        assert errors == []


# =============================================================================
# Test Hex Validation Helper
# =============================================================================


class TestHexValidation:
    """Tests for hex color validation helper."""

    def test_valid_hex_formats(self, agent: ValidationAgent):
        """Test various valid hex formats."""
        valid_colors = [
            "#FFF",
            "#fff",
            "#FFFFFF",
            "#ffffff",
            "#FFFFFFFF",
            "#ffffffff",
            "#123",
            "#ABC",
            "#abc",
            "#123456",
            "#ABCDEF",
            "#12345678",
        ]
        for color in valid_colors:
            assert agent._is_valid_hex(color), f"Expected {color} to be valid"

    def test_invalid_hex_formats(self, agent: ValidationAgent):
        """Test various invalid hex formats."""
        invalid_colors = [
            "FFF",  # No #
            "#FF",  # Too short
            "#FFFF",  # Wrong length (4)
            "#FFFFF",  # Wrong length (5)
            "#FFFFFFF",  # Wrong length (7)
            "#FFFFFFFFF",  # Too long (9)
            "#GGG",  # Invalid chars
            "##FFF",  # Double #
            "#FFF#",  # Trailing #
            "",  # Empty
            "#",  # Just #
        ]
        for color in invalid_colors:
            assert not agent._is_valid_hex(color), f"Expected {color} to be invalid"
