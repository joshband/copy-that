from cv_pipeline.control_classifier import ControlInstance, ControlType
from layout import metrics
from layout.layout_graph import PanelGraph


def _make_instance(x: int, y: int, w: int = 40, h: int = 40) -> ControlInstance:
    return ControlInstance(control_type=ControlType.BUTTON, bbox=(x, y, w, h), metadata={})


def test_metrics_regular_layout_has_higher_score() -> None:
    regular_graph = PanelGraph.from_instances([_make_instance(x * 60, 0) for x in range(4)])
    irregular_graph = PanelGraph.from_instances(
        [_make_instance(x * 60, (x % 2) * 30) for x in range(4)]
    )

    assert metrics.regularity_score(regular_graph) > metrics.regularity_score(irregular_graph)
    assert metrics.density(regular_graph) > 0
