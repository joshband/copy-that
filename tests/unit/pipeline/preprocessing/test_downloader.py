import httpx
import pytest

from copy_that.pipeline.preprocessing.downloader import (
    DownloadError,
    DownloadResult,
    ImageDownloader,
    TimeoutError,
)


class _FakeResponse:
    def __init__(
        self, *, status_code, content=b"", headers=None, url="http://example.com/image.png"
    ):
        self.status_code = status_code
        self.content = content
        self.headers = headers or {}
        self.url = url
        self.text = content.decode(errors="ignore")


class _FakeClient:
    def __init__(self, responses):
        self._responses = responses

    async def get(self, url):
        if not self._responses:
            return _FakeResponse(
                status_code=500, content=b"", headers={"content-type": "image/png"}
            )
        resp = self._responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp

    async def aclose(self):
        pass


@pytest.mark.asyncio
async def test_download_success(monkeypatch):
    downloader = ImageDownloader(timeout=1, max_retries=1)
    response = _FakeResponse(
        status_code=200,
        content=b"\x89PNG\r\n\x1a\nsomecontent",
        headers={"content-type": "image/png", "content-length": "10"},
    )

    async def fake_get_client():
        return _FakeClient([response])

    monkeypatch.setattr(downloader, "_get_client", fake_get_client)

    result = await downloader.download("http://example.com/image.png")
    assert isinstance(result, DownloadResult)
    assert result.content == response.content
    assert result.content_type == "image/png"
    assert result.content_length == 10


@pytest.mark.asyncio
async def test_invalid_content_type_raises(monkeypatch):
    downloader = ImageDownloader(timeout=1)
    response = _FakeResponse(
        status_code=200,
        content=b"data",
        headers={"content-type": "text/plain", "content-length": "4"},
    )

    async def fake_client():
        return _FakeClient([response])

    monkeypatch.setattr(downloader, "_get_client", fake_client)

    with pytest.raises(DownloadError, match="Invalid content-type"):
        await downloader.download("http://example.com/not-image")


@pytest.mark.asyncio
async def test_server_error_retries_and_fails(monkeypatch):
    downloader = ImageDownloader(timeout=1, max_retries=1, backoff_factor=0.1)
    responses = [
        _FakeResponse(status_code=500, content=b"", headers={"content-type": "image/png"}),
        _FakeResponse(status_code=500, content=b"", headers={"content-type": "image/png"}),
    ]

    async def fake_client():
        return _FakeClient(responses.copy())

    monkeypatch.setattr(downloader, "_get_client", fake_client)

    with pytest.raises(DownloadError, match="Server error"):
        await downloader.download("http://example.com/server-error")


@pytest.mark.asyncio
async def test_timeout_exception_raises(monkeypatch):
    downloader = ImageDownloader(timeout=1)

    class _TimeoutClient:
        async def get(self, url):
            raise httpx.TimeoutException("timeout")

        async def aclose(self):
            pass

    async def fake_get_client():
        return _TimeoutClient()

    monkeypatch.setattr(downloader, "_get_client", fake_get_client)

    with pytest.raises(TimeoutError):
        await downloader.download("http://example.com/timeout")
