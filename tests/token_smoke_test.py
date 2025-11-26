"""Smoke test for color extraction pipeline imports."""


def test_color_pipeline_import() -> None:
    # Import a lightweight module from the preprocessing pipeline to ensure dependencies load.
    from copy_that.pipeline.preprocessing import agent  # noqa: F401

    assert agent is not None
