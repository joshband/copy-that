"""
Visualization utilities for shadow analysis debugging and inspection.

Provides tools to visually inspect shadow extraction results,
including multi-panel compositions showing original, masks, and derived maps.
"""

import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def visualize_shadow_analysis(
    image_bgr: np.ndarray,
    analysis: dict,
    show: bool = False,
    save_path: str | None = None,
) -> np.ndarray:
    """
    Create a multi-panel visualization of shadow analysis results.

    Args:
        image_bgr: Original image (H×W×3, uint8)
        analysis: Dictionary from analyze_image_for_shadows() or similar
        show: If True, display the visualization (requires display)
        save_path: If provided, save visualization to this path

    Returns:
        Composed visualization image (H×W×3, uint8)

    Panels included:
        - Original image
        - Soft shadow map (heatmap)
        - Binary shadow mask overlay
        - Shading map (if available)
        - Depth map (if available)
        - Information text overlay

    Example:
        >>> result = analyze_image_for_shadows(image)
        >>> vis = visualize_shadow_analysis(image, result)
        >>> cv2.imwrite("shadow_analysis.png", vis)
    """
    height, width = image_bgr.shape[:2]

    # Extract components
    shadow_soft = analysis.get("shadow_soft", np.zeros((height, width)))
    shadow_mask = analysis.get("shadow_mask", np.zeros((height, width), dtype=np.uint8))
    depth = analysis.get("depth")
    shading = analysis.get("shading")
    features = analysis.get("features", {})
    tokens = analysis.get("tokens", {})

    # Determine layout: create 2-3 rows depending on available data
    panel_count = 3  # Original, soft, mask
    if shading is not None:
        panel_count += 1
    if depth is not None:
        panel_count += 1

    cols = 3
    rows = (panel_count + cols - 1) // cols
    panel_height = height
    panel_width = width

    # Create canvas
    canvas_height = rows * (panel_height + 30)  # +30 for labels
    canvas_width = cols * (panel_width + 2)
    canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255

    panel_idx = 0

    def _place_panel(img, title: str, idx: int):
        """Helper to place image panel and add title."""
        row = idx // cols
        col = idx % cols
        y_start = row * (panel_height + 30) + 30
        x_start = col * (panel_width + 2)

        # Ensure image is uint8
        if img.dtype != np.uint8:
            if img.ndim == 2:
                img_display = (np.clip(img, 0, 1) * 255).astype(np.uint8)
            else:
                img_display = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        else:
            img_display = img

        # Resize if needed
        if img_display.shape[:2] != (panel_height, panel_width):
            img_display = cv2.resize(img_display, (panel_width, panel_height))

        # Convert grayscale to BGR for consistent compositing
        if img_display.ndim == 2:
            img_display = cv2.cvtColor(img_display, cv2.COLOR_GRAY2BGR)

        canvas[
            y_start : y_start + panel_height,
            x_start : x_start + panel_width,
        ] = img_display

        # Add title
        cv2.putText(
            canvas,
            title,
            (x_start + 5, y_start - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
        )

    # Panel 1: Original
    _place_panel(image_bgr, "Original", panel_idx)
    panel_idx += 1

    # Panel 2: Soft shadow map (heatmap)
    shadow_soft_uint8 = (np.clip(shadow_soft, 0, 1) * 255).astype(np.uint8)
    shadow_heatmap = cv2.applyColorMap(shadow_soft_uint8, cv2.COLORMAP_JET)
    _place_panel(shadow_heatmap, "Soft Shadow (Heat)", panel_idx)
    panel_idx += 1

    # Panel 3: Mask overlay on original
    mask_overlay = image_bgr.copy().astype(np.float32)
    shadow_regions = shadow_mask > 127
    mask_overlay[shadow_regions] = mask_overlay[shadow_regions] * 0.5 + np.array([0, 0, 255]) * 0.5
    _place_panel(mask_overlay.astype(np.uint8), "Mask Overlay", panel_idx)
    panel_idx += 1

    # Panel 4: Shading (if available)
    if shading is not None:
        shading_display = (np.clip(shading, 0, 1) * 255).astype(np.uint8)
        _place_panel(shading_display, "Shading", panel_idx)
        panel_idx += 1

    # Panel 5: Depth (if available)
    if depth is not None:
        depth_display = (np.clip(depth, 0, 1) * 255).astype(np.uint8)
        depth_heatmap = cv2.applyColorMap(depth_display, cv2.COLORMAP_TURBO)
        _place_panel(depth_heatmap, "Depth Map", panel_idx)
        panel_idx += 1

    # Add text information at bottom
    info_y = canvas_height - 100
    text_lines = [
        f"Shadow Area: {features.get('shadow_area_fraction', 0):.1%}",
        f"Softness: {tokens.get('style_softness', 'unknown')}",
        f"Direction: {tokens.get('style_key_direction', 'unknown')}",
        f"Contrast: {tokens.get('style_contrast', 'unknown')}",
    ]

    for i, line in enumerate(text_lines):
        cv2.putText(
            canvas,
            line,
            (10, info_y + i * 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
        )

    # Save if requested
    if save_path:
        cv2.imwrite(save_path, canvas)
        logger.info(f"Saved visualization to {save_path}")

    # Show if requested
    if show:
        cv2.imshow("Shadow Analysis", canvas)
        cv2.waitKey(0)

    return canvas


def visualize_depth_map(
    depth: np.ndarray,
    colormap: int = cv2.COLORMAP_TURBO,
) -> np.ndarray:
    """
    Visualize a depth map as a colored image.

    Args:
        depth: Depth map (H×W float32, 0..1 or arbitrary range)
        colormap: OpenCV colormap ID

    Returns:
        Colored depth visualization (H×W×3 uint8)
    """
    # Normalize to 0..1 if needed
    depth_norm = depth.copy().astype(np.float32)
    if depth_norm.max() > 1.0:
        depth_norm = (depth_norm - depth_norm.min()) / (depth_norm.max() - depth_norm.min() + 1e-8)

    # Convert to uint8 and apply colormap
    depth_uint8 = (np.clip(depth_norm, 0, 1) * 255).astype(np.uint8)
    colored = cv2.applyColorMap(depth_uint8, colormap)

    return colored


def visualize_normals(normals: np.ndarray) -> np.ndarray:
    """
    Visualize surface normals as an RGB image.

    Converts unit normal vectors to RGB colors using the convention:
        RGB = (N + 1) / 2 * 255
    where N is in [-1, 1].

    Args:
        normals: Normal map (H×W×3 float32, unit vectors in [-1, 1])

    Returns:
        Colored normals visualization (H×W×3 uint8)
    """
    # Ensure normals are in [-1, 1]
    normals_clipped = np.clip(normals, -1, 1)

    # Convert to RGB
    rgb = (normals_clipped + 1) / 2 * 255
    rgb_uint8 = rgb.astype(np.uint8)

    # OpenCV uses BGR, so swap R and B channels from standard RGB
    bgr_uint8 = cv2.cvtColor(rgb_uint8, cv2.COLOR_RGB2BGR)

    return bgr_uint8


def create_shadow_comparison(
    image_original: np.ndarray,
    shadow_mask_cv: np.ndarray,
    shadow_mask_ai: np.ndarray | None = None,
    shadow_mask_deep: np.ndarray | None = None,
) -> np.ndarray:
    """
    Create a comparison visualization of different shadow detection methods.

    Args:
        image_original: Original image (H×W×3)
        shadow_mask_cv: CV-based detection (H×W uint8)
        shadow_mask_ai: Optional AI-based detection
        shadow_mask_deep: Optional deep learning-based detection

    Returns:
        Comparison visualization (H×W×3)
    """
    height, width = image_original.shape[:2]

    # Prepare masks (all should be binary)
    masks = {
        "CV": shadow_mask_cv,
        "AI": shadow_mask_ai,
        "Deep": shadow_mask_deep,
    }
    masks = {k: v for k, v in masks.items() if v is not None}

    panel_height = height
    panel_width = width
    num_panels = len(masks) + 1  # +1 for original
    canvas_width = panel_width * num_panels
    canvas_height = panel_height + 30

    canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255

    # Original
    canvas[30 : 30 + panel_height, 0 : 0 + panel_width] = image_original

    # Masks
    for i, (name, mask) in enumerate(masks.items(), 1):
        if mask is None:
            continue

        # Create overlay
        overlay = image_original.copy().astype(np.float32)
        mask_binary = mask > 127
        overlay[mask_binary] = overlay[mask_binary] * 0.5 + np.array([0, 0, 255]) * 0.5

        x_start = i * panel_width
        canvas[30 : 30 + panel_height, x_start : x_start + panel_width] = overlay.astype(np.uint8)

        # Add label
        cv2.putText(
            canvas,
            name,
            (x_start + 5, 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
        )

    return canvas
