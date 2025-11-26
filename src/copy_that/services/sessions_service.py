"""Session service helpers to encapsulate DB access for extraction sessions."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.models import ExtractionSession, TokenLibrary


async def get_session(db: AsyncSession, session_id: int) -> ExtractionSession | None:
    result = await db.execute(select(ExtractionSession).where(ExtractionSession.id == session_id))
    return result.scalar_one_or_none()


async def create_session(
    db: AsyncSession, project_id: int, name: str, description: str | None = None
) -> ExtractionSession:
    session = ExtractionSession(project_id=project_id, name=name, description=description)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_or_create_library(
    db: AsyncSession, session_id: int, token_type: str, statistics: dict[str, Any] | None = None
) -> TokenLibrary:
    result = await db.execute(
        select(TokenLibrary)
        .where(TokenLibrary.session_id == session_id)
        .where(TokenLibrary.token_type == token_type)
    )
    library = result.scalar_one_or_none()
    if library:
        if statistics is not None:
            library.statistics = json.dumps(statistics)
            await db.commit()
        return library

    library = TokenLibrary(
        session_id=session_id,
        token_type=token_type,
        statistics=json.dumps(statistics) if statistics is not None else None,
    )
    db.add(library)
    await db.commit()
    await db.refresh(library)
    return library
