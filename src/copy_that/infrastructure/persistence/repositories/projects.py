from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.projects import Project as ProjectEntity
from copy_that.domain.time import utc_now
from copy_that.infrastructure.persistence.models import Project as ProjectModel


def _to_entity(model: ProjectModel) -> ProjectEntity:
    return ProjectEntity(
        id=model.id,
        name=model.name,
        description=model.description,
        owner_id=model.owner_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SQLAlchemyProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, name: str, description: str | None) -> ProjectEntity:
        project = ProjectModel(name=name, description=description)
        self._session.add(project)
        await self._session.commit()
        await self._session.refresh(project)
        return _to_entity(project)

    async def get(self, *, project_id: int) -> ProjectEntity | None:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        project = result.scalar_one_or_none()
        return _to_entity(project) if project else None

    async def list(self, *, limit: int, offset: int) -> list[ProjectEntity]:
        result = await self._session.execute(
            select(ProjectModel)
            .order_by(ProjectModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [_to_entity(p) for p in result.scalars().all()]

    async def count(self) -> int:
        result = await self._session.execute(select(func.count(ProjectModel.id)))
        count = result.scalar_one()
        return int(count or 0)

    async def update(
        self, *, project_id: int, name: str | None, description: str | None
    ) -> ProjectEntity | None:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        project = result.scalar_one_or_none()
        if not project:
            return None

        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        project.updated_at = utc_now()

        self._session.add(project)
        await self._session.commit()
        await self._session.refresh(project)
        return _to_entity(project)

    async def delete(self, *, project_id: int) -> bool:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        project = result.scalar_one_or_none()
        if not project:
            return False

        await self._session.delete(project)
        await self._session.commit()
        return True
