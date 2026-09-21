from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.application.ports.color_token_library import ColorTokenLibraryRepository
from copy_that.application.ports.color_token_records import ColorTokenRepository
from copy_that.application.ports.color_tokens import ColorTokenWriter
from copy_that.application.ports.jobs import JobExecutor, JobRepository
from copy_that.application.ports.metrics import MetricsService
from copy_that.application.ports.projects import ProjectRepository
from copy_that.application.ports.security import PasswordHasher, TokenCodec
from copy_that.application.ports.sessions import SessionRepository
from copy_that.application.ports.shadow_tokens import ShadowTokenRepository
from copy_that.application.ports.snapshots import SnapshotRepository
from copy_that.application.ports.layout_tokens import LayoutTokenRepository
from copy_that.application.ports.spacing_tokens import SpacingTokenRepository
from copy_that.application.ports.token_exports import TokenExportRepository
from copy_that.application.ports.token_libraries import TokenLibraryRepository
from copy_that.application.ports.typography_tokens import TypographyTokenRepository
from copy_that.application.ports.users import UserRepository
from copy_that.infrastructure.celery.app import app as celery_app
from copy_that.infrastructure.execution.celery_executor import CeleryJobExecutor
from copy_that.infrastructure.metrics.service import SQLAlchemyMetricsService
from copy_that.infrastructure.persistence.repositories.color_token_library import (
    SQLAlchemyColorTokenLibraryRepository,
)
from copy_that.infrastructure.persistence.repositories.color_token_records import (
    SQLAlchemyColorTokenRepository,
)
from copy_that.infrastructure.persistence.repositories.color_tokens import (
    SQLAlchemyColorTokenWriter,
)
from copy_that.infrastructure.persistence.repositories.jobs import SQLAlchemyJobRepository
from copy_that.infrastructure.persistence.repositories.layout_tokens import (
    SQLAlchemyLayoutTokenRepository,
)
from copy_that.infrastructure.persistence.repositories.projects import SQLAlchemyProjectRepository
from copy_that.infrastructure.persistence.repositories.sessions import SQLAlchemySessionRepository
from copy_that.infrastructure.persistence.repositories.shadow_tokens import (
    SQLAlchemyShadowTokenRepository,
)
from copy_that.infrastructure.persistence.repositories.snapshots import SQLAlchemySnapshotRepository
from copy_that.infrastructure.persistence.repositories.spacing_tokens import (
    SQLAlchemySpacingTokenRepository,
)
from copy_that.infrastructure.persistence.repositories.token_exports import (
    SQLAlchemyTokenExportRepository,
)
from copy_that.infrastructure.persistence.repositories.token_libraries import (
    SQLAlchemyTokenLibraryRepository,
)
from copy_that.infrastructure.persistence.repositories.typography_tokens import (
    SQLAlchemyTypographyTokenRepository,
)
from copy_that.infrastructure.persistence.repositories.users import SQLAlchemyUserRepository
from copy_that.infrastructure.security.services import JoseTokenCodec, PasslibPasswordHasher


@dataclass(frozen=True, slots=True)
class Container:
    """Application composition root.

    This object is the single allowed place to bind application ports to concrete
    infrastructure implementations.
    """

    def project_repo(self, db: AsyncSession) -> ProjectRepository:
        return SQLAlchemyProjectRepository(db)

    def job_repo(self, db: AsyncSession) -> JobRepository:
        return SQLAlchemyJobRepository(db)

    def snapshot_repo(self, db: AsyncSession) -> SnapshotRepository:
        return SQLAlchemySnapshotRepository(db)

    def user_repo(self, db: AsyncSession) -> UserRepository:
        return SQLAlchemyUserRepository(db)

    def session_repo(self, db: AsyncSession) -> SessionRepository:
        return SQLAlchemySessionRepository(db)

    def password_hasher(self) -> PasswordHasher:
        return PasslibPasswordHasher()

    def token_codec(self) -> TokenCodec:
        return JoseTokenCodec()

    def job_executor(self) -> JobExecutor:
        return CeleryJobExecutor(celery_app)

    def metrics_service(self, db: AsyncSession) -> MetricsService:
        return SQLAlchemyMetricsService(db)

    def color_token_repo(self, db: AsyncSession) -> ColorTokenRepository:
        return SQLAlchemyColorTokenRepository(db)

    def color_token_writer(self, db: AsyncSession) -> ColorTokenWriter:
        return SQLAlchemyColorTokenWriter(db)

    def color_token_library_repo(self, db: AsyncSession) -> ColorTokenLibraryRepository:
        return SQLAlchemyColorTokenLibraryRepository(db)

    def token_library_repo(self, db: AsyncSession) -> TokenLibraryRepository:
        return SQLAlchemyTokenLibraryRepository(db)

    def token_export_repo(self, db: AsyncSession) -> TokenExportRepository:
        return SQLAlchemyTokenExportRepository(db)

    def shadow_repo(self, db: AsyncSession) -> ShadowTokenRepository:
        return SQLAlchemyShadowTokenRepository(db)

    def spacing_repo(self, db: AsyncSession) -> SpacingTokenRepository:
        return SQLAlchemySpacingTokenRepository(db)

    def layout_repo(self, db: AsyncSession) -> LayoutTokenRepository:
        return SQLAlchemyLayoutTokenRepository(db)

    def typography_repo(self, db: AsyncSession) -> TypographyTokenRepository:
        return SQLAlchemyTypographyTokenRepository(db)


def project_repo(db: AsyncSession) -> ProjectRepository:
    return SQLAlchemyProjectRepository(db)


def job_repo(db: AsyncSession) -> JobRepository:
    return SQLAlchemyJobRepository(db)


def snapshot_repo(db: AsyncSession) -> SnapshotRepository:
    return SQLAlchemySnapshotRepository(db)


def user_repo(db: AsyncSession) -> UserRepository:
    return SQLAlchemyUserRepository(db)


def session_repo(db: AsyncSession) -> SessionRepository:
    return SQLAlchemySessionRepository(db)


def password_hasher() -> PasswordHasher:
    return PasslibPasswordHasher()


def token_codec() -> TokenCodec:
    return JoseTokenCodec()


def job_executor() -> JobExecutor:
    return CeleryJobExecutor(celery_app)


def metrics_service(db: AsyncSession) -> MetricsService:
    return SQLAlchemyMetricsService(db)


def color_token_repo(db: AsyncSession) -> ColorTokenRepository:
    return SQLAlchemyColorTokenRepository(db)


def color_token_writer(db: AsyncSession) -> ColorTokenWriter:
    return SQLAlchemyColorTokenWriter(db)


def color_token_library_repo(db: AsyncSession) -> ColorTokenLibraryRepository:
    return SQLAlchemyColorTokenLibraryRepository(db)


def token_library_repo(db: AsyncSession) -> TokenLibraryRepository:
    return SQLAlchemyTokenLibraryRepository(db)


def token_export_repo(db: AsyncSession) -> TokenExportRepository:
    return SQLAlchemyTokenExportRepository(db)


def shadow_repo(db: AsyncSession) -> ShadowTokenRepository:
    return SQLAlchemyShadowTokenRepository(db)


def spacing_repo(db: AsyncSession) -> SpacingTokenRepository:
    return SQLAlchemySpacingTokenRepository(db)


def layout_repo(db: AsyncSession) -> LayoutTokenRepository:
    return SQLAlchemyLayoutTokenRepository(db)


def typography_repo(db: AsyncSession) -> TypographyTokenRepository:
    return SQLAlchemyTypographyTokenRepository(db)
