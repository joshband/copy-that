"""
Shadow feature extraction and design tokenization.

Converts raw shadow analysis (masks, maps, geometry) into:
1. ShadowFeatures: Numeric metrics (area, intensity, softness, direction, etc.)
2. ShadowTokens: Quantized, design-system-friendly values (categorical)

This layer bridges computer vision output and design systems.
"""

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from .classical import detect_shadows_classical
from .depth_normals import estimate_depth_and_normals
from .intrinsic import decompose_intrinsic


@dataclass
class ShadowFeatures:
    """Numeric shadow features extracted from analysis."""

    shadow_area_fraction: float
    """Fraction of image that is shadow (0..1)."""

    mean_shadow_intensity: float
    """Average brightness in shadow regions (0..1, lower=darker)."""

    mean_lit_intensity: float
    """Average brightness in lit regions (0..1)."""

    mean_shadow_to_lit_ratio: float
    """Ratio of shadow intensity to lit intensity (0..1)."""

    edge_softness_mean: float
    """Average softness of shadow edges (0..1, 0=hard, 1=very soft)."""

    edge_softness_std: float
    """Standard deviation of edge softness."""

    dominant_light_direction: tuple[float, float] | None
    """Estimated light direction as (azimuth, elevation) in radians. None if unknown."""

    inconsistency_score: float
    """How inconsistent shading is with geometry (0..1, 0=perfect, 1=impossible)."""

    shadow_contrast: float
    """Contrast between shadow and lit regions (0..1)."""

    shadow_count_major: int
    """Number of significant shadow regions detected."""

    light_direction_confidence: float
    """Confidence in light direction estimate (0..1)."""


