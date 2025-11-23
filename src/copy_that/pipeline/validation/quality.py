"""
Quality scoring for design tokens.

Provides confidence aggregation and completeness validation.
"""

import re

from pydantic import BaseModel, Field

from copy_that.pipeline.types import TokenResult, TokenType


class QualityReport(BaseModel):
    """Report of quality analysis for tokens."""

    total_tokens: int = 0
    avg_confidence: float = 0.0
    avg_completeness: float = 0.0
    avg_quality_score: float = 0.0
    tokens_by_type: dict[str, int] = Field(default_factory=dict)
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class QualityScorer:
    """
    Score quality of extracted tokens.

    Evaluates confidence, completeness, and generates reports.
    """

    # Weights for quality score components
    CONFIDENCE_WEIGHT = 0.5
    COMPLETENESS_WEIGHT = 0.3
    NAMING_WEIGHT = 0.2

    # Generic name patterns to penalize
    GENERIC_NAME_PATTERN = re.compile(r"^(color|font|spacing|shadow|gradient)\d+$", re.IGNORECASE)

    # Valid identifier patterns
    KEBAB_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
    CAMEL_CASE_PATTERN = re.compile(r"^[a-z][a-zA-Z0-9]*$")

    # Invalid patterns
    STARTS_WITH_NUMBER = re.compile(r"^\d")
    HAS_SPACES = re.compile(r"\s")

    def calculate_confidence_score(self, tokens: list[TokenResult]) -> float:
        """
        Calculate aggregate confidence score for a list of tokens.

        Returns weighted average based on token importance.
        Returns 0.0 for empty list.
        """
        if not tokens:
            return 0.0

        total_confidence = sum(token.confidence for token in tokens)
        return total_confidence / len(tokens)

    def check_completeness(self, token: TokenResult) -> float:
        """
        Check completeness of a token (0-1 score).

        Evaluates presence of:
        - Required: name, value, token_type, confidence (base score)
        - Recommended: w3c_type, path, description (+bonus)
        - Optional: reference, extensions, metadata (+small bonus)
        """
        # Base score for required fields (always present in valid TokenResult)
        score = 0.6

        # Recommended fields bonus
        if token.w3c_type:
            score += 0.15
        if token.path and len(token.path) > 0:
            score += 0.1
        if token.description and len(token.description) > 0:
            score += 0.1

        # Optional fields small bonus (only one bonus even if multiple present)
        if token.reference or token.extensions or token.metadata:
            score += 0.05

        # Cap at 1.0
        return min(score, 1.0)

    def check_naming_quality(self, token: TokenResult) -> float:
        """
        Check quality of token naming (0-1 score).

        Evaluates:
        - Valid identifier format (kebab-case or camelCase)
        - Meaningful name (not generic like 'color1')
        - Appropriate path structure
        """
        name = token.name
        score = 0.0

        # Check for invalid patterns first
        if self.HAS_SPACES.search(name):
            return 0.2
        if self.STARTS_WITH_NUMBER.match(name):
            return 0.3
        if len(name) <= 1:
            return 0.3

        # Base score for valid format
        is_kebab = self.KEBAB_CASE_PATTERN.match(name)
        is_camel = self.CAMEL_CASE_PATTERN.match(name)

        if is_kebab or is_camel:
            score = 0.8
        else:
            # Partial score for other valid identifiers
            score = 0.5

        # Penalize generic names
        if self.GENERIC_NAME_PATTERN.match(name):
            score = 0.5

        # Bonus for good path structure
        if token.path and len(token.path) >= 2:
            score += 0.1

        # Cap at 1.0
        return min(score, 1.0)

    def calculate_quality_score(self, token: TokenResult) -> float:
        """
        Calculate overall quality score for a single token (0-1).

        Combines confidence, completeness, and naming quality.
        """
        confidence_score = token.confidence
        completeness_score = self.check_completeness(token)
        naming_score = self.check_naming_quality(token)

        quality_score = (
            confidence_score * self.CONFIDENCE_WEIGHT
            + completeness_score * self.COMPLETENESS_WEIGHT
            + naming_score * self.NAMING_WEIGHT
        )

        return min(quality_score, 1.0)

    def generate_quality_report(self, tokens: list[TokenResult]) -> QualityReport:
        """
        Generate a comprehensive quality report for tokens.

        Includes:
        - Aggregate scores
        - Token breakdown by type
        - Issues found
        - Recommendations for improvement
        """
        if not tokens:
            return QualityReport(
                issues=["No tokens to analyze"],
                recommendations=["Extract tokens from design files to begin analysis"],
            )

        # Calculate aggregate scores
        avg_confidence = self.calculate_confidence_score(tokens)
        completeness_scores = [self.check_completeness(token) for token in tokens]
        avg_completeness = sum(completeness_scores) / len(tokens)
        quality_scores = [self.calculate_quality_score(token) for token in tokens]
        avg_quality_score = sum(quality_scores) / len(tokens)

        # Group by type
        tokens_by_type: dict[str, int] = {}
        for token in tokens:
            token_type_value = (
                token.token_type.value
                if isinstance(token.token_type, TokenType)
                else token.token_type
            )
            tokens_by_type[token_type_value] = tokens_by_type.get(token_type_value, 0) + 1

        # Collect all issues
        all_issues: list[str] = []
        for token in tokens:
            issues = self.get_issues(token)
            all_issues.extend(issues)

        # Deduplicate and summarize issues
        issue_counts: dict[str, int] = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        summarized_issues = []
        for issue, count in issue_counts.items():
            if count > 1:
                summarized_issues.append(f"{issue} ({count} tokens)")
            else:
                summarized_issues.append(issue)

        # Get recommendations
        recommendations = self.get_recommendations(tokens)

        return QualityReport(
            total_tokens=len(tokens),
            avg_confidence=avg_confidence,
            avg_completeness=avg_completeness,
            avg_quality_score=avg_quality_score,
            tokens_by_type=tokens_by_type,
            issues=summarized_issues,
            recommendations=recommendations,
        )

    def get_issues(self, token: TokenResult) -> list[str]:
        """Get list of quality issues for a token."""
        issues = []

        # Check confidence
        if token.confidence < 0.5:
            issues.append("Low confidence score")

        # Check for missing recommended fields
        if not token.description:
            issues.append("Missing description")

        if not token.w3c_type:
            issues.append("Missing W3C type specification")

        # Check for poor naming
        if self.GENERIC_NAME_PATTERN.match(token.name):
            issues.append("Generic name pattern detected")

        if self.STARTS_WITH_NUMBER.match(token.name):
            issues.append("Name starts with number")

        if self.HAS_SPACES.search(token.name):
            issues.append("Name contains spaces")

        if len(token.name) <= 1:
            issues.append("Name too short")

        return issues

    def get_recommendations(self, tokens: list[TokenResult]) -> list[str]:
        """Get recommendations for improving token quality."""
        if not tokens:
            return ["Extract tokens from design files to begin"]

        recommendations = []

        # Count issues across all tokens
        missing_descriptions = sum(1 for t in tokens if not t.description)
        missing_w3c_types = sum(1 for t in tokens if not t.w3c_type)
        missing_paths = sum(1 for t in tokens if not t.path or len(t.path) == 0)
        low_confidence = sum(1 for t in tokens if t.confidence < 0.7)
        generic_names = sum(1 for t in tokens if self.GENERIC_NAME_PATTERN.match(t.name))

        total = len(tokens)

        # Generate recommendations based on common issues
        if missing_descriptions > total * 0.5:
            recommendations.append(
                f"Add descriptions to tokens ({missing_descriptions}/{total} missing)"
            )

        if missing_w3c_types > total * 0.5:
            recommendations.append(
                f"Add W3C type specifications ({missing_w3c_types}/{total} missing)"
            )

        if missing_paths > total * 0.5:
            recommendations.append(
                f"Add path hierarchies for better organization ({missing_paths}/{total} missing)"
            )

        if low_confidence > total * 0.3:
            recommendations.append(
                f"Review tokens with low confidence scores ({low_confidence}/{total} below 0.7)"
            )

        if generic_names > 0:
            recommendations.append(
                f"Replace generic names with meaningful identifiers ({generic_names} found)"
            )

        # Add general recommendations if few specific ones
        if not recommendations:
            if missing_descriptions > 0:
                recommendations.append("Consider adding descriptions for documentation")
            if missing_w3c_types > 0:
                recommendations.append("Consider adding W3C types for better interoperability")
            if missing_paths > 0:
                recommendations.append("Consider adding paths for token organization")

        return recommendations
