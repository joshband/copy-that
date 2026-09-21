from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.snapshots import ProjectSnapshot as SnapshotEntity
from copy_that.infrastructure.persistence.models import ProjectSnapshot as SnapshotModel


def _to_entity(model: SnapshotModel) -> SnapshotEntity:
    return SnapshotEntity(
        id=model.id,
        project_id=model.project_id,
        version=model.version,
        data=model.data,
        created_at=model.created_at,
    )


class SQLAlchemySnapshotRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_project(self, *, project_id: int) -> list[SnapshotEntity]:
        result = await self._session.execute(
            select(SnapshotModel)
            .where(SnapshotModel.project_id == project_id)
            .order_by(SnapshotModel.created_at.desc())
        )
        return [_to_entity(s) for s in result.scalars().all()]

    async def get_for_project(self, *, project_id: int, snapshot_id: int) -> SnapshotEntity | None:
        snapshot = await self._session.scalar(
            select(SnapshotModel).where(
                SnapshotModel.id == snapshot_id, SnapshotModel.project_id == project_id
            )
        )
        return _to_entity(snapshot) if snapshot else None

    async def create(self, *, project_id: int, version: int, data: str) -> SnapshotEntity:
        snapshot = SnapshotModel(project_id=project_id, version=version, data=data)
        self._session.add(snapshot)
        await self._session.commit()
        await self._session.refresh(snapshot)
        return _to_entity(snapshot)
