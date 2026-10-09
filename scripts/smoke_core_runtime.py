"""Exercise the core-only API without credentials, env files, network, or deep models.

Run with a fresh environment installed by `uv sync --frozen --no-dev`.
"""

from __future__ import annotations

import asyncio
import base64
import importlib.metadata
import io
import os
from unittest.mock import patch

OPTIONAL_DISTRIBUTIONS = (
    "transformers",
    "diffusers",
    "accelerate",
    "torch",
    "torchvision",
    "ultralytics",
    "layoutparser",
    "google-cloud-storage",
    "google-cloud-vision",
    "google-cloud-aiplatform",
    "google-cloud-secret-manager",
    "google-cloud-run",
    "google-cloud-billing",
)


async def smoke() -> None:
    for distribution in OPTIONAL_DISTRIBUTIONS:
        try:
            importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            continue
        raise AssertionError(f"Core-only smoke requires {distribution} to be absent")

    # Force hermetic runtime configuration before any application import.
    for key in list(os.environ):
        if key.startswith(("ANTHROPIC_", "OPENAI_", "FAL_", "MOOD_BOARD_", "LM_STUDIO_")):
            os.environ.pop(key)
    os.environ.update(
        ENVIRONMENT="local",
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        SECRET_KEY="hermetic-core-smoke-secret",
        ENABLE_GPU="false",
        RATE_LIMIT_ENABLED="false",
        ENABLE_SHADOWLAB="true",
    )
    with (
        patch("dotenv.load_dotenv", return_value=False),
        patch("decouple.RepositoryEnv", side_effect=AssertionError("Env files forbidden")),
        patch("socket.socket.connect", side_effect=AssertionError("Network forbidden")),
    ):
        from httpx import ASGITransport, AsyncClient
        from PIL import Image

        from copy_that.infrastructure.database import engine
        from copy_that.interfaces.api import shadows
        from copy_that.interfaces.api.app_factory import create_app

        image = io.BytesIO()
        Image.new("RGB", (32, 32), "white").save(image, format="PNG")
        encoded = base64.b64encode(image.getvalue()).decode("ascii")
        engine.echo = False
        app = create_app()
        async with (
            app.router.lifespan_context(app),
            AsyncClient(transport=ASGITransport(app=app), base_url="http://smoke") as client,
        ):
            health = await client.get("/health")
            assert health.status_code == 200, health.text
            assert health.json()["status"] == "healthy"
            with patch.object(
                shadows, "AIShadowExtractor", side_effect=RuntimeError("AI disabled for smoke")
            ):
                response = await client.post(
                    "/api/v1/shadows/extract",
                    json={"image_base64": encoded, "include_artifacts": True},
                )
            assert response.status_code == 200, response.text
            body = response.json()
            metadata = body["extraction_metadata"]
            assert metadata["cv_extractor_used"] == "cv_classical_empty", body
            assert metadata["shadowlab"]["pipeline"]["mode"] == "classical_upload", body
            assert body["artifacts"]["images"], body
            geometry = await client.post(
                "/api/v1/geometry/extract",
                json={"image_base64": encoded},
            )
            assert geometry.status_code == 503, geometry.text
            assert "cv-deep" in geometry.json()["detail"]
        await engine.dispose()
    print("Core smoke passed: startup, health, classical upload artifacts, optional geometry 503")


if __name__ == "__main__":
    asyncio.run(smoke())
