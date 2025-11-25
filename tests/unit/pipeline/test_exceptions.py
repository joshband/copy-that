from copy_that.pipeline.exceptions import (
    AggregationError,
    ExtractionError,
    GenerationError,
    PipelineError,
    PreprocessingError,
    ValidationError,
)


class DummyError(Exception):
    pass


def test_pipeline_error_str_and_repr():
    err = PipelineError("base failure")
    assert str(err) == "base failure"
    assert repr(err) == "PipelineError('base failure')"

    err_with_details = PipelineError("more detail", details={"stage": "test"})
    assert str(err_with_details) == "more detail"
    assert "details" in repr(err_with_details)


def test_specialized_exceptions_inherit_pipeline_error():
    for exc_cls in (
        PreprocessingError,
        ExtractionError,
        AggregationError,
        ValidationError,
        GenerationError,
    ):
        err = exc_cls("failed step", details={"retry": False})
        assert isinstance(err, PipelineError)
        assert "retry" in repr(err)


def test_generation_error_wrapper():
    try:
        raise DummyError("downstream")
    except DummyError as exc:
        gen_err = GenerationError("generation failed", details={"cause": str(exc)})
        assert gen_err.details["cause"] == "downstream"
