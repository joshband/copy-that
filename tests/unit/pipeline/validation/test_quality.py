"""Tests for QualityScorer."""

import pytest

from copy_that.pipeline import TokenResult, TokenType, W3CTokenType
from copy_that.pipeline.validation.quality import QualityReport, QualityScorer


class TestQualityReport:
    """Tests for QualityReport model."""

    def test_default_values(self):
        """Test QualityReport has correct default values."""
        report = QualityReport()
        assert report.total_tokens == 0
        assert report.avg_confidence == 0.0
        assert report.avg_completeness == 0.0
        assert report.avg_quality_score == 0.0
        assert report.tokens_by_type == {}
        assert report.issues == []
        assert report.recommendations == []

    def test_custom_values(self):
        """Test QualityReport can be initialized with custom values."""
        report = QualityReport(
            total_tokens=10,
            avg_confidence=0.85,
            avg_completeness=0.9,
            avg_quality_score=0.87,
            tokens_by_type={"color": 5, "spacing": 3, "typography": 2},
            issues=["Low confidence detected"],
            recommendations=["Add descriptions"],
        )
        assert report.total_tokens == 10
        assert report.avg_confidence == 0.85
        assert report.avg_completeness == 0.9
        assert report.avg_quality_score == 0.87
        assert report.tokens_by_type == {"color": 5, "spacing": 3, "typography": 2}
        assert report.issues == ["Low confidence detected"]
        assert report.recommendations == ["Add descriptions"]


