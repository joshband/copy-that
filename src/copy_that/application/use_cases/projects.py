from __future__ import annotations

from copy_that.application.ports.projects import ProjectRepository
from copy_that.domain.projects import Project


async def create_project(repo: ProjectRepository, *, name: str, description: str | None) -> Project:
    return await repo.create(name=name, description=description)


async def get_project(repo: ProjectRepository, *, project_id: int) -> Project | None:
    return await repo.get(project_id=project_id)


async def list_projects(repo: ProjectRepository, *, limit: int, offset: int) -> list[Project]:
    return await repo.list(limit=limit, offset=offset)


async def update_project(
    repo: ProjectRepository, *, project_id: int, name: str | None, description: str | None
) -> Project | None:
    return await repo.update(project_id=project_id, name=name, description=description)


async def delete_project(repo: ProjectRepository, *, project_id: int) -> bool:
    return await repo.delete(project_id=project_id)
