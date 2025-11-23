"""Tests for ImageValidator with SSRF protection.

TESTS FIRST: These tests define the security requirements before implementation.
"""

import pytest

from copy_that.pipeline.preprocessing.validator import (
    FileSizeError,
    ImageValidator,
    InvalidImageError,
    SSRFError,
    ValidationError,
)


class TestSSRFProtection:
    """Test SSRF protection - blocking private IPs and metadata endpoints."""

    @pytest.fixture
    def validator(self) -> ImageValidator:
        return ImageValidator()

    # Private IP ranges - 10.0.0.0/8
    @pytest.mark.parametrize(
        "url",
        [
            "http://10.0.0.1/image.png",
            "http://10.255.255.255/image.png",
            "http://10.0.0.0/image.png",
            "http://10.1.2.3:8080/image.png",
            "https://10.10.10.10/path/to/image.jpg",
        ],
    )
    def test_blocks_10_x_private_ips(self, validator: ImageValidator, url: str) -> None:
        """Should block all 10.x.x.x private IPs."""
        with pytest.raises(SSRFError) as exc_info:
            validator.validate_url(url)
        assert "private" in str(exc_info.value).lower() or "blocked" in str(exc_info.value).lower()

    # Private IP ranges - 172.16.0.0/12
    @pytest.mark.parametrize(
        "url",
        [
            "http://172.16.0.1/image.png",
            "http://172.31.255.255/image.png",
            "http://172.20.0.1/image.png",
            "https://172.16.0.0:443/image.jpg",
        ],
    )
    def test_blocks_172_16_x_private_ips(self, validator: ImageValidator, url: str) -> None:
        """Should block all 172.16.x.x - 172.31.x.x private IPs."""
        with pytest.raises(SSRFError) as exc_info:
            validator.validate_url(url)
        assert "private" in str(exc_info.value).lower() or "blocked" in str(exc_info.value).lower()

    # Private IP ranges - 192.168.0.0/16
    @pytest.mark.parametrize(
        "url",
        [
            "http://192.168.0.1/image.png",
            "http://192.168.1.1/image.png",
            "http://192.168.255.255/image.png",
            "https://192.168.0.0/image.jpg",
        ],
    )
    def test_blocks_192_168_x_private_ips(self, validator: ImageValidator, url: str) -> None:
        """Should block all 192.168.x.x private IPs."""
        with pytest.raises(SSRFError) as exc_info:
            validator.validate_url(url)
        assert "private" in str(exc_info.value).lower() or "blocked" in str(exc_info.value).lower()

    # Loopback addresses - 127.0.0.0/8
    @pytest.mark.parametrize(
        "url",
        [
            "http://127.0.0.1/image.png",
            "http://127.0.0.1:8080/image.png",
            "http://127.1.2.3/image.png",
            "http://127.255.255.255/image.png",
            "https://localhost/image.jpg",
            "http://localhost:3000/image.png",
        ],
    )
    def test_blocks_loopback_addresses(self, validator: ImageValidator, url: str) -> None:
        """Should block all loopback addresses (127.x.x.x and localhost)."""
        with pytest.raises(SSRFError) as exc_info:
            validator.validate_url(url)
        assert "loopback" in str(exc_info.value).lower() or "blocked" in str(exc_info.value).lower()

    # Cloud metadata endpoints
    @pytest.mark.parametrize(
        "url",
        [
            "http://169.254.169.254/",
            "http://169.254.169.254/latest/meta-data/",
            "http://169.254.169.254/metadata/instance",
            "http://169.254.169.254/computeMetadata/v1/",
            "http://169.254.169.254:80/image.png",
        ],
    )
    def test_blocks_cloud_metadata_endpoints(self, validator: ImageValidator, url: str) -> None:
        """Should block cloud metadata endpoints (AWS, GCP, Azure)."""
        with pytest.raises(SSRFError) as exc_info:
            validator.validate_url(url)
        assert "metadata" in str(exc_info.value).lower() or "blocked" in str(exc_info.value).lower()

    # Link-local addresses
    @pytest.mark.parametrize(
        "url",
        [
            "http://169.254.0.1/image.png",
            "http://169.254.255.255/image.png",
        ],
    )
    def test_blocks_link_local_addresses(self, validator: ImageValidator, url: str) -> None:
        """Should block link-local addresses (169.254.x.x)."""
        with pytest.raises(SSRFError) as exc_info:
            validator.validate_url(url)
        assert "blocked" in str(exc_info.value).lower()

    # Valid public URLs should pass
    @pytest.mark.parametrize(
        "url",
        [
            "https://example.com/image.png",
            "https://cdn.example.com/images/photo.jpg",
            "http://8.8.8.8/image.png",
            "https://images.unsplash.com/photo.jpg",
        ],
    )
    def test_allows_public_urls(self, validator: ImageValidator, url: str) -> None:
        """Should allow valid public URLs."""
        # Should not raise
        validator.validate_url(url)

    # URL scheme validation
    @pytest.mark.parametrize(
        "url",
        [
            "file:///etc/passwd",
            "ftp://example.com/image.png",
            "gopher://example.com/image.png",
            "data:image/png;base64,abc",
        ],
    )
    def test_blocks_non_http_schemes(self, validator: ImageValidator, url: str) -> None:
        """Should only allow http and https schemes."""
        with pytest.raises(ValidationError):
            validator.validate_url(url)

    # DNS rebinding protection
    def test_blocks_special_hostnames(self, validator: ImageValidator) -> None:
        """Should block special hostnames that could resolve to private IPs."""
        dangerous_urls = [
            "http://0.0.0.0/image.png",
            "http://0/image.png",
        ]
        for url in dangerous_urls:
            with pytest.raises(SSRFError):
                validator.validate_url(url)

    # IPv6 private addresses
    @pytest.mark.parametrize(
        "url",
        [
            "http://[::1]/image.png",
            "http://[fe80::1]/image.png",
            "http://[fc00::1]/image.png",
            "http://[fd00::1]/image.png",
        ],
    )
    def test_blocks_ipv6_private_addresses(self, validator: ImageValidator, url: str) -> None:
        """Should block IPv6 private and loopback addresses."""
        with pytest.raises(SSRFError):
            validator.validate_url(url)

    def test_blocks_url_with_credentials(self, validator: ImageValidator) -> None:
        """Should block URLs with embedded credentials."""
        with pytest.raises(ValidationError):
            validator.validate_url("http://user:pass@example.com/image.png")


