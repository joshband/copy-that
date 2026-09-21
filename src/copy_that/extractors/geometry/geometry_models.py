from __future__ import annotations

import importlib
import io
import logging
import os
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from functools import lru_cache

import torch


class OptionalDependencyError(RuntimeError):
    pass


def _require(pkg: str):
    try:
        return __import__(pkg, fromlist=["*"])
    except Exception as exc:
        raise OptionalDependencyError(f"Missing dependency: {pkg}") from exc


@contextmanager
def _silence_transformers_warnings():
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        try:
            auto_docstring = importlib.import_module("transformers.utils.auto_docstring")
            from transformers.utils import logging as hf_logging
        except Exception:
            yield
            return

        auto_docstring.HARDCODED_CONFIG_FOR_MODELS.setdefault("parakeet", "ModelConfig")

        prev_verbosity = hf_logging.get_verbosity()
        auto_doc_logger = logging.getLogger("transformers.utils.auto_docstring")
        prev_auto_doc_level = auto_doc_logger.level
        hf_logging.set_verbosity_error()
        auto_doc_logger.setLevel(logging.ERROR)
        try:
            yield
        finally:
            hf_logging.set_verbosity(prev_verbosity)
            auto_doc_logger.setLevel(prev_auto_doc_level)


@lru_cache(maxsize=4)
def depth_anything(model_id: str, device: str):
    with _silence_transformers_warnings():
        transformers = _require("transformers")

        is_cuda = device.startswith("cuda")
        is_mps = device.startswith("mps")
        dtype = torch.float16 if is_cuda else torch.float32
        if hasattr(transformers, "DepthAnythingPipeline"):
            pipe = transformers.DepthAnythingPipeline.from_pretrained(
                model_id,
                torch_dtype=dtype,
            )
            return pipe.to(device)

        if hasattr(transformers, "pipeline"):
            from transformers import DPTImageProcessor

            if is_cuda:
                device_index = 0
            elif is_mps:
                device_index = "mps"
            else:
                device_index = -1
            trust_remote = os.getenv("DEPTH_ANYTHING_TRUST_REMOTE_CODE", "").lower() in {
                "1",
                "true",
                "yes",
            }
            if trust_remote:
                return transformers.pipeline(
                    "depth-estimation",
                    model=model_id,
                    torch_dtype=dtype,
                    device=device_index,
                    trust_remote_code=True,
                )

            processor = DPTImageProcessor(
                size={"height": 518, "width": 518},
                keep_aspect_ratio=True,
                ensure_multiple_of=14,
            )
            return transformers.pipeline(
                "depth-estimation",
                model=model_id,
                torch_dtype=dtype,
                device=device_index,
                image_processor=processor,
            )

    raise OptionalDependencyError(
        "transformers.DepthAnythingPipeline or transformers.pipeline missing"
    )


@lru_cache(maxsize=4)
def marigold_normals(model_id: str, device: str):
    diffusers = _require("diffusers")

    if not hasattr(diffusers, "MarigoldNormalsPipeline"):
        raise OptionalDependencyError("diffusers.MarigoldNormalsPipeline missing")

    if not device.startswith("cuda"):
        raise OptionalDependencyError("Marigold requires CUDA")

    dtype = torch.float16
    kwargs = {"torch_dtype": dtype}
    kwargs["variant"] = "fp16"
    pipe = diffusers.MarigoldNormalsPipeline.from_pretrained(
        model_id,
        **kwargs,
    )
    return pipe.to(device)
