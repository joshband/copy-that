"""Project service helpers to encapsulate DB access for projects."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.models import Project


async def get_project(db: AsyncSession, project_id: int) -> Project | None:
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()


async def create_project(db: AsyncSession, name: str, description: str | None = None) -> Project:
    project = Project(name=name, description=description)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project
