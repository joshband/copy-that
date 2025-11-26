from cv_pipeline.control_classifier import (
    ControlCandidate,
    ControlClassifier,
    ControlType,
)
from cv_pipeline.primitives import Circle, Rectangle


def test_classifies_circle_as_knob() -> None:
    classifier = ControlClassifier()
    candidate = ControlCandidate(primitive=Circle(center=(10, 10), radius=20), bbox=(0, 0, 40, 40))

    result = classifier.classify([candidate])[0]

    assert result.control_type == ControlType.KNOB
    assert result.metadata["radius"] == 20


def test_classifies_rectangle_as_button_or_fader() -> None:
    classifier = ControlClassifier()
    wide_candidate = ControlCandidate(
        primitive=Rectangle(x=0, y=0, width=100, height=20),
        bbox=(0, 0, 100, 20),
    )
    result = classifier.classify([wide_candidate])[0]
    assert result.control_type == ControlType.FADER
