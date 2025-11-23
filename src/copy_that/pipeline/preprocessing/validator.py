"""Image validator with SSRF protection.

Security-critical component that validates URLs and image content.
"""

import socket
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Any
from urllib.parse import urlparse


class ValidationError(Exception):
    """Base validation error."""

    pass


class SSRFError(ValidationError):
    """Server-Side Request Forgery attempt detected."""

    pass


class InvalidImageError(ValidationError):
    """Invalid image format or content."""

    pass


class FileSizeError(ValidationError):
    """File exceeds size limit."""

    pass


# Magic bytes for supported image formats
MAGIC_BYTES = {
    "png": b"\x89PNG\r\n\x1a\n",
    "jpeg": [
        b"\xff\xd8\xff\xe0",
        b"\xff\xd8\xff\xe1",
        b"\xff\xd8\xff\xe2",
        b"\xff\xd8\xff\xdb",
        b"\xff\xd8\xff\xee",
    ],
    "gif": [b"GIF87a", b"GIF89a"],
    "webp": b"RIFF",  # Full check includes WEBP at offset 8
}


class ImageValidator:
    """Validates image URLs and content with SSRF protection."""

    def __init__(self, max_file_size_mb: int = 10) -> None:
        """Initialize validator.

        Args:
            max_file_size_mb: Maximum allowed file size in MB (default 10MB)
        """
        self.max_file_size = max_file_size_mb * 1024 * 1024  # Convert to bytes

    def validate(self, url: str, data: bytes) -> dict[str, Any]:
        """Validate URL and image data.

        Args:
            url: Image URL
            data: Image binary data

        Returns:
            Dict with format, size, and url

        Raises:
            SSRFError: If URL points to private/blocked IP
            InvalidImageError: If image format is invalid
            FileSizeError: If file exceeds size limit
        """
        self.validate_url(url)
        self.validate_file_size(data)
        image_format = self.validate_magic_bytes(data)

        return {
            "format": image_format,
            "size": len(data),
            "url": url,
        }

    def validate_url(self, url: str) -> None:
        """Validate URL for SSRF attacks.

        Args:
            url: URL to validate

        Raises:
            ValidationError: If URL is malformed or uses invalid scheme
            SSRFError: If URL points to private/blocked IP
        """
        if not url:
            raise ValidationError("URL cannot be empty")

        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValidationError(f"Malformed URL: {e}")

        # Validate scheme
        if parsed.scheme.lower() not in ("http", "https"):
            raise ValidationError(
                f"Invalid URL scheme: {parsed.scheme}. Only http and https are allowed"
            )

        # Check for credentials in URL
        if parsed.username or parsed.password:
            raise ValidationError("URLs with embedded credentials are not allowed")

        # Get hostname
        hostname = parsed.hostname
        if not hostname:
            raise ValidationError("URL must have a hostname")

        # Check for localhost
        if hostname.lower() in ("localhost", "localhost.localdomain"):
            raise SSRFError("Loopback address blocked: localhost")

        # Try to parse as IP address directly
        try:
            ip = ip_address(hostname)
            self._validate_ip(ip)
            return
        except ValueError:
            # Not an IP address, try to resolve hostname
            pass

        # For domain names, we'll validate when resolved
        # The actual resolution and IP check happens during download
        # For now, just ensure hostname is valid

    def _validate_ip(self, ip: IPv4Address | IPv6Address) -> None:
        """Validate that IP address is not private/blocked.

        Args:
            ip: IP address to validate

        Raises:
            SSRFError: If IP is private, loopback, or otherwise blocked
        """
        ip_str = str(ip)

        # Check for special addresses
        if ip.is_loopback:
            raise SSRFError(f"Loopback address blocked: {ip_str}")

        if ip.is_private:
            raise SSRFError(f"Private IP address blocked: {ip_str}")

        if ip.is_reserved:
            raise SSRFError(f"Reserved IP address blocked: {ip_str}")

        if ip.is_link_local:
            raise SSRFError(f"Link-local address blocked: {ip_str}")

        if ip.is_multicast:
            raise SSRFError(f"Multicast address blocked: {ip_str}")

        # Block cloud metadata endpoints (169.254.169.254)
        if isinstance(ip, IPv4Address):
            if ip_str == "169.254.169.254":
                raise SSRFError(f"Cloud metadata endpoint blocked: {ip_str}")

            # Block 0.0.0.0
            if ip_str == "0.0.0.0" or ip_str == "0":
                raise SSRFError(f"Invalid IP address blocked: {ip_str}")

    def is_private_ip(self, ip_str: str) -> bool:
        """Check if IP address is private.

        Args:
            ip_str: IP address string

        Returns:
            True if IP is private, False otherwise
        """
        try:
            ip = ip_address(ip_str)
            return (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip_str == "169.254.169.254"
            )
        except ValueError:
            return False

    def validate_magic_bytes(self, data: bytes) -> str:
        """Validate image magic bytes.

        Args:
            data: Image binary data

        Returns:
            Detected image format (png, jpeg, webp, gif)

        Raises:
            InvalidImageError: If magic bytes don't match supported formats
        """
        if not data:
            raise InvalidImageError("Empty image data")

        if len(data) < 8:
            raise InvalidImageError("Image data too short to contain valid magic bytes")

        # Check PNG
        if data[:8] == MAGIC_BYTES["png"]:
            return "png"

        # Check JPEG (multiple variants)
        for jpeg_magic in MAGIC_BYTES["jpeg"]:
            if data[:4] == jpeg_magic[:4] and data[:3] == b"\xff\xd8\xff":
                return "jpeg"

        # Check WebP (RIFF....WEBP)
        if data[:4] == MAGIC_BYTES["webp"] and len(data) >= 12 and data[8:12] == b"WEBP":
            return "webp"

        # Check GIF
        for gif_magic in MAGIC_BYTES["gif"]:
            if data[:6] == gif_magic:
                return "gif"

        raise InvalidImageError(
            "Unsupported or invalid image format. Supported: PNG, JPEG, WebP, GIF"
        )

    def validate_file_size(self, data: bytes) -> None:
        """Validate file size is within limit.

        Args:
            data: Image binary data

        Raises:
            FileSizeError: If file exceeds size limit
        """
        if len(data) > self.max_file_size:
            max_mb = self.max_file_size / (1024 * 1024)
            actual_mb = len(data) / (1024 * 1024)
            raise FileSizeError(f"File size {actual_mb:.2f}MB exceeds maximum {max_mb:.0f}MB")

    def validate_file_size_value(self, size_bytes: int) -> None:
        """Validate file size value without actual data.

        Args:
            size_bytes: File size in bytes

        Raises:
            FileSizeError: If size exceeds limit
        """
        if size_bytes > self.max_file_size:
            max_mb = self.max_file_size / (1024 * 1024)
            actual_mb = size_bytes / (1024 * 1024)
            raise FileSizeError(f"File size {actual_mb:.2f}MB exceeds maximum {max_mb:.0f}MB")

    async def resolve_and_validate_hostname(self, hostname: str) -> str:
        """Resolve hostname and validate resulting IP.

        Args:
            hostname: Hostname to resolve

        Returns:
            Resolved IP address string

        Raises:
            SSRFError: If resolved IP is private/blocked
            ValidationError: If hostname cannot be resolved
        """
        try:
            # Get all IP addresses for the hostname
            results = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)

            if not results:
                raise ValidationError(f"Could not resolve hostname: {hostname}")

            # Validate all resolved IPs
            for result in results:
                ip_str = result[4][0]
                ip = ip_address(ip_str)
                self._validate_ip(ip)

            # Return the first resolved IP
            return results[0][4][0]

        except socket.gaierror as e:
            raise ValidationError(f"Could not resolve hostname: {hostname} - {e}")
