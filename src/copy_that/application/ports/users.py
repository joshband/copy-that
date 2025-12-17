from __future__ import annotations

from datetime import datetime
from typing import Protocol

from copy_that.domain.users import User


class UserRepository(Protocol):
    async def get_by_id(self, *, user_id: str) -> User | None: ...

    async def get_by_email(self, *, email: str) -> User | None: ...

    async def create(
        self,
        *,
        email: str,
        hashed_password: str,
        full_name: str | None,
        roles: list[str],
    ) -> User: ...

    async def set_last_login(self, *, user_id: str, last_login: datetime) -> None: ...