class TestMagicByteValidation:
    """Test image format validation using magic bytes."""

    @pytest.fixture
    def validator(self) -> ImageValidator:
        return ImageValidator()

    # Valid magic bytes
    def test_validates_png_magic_bytes(self, validator: ImageValidator) -> None:
        """Should accept valid PNG magic bytes."""
        png_magic = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        assert validator.validate_magic_bytes(png_magic) == "png"

    def test_validates_jpeg_magic_bytes(self, validator: ImageValidator) -> None:
        """Should accept valid JPEG magic bytes (FFD8FF)."""
        jpeg_magic = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        assert validator.validate_magic_bytes(jpeg_magic) == "jpeg"

    def test_validates_jpeg_exif_magic_bytes(self, validator: ImageValidator) -> None:
        """Should accept JPEG with EXIF marker."""
        jpeg_exif = b"\xff\xd8\xff\xe1" + b"\x00" * 100
        assert validator.validate_magic_bytes(jpeg_exif) == "jpeg"

    def test_validates_webp_magic_bytes(self, validator: ImageValidator) -> None:
        """Should accept valid WebP magic bytes (RIFF....WEBP)."""
        webp_magic = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 100
        assert validator.validate_magic_bytes(webp_magic) == "webp"

    def test_validates_gif_magic_bytes(self, validator: ImageValidator) -> None:
        """Should accept valid GIF magic bytes (GIF87a or GIF89a)."""
        gif87_magic = b"GIF87a" + b"\x00" * 100
        gif89_magic = b"GIF89a" + b"\x00" * 100
        assert validator.validate_magic_bytes(gif87_magic) == "gif"
        assert validator.validate_magic_bytes(gif89_magic) == "gif"

    # Invalid magic bytes
    @pytest.mark.parametrize(
        "data",
        [
            b"\x00\x00\x00\x00",  # Null bytes
            b"PK\x03\x04",  # ZIP file
            b"%PDF-1.4",  # PDF file
            b"BM",  # BMP file (not supported)
            b"\x1f\x8b\x08",  # GZIP
            b"<!DOCTYPE html>",  # HTML
            b"<?xml version",  # XML
        ],
    )
    def test_rejects_invalid_magic_bytes(self, validator: ImageValidator, data: bytes) -> None:
        """Should reject files with invalid/unsupported magic bytes."""
        with pytest.raises(InvalidImageError) as exc_info:
            validator.validate_magic_bytes(data)
        assert (
            "unsupported" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()
        )

    def test_rejects_empty_data(self, validator: ImageValidator) -> None:
        """Should reject empty data."""
        with pytest.raises(InvalidImageError):
            validator.validate_magic_bytes(b"")

    def test_rejects_too_short_data(self, validator: ImageValidator) -> None:
        """Should reject data too short to contain magic bytes."""
        with pytest.raises(InvalidImageError):
            validator.validate_magic_bytes(b"\x89PN")  # Incomplete PNG header


