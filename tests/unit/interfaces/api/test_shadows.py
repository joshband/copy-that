import base64

import cv2
import numpy as np
import pytest
from sqlalchemy import select

from copy_that.infrastructure.persistence.models import ShadowToken


@pytest.mark.asyncio
async def test_extract_shadows_persists_and_classifies(async_client, test_db):
    # Create a simple image with a centered dark rectangle to trigger CV shadow detection.
    image = np.ones((50, 50, 3), dtype=np.uint8) * 255
    cv2.rectangle(image, (10, 10), (40, 40), (0, 0, 0), thickness=-1)
    success, buf = cv2.imencode(".png", image)
    assert success
    image_b64 = base64.b64encode(buf.tobytes()).decode("utf-8")

    response = await async_client.post(
        "/api/v1/shadows/extract",
        json={
            "image_base64": image_b64,
            "image_media_type": "image/png",
            "project_id": 1,
            "max_tokens": 5,
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["tokens"], "Expected at least one shadow token"
    first = data["tokens"][0]
    assert first["semantic_role"] == "drop"
    assert first["name"].startswith("shadow-")

    # Verify persistence occurred in the test DB
    result = await test_db.execute(select(ShadowToken))
    saved = result.scalars().all()
    assert len(saved) >= 1
