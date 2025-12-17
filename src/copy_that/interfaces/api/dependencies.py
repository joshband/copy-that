"""FastAPI dependency declarations (interfaces layer).

These are intentionally *unwired* placeholders: the concrete wiring (SQLAlchemy
repos, external clients) is provided by the application factory via
`app.dependency_overrides`.

This keeps router modules importing only application ports, while the runtime
composition is centralized in one place.
"""

from __future__ import annotations

from copy_that.application.ports.color_token_library import ColorTokenLibraryRepository
from copy_that.application.ports.color_token_records import ColorTokenRepository
from copy_that.application.ports.color_tokens import ColorTokenWriter
from copy_that.application.ports.metrics import MetricsService
from copy_that.application.ports.projects import ProjectRepository
from copy_that.application.ports.security import PasswordHasher, TokenCodec
from copy_that.application.ports.sessions import SessionRepository
from copy_that.application.ports.shadow_tokens import ShadowTokenRepository
from copy_that.application.ports.snapshots import SnapshotRepository
from copy_that.application.ports.spacing_tokens import SpacingTokenRepository
from copy_that.application.ports.token_exports import TokenExportRepository
from copy_that.application.ports.token_libraries import TokenLibraryRepository
from copy_that.application.ports.typography_tokens import TypographyTokenRepository
from copy_that.application.ports.users import UserRepository


def _unwired(name: str) -> RuntimeError:
    return RuntimeError(
        f"Dependency '{name}' is not wired. Ensure the FastAPI app is created via "
        "'copy_that.interfaces.api.app_factory.create_app()'."
    )


def get_project_repo() -> ProjectRepository:  # pragma: no cover
    raise _unwired("get_project_repo")


def get_snapshot_repo() -> SnapshotRepository:  # pragma: no cover
    raise _unwired("get_snapshot_repo")


def get_user_repo() -> UserRepository:  # pragma: no cover
    raise _unwired("get_user_repo")


def get_session_repo() -> SessionRepository:  # pragma: no cover
    raise _unwired("get_session_repo")


def get_password_hasher() -> PasswordHasher:  # pragma: no cover
    raise _unwired("get_password_hasher")


def get_token_codec() -> TokenCodec:  # pragma: no cover
    raise _unwired("get_token_codec")


def get_metrics_service() -> MetricsService:  # pragma: no cover
    raise _unwired("get_metrics_service")


def get_color_token_repo() -> ColorTokenRepository:  # pragma: no cover
    raise _unwired("get_color_token_repo")


def get_color_token_writer() -> ColorTokenWriter:  # pragma: no cover
    raise _unwired("get_color_token_writer")


def get_color_token_library_repo() -> ColorTokenLibraryRepository:  # pragma: no cover
    raise _unwired("get_color_token_library_repo")


def get_token_library_repo() -> TokenLibraryRepository:  # pragma: no cover
    raise _unwired("get_token_library_repo")


def get_token_export_repo() -> TokenExportRepository:  # pragma: no cover
    raise _unwired("get_token_export_repo")


def get_shadow_repo() -> ShadowTokenRepository:  # pragma: no cover
    raise _unwired("get_shadow_repo")


def get_spacing_repo() -> SpacingTokenRepository:  # pragma: no cover
    raise _unwired("get_spacing_repo")


def get_typography_repo() -> TypographyTokenRepository:  # pragma: no cover
    raise _unwired("get_typography_repo")
