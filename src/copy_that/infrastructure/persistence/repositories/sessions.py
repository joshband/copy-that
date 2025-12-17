from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.sessions import ExtractionSession as SessionEntity
from copy_that.infrastructure.persistence.models import ExtractionSession as SessionModel


def _to_entity(model: SessionModel) -> SessionEntity:
    return SessionEntity(
        id=model.id,
        project_id=model.project_id,
        name=model.name,
        description=model.description,
        image_count=model.image_count,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SQLAlchemySessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, *, session_id: int) -> SessionEntity | None:
        result = await self._session.execute(
            select(SessionModel).where(SessionModel.id == session_id)
        )
        session = result.scalar_one_or_none()
        return _to_entity(session) if session else None

    async def create(self, *, project_id: int, name: str, description: str | None) -> SessionEntity:
        session = SessionModel(project_id=project_id, name=name, description=description)
        self._session.add(session)
        await self._session.commit()
        await self._session.refresh(session)
        return _to_entity(session)

    async def set_image_count(self, *, session_id: int, image_count: int) -> SessionEntity | None:
        result = await self._session.execute(
            select(SessionModel).where(SessionModel.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            return None
        session.image_count = image_count
        self._session.add(session)
        await self._session.commit()
        await self._session.refresh(session)
        return _to_entity(session)
