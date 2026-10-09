"""Core runtime must import without cloud or deep-CV extras."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_CORE_IMPORT_CHECK = """
import builtins
from unittest.mock import patch

original_import = builtins.__import__
blocked = {"torch", "torchvision", "ultralytics", "layoutparser", "transformers", "diffusers", "accelerate", "google.cloud"}
def core_import(name, *args, **kwargs):
    if any(name == package or name.startswith(package + ".") for package in blocked):
        raise ModuleNotFoundError("Optional dependency blocked: " + name, name=name)
    return original_import(name, *args, **kwargs)

with patch("dotenv.load_dotenv", return_value=False), patch("decouple.RepositoryEnv", side_effect=AssertionError("No env file access")), patch("builtins.__import__", side_effect=core_import):
    from copy_that.interfaces.api.app_factory import create_app
    app = create_app()
    assert app.openapi()["paths"]["/api/v1/shadows/extract"]
    from copy_that.extractors.geometry.optional_runtime import extract_depth_and_normals
    from copy_that.extractors.geometry.geometry_models import OptionalDependencyError
    try:
        extract_depth_and_normals(None)
    except OptionalDependencyError as exc:
        assert "cv-deep" in str(exc)
    else:
        raise AssertionError("Missing geometry extras did not raise OptionalDependencyError")
"""


def test_core_app_imports_and_optional_geometry_fails_explicitly(tmp_path):
    env = dict(os.environ)
    env.update(
        ENVIRONMENT="local",
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        SECRET_KEY="hermetic-core-runtime-test-secret",
        PYTHONPATH=str(Path(__file__).resolve().parents[2] / "src"),
    )
    result = subprocess.run(
        [sys.executable, "-c", _CORE_IMPORT_CHECK],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=45,
    )
    assert result.returncode == 0, result.stderr
