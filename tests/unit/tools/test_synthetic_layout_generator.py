from copy_that.tools.synthetic_layout_generator import (
    evaluate_spacing_accuracy,
    generate_grid_layout,
    generate_stack,
)


def test_grid_layout_accuracy_hits_expected_gap():
    layout = generate_grid_layout(rows=2, cols=2, cell_size=10, gap=6)
    metrics = evaluate_spacing_accuracy(layout, tolerance=0)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["expected"] == [6]


def test_stack_layout_accuracy():
    layout = generate_stack(count=3, width=20, height=8, gap=5)
    metrics = evaluate_spacing_accuracy(layout, tolerance=0)
    assert metrics["detected"]
    assert 5 in metrics["detected"]