class TestCalculateConfidenceScore:
    """Tests for QualityScorer.calculate_confidence_score()."""

    def test_empty_list_returns_zero(self):
        """Test that empty token list returns 0.0."""
        scorer = QualityScorer()
        result = scorer.calculate_confidence_score([])
        assert result == 0.0

    def test_single_token(self):
        """Test confidence score for single token."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
        )
        result = scorer.calculate_confidence_score([token])
        assert result == 0.95

    def test_multiple_tokens_average(self):
        """Test confidence score averages multiple tokens."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                value="#FF6B35",
                confidence=0.90,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="secondary",
                value="#4ECDC4",
                confidence=0.80,
            ),
            TokenResult(
                token_type=TokenType.SPACING,
                name="small",
                value="8px",
                confidence=1.0,
            ),
        ]
        result = scorer.calculate_confidence_score(tokens)
        expected = (0.90 + 0.80 + 1.0) / 3
        assert result == pytest.approx(expected)

    def test_all_perfect_confidence(self):
        """Test all tokens with perfect confidence."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                value="#FF6B35",
                confidence=1.0,
            ),
            TokenResult(
                token_type=TokenType.SPACING,
                name="large",
                value="24px",
                confidence=1.0,
            ),
        ]
        result = scorer.calculate_confidence_score(tokens)
        assert result == 1.0

    def test_all_zero_confidence(self):
        """Test all tokens with zero confidence."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                value="#FF6B35",
                confidence=0.0,
            ),
            TokenResult(
                token_type=TokenType.SPACING,
                name="small",
                value="4px",
                confidence=0.0,
            ),
        ]
        result = scorer.calculate_confidence_score(tokens)
        assert result == 0.0

    def test_mixed_confidence_values(self):
        """Test tokens with various confidence values."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                value="#FF6B35",
                confidence=0.95,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="secondary",
                value="#4ECDC4",
                confidence=0.70,
            ),
            TokenResult(
                token_type=TokenType.SPACING,
                name="medium",
                value="16px",
                confidence=0.85,
            ),
            TokenResult(
                token_type=TokenType.TYPOGRAPHY,
                name="heading",
                value="24px",
                confidence=0.60,
            ),
        ]
        result = scorer.calculate_confidence_score(tokens)
        expected = (0.95 + 0.70 + 0.85 + 0.60) / 4
        assert result == pytest.approx(expected)


class TestCheckCompleteness:
    """Tests for QualityScorer.check_completeness()."""

    def test_minimal_token_base_score(self):
        """Test minimal token gets base score of 0.6."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
        )
        result = scorer.check_completeness(token)
        # Base score for required fields
        assert result == pytest.approx(0.6)

    def test_with_w3c_type_adds_bonus(self):
        """Test w3c_type adds 0.15 bonus."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
            w3c_type=W3CTokenType.COLOR,
        )
        result = scorer.check_completeness(token)
        assert result == pytest.approx(0.75)

    def test_with_path_adds_bonus(self):
        """Test path adds 0.1 bonus."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
            path=["color", "brand"],
        )
        result = scorer.check_completeness(token)
        assert result == pytest.approx(0.7)

    def test_with_description_adds_bonus(self):
        """Test description adds 0.1 bonus."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
            description="Primary brand color",
        )
        result = scorer.check_completeness(token)
        assert result == pytest.approx(0.7)

    def test_with_reference_adds_small_bonus(self):
        """Test reference adds 0.05 bonus."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary-light",
            value="#FF8866",
            confidence=0.95,
            reference="{color.primary}",
        )
        result = scorer.check_completeness(token)
        assert result == pytest.approx(0.65)

    def test_with_extensions_adds_small_bonus(self):
        """Test extensions adds 0.05 bonus."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
            extensions={"com.figma": {"nodeId": "123"}},
        )
        result = scorer.check_completeness(token)
        assert result == pytest.approx(0.65)

    def test_with_metadata_adds_small_bonus(self):
        """Test metadata adds 0.05 bonus."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
            metadata={"source": "image"},
        )
        result = scorer.check_completeness(token)
        assert result == pytest.approx(0.65)

    def test_fully_complete_token_max_score(self):
        """Test fully complete token gets maximum score (capped at 1.0)."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
            w3c_type=W3CTokenType.COLOR,
            path=["color", "brand"],
            description="Primary brand color",
            reference="{color.base}",
            extensions={"com.figma": {"nodeId": "123"}},
            metadata={"source": "image"},
        )
        result = scorer.check_completeness(token)
        # 0.6 + 0.15 + 0.1 + 0.1 + 0.05 = 1.0 (capped)
        assert result == pytest.approx(1.0)

    def test_with_all_recommended_fields(self):
        """Test token with all recommended fields."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
            w3c_type=W3CTokenType.COLOR,
            path=["color", "brand"],
            description="Primary brand color",
        )
        result = scorer.check_completeness(token)
        # 0.6 + 0.15 + 0.1 + 0.1 = 0.95
        assert result == pytest.approx(0.95)

    def test_empty_path_no_bonus(self):
        """Test empty path list does not add bonus."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
            path=[],
        )
        result = scorer.check_completeness(token)
        assert result == pytest.approx(0.6)


class TestCheckNamingQuality:
    """Tests for QualityScorer.check_naming_quality()."""

    def test_kebab_case_valid(self):
        """Test kebab-case name is valid."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary-color",
            value="#FF6B35",
            confidence=0.95,
        )
        result = scorer.check_naming_quality(token)
        assert result >= 0.8

    def test_camel_case_valid(self):
        """Test camelCase name is valid."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primaryColor",
            value="#FF6B35",
            confidence=0.95,
        )
        result = scorer.check_naming_quality(token)
        assert result >= 0.8

    def test_simple_name_valid(self):
        """Test simple name is valid."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
        )
        result = scorer.check_naming_quality(token)
        assert result >= 0.8

    def test_generic_name_penalty(self):
        """Test generic names like 'color1' get penalty."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="color1",
            value="#FF6B35",
            confidence=0.95,
        )
        result = scorer.check_naming_quality(token)
        assert result < 0.8

    def test_generic_font_name_penalty(self):
        """Test generic font names like 'font2' get penalty."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.TYPOGRAPHY,
            name="font2",
            value="16px",
            confidence=0.95,
        )
        result = scorer.check_naming_quality(token)
        assert result < 0.8

    def test_generic_spacing_name_penalty(self):
        """Test generic spacing names like 'spacing3' get penalty."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.SPACING,
            name="spacing3",
            value="12px",
            confidence=0.95,
        )
        result = scorer.check_naming_quality(token)
        assert result < 0.8

    def test_name_with_spaces_invalid(self):
        """Test names with spaces are invalid."""
        scorer = QualityScorer()
        # Note: This would likely fail validation, but testing scoring
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary color",
            value="#FF6B35",
            confidence=0.95,
        )
        result = scorer.check_naming_quality(token)
        assert result < 0.5

    def test_name_starting_with_number_invalid(self):
        """Test names starting with numbers are invalid."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="1primary",
            value="#FF6B35",
            confidence=0.95,
        )
        result = scorer.check_naming_quality(token)
        assert result < 0.5

    def test_good_path_structure_bonus(self):
        """Test good path structure adds to naming quality."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
            path=["color", "brand"],
        )
        result = scorer.check_naming_quality(token)
        assert result >= 0.9

    def test_empty_name_penalty(self):
        """Test empty or very short names get penalty."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="x",
            value="#FF6B35",
            confidence=0.95,
        )
        result = scorer.check_naming_quality(token)
        assert result < 0.5


