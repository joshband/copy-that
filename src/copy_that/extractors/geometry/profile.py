from enum import Enum


class GeometryProfile(str, Enum):
    AUTO = "auto"
    CPU_FAST = "cpu_fast"
    CPU_ACCURATE = "cpu_accurate"
    GPU_FULL = "gpu_full"
