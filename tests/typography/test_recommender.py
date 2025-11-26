import pytest

from core.tokens.model import Token
from core.tokens.repository import InMemoryTokenRepository
from cv_pipeline.control_classifier import ControlInstance, ControlType
from layout.layout_graph import PanelGraph
from typography.recommender import recommend_typography


def _graph(rows: int = 2, cols: int = 3) -> PanelGraph:
    instances = []
    spacing = 60
    for row in range(rows):
        for col in range(cols):
            instances.append(
                ControlInstance(
                    control_type=ControlType.BUTTON,
                    bbox=(col * spacing, row * spacing, 40, 40),
                    metadata={},
                )
            )
    return PanelGraph.from_instances(instances)


def test_recommend_typography_populates_repository() -> None:
    repo = InMemoryTokenRepository()
    repo.upsert_token(
        Token(
            id="token/color/text/primary",
            type="color",
            value={"l": 0.5, "c": 0.05, "h": 120, "alpha": 1, "space": "oklch"},
        )
    )
    repo.upsert_token(
        Token(
            id="token/color/text/muted",
            type="color",
            value={"l": 0.6, "c": 0.02, "h": 120, "alpha": 1, "space": "oklch"},
        )
    )

    descriptors = recommend_typography(
        _graph(),
        repo,
        color_tokens={
            "primary": "token/color/text/primary",
            "muted": "token/color/text/muted",
        },
    )

    typography_tokens = {token.id: token for token in repo.find_by_type("typography")}

    assert set(typography_tokens) == {
        "token/typography/headline",
        "token/typography/controlLabel",
        "token/typography/panelCaption",
    }
    assert typography_tokens["token/typography/headline"].value["color"] == (
        "token/color/text/primary"
    )
    assert (
        typography_tokens["token/typography/panelCaption"].value["color"]
        == "token/color/text/muted"
    )
    assert descriptors["headline"].classification in {
        "geometric-sans",
        "humanist-sans",
        "technical-grotesk",
    }


def test_recommend_typography_requires_color_tokens() -> None:
    repo = InMemoryTokenRepository()

    with pytest.raises(ValueError):
        recommend_typography(_graph(), repo, color_tokens={})