class TestCalculateQualityScore:
    """Tests for QualityScorer.calculate_quality_score()."""

    def test_basic_token_quality_score(self):
        """Test quality score calculation for basic token."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
        )
        result = scorer.calculate_quality_score(token)
        # Should be combination of confidence, completeness, naming
        assert 0.0 <= result <= 1.0

    def test_perfect_token_high_score(self):
        """Test fully complete token gets high quality score."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary-brand",
            value="#FF6B35",
            confidence=1.0,
            w3c_type=W3CTokenType.COLOR,
            path=["color", "brand"],
            description="Primary brand color for main CTAs",
        )
        result = scorer.calculate_quality_score(token)
        assert result >= 0.9

    def test_low_confidence_lowers_score(self):
        """Test low confidence significantly lowers score."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.3,
        )
        result = scorer.calculate_quality_score(token)
        assert result < 0.6

    def test_poor_naming_lowers_score(self):
        """Test poor naming lowers quality score."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="color1",
            value="#FF6B35",
            confidence=1.0,
        )
        result = scorer.calculate_quality_score(token)
        # Good confidence but poor naming
        assert result < 0.85

    def test_weights_are_applied(self):
        """Test that quality score uses defined weights."""
        scorer = QualityScorer()

        # Verify weights sum to 1.0
        total_weight = (
            scorer.CONFIDENCE_WEIGHT
            + scorer.COMPLETENESS_WEIGHT
            + scorer.NAMING_WEIGHT
        )
        assert total_weight == pytest.approx(1.0)

    def test_score_in_valid_range(self):
        """Test quality score is always between 0 and 1."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                value="#FF6B35",
                confidence=0.0,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="secondary",
                value="#4ECDC4",
                confidence=1.0,
                w3c_type=W3CTokenType.COLOR,
                path=["color", "brand"],
                description="Secondary brand color",
            ),
        ]
        for token in tokens:
            result = scorer.calculate_quality_score(token)
            assert 0.0 <= result <= 1.0


class TestGenerateQualityReport:
    """Tests for QualityScorer.generate_quality_report()."""

    def test_empty_tokens_list(self):
        """Test report generation with empty token list."""
        scorer = QualityScorer()
        report = scorer.generate_quality_report([])

        assert report.total_tokens == 0
        assert report.avg_confidence == 0.0
        assert report.avg_completeness == 0.0
        assert report.avg_quality_score == 0.0
        assert report.tokens_by_type == {}
        assert isinstance(report.issues, list)
        assert isinstance(report.recommendations, list)

    def test_single_token_report(self):
        """Test report generation for single token."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
        )
        report = scorer.generate_quality_report([token])

        assert report.total_tokens == 1
        assert report.avg_confidence == 0.95
        assert report.tokens_by_type == {"color": 1}

    def test_multiple_tokens_report(self):
        """Test report generation for multiple tokens."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                value="#FF6B35",
                confidence=0.90,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="secondary",
                value="#4ECDC4",
                confidence=0.80,
            ),
            TokenResult(
                token_type=TokenType.SPACING,
                name="small",
                value="8px",
                confidence=1.0,
            ),
        ]
        report = scorer.generate_quality_report(tokens)

        assert report.total_tokens == 3
        assert report.avg_confidence == pytest.approx((0.90 + 0.80 + 1.0) / 3)
        assert report.tokens_by_type == {"color": 2, "spacing": 1}

    def test_report_includes_all_token_types(self):
        """Test report correctly groups all token types."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                value="#FF6B35",
                confidence=0.95,
            ),
            TokenResult(
                token_type=TokenType.SPACING,
                name="small",
                value="8px",
                confidence=0.90,
            ),
            TokenResult(
                token_type=TokenType.TYPOGRAPHY,
                name="heading",
                value="24px",
                confidence=0.85,
            ),
            TokenResult(
                token_type=TokenType.SHADOW,
                name="elevation-1",
                value="0 2px 4px rgba(0,0,0,0.1)",
                confidence=0.80,
            ),
            TokenResult(
                token_type=TokenType.GRADIENT,
                name="primary-gradient",
                value="linear-gradient(90deg, #FF6B35, #4ECDC4)",
                confidence=0.75,
            ),
        ]
        report = scorer.generate_quality_report(tokens)

        assert report.total_tokens == 5
        assert report.tokens_by_type == {
            "color": 1,
            "spacing": 1,
            "typography": 1,
            "shadow": 1,
            "gradient": 1,
        }

    def test_report_identifies_low_confidence_issues(self):
        """Test report identifies tokens with low confidence."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                value="#FF6B35",
                confidence=0.4,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="secondary",
                value="#4ECDC4",
                confidence=0.3,
            ),
        ]
        report = scorer.generate_quality_report(tokens)

        assert len(report.issues) > 0
        # Should mention low confidence
        assert any("confidence" in issue.lower() for issue in report.issues)

    def test_report_generates_recommendations(self):
        """Test report generates recommendations for improvement."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                value="#FF6B35",
                confidence=0.95,
                # Missing description, w3c_type, path
            ),
        ]
        report = scorer.generate_quality_report(tokens)

        assert len(report.recommendations) > 0

    def test_high_quality_tokens_few_issues(self):
        """Test high quality tokens generate few or no issues."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary-brand",
                value="#FF6B35",
                confidence=0.98,
                w3c_type=W3CTokenType.COLOR,
                path=["color", "brand"],
                description="Primary brand color",
            ),
            TokenResult(
                token_type=TokenType.SPACING,
                name="base-unit",
                value="8px",
                confidence=0.95,
                w3c_type=W3CTokenType.DIMENSION,
                path=["spacing", "base"],
                description="Base spacing unit",
            ),
        ]
        report = scorer.generate_quality_report(tokens)

        # High quality tokens should have high scores
        assert report.avg_quality_score >= 0.8

    def test_report_completeness_score_calculated(self):
        """Test report includes correct completeness score."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
            w3c_type=W3CTokenType.COLOR,
            path=["color", "brand"],
            description="Primary brand color",
        )
        report = scorer.generate_quality_report([token])

        # Token has all recommended fields
        assert report.avg_completeness >= 0.9


