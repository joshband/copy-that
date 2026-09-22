"""
FastAPI application factory.

This is the runtime composition boundary for the HTTP interface: it wires the
composition container onto `app.state` and configures routers/middleware.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from copy_that.application.execution.async_executor import AsyncExecutor
from copy_that.application.ports.projects import ProjectRepository
from copy_that.composition.container import Container
from copy_that.infrastructure.config import config
from copy_that.infrastructure.database import Base, engine, get_db
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.auth import router as auth_router
from copy_that.interfaces.api.batch import router as batch_router
from copy_that.interfaces.api.colors import router as colors_router
from copy_that.interfaces.api.design_tokens import router as design_tokens_router
from copy_that.interfaces.api.geometry import router as geometry_router
from copy_that.interfaces.api.gradients import router as gradients_router
from copy_that.interfaces.api.jobs import router as jobs_router
from copy_that.interfaces.api.lighting import router as lighting_router
from copy_that.interfaces.api.metrics import router as metrics_router
from copy_that.interfaces.api.middleware.security_headers import SecurityHeadersMiddleware
from copy_that.interfaces.api.mood_board import router as mood_board_router
from copy_that.interfaces.api.multi_extract import router as multi_extract_router
from copy_that.interfaces.api.projects import router as projects_router
from copy_that.interfaces.api.sessions import router as sessions_router
from copy_that.interfaces.api.shadows import router as shadows_router
from copy_that.interfaces.api.snapshots import router as snapshots_router
from copy_that.interfaces.api.spacing import router as spacing_router
from copy_that.interfaces.api.typography import router as typography_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    if os.getenv("ENVIRONMENT") in ("local", "development", None):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    # Fail fast on missing critical configuration
    config.validate_required()

    app = FastAPI(
        title="Copy That API",
        description="Multi-Modal Token Platform - Transform images, video, and audio into universal design tokens",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    container = Container()
    app.state.container = container

    def _project_repo(db=Depends(get_db)):
        return container.project_repo(db)

    def _job_repo(db=Depends(get_db)):
        return container.job_repo(db)

    def _snapshot_repo(db=Depends(get_db)):
        return container.snapshot_repo(db)

    def _user_repo(db=Depends(get_db)):
        return container.user_repo(db)

    def _session_repo(db=Depends(get_db)):
        return container.session_repo(db)

    def _password_hasher():
        return container.password_hasher()

    def _token_codec():
        return container.token_codec()

    def _job_executor():
        return container.job_executor()

    def _async_executor():
        return AsyncExecutor()

    def _metrics_service(db=Depends(get_db)):
        return container.metrics_service(db)

    def _color_token_repo(db=Depends(get_db)):
        return container.color_token_repo(db)

    def _color_token_writer(db=Depends(get_db)):
        return container.color_token_writer(db)

    def _color_token_library_repo(db=Depends(get_db)):
        return container.color_token_library_repo(db)

    def _token_library_repo(db=Depends(get_db)):
        return container.token_library_repo(db)

    def _token_export_repo(db=Depends(get_db)):
        return container.token_export_repo(db)

    def _shadow_repo(db=Depends(get_db)):
        return container.shadow_repo(db)

    def _gradient_repo(db=Depends(get_db)):
        return container.gradient_repo(db)

    def _spacing_repo(db=Depends(get_db)):
        return container.spacing_repo(db)

    def _layout_repo(db=Depends(get_db)):
        return container.layout_repo(db)

    def _typography_repo(db=Depends(get_db)):
        return container.typography_repo(db)

    def _db_session(db=Depends(get_db)):
        # Backwards-compatible override for routers that depend on get_db_session
        return db

    app.dependency_overrides[deps.get_project_repo] = _project_repo
    app.dependency_overrides[deps.get_job_repo] = _job_repo
    app.dependency_overrides[deps.get_snapshot_repo] = _snapshot_repo
    app.dependency_overrides[deps.get_user_repo] = _user_repo
    app.dependency_overrides[deps.get_session_repo] = _session_repo
    app.dependency_overrides[deps.get_password_hasher] = _password_hasher
    app.dependency_overrides[deps.get_token_codec] = _token_codec
    app.dependency_overrides[deps.get_job_executor] = _job_executor
    app.dependency_overrides[deps.get_async_executor] = _async_executor
    app.dependency_overrides[deps.get_metrics_service] = _metrics_service
    app.dependency_overrides[deps.get_color_token_repo] = _color_token_repo
    app.dependency_overrides[deps.get_color_token_writer] = _color_token_writer
    app.dependency_overrides[deps.get_color_token_library_repo] = _color_token_library_repo
    app.dependency_overrides[deps.get_token_library_repo] = _token_library_repo
    app.dependency_overrides[deps.get_token_export_repo] = _token_export_repo
    app.dependency_overrides[deps.get_shadow_repo] = _shadow_repo
    app.dependency_overrides[deps.get_gradient_repo] = _gradient_repo
    app.dependency_overrides[deps.get_spacing_repo] = _spacing_repo
    app.dependency_overrides[deps.get_layout_repo] = _layout_repo
    app.dependency_overrides[deps.get_typography_repo] = _typography_repo
    app.dependency_overrides[deps.get_db_session] = _db_session

    # CORS (allow frontend to call API)
    cors_origins_raw = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:5174,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:3000",
    )
    cors_origins = [origin.strip() for origin in cors_origins_raw.split(",")]

    environment = os.getenv("ENVIRONMENT", "local")
    if "*" in cors_origins and environment not in ("local", "development"):
        import logging

        logging.warning(
            f"SECURITY WARNING: CORS_ORIGINS contains wildcard '*' in {environment} environment. "
            "This allows any origin to make requests. Configure explicit origins for production."
        )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-API-Key",
            "X-Requested-With",
        ],
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ],
        max_age=600,
    )

    # MVP happy-path routers (P0/P1 — see docs/planning/MVP_EXPANSION_ROADMAP.md)
    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(colors_router)
    app.include_router(spacing_router)
    app.include_router(typography_router)
    app.include_router(shadows_router)
    app.include_router(gradients_router)
    app.include_router(design_tokens_router)

    # Park decision (2026-09-19 harden wave): KEEP routers mounted behind App feature
    # flags — do NOT hard-unmount. Reasons: existing API clients/tests, P4/P5 promotion
    # without rewiring imports, and safer rollback. Default UI hides these via
    # frontend/src/config/featureFlags.ts (all park flags false).
    #
    # Parked routers:
    #   P4 — lighting, geometry, mood_board
    #   P5 — sessions, jobs, batch
    #   demos/ops — multi_extract, snapshots, metrics, admin
    app.include_router(sessions_router)  # P5: libraries / curation
    app.include_router(multi_extract_router)  # alt SSE path / demos
    app.include_router(snapshots_router)
    app.include_router(lighting_router)  # P4
    app.include_router(geometry_router)  # P4 — gates: docs/planning/P4_GEOMETRY_GATES.md
    app.include_router(metrics_router)
    app.include_router(jobs_router)  # P5
    app.include_router(batch_router)  # P5
    app.include_router(mood_board_router)  # P4
    try:
        from copy_that.interfaces.api.admin import router as admin_router

        app.include_router(admin_router)
    except Exception:
        logger.warning("Admin router not available; skipping /api/v1/admin routes")

    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    static_dir = Path(__file__).parent.parent.parent.parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "version": "1.0.0",
        }

    @app.get("/", response_class=FileResponse)
    async def root():
        demo_file = Path(__file__).parent.parent.parent.parent.parent / "static" / "index.html"
        if demo_file.exists():
            return demo_file
        return JSONResponse(
            {
                "message": "Welcome to Copy That API!",
                "tagline": "Multi-Modal Token Platform",
                "demo": "/static/index.html",
                "docs": "/docs",
                "health": "/health",
            }
        )

    @app.get("/api/v1/status")
    async def api_status():
        return {
            "api": "Copy That v1.0.0",
            "status": "operational",
            "features": {
                "color_tokens": "available",
                "spacing_tokens": "available",
                "typography_tokens": "available",
            },
            "gcp_project": os.getenv("GCP_PROJECT_ID", "copy-that-platform"),
            "environment": os.getenv("ENVIRONMENT", "production"),
        }

    @app.get("/api/v1/docs", response_class=JSONResponse)
    async def api_documentation():
        return {
            "title": "Copy That API v1.0.0",
            "description": "AI-powered color extraction platform using Claude Sonnet 4.5",
            "endpoints": {
                "auth": {
                    "register": "POST /api/v1/auth/register",
                    "login": "POST /api/v1/auth/token",
                    "refresh": "POST /api/v1/auth/refresh",
                    "me": "GET /api/v1/auth/me",
                },
                "projects": {
                    "list": "GET /api/v1/projects",
                    "create": "POST /api/v1/projects",
                    "get": "GET /api/v1/projects/{id}",
                    "update": "PUT /api/v1/projects/{id}",
                    "delete": "DELETE /api/v1/projects/{id}",
                },
                "colors": {
                    "extract": "POST /api/v1/colors/extract",
                    "extract_streaming": "POST /api/v1/colors/extract-streaming",
                    "list_by_project": "GET /api/v1/projects/{id}/colors",
                    "create": "POST /api/v1/colors",
                    "get": "GET /api/v1/colors/{id}",
                },
                "typography": {
                    "extract": "POST /api/v1/typography/extract",
                    "list_by_project": "GET /api/v1/projects/{id}/typography",
                    "batch_extract": "POST /api/v1/typography/batch",
                    "create": "POST /api/v1/typography",
                    "get": "GET /api/v1/typography/{id}",
                    "update": "PUT /api/v1/typography/{id}",
                    "delete": "DELETE /api/v1/typography/{id}",
                    "export": "GET /api/v1/typography/export/w3c",
                },
                "spacing": {
                    "extract": "POST /api/v1/spacing/extract",
                    "extract_streaming": "POST /api/v1/spacing/extract-streaming",
                    "batch_extract": "POST /api/v1/spacing/batch-extract",
                    "scales": "GET /api/v1/spacing/scales",
                },
                "multi_extract": {
                    "extract_streaming": "POST /api/v1/extract/stream",
                },
                "sessions": {
                    "create": "POST /api/v1/sessions",
                    "get": "GET /api/v1/sessions/{id}",
                    "get_library": "GET /api/v1/sessions/{id}/library",
                    "batch_extract": "POST /api/v1/sessions/{id}/extract",
                    "curate": "POST /api/v1/sessions/{id}/library/curate",
                    "export": "GET /api/v1/sessions/{id}/library/export",
                },
            },
            "documentation": {
                "interactive_swagger": "/docs",
                "interactive_redoc": "/redoc",
                "openapi_json": "/openapi.json",
            },
        }

    @app.get("/api/v1/db-test")
    async def test_database(project_repo: ProjectRepository = Depends(deps.get_project_repo)):
        projects_count = await project_repo.count()
        return {
            "database": "connected",
            "provider": "Neon",
            "projects_count": projects_count,
            "message": "Database connection successful!",
        }

    return app
