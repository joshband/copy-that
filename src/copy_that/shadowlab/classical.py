"""
Classical computer vision shadow detection baseline.

Implements illumination-invariant transforms and morphological analysis
to detect shadow regions in images.

Algorithm overview:
1. Convert RGB to illumination-invariant representations (HSV, log-chromaticity)
2. Compute soft shadow likelihood using:
   - Brightness/value channel (dark regions are likely shadows)
   - Local contrast (shadow regions are dark relative to neighborhood)
   - Color-invariance constraints (shadows maintain chromaticity)
3. Apply morphological cleanup and adaptive thresholding
4. Produce soft map (float32, 0..1) and binary mask (uint8/bool)

Limitations:
- Works best on natural images with clear light/shadow boundaries
- May struggle with stylized/AI-generated images
- Requires reasonable image contrast
"""

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np


@dataclass
class ShadowClassicalConfig:
    """Configuration for classical shadow detection."""

    # Thresholding
    brightness_percentile: float = 35.0
    """Percentile threshold for brightness-based shadow detection (0-100)."""

    local_window_size: int = 31
    """Size of local neighborhood for contrast computation (odd number)."""

    morph_open_size: int = 3
    """Kernel size for morphological opening (noise removal)."""

    morph_close_size: int = 5
    """Kernel size for morphological closing (hole filling)."""

    # Constraints
    chroma_variance_threshold: float = 0.15
    """Max chromaticity variance within shadow region (0-1)."""

    min_shadow_area_fraction: float = 0.001
    """Minimum shadow area as fraction of image size."""


def detect_shadows_classical(
    image_bgr: np.ndarray,
    config: ShadowClassicalConfig | None = None,
) -> dict[str, Any]:
    """
    Detect shadows in an image using classical CV techniques.

    This function implements a classical computer vision approach to shadow
    detection without deep learning. It uses illumination-invariant color
    spaces and morphological analysis.

    Args:
        image_bgr: Input image in BGR format (H×W×3, uint8)
        config: ShadowClassicalConfig with tunable parameters

    Returns:
        Dictionary containing:
            - shadow_soft: Soft shadow map (H×W float32, 0..1)
            - shadow_mask: Binary shadow mask (H×W uint8, 0-255)
            - debug: Dictionary with intermediate maps:
                - brightness: V channel from HSV
                - chroma_norm: Normalized chromaticity
                - local_contrast: Local contrast map
                - brightness_likelihood: Shadow likelihood from brightness
                - contrast_likelihood: Shadow likelihood from contrast
                - threshold_used: Adaptive threshold value
    """
    if config is None:
        config = ShadowClassicalConfig()

    if image_bgr is None or image_bgr.size == 0:
        raise ValueError("Invalid image")

    height, width = image_bgr.shape[:2]

    # ========== Step 1: Convert to illumination-invariant representations ==========

    # HSV: Extract value (brightness) channel
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    brightness = hsv[:, :, 2] / 255.0  # Normalize to [0, 1]

    # Log-chromaticity (illumination-invariant color)
    # Safe division: avoid log(0)
    img_float = image_bgr.astype(np.float32) + 1e-6
    log_r = np.log(img_float[:, :, 2])
    log_g = np.log(img_float[:, :, 1])
    log_b = np.log(img_float[:, :, 0])

    log_sum = log_r + log_g + log_b
    log_chromaticity = np.stack(
        [
            log_r - log_sum / 3.0,
            log_g - log_sum / 3.0,
            log_b - log_sum / 3.0,
        ],
        axis=2,
    )

    # Normalize chromaticity for comparison
    chroma_norm = np.linalg.norm(log_chromaticity, axis=2)
    chroma_norm = (chroma_norm - chroma_norm.min()) / (chroma_norm.max() - chroma_norm.min() + 1e-8)

    # ========== Step 2: Compute shadow likelihood maps ==========

    # Brightness-based likelihood: darker regions are likely shadows
    brightness_threshold = np.percentile(brightness, config.brightness_percentile)
    brightness_likelihood = np.clip(
        (brightness_threshold - brightness) / (brightness_threshold + 1e-8),
        0,
        1,
    )

    # Local contrast: shadows are darker than their surroundings
    # Use morphological operations to estimate local brightness
    kernel_size = max(3, config.local_window_size - (config.local_window_size % 2))
    local_max = cv2.morphologyEx(
        (brightness * 255).astype(np.uint8),
        cv2.MORPH_DILATE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)),
    )
    local_contrast = 1.0 - (brightness * 255 / (local_max.astype(np.float32) + 1e-8))
    local_contrast = np.clip(local_contrast, 0, 1)

    # Combine: soft shadow map
    shadow_soft = brightness_likelihood * 0.6 + local_contrast * 0.4

    # ========== Step 3: Morphological cleanup ==========

    # Convert soft map to uint8 for morphology operations
    shadow_uint8 = (shadow_soft * 255).astype(np.uint8)

    # Opening: remove small noise
    open_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (config.morph_open_size, config.morph_open_size),
    )
    shadow_opened = cv2.morphologyEx(shadow_uint8, cv2.MORPH_OPEN, open_kernel, iterations=1)

    # Closing: fill holes
    close_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (config.morph_close_size, config.morph_close_size),
    )
    shadow_closed = cv2.morphologyEx(shadow_opened, cv2.MORPH_CLOSE, close_kernel, iterations=1)

    # ========== Step 4: Binary mask via adaptive threshold ==========

    # Use Otsu's method for automatic threshold selection
    _, shadow_mask = cv2.threshold(shadow_closed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Filter by area: remove shadows smaller than threshold
    min_area = int(height * width * config.min_shadow_area_fraction)
    contours, _ = cv2.findContours(shadow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    filtered_mask = np.zeros_like(shadow_mask)
    for contour in contours:
        if cv2.contourArea(contour) >= min_area:
            cv2.drawContours(filtered_mask, [contour], 0, 255, -1)

    shadow_mask = filtered_mask

    # ========== Return results ==========

    return {
        "shadow_soft": shadow_soft.astype(np.float32),
        "shadow_mask": shadow_mask.astype(np.uint8),
        "debug": {
            "brightness": brightness.astype(np.float32),
            "chroma_norm": chroma_norm.astype(np.float32),
            "local_contrast": local_contrast.astype(np.float32),
            "brightness_likelihood": brightness_likelihood.astype(np.float32),
            "contrast_likelihood": (local_contrast * 255).astype(np.uint8),
            "threshold_used": float(brightness_threshold),
            "config": {
                "brightness_percentile": config.brightness_percentile,
                "local_window_size": config.local_window_size,
                "morph_open_size": config.morph_open_size,
                "morph_close_size": config.morph_close_size,
            },
        },
    }