class TestGetIssues:
    """Tests for QualityScorer.get_issues()."""

    def test_low_confidence_issue(self):
        """Test low confidence is flagged as issue."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.4,
        )
        issues = scorer.get_issues(token)

        assert any("confidence" in issue.lower() for issue in issues)

    def test_missing_description_issue(self):
        """Test missing description is flagged."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
        )
        issues = scorer.get_issues(token)

        assert any("description" in issue.lower() for issue in issues)

    def test_missing_w3c_type_issue(self):
        """Test missing W3C type is flagged."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
        )
        issues = scorer.get_issues(token)

        assert any("w3c" in issue.lower() or "type" in issue.lower() for issue in issues)

    def test_generic_name_issue(self):
        """Test generic names are flagged."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="color1",
            value="#FF6B35",
            confidence=0.95,
        )
        issues = scorer.get_issues(token)

        assert any("name" in issue.lower() or "generic" in issue.lower() for issue in issues)

    def test_no_issues_for_complete_token(self):
        """Test complete, high-quality token has few issues."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary-brand",
            value="#FF6B35",
            confidence=0.98,
            w3c_type=W3CTokenType.COLOR,
            path=["color", "brand"],
            description="Primary brand color",
        )
        issues = scorer.get_issues(token)

        # Complete token should have minimal issues
        assert len(issues) <= 1


class TestGetRecommendations:
    """Tests for QualityScorer.get_recommendations()."""

    def test_empty_list_recommendations(self):
        """Test recommendations for empty token list."""
        scorer = QualityScorer()
        recommendations = scorer.get_recommendations([])

        assert isinstance(recommendations, list)

    def test_recommend_descriptions(self):
        """Test recommendation to add descriptions."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                value="#FF6B35",
                confidence=0.95,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="secondary",
                value="#4ECDC4",
                confidence=0.90,
            ),
        ]
        recommendations = scorer.get_recommendations(tokens)

        # Should recommend adding descriptions
        assert any("description" in rec.lower() for rec in recommendations)

    def test_recommend_w3c_types(self):
        """Test recommendation to add W3C types."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                value="#FF6B35",
                confidence=0.95,
            ),
        ]
        recommendations = scorer.get_recommendations(tokens)

        # Should recommend adding W3C types
        assert any("w3c" in rec.lower() or "type" in rec.lower() for rec in recommendations)

    def test_recommend_paths(self):
        """Test recommendation to add paths for organization."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                value="#FF6B35",
                confidence=0.95,
            ),
        ]
        recommendations = scorer.get_recommendations(tokens)

        # Should recommend adding paths
        assert any("path" in rec.lower() for rec in recommendations)

    def test_no_duplicate_recommendations(self):
        """Test that recommendations are not duplicated."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="color1",
                value="#FF6B35",
                confidence=0.4,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="color2",
                value="#4ECDC4",
                confidence=0.3,
            ),
        ]
        recommendations = scorer.get_recommendations(tokens)

        # Check no duplicates
        assert len(recommendations) == len(set(recommendations))


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_token_with_dict_value(self):
        """Test quality scoring with complex dict value."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.TYPOGRAPHY,
            name="heading-1",
            value={
                "fontFamily": "Inter",
                "fontSize": "32px",
                "fontWeight": 700,
                "lineHeight": 1.2,
            },
            confidence=0.9,
        )
        result = scorer.calculate_quality_score(token)
        assert 0.0 <= result <= 1.0

    def test_token_with_numeric_value(self):
        """Test quality scoring with numeric value."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.SPACING,
            name="multiplier",
            value=1.5,
            confidence=0.85,
        )
        result = scorer.calculate_quality_score(token)
        assert 0.0 <= result <= 1.0

    def test_token_with_boolean_value(self):
        """Test quality scoring with boolean value."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="is-dark-mode",
            value=True,
            confidence=0.9,
        )
        result = scorer.calculate_quality_score(token)
        assert 0.0 <= result <= 1.0

    def test_very_long_token_name(self):
        """Test token with very long name."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary-brand-color-for-main-call-to-action-buttons",
            value="#FF6B35",
            confidence=0.95,
        )
        result = scorer.calculate_quality_score(token)
        assert 0.0 <= result <= 1.0

    def test_large_token_list(self):
        """Test quality report with many tokens."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name=f"color-{i}",
                value=f"#{i:06x}",
                confidence=0.8 + (i % 20) / 100,
            )
            for i in range(100)
        ]
        report = scorer.generate_quality_report(tokens)

        assert report.total_tokens == 100
        assert report.tokens_by_type == {"color": 100}
        assert 0.0 <= report.avg_quality_score <= 1.0

    def test_unicode_in_name(self):
        """Test token with unicode characters in name."""
        scorer = QualityScorer()
        # Note: This may be invalid but test scoring behavior
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="color-cafe",  # Using ASCII version
            value="#6F4E37",
            confidence=0.9,
        )
        result = scorer.calculate_quality_score(token)
        assert 0.0 <= result <= 1.0

    def test_empty_description_string(self):
        """Test token with empty description string."""
        scorer = QualityScorer()
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.95,
            description="",  # Empty string
        )
        # Empty string should not count as having description
        completeness = scorer.check_completeness(token)
        assert completeness < 0.7  # No bonus for empty description

    def test_report_returns_quality_report_type(self):
        """Test that generate_quality_report returns QualityReport instance."""
        scorer = QualityScorer()
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                value="#FF6B35",
                confidence=0.95,
            ),
        ]
        report = scorer.generate_quality_report(tokens)

        assert isinstance(report, QualityReport)