class TestFileSizeValidation:
    """Test file size limit enforcement."""

    @pytest.fixture
    def validator(self) -> ImageValidator:
        return ImageValidator()

    def test_accepts_file_under_limit(self, validator: ImageValidator) -> None:
        """Should accept files under 10MB."""
        small_data = b"\x00" * (5 * 1024 * 1024)  # 5MB
        validator.validate_file_size(small_data)  # Should not raise

    def test_accepts_file_at_limit(self, validator: ImageValidator) -> None:
        """Should accept files exactly at 10MB."""
        max_data = b"\x00" * (10 * 1024 * 1024)  # 10MB
        validator.validate_file_size(max_data)  # Should not raise

    def test_rejects_file_over_limit(self, validator: ImageValidator) -> None:
        """Should reject files over 10MB."""
        large_data = b"\x00" * (10 * 1024 * 1024 + 1)  # 10MB + 1 byte
        with pytest.raises(FileSizeError) as exc_info:
            validator.validate_file_size(large_data)
        assert "10" in str(exc_info.value) or "size" in str(exc_info.value).lower()

    def test_rejects_very_large_file(self, validator: ImageValidator) -> None:
        """Should reject very large files."""
        # Test with size check, not actual data (to avoid memory issues)
        with pytest.raises(FileSizeError):
            validator.validate_file_size_value(100 * 1024 * 1024)  # 100MB

    def test_custom_size_limit(self) -> None:
        """Should support custom size limits."""
        validator = ImageValidator(max_file_size_mb=5)
        large_data = b"\x00" * (6 * 1024 * 1024)  # 6MB
        with pytest.raises(FileSizeError):
            validator.validate_file_size(large_data)


class TestFullValidation:
    """Test complete validation pipeline."""

    @pytest.fixture
    def validator(self) -> ImageValidator:
        return ImageValidator()

    def test_validate_all_passes_valid_image(self, validator: ImageValidator) -> None:
        """Should pass a valid image through all validations."""
        url = "https://example.com/image.png"
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        result = validator.validate(url, png_data)
        assert result["format"] == "png"
        assert result["size"] == len(png_data)
        assert result["url"] == url

    def test_validate_all_fails_on_ssrf(self, validator: ImageValidator) -> None:
        """Should fail if URL is blocked."""
        url = "http://192.168.1.1/image.png"
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with pytest.raises(SSRFError):
            validator.validate(url, png_data)

    def test_validate_all_fails_on_invalid_magic_bytes(self, validator: ImageValidator) -> None:
        """Should fail if magic bytes are invalid."""
        url = "https://example.com/image.png"
        invalid_data = b"not an image"

        with pytest.raises(InvalidImageError):
            validator.validate(url, invalid_data)

    def test_validate_all_fails_on_size_limit(self, validator: ImageValidator) -> None:
        """Should fail if file is too large."""
        url = "https://example.com/image.png"
        png_header = b"\x89PNG\r\n\x1a\n"
        large_data = png_header + b"\x00" * (11 * 1024 * 1024)  # 11MB

        with pytest.raises(FileSizeError):
            validator.validate(url, large_data)


class TestIPAddressResolution:
    """Test DNS resolution and IP validation."""

    @pytest.fixture
    def validator(self) -> ImageValidator:
        return ImageValidator()

    @pytest.mark.asyncio
    async def test_resolves_hostname_and_validates_ip(self, validator: ImageValidator) -> None:
        """Should resolve hostname and validate the resulting IP."""
        # This would require mocking DNS resolution in implementation
        pass  # Implementation will handle async resolution

    def test_is_private_ip_helper(self, validator: ImageValidator) -> None:
        """Test the is_private_ip helper method."""
        # Private IPs
        assert validator.is_private_ip("10.0.0.1") is True
        assert validator.is_private_ip("172.16.0.1") is True
        assert validator.is_private_ip("192.168.1.1") is True
        assert validator.is_private_ip("127.0.0.1") is True
        assert validator.is_private_ip("169.254.169.254") is True

        # Public IPs
        assert validator.is_private_ip("8.8.8.8") is False
        assert validator.is_private_ip("1.1.1.1") is False
        assert validator.is_private_ip("93.184.216.34") is False  # example.com


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def validator(self) -> ImageValidator:
        return ImageValidator()

    def test_handles_url_with_port(self, validator: ImageValidator) -> None:
        """Should correctly parse and validate URLs with ports."""
        validator.validate_url("https://example.com:443/image.png")
        with pytest.raises(SSRFError):
            validator.validate_url("http://127.0.0.1:8080/image.png")

    def test_handles_url_with_query_params(self, validator: ImageValidator) -> None:
        """Should correctly parse URLs with query parameters."""
        validator.validate_url("https://example.com/image.png?width=100&height=100")

    def test_handles_url_with_fragments(self, validator: ImageValidator) -> None:
        """Should correctly parse URLs with fragments."""
        validator.validate_url("https://example.com/image.png#section")

    def test_handles_url_encoding(self, validator: ImageValidator) -> None:
        """Should handle URL-encoded characters."""
        validator.validate_url("https://example.com/path%20with%20spaces/image.png")

    def test_rejects_malformed_url(self, validator: ImageValidator) -> None:
        """Should reject malformed URLs."""
        with pytest.raises(ValidationError):
            validator.validate_url("not-a-valid-url")

    def test_rejects_empty_url(self, validator: ImageValidator) -> None:
        """Should reject empty URLs."""
        with pytest.raises(ValidationError):
            validator.validate_url("")

    def test_handles_case_insensitive_scheme(self, validator: ImageValidator) -> None:
        """Should handle case-insensitive schemes."""
        validator.validate_url("HTTPS://example.com/image.png")
        validator.validate_url("Http://example.com/image.png")
