"""
Multi-stage shadow extraction pipeline for Midjourney-style images.

Implements 8-stage processing chain:
1. Input & Preprocessing
2. Illumination-Invariant View
3. Classical Shadow Candidates
4. ML Shadow Mask
5. Intrinsic Image Decomposition
6. Depth & Surface Normals
7. Lighting Fit & Consistency
8. Fusion & Token Generation

Emits:
- ShadowStageResult[] (structured per-stage outputs)
- ShadowVisualLayer[] (visualization metadata)
- ShadowTokenSet (final consolidated tokens)
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import cv2
import numpy as np


class VisualLayerType(str, Enum):
    """Visual layer render type."""

    RGB = "rgb"
    GRAYSCALE_MAP = "grayscale_map"
    HEATMAP = "heatmap"
    MASK_OVERLAY = "mask_overlay"
    DEPTH = "depth"
    NORMAL = "normal"
    COMPOSITE = "composite"


class BlendMode(str, Enum):
    """Layer blend mode."""

    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"


@dataclass
class RenderParams:
    """Rendering parameters for visual layer."""

    colormap: str | None = None
    opacity: float = 1.0
    blend_mode: BlendMode = BlendMode.NORMAL
    value_range: tuple[float, float] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "colormap": self.colormap,
            "opacity": self.opacity,
            "blend_mode": self.blend_mode.value,
            "value_range": self.value_range,
        }


@dataclass
class UIConfig:
    """UI configuration for visual layer."""

    title: str
    subtitle: str | None = None
    default_visible: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "default_visible": self.default_visible,
        }


@dataclass
class ShadowVisualLayer:
    """Visualization layer definition."""

    id: str
    stage_id: str
    type: VisualLayerType
    source_artifact: str
    render_params: RenderParams
    ui: UIConfig

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "stage_id": self.stage_id,
            "type": self.type.value,
            "source_artifact": self.source_artifact,
            "render_params": self.render_params.to_dict(),
            "ui": self.ui.to_dict(),
        }


@dataclass
class ShadowStageResult:
    """Result from a single stage of the pipeline."""

    id: str
    name: str
    description: str
    inputs: list[str]
    outputs: list[str]
    metrics: dict[str, float] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    visual_layers: list[str] = field(default_factory=list)
    stage_narrative: str = ""
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "metrics": self.metrics,
            "artifacts": self.artifacts,
            "visual_layers": self.visual_layers,
            "stage_narrative": self.stage_narrative,
            "duration_ms": self.duration_ms,
        }


@dataclass
class LightDirection:
    """Light direction in spherical coordinates."""

    azimuth_deg: float  # 0-360
    elevation_deg: float  # -90 to 90

    def to_dict(self) -> dict[str, float]:
        return {"azimuth_deg": self.azimuth_deg, "elevation_deg": self.elevation_deg}


@dataclass
class ShadowClusterStats:
    """Statistics for a shadow cluster region."""

    cluster_id: int
    region_label: str | None = None
    coverage: float = 0.0  # 0-1
    mean_strength: float = 0.0  # 0-1

    def to_dict(self) -> dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "region_label": self.region_label,
            "coverage": self.coverage,
            "mean_strength": self.mean_strength,
        }


@dataclass
class ShadowTokens:
    """Shadow token metrics."""

    coverage: float  # Fraction of image in shadow
    mean_strength: float  # Average shadow opacity
    edge_softness_mean: float  # Penumbra width
    edge_softness_std: float  # Penumbra variation
    key_light_direction: LightDirection
    key_light_softness: float  # 0-1, how soft is main light
    physics_consistency: float  # 0-1, how physically plausible
    style_label: str | None = None
    style_embedding: list[float] | None = None
    shadow_cluster_stats: list[ShadowClusterStats] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "coverage": self.coverage,
            "mean_strength": self.mean_strength,
            "edge_softness_mean": self.edge_softness_mean,
            "edge_softness_std": self.edge_softness_std,
            "key_light_direction": self.key_light_direction.to_dict(),
            "key_light_softness": self.key_light_softness,
            "physics_consistency": self.physics_consistency,
            "style_label": self.style_label,
            "style_embedding": self.style_embedding,
            "shadow_cluster_stats": [s.to_dict() for s in self.shadow_cluster_stats],
        }


@dataclass
class ShadowTokenSet:
    """Final consolidated shadow token set."""

    image_id: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    shadow_tokens: ShadowTokens = field(
        default_factory=lambda: ShadowTokens(
            coverage=0.0,
            mean_strength=0.0,
            edge_softness_mean=0.0,
            edge_softness_std=0.0,
            key_light_direction=LightDirection(180.0, 45.0),
            key_light_softness=0.5,
            physics_consistency=0.5,
        )
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "image_id": self.image_id,
            "timestamp": self.timestamp,
            "shadow_tokens": self.shadow_tokens.to_dict(),
        }

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2)


class ShadowPipeline:
    """
    Multi-stage shadow extraction pipeline.

    Manages the flow through all 8 stages and produces structured outputs.
    """

    def __init__(self, output_dir: Path | None = None):
        """
        Initialize pipeline.

        Args:
            output_dir: Where to save artifacts and visualizations
        """
        self.output_dir = output_dir or Path("/tmp/shadow_pipeline")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.stages: dict[str, ShadowStageResult] = {}
        self.visual_layers: dict[str, ShadowVisualLayer] = {}
        self.artifacts: dict[str, np.ndarray] = {}

    def register_stage(
        self, stage_result: ShadowStageResult, visual_layers: list[ShadowVisualLayer] | None = None
    ) -> None:
        """
        Register a completed stage.

        Args:
            stage_result: Stage output
            visual_layers: Associated visualization layers
        """
        self.stages[stage_result.id] = stage_result

        if visual_layers:
            for layer in visual_layers:
                self.visual_layers[layer.id] = layer
                stage_result.visual_layers.append(layer.id)

    def register_artifact(self, name: str, data: np.ndarray) -> None:
        """
        Register an artifact (intermediate or final result).

        Args:
            name: Artifact name (e.g., 'illumination_map')
            data: NumPy array
        """
        self.artifacts[name] = data

    def get_results_summary(self) -> dict[str, Any]:
        """
        Get summary of all stages.

        Returns:
            Structured summary with all stage results and visual layers
        """
        return {
            "stages": [s.to_dict() for s in self.stages.values()],
            "visual_layers": [l.to_dict() for l in self.visual_layers.values()],
            "artifacts_list": list(self.artifacts.keys()),
            "total_duration_ms": sum(s.duration_ms for s in self.stages.values()),
        }

    def save_results(self, filename: str = "pipeline_results.json") -> Path:
        """
        Save pipeline results to JSON.

        Args:
            filename: Output filename

        Returns:
            Path to saved file
        """
        output_path = self.output_dir / filename
        with open(output_path, "w") as f:
            json.dump(self.get_results_summary(), f, indent=2)
        return output_path

    def save_artifact(self, name: str, filename: str | None = None) -> Path | None:
        """
        Save an artifact to disk.

        Args:
            name: Artifact name
            filename: Custom filename (defaults to artifact name)

        Returns:
            Path to saved file, or None if artifact doesn't exist
        """
        if name not in self.artifacts:
            return None

        filename = filename or f"{name}.npy"
        output_path = self.output_dir / filename
        np.save(output_path, self.artifacts[name])
        return output_path

    def save_all_artifacts(self) -> dict[str, Path]:
        """
        Save all artifacts to disk.

        Returns:
            Map of artifact names to saved paths
        """
        saved = {}
        for name in self.artifacts:
            path = self.save_artifact(name)
            if path:
                saved[name] = path
        return saved


# ============================================================================
# TASK 1: Image I/O and Illumination-Invariant Map
# ============================================================================


def load_rgb(path: str) -> np.ndarray:
    """
    Load image and normalize to float32 RGB.

    Args:
        path: Image file path

    Returns:
        RGB image as float32 in range [0, 1]
    """
    img = cv2.imread(path)
    if img is None:
        raise OSError(f"Cannot load image: {path}")

    # BGR -> RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Normalize to [0, 1]
    img_float = img_rgb.astype(np.float32) / 255.0

    return img_float


def illumination_invariant_v(rgb: np.ndarray) -> np.ndarray:
    """
    Compute illumination-invariant brightness map.

    Uses HSV value channel (brightness) as the primary illumination signal.

    Args:
        rgb: RGB image, float32 in [0, 1]

    Returns:
        Grayscale illumination map, float32 in [0, 1]
    """
    # Convert to HSV
    rgb_uint8 = (rgb * 255).astype(np.uint8)
    hsv = cv2.cvtColor(rgb_uint8, cv2.COLOR_RGB2HSV)

    # Extract V (value/brightness) channel
    v_channel = hsv[:, :, 2].astype(np.float32) / 255.0

    # Optional: contrast stretching for emphasis
    v_min, v_max = np.percentile(v_channel, [2, 98])
    if v_max > v_min:
        v_stretched = (v_channel - v_min) / (v_max - v_min)
        v_stretched = np.clip(v_stretched, 0, 1)
    else:
        v_stretched = v_channel

    return v_stretched.astype(np.float32)


# ============================================================================
# TASK 2: Classical Shadow Candidates
# ============================================================================


def classical_shadow_candidates(
    v: np.ndarray, threshold_percentile: float = 20.0, min_area: int = 10
) -> np.ndarray:
    """
    Classical shadow detection via adaptive thresholding and morphology.

    Args:
        v: Illumination map from illumination_invariant_v()
        threshold_percentile: Percentile for darkness threshold (lower = darker)
        min_area: Minimum connected component size in pixels

    Returns:
        Soft shadow mask in [0, 1]
    """
    v_uint8 = (v * 255).astype(np.uint8)

    # Step 1: Adaptive thresholding
    # Compute local mean in 31x31 neighborhood
    local_mean = cv2.blur(v_uint8, (31, 31))

    # Threshold: pixels significantly darker than local mean
    threshold = np.percentile(v_uint8, threshold_percentile)
    dark_mask = v_uint8 < (local_mean * 0.8)
    dark_mask = dark_mask & (v_uint8 < threshold)

    # Step 2: Morphological cleanup (open to remove noise)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dark_clean = cv2.morphologyEx(dark_mask.astype(np.uint8), cv2.MORPH_OPEN, kernel)

    # Step 3: Remove small components
    from scipy import ndimage

    labeled, n_labels = ndimage.label(dark_clean)
    sizes = ndimage.sum(dark_clean, labeled, range(n_labels + 1))

    size_mask = sizes >= min_area
    dark_filtered = size_mask[labeled]

    # Step 4: Soft mask via distance transform
    dist_transform = cv2.distanceTransform(
        dark_filtered.astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE
    )

    # Normalize to [0, 1]
    if dist_transform.max() > 0:
        soft_mask = dist_transform / dist_transform.max()
    else:
        soft_mask = dist_transform

    return soft_mask.astype(np.float32)


# ============================================================================
# TASK 3: ML Shadow Model (Placeholder)
# ============================================================================


def run_shadow_model(rgb: np.ndarray) -> np.ndarray:
    """
    Run pre-trained shadow detection model.

    Placeholder: loads a model from torchvision/timm.
    In production, integrate BDRAR, DSDNet, or similar.

    Args:
        rgb: RGB image, float32 in [0, 1]

    Returns:
        Shadow probability map in [0, 1]
    """
    # TODO: Replace with actual model loading
    # When implementing, will require: import torch; from torchvision import transforms
    h, w = rgb.shape[:2]
    return np.random.rand(h, w).astype(np.float32)


# ============================================================================
# TASK 4: Depth and Intrinsic Decomposition
# ============================================================================


# Global cache for MiDaS model (load once, reuse)
_midas_model = None
_midas_transform = None
_midas_device = None
_midas_load_attempted = False
_midas_load_failed = False


def _get_midas_model(model_type: str = "MiDaS_small"):
    """
    Load MiDaS model (cached).

    Args:
        model_type: One of 'DPT_Large', 'DPT_Hybrid', 'MiDaS_small'
                   Default 'MiDaS_small' for speed/memory balance.

    Returns:
        (model, transform, device) or (None, None, None) if load fails
    """
    global _midas_model, _midas_transform, _midas_device, _midas_load_attempted, _midas_load_failed

    if _midas_load_failed:
        return None, None, None

    if _midas_model is not None:
        return _midas_model, _midas_transform, _midas_device

    if _midas_load_attempted:
        return None, None, None

    _midas_load_attempted = True

    try:
        import torch

        # Determine device
        if torch.cuda.is_available():
            _midas_device = torch.device("cuda")
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            _midas_device = torch.device("mps")
        else:
            _midas_device = torch.device("cpu")

        # Load MiDaS from torch hub
        _midas_model = torch.hub.load("intel-isl/MiDaS", model_type, trust_repo=True)
        _midas_model.to(_midas_device)
        _midas_model.eval()

        # Load transforms
        midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True)
        if model_type in ["DPT_Large", "DPT_Hybrid"]:
            _midas_transform = midas_transforms.dpt_transform
        else:
            _midas_transform = midas_transforms.small_transform

        return _midas_model, _midas_transform, _midas_device

    except Exception as e:
        import warnings

        warnings.warn(f"MiDaS model load failed: {e}. Using depth estimation fallback.")
        _midas_load_failed = True
        return None, None, None


def _fallback_depth_estimation(rgb: np.ndarray) -> np.ndarray:
    """
    Fallback depth estimation using image gradients and heuristics.

    This provides a reasonable approximation when MiDaS is unavailable.

    Args:
        rgb: RGB image, float32 in [0, 1]

    Returns:
        Approximate depth map, normalized to [0, 1]
    """
    # Convert to grayscale
    gray = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]

    # Heuristic 1: Darker regions tend to be further (ambient occlusion)
    darkness_depth = 1.0 - gray

    # Heuristic 2: Vertical position (higher = further in many scenes)
    h, w = rgb.shape[:2]
    y_gradient = np.linspace(0, 1, h)[:, np.newaxis]
    y_gradient = np.broadcast_to(y_gradient, (h, w))

    # Heuristic 3: Blur indicates distance (defocus)
    blurred = cv2.GaussianBlur(gray, (21, 21), 0)
    blur_depth = np.abs(gray - blurred)

    # Combine heuristics
    depth = 0.4 * darkness_depth + 0.4 * y_gradient + 0.2 * blur_depth

    # Normalize
    depth = (depth - depth.min()) / (depth.max() - depth.min() + 1e-8)

    return depth.astype(np.float32)


def run_midas_depth(rgb: np.ndarray, model_type: str = "MiDaS_small") -> np.ndarray:
    """
    Estimate depth map using MiDaS.

    Falls back to heuristic estimation if MiDaS cannot be loaded.

    Args:
        rgb: RGB image, float32 in [0, 1]
        model_type: MiDaS model variant ('MiDaS_small', 'DPT_Large', 'DPT_Hybrid')

    Returns:
        Depth map, normalized to [0, 1] (farther = higher values)
    """
    h, w = rgb.shape[:2]

    # Try to get MiDaS model
    model, transform, device = _get_midas_model(model_type)

    # If MiDaS unavailable, use fallback
    if model is None:
        return _fallback_depth_estimation(rgb)

    import torch

    # Convert to uint8 for MiDaS transform (expects 0-255)
    rgb_uint8 = (rgb * 255).astype(np.uint8)

    # Apply MiDaS transform
    input_batch = transform(rgb_uint8).to(device)

    # Inference
    with torch.no_grad():
        prediction = model(input_batch)

        # Resize to original resolution
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=(h, w),
            mode="bicubic",
            align_corners=False,
        ).squeeze()

    # Convert to numpy
    depth = prediction.cpu().numpy()

    # Normalize to [0, 1]
    depth_min = depth.min()
    depth_max = depth.max()
    if depth_max > depth_min:
        depth = (depth - depth_min) / (depth_max - depth_min)
    else:
        depth = np.zeros_like(depth)

    return depth.astype(np.float32)


def run_intrinsic(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Decompose image into reflectance and shading.

    Args:
        rgb: RGB image, float32 in [0, 1]

    Returns:
        (reflectance, shading) - both float32 in [0, 1]
    """
    # Placeholder: simple approximation
    # TODO: Replace with actual intrinsic decomposition model

    # Use Gaussian blur as rough shading estimate
    rgb_uint8 = (rgb * 255).astype(np.uint8)
    shading_blurred = cv2.GaussianBlur(rgb_uint8, (51, 51), 0)
    shading = shading_blurred.astype(np.float32) / 255.0

    # Rough reflectance = original / shading
    reflectance = np.clip(rgb / (shading + 0.01), 0, 1)

    return reflectance, shading


