import logging

import pytest

from copy_that.application.perf import track_perf


def test_track_perf_logs_without_enforce(caplog):
    caplog.set_level(logging.INFO)
    with track_perf("extract.color.ai", {"model": "test-model"}):
        pass

    records = [rec for rec in caplog.records if rec.message == "perf_timing"]
    assert records, "expected perf_timing log"
    payload = records[0].__dict__.get("perf") or {}
    assert payload.get("operation") == "extract.color.ai"
    assert "duration_ms" in payload
    assert payload.get("budget_ms") == 10_000


def test_track_perf_enforces_budget(monkeypatch):
    monkeypatch.setenv("PERF_BUDGET_ENFORCE", "true")
    import copy_that.application.perf as perf

    perf.BUDGETS_MS["extract.color.ai"] = 0  # force any work to exceed budget
    with pytest.raises(RuntimeError), track_perf("extract.color.ai"):
        pass


def test_track_perf_memory_budget(monkeypatch, caplog):
    monkeypatch.setenv("PERF_BUDGET_ENFORCE", "false")
    caplog.set_level(logging.INFO)
    with track_perf("extract.color.ai", measure_memory=True):
        pass

    records = [rec for rec in caplog.records if rec.message == "perf_timing"]
    payload = records[0].__dict__.get("perf") or {}
    assert "rss_mb" in payload
    assert "memory_budget_mb" in payload
