from enum import StrEnum


class GeometryProfile(StrEnum):
    AUTO = "auto"
    CPU_FAST = "cpu_fast"
    CPU_ACCURATE = "cpu_accurate"
    GPU_FULL = "gpu_full"