# ============================================================================
# TASK 5: Depth-to-Normals and Light Estimation
# ============================================================================


def depth_to_normals(depth: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Derive surface normals from depth map.

    Args:
        depth: Depth map, float32

    Returns:
        (normals, normals_vis)
        - normals: (H, W, 3) unit normal vectors
        - normals_vis: (H, W, 3) RGB visualization (0-1)
    """
    h, w = depth.shape

    # Compute gradients
    grad_x = cv2.Sobel(depth, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(depth, cv2.CV_32F, 0, 1, ksize=3)

    # Build normal vectors: (−∂z/∂x, −∂z/∂y, 1)
    normals = np.stack([-grad_x, -grad_y, np.ones_like(depth)], axis=2)

    # Normalize
    norm = np.linalg.norm(normals, axis=2, keepdims=True)
    normals = normals / (norm + 1e-8)

    # Visualize: map to [0, 1] RGB
    # Normal.xyz ≈ (−1, −1, 1) to (1, 1, 1) maps to (0, 0, 0) to (1, 1, 1)
    normals_vis = (normals + 1) / 2  # Map from [-1, 1] to [0, 1]
    normals_vis = np.clip(normals_vis, 0, 1)

    return normals, normals_vis


def fit_directional_light(normals: np.ndarray, shading: np.ndarray) -> np.ndarray:
    """
    Fit a directional light direction to the shading field.

    Minimizes: ||N·L - shading||²

    Args:
        normals: (H, W, 3) unit normal vectors
        shading: (H, W) or (H, W, 3) shading map

    Returns:
        Light direction vector (unit length)
    """
    h, w = normals.shape[:2]

    # Convert shading to grayscale if needed
    if shading.ndim == 3:
        shading_gray = np.mean(shading, axis=2)
    else:
        shading_gray = shading

    # Reshape for linear algebra
    N = normals.reshape(-1, 3)  # (H*W, 3)
    S = shading_gray.reshape(-1)  # (H*W,)

    # Solve N·L ≈ S using least squares
    # L = (N^T N)^{-1} N^T S
    try:
        L = np.linalg.lstsq(N, S, rcond=None)[0]
    except np.linalg.LinAlgError:
        # Fallback to default
        L = np.array([0.0, 0.0, 1.0])

    # Normalize
    L = L / (np.linalg.norm(L) + 1e-8)

    return L


def light_dir_to_angles(L: np.ndarray) -> tuple[float, float]:
    """
    Convert light direction vector to spherical angles.

    Args:
        L: Direction vector (3D)

    Returns:
        (azimuth_deg, elevation_deg)
        - azimuth: 0-360 degrees, 0 = +X, 90 = +Y
        - elevation: -90 to 90 degrees, 0 = horizon, 90 = zenith
    """
    x, y, z = L[0], L[1], L[2]

    # Azimuth: angle in XY plane from +X axis
    azimuth_rad = np.arctan2(y, x)
    azimuth_deg = np.degrees(azimuth_rad) % 360

    # Elevation: angle from XY plane
    r_xy = np.sqrt(x**2 + y**2)
    elevation_rad = np.arctan2(z, r_xy)
    elevation_deg = np.degrees(elevation_rad)

    return azimuth_deg, elevation_deg


# ============================================================================
# TASK 6: Shadow Fusion and Token Computation
# ============================================================================


def fuse_shadow_masks(
    classical: np.ndarray,
    ml_mask: np.ndarray,
    shading: np.ndarray,
    classical_weight: float = 0.3,
    ml_weight: float = 0.5,
    shading_weight: float = 0.2,
) -> np.ndarray:
    """
    Fuse multiple shadow signals into a single mask.

    Args:
        classical: Classical heuristic mask [0, 1]
        ml_mask: ML model output [0, 1]
        shading: Shading map (grayscale or 3-channel) [0, 1]
        classical_weight: Weight for classical signal
        ml_weight: Weight for ML signal
        shading_weight: Weight for shading-derived signal

    Returns:
        Fused shadow mask [0, 1]
    """
    # Convert shading to single channel
    if shading.ndim == 3:
        shading_gray = np.mean(shading, axis=2)
    else:
        shading_gray = shading

    # Invert shading (bright = no shadow, dark = shadow)
    shading_shadow = 1.0 - shading_gray

    # Weighted average
    fused = classical_weight * classical + ml_weight * ml_mask + shading_weight * shading_shadow

    # Normalize if weights don't sum to 1
    total_weight = classical_weight + ml_weight + shading_weight
    fused = fused / total_weight

    return np.clip(fused, 0, 1).astype(np.float32)


def compute_shadow_strength(shading: np.ndarray, fused_mask: np.ndarray) -> float:
    """
    Compute average shadow strength from shading in masked regions.

    Args:
        shading: Shading map [0, 1]
        fused_mask: Shadow mask [0, 1]

    Returns:
        Mean shadow strength [0, 1], where 1 = fully shadowed
    """
    if shading.ndim == 3:
        shading_gray = np.mean(shading, axis=2)
    else:
        shading_gray = shading

    # Shadow strength = 1 - shading
    shadow_strength = 1.0 - shading_gray

    # Average over masked regions
    if np.sum(fused_mask) > 0:
        mean_strength = np.average(shadow_strength, weights=fused_mask)
    else:
        mean_strength = 0.0

    return float(mean_strength)


def compute_edge_softness(fused_mask: np.ndarray, kernel_size: int = 5) -> tuple[float, float]:
    """
    Compute edge softness (penumbra width) statistics.

    Args:
        fused_mask: Shadow mask [0, 1]
        kernel_size: Kernel for gradient computation

    Returns:
        (mean_softness, std_softness)
    """
    # Compute gradients at shadow boundaries
    grad_x = cv2.Sobel(fused_mask, cv2.CV_32F, 1, 0, ksize=kernel_size)
    grad_y = cv2.Sobel(fused_mask, cv2.CV_32F, 0, 1, ksize=kernel_size)

    # Magnitude
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)

    # Find boundary regions (where gradient is high)
    boundary_mask = grad_mag > np.percentile(grad_mag, 50)

    if np.sum(boundary_mask) > 0:
        softness_values = grad_mag[boundary_mask]
        mean_softness = float(np.mean(softness_values))
        std_softness = float(np.std(softness_values))
    else:
        mean_softness = 0.0
        std_softness = 0.0

    return mean_softness, std_softness


def compute_shadow_tokens(
    fused_mask: np.ndarray,
    shading: np.ndarray,
    light_direction: np.ndarray,
    physics_consistency: float = 0.8,
) -> ShadowTokens:
    """
    Compute consolidated shadow tokens.

    Args:
        fused_mask: Final shadow mask [0, 1]
        shading: Shading map [0, 1]
        light_direction: Unit light direction vector
        physics_consistency: Plausibility score [0, 1]

    Returns:
        ShadowTokens with all metrics
    """
    # Coverage: fraction of image in shadow
    coverage = float(np.mean(fused_mask))

    # Mean shadow strength
    mean_strength = compute_shadow_strength(shading, fused_mask)

    # Edge softness
    softness_mean, softness_std = compute_edge_softness(fused_mask)

    # Light direction angles
    azimuth, elevation = light_dir_to_angles(light_direction)
    light_angles = LightDirection(azimuth, elevation)

    # Light softness: estimate from penumbra width
    light_softness = min(1.0, softness_mean / 10.0)  # Heuristic scaling

    return ShadowTokens(
        coverage=coverage,
        mean_strength=mean_strength,
        edge_softness_mean=softness_mean,
        edge_softness_std=softness_std,
        key_light_direction=light_angles,
        key_light_softness=light_softness,
        physics_consistency=physics_consistency,
    )
