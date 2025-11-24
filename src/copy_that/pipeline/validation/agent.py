"""
ValidationAgent for the token extraction pipeline.

Orchestrates schema validation, accessibility checks, and quality scoring.
"""

import re

from pydantic import BaseModel, Field

from copy_that.pipeline.exceptions import ValidationError
from copy_that.pipeline.interfaces import BasePipelineAgent
from copy_that.pipeline.types import PipelineTask, TokenResult, TokenType
from copy_that.pipeline.validation.accessibility import AccessibilityCalculator
from copy_that.pipeline.validation.quality import QualityReport, QualityScorer


class ValidationConfig(BaseModel):
    """Configuration for ValidationAgent."""

    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    strict_mode: bool = False
    check_accessibility: bool = True
    check_quality: bool = True
    background_color: str = "#FFFFFF"


class ValidatedToken(BaseModel):
    """Token with validation results."""

    token: TokenResult
    is_valid: bool = True
    validation_errors: list[str] = Field(default_factory=list)
    accessibility_score: float = 1.0
    quality_score: float = 1.0
    overall_score: float = 1.0


class ValidationAgent(BasePipelineAgent):
    """
    Pipeline agent for token validation.

    Validates token schemas, calculates accessibility scores,
    and generates quality metrics.
    """

    def __init__(self, config: ValidationConfig | None = None):
        """Initialize with optional configuration."""
        self.config = config or ValidationConfig()
        self.accessibility_calculator = AccessibilityCalculator()
        self.quality_scorer = QualityScorer()

    @property
    def agent_type(self) -> str:
        return "validation"

    @property
    def stage_name(self) -> str:
        return "validation"

    async def process(self, task: PipelineTask) -> list[TokenResult]:
        """
        Process pipeline task - validate tokens from context.

        Expects task.context['tokens'] to contain tokens to validate.
        Returns validated tokens (filtered if strict_mode).
        """
        # Get tokens from context
        if task.context is None:
            raise ValidationError(
                "No tokens found in task context",
                details={"task_id": task.task_id},
            )

        tokens = task.context.get("tokens", [])
        if not tokens:
            raise ValidationError(
                "No tokens to validate",
                details={"task_id": task.task_id},
            )

        # Validate all tokens
        validated_tokens = self.validate_tokens(tokens)

        # Filter based on configuration
        if self.config.strict_mode:
            # Filter out invalid tokens and those below min_confidence
            result_tokens = [
                vt.token
                for vt in validated_tokens
                if vt.is_valid and vt.token.confidence >= self.config.min_confidence
            ]

            if not result_tokens:
                raise ValidationError(
                    "All tokens failed validation in strict mode",
                    details={
                        "task_id": task.task_id,
                        "total_tokens": len(tokens),
                        "min_confidence": self.config.min_confidence,
                    },
                )
        else:
            # Return all tokens in lenient mode
            result_tokens = [vt.token for vt in validated_tokens]

        return result_tokens

    async def health_check(self) -> bool:
        """Check if validation agent is ready."""
        return True

    def validate_schema(self, token: TokenResult) -> list[str]:
        """
        Validate token against schema requirements.

        Checks:
        - Hex color format (if color type)
        - Positive dimensions (if spacing/size)
        - Valid confidence range
        - Required fields present

        Returns list of validation error messages.
        """
        errors = []

        # Check confidence bounds (already in model but double-check)
        if not 0 <= token.confidence <= 1:
            errors.append(f"Confidence {token.confidence} out of range [0, 1]")

        # Check hex color format for color tokens
        if (
            token.token_type == TokenType.COLOR
            and isinstance(token.value, str)
            and not self._is_valid_hex(token.value)
        ):
            errors.append(f"Invalid hex color format: {token.value}")

        # Check positive dimensions for spacing
        if (
            token.token_type == TokenType.SPACING
            and isinstance(token.value, (int | float))
            and token.value <= 0
        ):
            errors.append(f"Spacing value must be positive: {token.value}")

        # Check required name
        if not token.name or not token.name.strip():
            errors.append("Token name is required")

        return errors

    def validate_token(self, token: TokenResult) -> ValidatedToken:
        """
        Fully validate a single token.

        Runs schema validation, accessibility checks, and quality scoring.
        Returns ValidatedToken with all scores and errors.
        """
        # Schema validation
        validation_errors = self.validate_schema(token)

        # Accessibility score
        accessibility_score = 1.0
        if self.config.check_accessibility:
            try:
                accessibility_score = self.accessibility_calculator.calculate_accessibility_score(
                    token, self.config.background_color
                )
            except ValidationError:
                # If accessibility calculation fails, use default
                accessibility_score = 1.0

        # Quality score
        quality_score = 1.0
        if self.config.check_quality:
            quality_score = self.quality_scorer.calculate_quality_score(token)

        # Calculate overall score
        # overall = accessibility * 0.4 + quality * 0.4 + (1.0 if no errors else 0.5) * 0.2
        error_factor = 1.0 if not validation_errors else 0.5
        overall_score = accessibility_score * 0.4 + quality_score * 0.4 + error_factor * 0.2

        # Determine if token is valid
        is_valid = len(validation_errors) == 0

        return ValidatedToken(
            token=token,
            is_valid=is_valid,
            validation_errors=validation_errors,
            accessibility_score=accessibility_score,
            quality_score=quality_score,
            overall_score=overall_score,
        )

    def validate_tokens(self, tokens: list[TokenResult]) -> list[ValidatedToken]:
        """
        Validate a batch of tokens.

        Returns list of ValidatedToken results.
        """
        return [self.validate_token(token) for token in tokens]

    def get_quality_report(self, tokens: list[TokenResult]) -> QualityReport:
        """Get quality report for tokens."""
        return self.quality_scorer.generate_quality_report(tokens)

    def _is_valid_hex(self, value: str) -> bool:
        """
        Check if a string is a valid hex color.

        Matches #RGB, #RRGGBB, #RRGGBBAA formats.
        """
        return bool(re.match(r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$", value))
