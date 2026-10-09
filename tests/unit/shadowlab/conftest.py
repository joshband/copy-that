"""Keep shadowlab unit tests independent of downloaded model weights."""

import pytest


@pytest.fixture(autouse=True)
def isolate_pretrained_pipeline_loaders(monkeypatch):
    from copy_that.shadowlab import pipeline

    # These tests exercise classical fallback and stage contracts. A model test
    # can override the loader with its own fake after this fixture runs.
    for loader in ("_get_shadow_model", "_get_sam_model", "_get_midas_model"):
        monkeypatch.setattr(pipeline, loader, lambda *args, **kwargs: (None, None, None))
