import pytest

from copy_that.pipeline import TokenResult, TokenType
from copy_that.pipeline.validation.quality import QualityScorer


def _token(
    name: str,
    value: str,
    confidence: float = 0.8,
    path: list[str] | None = None,
    w3c_type: str | None = None,
    description: str | None = None,
) -> TokenResult:
    return TokenResult(
        token_type=TokenType.COLOR,
        name=name,
        value=value,
        confidence=confidence,
        path=path or [],
        w3c_type=w3c_type,
        description=description,
    )


def test_calculate_confidence_score_empty():
    scorer = QualityScorer()
    assert scorer.calculate_confidence_score([]) == 0.0


def test_check_completeness_with_bonus_fields():
    scorer = QualityScorer()
    token = _token(
        "color-primary", "#FF0000", path=["color"], w3c_type="color", description="primary"
    )
    score = scorer.check_completeness(token)
    assert score > 0.6
    assert score <= 1.0


@pytest.mark.parametrize(
    "name,expected",
    [
        ("color1", pytest.approx(0.6)),  # generic name penalty with path bonus
        ("primary-color", pytest.approx(0.9)),  # valid kebab + path
        ("invalid name", pytest.approx(0.2)),  # spaces
        ("1tone", pytest.approx(0.3)),  # starts with number
    ],
)
def test_check_naming_quality_various(name, expected):
    scorer = QualityScorer()
    token = _token(name, "#00FF00", path=["color", "brand"])
    assert scorer.check_naming_quality(token) == expected


def test_calculate_quality_score_combines_components(monkeypatch):
    scorer = QualityScorer()
    token = _token("primary", "#0000FF")

    # Ensure naming score high by mocking regex match
    score = scorer.calculate_quality_score(token)
    assert 0 <= score <= 1


def test_generate_quality_report_includes_issues_and_recommendations(monkeypatch):
    scorer = QualityScorer()
    tokens = [
        _token("color-1", "#000000", confidence=0.4),
        _token("color-2", "#FFFFFF", confidence=0.6),
    ]

    report = scorer.generate_quality_report(tokens)

    assert report.total_tokens == 2
    assert any("missing description" in issue.lower() for issue in report.issues)
    assert any(
        "low confidence" in recommendation.lower() for recommendation in report.recommendations
    )
