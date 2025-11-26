import pytest

from copy_that.pipeline.preprocessing.validator import (
    FileSizeError,
    ImageValidator,
    InvalidImageError,
    SSRFError,
    ValidationError,
)


def _png_bytes() -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 10


@pytest.mark.parametrize("host", ["http://localhost/image.png", "http://127.0.0.1/image.png"])
def test_validate_url_loopback(host):
    validator = ImageValidator()
    with pytest.raises(SSRFError):
        validator.validate(host, _png_bytes())


def test_validate_url_invalid_scheme():
    validator = ImageValidator()
    with pytest.raises(ValidationError):
        validator.validate("ftp://example.com/image.png", _png_bytes())


def test_validate_magic_bytes_invalid():
    validator = ImageValidator()
    with pytest.raises(InvalidImageError):
        validator.validate("http://example.com/image.png", b"NOTIMAGE")


def test_validate_file_size_limit():
    validator = ImageValidator(max_file_size_mb=0)
    with pytest.raises(FileSizeError):
        validator.validate("http://example.com/image.png", _png_bytes())


def test_validate_success():
    validator = ImageValidator()
    result = validator.validate("https://example.com/image.png", _png_bytes())
    assert result["format"] == "png"
    assert result["size"] == len(_png_bytes())
