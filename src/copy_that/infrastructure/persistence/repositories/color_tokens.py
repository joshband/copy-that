from __future__ import annotations

import json
from collections.abc import Sequence

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.application.ports.color_tokens import ColorTokenWriter
from copy_that.core_tokens.model import Token
from copy_that.infrastructure.persistence.models import ColorToken


class SQLAlchemyColorTokenWriter(ColorTokenWriter):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def persist_aggregated_library(
        self,
        *,
        library_id: int,
        project_id: int,
        aggregated_tokens: Sequence[Token],
        statistics: dict[str, object],
    ) -> int:
        token_records: list[dict[str, object]] = []
        for token in aggregated_tokens:
            attrs = getattr(token, "attributes", {}) or {}
            record: dict[str, object] = {
                "project_id": project_id,
                "library_id": library_id,
                "hex": attrs.get("hex") or getattr(token, "hex", None) or token.value,
                "rgb": attrs.get("rgb") or getattr(token, "rgb", None),
                "name": attrs.get("name") or getattr(token, "name", None),
                "confidence": attrs.get("confidence") or getattr(token, "confidence", None),
                "harmony": attrs.get("harmony") or getattr(token, "harmony", None),
                "temperature": attrs.get("temperature") or getattr(token, "temperature", None),
                "role": attrs.get("role") or getattr(token, "role", None),
                "provenance": json.dumps(
                    attrs.get("provenance") or getattr(token, "provenance", None) or {}
                ),
            }
            token_records.append(record)

        batch_size = 100
        for i in range(0, len(token_records), batch_size):
            batch = token_records[i : i + batch_size]
            await self._session.execute(insert(ColorToken).values(batch))

        await self._session.commit()
        return len(token_records)