@dataclass
class ShadowTokens:
    """Design-token-friendly shadow descriptors (categorical/bucketed)."""

    # Style tokens: design system categories
    style_key_direction: str
    """Light direction: "upper_left", "upper_right", "lower_left", "lower_right",
    "left", "right", "overhead", "front", "diffuse" or "unknown"."""

    style_softness: str
    """Edge softness: "very_hard", "hard", "medium", "soft", "very_soft"."""

    style_contrast: str
    """Shadow-to-lit contrast: "low", "medium", "high", "very_high"."""

    style_density: str
    """Shadow coverage: "sparse", "moderate", "heavy", "full"."""

    # Intensity tokens
    intensity_shadow: str
    """Shadow darkness: "very_light", "light", "medium", "dark", "very_dark"."""

    intensity_lit: str
    """Lit region brightness: "very_dark", "dark", "medium", "bright", "very_bright"."""

    # Metadata
    extraction_confidence: float
    """Overall confidence in extraction (0..1)."""

    lighting_style: str
    """High-level lighting type: "directional", "rim", "diffuse", "mixed", "complex"."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return asdict(self)


def compute_shadow_features(
    image_bgr: np.ndarray,
    shadow_soft: np.ndarray,
    shadow_mask: np.ndarray,
    depth: np.ndarray | None = None,
    normals: np.ndarray | None = None,
    shading: np.ndarray | None = None,
) -> ShadowFeatures:
    """
    Compute numeric shadow features from analysis outputs.

    Args:
        image_bgr: Original image (H×W×3, uint8)
        shadow_soft: Soft shadow map (H×W float32, 0..1)
        shadow_mask: Binary shadow mask (H×W uint8, 0-255)
        depth: Optional depth map (H×W float32, 0..1)
        normals: Optional normal map (H×W×3 float32)
        shading: Optional shading map (H×W float32, 0..1)

    Returns:
        ShadowFeatures with computed metrics
    """
    # Convert image to grayscale for intensity analysis
    gray = 0.299 * image_bgr[:, :, 2] + 0.587 * image_bgr[:, :, 1] + 0.114 * image_bgr[:, :, 0]
    gray = gray.astype(np.float32) / 255.0

    # ========== Area and coverage ==========
    shadow_binary = shadow_mask > 127
    shadow_area_fraction = np.sum(shadow_binary) / (shadow_mask.shape[0] * shadow_mask.shape[1])

    # ========== Intensity statistics ==========
    if shadow_binary.any():
        shadow_intensity = gray[shadow_binary]
        lit_intensity = gray[~shadow_binary]

        mean_shadow_intensity = float(np.mean(shadow_intensity))
        mean_lit_intensity = float(np.mean(lit_intensity)) if lit_intensity.size > 0 else 1.0
    else:
        mean_shadow_intensity = 1.0
        mean_lit_intensity = 1.0

    mean_shadow_to_lit_ratio = (
        mean_shadow_intensity / (mean_lit_intensity + 1e-8) if mean_lit_intensity > 0 else 1.0
    )
    shadow_contrast = float(np.clip(mean_lit_intensity - mean_shadow_intensity, 0, 1))

    # ========== Edge softness ==========
    # Compute gradient magnitude at shadow edges
    if shadow_soft.max() > 0:
        import cv2

        grad_x = cv2.Sobel(shadow_soft, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(shadow_soft, cv2.CV_32F, 0, 1, ksize=3)
        gradient_mag = np.sqrt(grad_x**2 + grad_y**2)

        # Softness: small gradients = soft edges, large gradients = hard edges
        # Normalize by max to get 0..1
        edge_softness = 1.0 - np.clip(gradient_mag / (gradient_mag.max() + 1e-8), 0, 1)
        edge_softness_mean = float(np.mean(edge_softness))
        edge_softness_std = float(np.std(edge_softness))
    else:
        edge_softness_mean = 0.0
        edge_softness_std = 0.0

    # ========== Light direction estimation ==========
    light_direction = None
    light_direction_confidence = 0.0

    if normals is not None and shading is not None:
        # If shading is available, we can estimate light direction via Lambertian fit
        # Assuming: shading ≈ max(0, light · normal)
        # This is a simplified approach

        # Flatten for computation
        normals_flat = normals.reshape(-1, 3)
        shading_flat = shading.flatten()

        # Normalize normals
        norm_lengths = np.linalg.norm(normals_flat, axis=1, keepdims=True)
        normals_normalized = normals_flat / (norm_lengths + 1e-8)

        # Simple least-squares fit for light direction
        # light · n ≈ shading (simplified Lambertian)
        try:
            light_est = np.linalg.lstsq(normals_normalized, shading_flat, rcond=None)[0]
            light_est_norm = np.linalg.norm(light_est)

            if light_est_norm > 0.1:  # Meaningful estimate
                light_est = light_est / light_est_norm

                # Convert to azimuth, elevation
                azimuth = np.arctan2(light_est[1], light_est[0])
                elevation = np.arccos(np.clip(light_est[2], -1, 1))

                light_direction = (float(azimuth), float(elevation))
                light_direction_confidence = float(np.clip(light_est_norm, 0, 1))
        except Exception:
            light_direction = None
            light_direction_confidence = 0.0

    # ========== Inconsistency scoring ==========
    # Measure how much shading deviates from what we'd expect from geometry
    inconsistency_score = 0.0
    if normals is not None and shading is not None and light_direction is not None:
        # Expected shading = max(0, light · normal)
        azimuth, elevation = light_direction
        light_vec = np.array(
            [
                np.cos(azimuth) * np.sin(elevation),
                np.sin(azimuth) * np.sin(elevation),
                np.cos(elevation),
            ]
        )

        expected_shading = np.maximum(0, np.dot(normals, light_vec))
        shading_diff = np.abs(shading - expected_shading)
        inconsistency_score = float(np.mean(shading_diff))

    # ========== Shadow region count ==========
    import cv2

    contours, _ = cv2.findContours(shadow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    shadow_count_major = sum(1 for c in contours if cv2.contourArea(c) > 100)

    # ========== Return features ==========
    return ShadowFeatures(
        shadow_area_fraction=float(np.clip(shadow_area_fraction, 0, 1)),
        mean_shadow_intensity=float(np.clip(mean_shadow_intensity, 0, 1)),
        mean_lit_intensity=float(np.clip(mean_lit_intensity, 0, 1)),
        mean_shadow_to_lit_ratio=float(np.clip(mean_shadow_to_lit_ratio, 0, 1)),
        edge_softness_mean=float(np.clip(edge_softness_mean, 0, 1)),
        edge_softness_std=float(np.clip(edge_softness_std, 0, 1)),
        dominant_light_direction=light_direction,
        inconsistency_score=float(np.clip(inconsistency_score, 0, 1)),
        shadow_contrast=float(np.clip(shadow_contrast, 0, 1)),
        shadow_count_major=int(shadow_count_major),
        light_direction_confidence=float(np.clip(light_direction_confidence, 0, 1)),
    )


def quantize_shadow_tokens(features: ShadowFeatures) -> ShadowTokens:
    """
    Convert numeric shadow features into discrete design tokens.

    Quantization rules are documented here; adjust thresholds as needed
    for your use case.

    Args:
        features: ShadowFeatures with numeric metrics

    Returns:
        ShadowTokens with categorical values suitable for design systems
    """
    # ========== Light direction ==========
    if features.dominant_light_direction is not None and features.light_direction_confidence > 0.3:
        azimuth, elevation = features.dominant_light_direction
        # Map azimuth (0..2π) and elevation (0..π/2 for front light)
        azimuth_deg = (azimuth * 180 / np.pi) % 360

        if elevation > np.pi / 3:  # ~60°, overhead-ish
            style_key_direction = "overhead"
        elif elevation > np.pi / 6:  # ~30°
            if azimuth_deg < 45 or azimuth_deg > 315:
                style_key_direction = "right"
            elif 45 <= azimuth_deg < 135:
                style_key_direction = "upper_left"
            elif 135 <= azimuth_deg < 225:
                style_key_direction = "left"
            else:
                style_key_direction = "upper_right"
        else:  # Low angle, rim lighting
            style_key_direction = "rim"
    else:
        style_key_direction = "unknown"

    # ========== Edge softness ==========
    if features.edge_softness_mean < 0.2:
        style_softness = "very_hard"
    elif features.edge_softness_mean < 0.4:
        style_softness = "hard"
    elif features.edge_softness_mean < 0.6:
        style_softness = "medium"
    elif features.edge_softness_mean < 0.8:
        style_softness = "soft"
    else:
        style_softness = "very_soft"

    # ========== Shadow-to-lit contrast ==========
    if features.shadow_contrast < 0.2:
        style_contrast = "low"
    elif features.shadow_contrast < 0.4:
        style_contrast = "medium"
    elif features.shadow_contrast < 0.7:
        style_contrast = "high"
    else:
        style_contrast = "very_high"

    # ========== Shadow density (coverage) ==========
    if features.shadow_area_fraction < 0.15:
        style_density = "sparse"
    elif features.shadow_area_fraction < 0.35:
        style_density = "moderate"
    elif features.shadow_area_fraction < 0.65:
        style_density = "heavy"
    else:
        style_density = "full"

    # ========== Intensity tokens ==========
    if features.mean_shadow_intensity < 0.2:
        intensity_shadow = "very_dark"
    elif features.mean_shadow_intensity < 0.4:
        intensity_shadow = "dark"
    elif features.mean_shadow_intensity < 0.6:
        intensity_shadow = "medium"
    elif features.mean_shadow_intensity < 0.8:
        intensity_shadow = "light"
    else:
        intensity_shadow = "very_light"

    if features.mean_lit_intensity < 0.3:
        intensity_lit = "very_dark"
    elif features.mean_lit_intensity < 0.45:
        intensity_lit = "dark"
    elif features.mean_lit_intensity < 0.6:
        intensity_lit = "medium"
    elif features.mean_lit_intensity < 0.75:
        intensity_lit = "bright"
    else:
        intensity_lit = "very_bright"

    # ========== Lighting style ==========
    if features.light_direction_confidence > 0.5:
        if features.shadow_area_fraction < 0.2:
            lighting_style = "rim"
        elif features.shadow_area_fraction < 0.4:
            lighting_style = "directional"
        else:
            lighting_style = "mixed"
    elif features.inconsistency_score > 0.3:
        lighting_style = "complex"
    else:
        lighting_style = "diffuse"

    return ShadowTokens(
        style_key_direction=style_key_direction,
        style_softness=style_softness,
        style_contrast=style_contrast,
        style_density=style_density,
        intensity_shadow=intensity_shadow,
        intensity_lit=intensity_lit,
        extraction_confidence=features.light_direction_confidence,
        lighting_style=lighting_style,
    )


def analyze_image_for_shadows(
    image_bgr: np.ndarray,
    use_deep: bool = False,
    use_geometry: bool = True,
    device: str = "cpu",
) -> dict[str, Any]:
    """
    High-level entrypoint for comprehensive shadow analysis.

    Orchestrates all components: classical detection, depth/normals estimation,
    intrinsic decomposition, feature extraction, and tokenization.

    Args:
        image_bgr: Input image in BGR format (H×W×3, uint8)
        use_deep: Whether to use deep learning models (slower, potentially more accurate)
        use_geometry: Whether to estimate depth/normals for geometry-aware analysis
        device: Compute device ("cuda" or "cpu")

    Returns:
        Dictionary containing:
            - shadow_soft: Soft shadow map (H×W float32, 0..1)
            - shadow_mask: Binary mask (H×W uint8, 0-255)
            - depth: Depth map if use_geometry=True (H×W float32)
            - normals: Surface normals if use_geometry=True (H×W×3 float32)
            - shading: Shading map from intrinsic decomposition (H×W float32)
            - features: ShadowFeatures dataclass
            - tokens: ShadowTokens dataclass
            - debug: Debug information

    Example:
        >>> result = analyze_image_for_shadows(image_bgr)
        >>> print(f"Shadow area: {result['features'].shadow_area_fraction:.1%}")
        >>> print(f"Lighting: {result['tokens'].style_key_direction}")
        >>> # Visualize
        >>> import cv2
        >>> cv2.imshow("Shadows", result["shadow_mask"])
    """
    # Step 1: Classical shadow detection
    classical_result = detect_shadows_classical(image_bgr)
    shadow_soft = classical_result["shadow_soft"]
    shadow_mask = classical_result["shadow_mask"]

    # Step 2: Geometry estimation (optional)
    depth = None
    normals = None
    if use_geometry:
        try:
            geom = estimate_depth_and_normals(image_bgr, device=device)
            depth = geom["depth"]
            normals = geom["normals"]
        except Exception as e:
            import logging

            logging.warning(f"Geometry estimation failed: {e}")

    # Step 3: Intrinsic decomposition
    try:
        intrinsic = decompose_intrinsic(image_bgr, device=device)
        shading = intrinsic["shading"]
    except Exception as e:
        import logging

        logging.warning(f"Intrinsic decomposition failed: {e}")
        shading = None

    # Step 4: Feature extraction
    features = compute_shadow_features(
        image_bgr,
        shadow_soft,
        shadow_mask,
        depth=depth,
        normals=normals,
        shading=shading,
    )

    # Step 5: Tokenization
    tokens = quantize_shadow_tokens(features)

    return {
        "shadow_soft": shadow_soft,
        "shadow_mask": shadow_mask,
        "depth": depth,
        "normals": normals,
        "shading": shading,
        "features": asdict(features),
        "tokens": tokens.to_dict(),
        "debug": classical_result.get("debug", {}),
    }
