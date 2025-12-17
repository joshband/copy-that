from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.users import User as UserEntity
from copy_that.infrastructure.persistence.models import User as UserModel


def _parse_roles(raw: str | None) -> list[str]:
    if not raw:
        return ["user"]
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return [str(x) for x in data]
        except json.JSONDecodeError:
            return [raw]
    return ["user"]


def _encode_roles(roles: list[str]) -> str:
    return json.dumps(list(roles))


def _to_entity(model: UserModel) -> UserEntity:
    return UserEntity(
        id=model.id,
        email=model.email,
        hashed_password=model.hashed_password,
        full_name=model.full_name,
        roles=_parse_roles(model.roles),
        is_active=model.is_active,
        created_at=model.created_at,
    )


class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, *, user_id: str) -> UserEntity | None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        user = result.scalar_one_or_none()
        return _to_entity(user) if user else None

    async def get_by_email(self, *, email: str) -> UserEntity | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        user = result.scalar_one_or_none()
        return _to_entity(user) if user else None

    async def create(
        self,
        *,
        email: str,
        hashed_password: str,
        full_name: str | None,
        roles: list[str],
    ) -> UserEntity:
        user = UserModel(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            roles=_encode_roles(roles),
        )
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return _to_entity(user)

    async def set_last_login(self, *, user_id: str, last_login: datetime) -> None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return
        # Stored as naive timestamp in DB model (consistent with existing code paths)
        user.last_login = last_login.astimezone(UTC).replace(tzinfo=None)
        self._session.add(user)
        await self._session.commit()
