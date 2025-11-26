from cv_pipeline.control_classifier import ControlInstance, ControlType
from layout.layout_graph import PanelGraph


def _make_instance(x: int, y: int, w: int = 50, h: int = 50) -> ControlInstance:
    return ControlInstance(control_type=ControlType.BUTTON, bbox=(x, y, w, h), metadata={})


def test_panel_graph_groups_rows_and_columns() -> None:
    instances = [
        _make_instance(0, 0),
        _make_instance(60, 5),
        _make_instance(0, 100),
    ]
    graph = PanelGraph.from_instances(instances)

    rows = graph.rows()
    columns = graph.columns()

    assert len(rows) == 2
    assert len(columns) >= 2
