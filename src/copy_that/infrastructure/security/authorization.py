"""Resource authorization and ownership checks"""

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..database import get_db
from .authentication import get_current_user


async def get_owned_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get project and verify ownership"""
    from copy_that.domain.models import Project

    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check ownership
    if (project.owner_id and project.owner_id != current_user.id
            and "admin" not in (current_user.roles or [])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )

    return project


async def get_owned_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get session and verify ownership through project"""
    from copy_that.domain.models import ExtractionSession

    result = await db.execute(
        select(ExtractionSession)
        .where(ExtractionSession.id == session_id)
        .options(joinedload(ExtractionSession.project))
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Check ownership through project
    if (session.project and session.project.owner_id
            and session.project.owner_id != current_user.id
            and "admin" not in (current_user.roles or [])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )

    return session
