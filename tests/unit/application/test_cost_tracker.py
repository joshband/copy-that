from copy_that.application.cost_tracker import CostTracker, InMemoryCostBackend


def test_cost_tracker_blocks_on_hard_limit():
    tracker = CostTracker(InMemoryCostBackend())
    tracker.hard_limit = 1.0
    state = tracker.record(project_id=1, amount=0.6)
    assert state.warned is True
    assert state.blocked is False

    state = tracker.record(project_id=1, amount=0.5)
    assert state.blocked is True


def test_cost_tracker_resets_by_day(monkeypatch):
    backend = InMemoryCostBackend()
    tracker = CostTracker(backend)
    tracker.record(project_id=1, amount=0.5)
    today_key = backend.get("cost:project:1")["window"]
    # Force window to previous day
    backend.set("cost:project:1", {"window": "1999-01-01", "total": 5.0})
    state = tracker.get(project_id=1)
    assert state.total == 0.0
    assert state.window == tracker._load(1)["window"]
    assert state.window != "1999-01-01"
