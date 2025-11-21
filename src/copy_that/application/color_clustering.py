"""
K-means and advanced color clustering for palette extraction.

Implements:
- K-means clustering (simple, fast)
- Adaptive k-selection
- Perceptual color distance in LAB space
- Cluster prominence calculation
"""

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class ColorClusterResult:
    """Result of color clustering"""
    hex_color: str
    rgb: tuple[int, int, int]
    center_lab: tuple[float, float, float]
    pixel_count: int
    prominence_percentage: float
    cluster_id: int
    confidence: float


class ColorKMeansClustering:
    """K-means clustering for color palette extraction"""

    def __init__(
        self,
        k: int = 12,
        max_iterations: int = 100,
        epsilon: float = 0.1,
        filter_background: bool = True,
        resize_for_speed: bool = True
    ):
        """Initialize K-means color clusterer

        Args:
            k: Number of color clusters to extract
            max_iterations: Max iterations for K-means
            epsilon: Convergence threshold
            filter_background: Filter out very dark/light pixels
            resize_for_speed: Resize image for faster processing
        """
        self.k = k
        self.max_iterations = max_iterations
        self.epsilon = epsilon
        self.filter_background = filter_background
        self.resize_for_speed = resize_for_speed

    def extract_palette(self, image: np.ndarray) -> list[ColorClusterResult]:
        """Extract color palette from image using K-means

        Args:
            image: RGB image array

        Returns:
            List of ColorClusterResult sorted by prominence
        """
        # Ensure RGB format
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Convert to RGB if needed
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)

        # Resize for speed if requested
        if self.resize_for_speed:
            image = cv2.resize(image, (256, 256), interpolation=cv2.INTER_AREA)

        # Prepare data for K-means
        pixel_data = image.reshape(-1, 3).astype(np.float32)

        # Filter background if requested
        if self.filter_background:
            pixel_data = self._filter_background_pixels(pixel_data)

        # If too few pixels after filtering, skip filtering
        if len(pixel_data) < self.k * 10:
            pixel_data = image.reshape(-1, 3).astype(np.float32)

        # K-means clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
                   self.max_iterations, self.epsilon)
        _, labels, centers = cv2.kmeans(
            pixel_data, self.k, None, criteria, 10, cv2.KMEANS_PP_CENTERS
        )

        # Calculate cluster statistics
        clusters = []
        total_pixels = len(pixel_data)

        for cluster_id in range(self.k):
            cluster_pixels = pixel_data[labels.flatten() == cluster_id]
            if len(cluster_pixels) == 0:
                continue

            # Center color in RGB
            center_rgb = centers[cluster_id].astype(np.uint8)
            hex_color = self._rgb_to_hex(tuple(center_rgb))

            # Convert to LAB for perceptual analysis
            center_bgr = cv2.cvtColor(
                np.uint8([[center_rgb]]), cv2.COLOR_RGB2BGR
            )
            center_lab = cv2.cvtColor(center_bgr, cv2.COLOR_BGR2LAB)[0, 0]

            # Calculate prominence
            pixel_count = len(cluster_pixels)
            prominence_pct = (pixel_count / total_pixels) * 100

            result = ColorClusterResult(
                hex_color=hex_color,
                rgb=tuple(center_rgb),
                center_lab=tuple(center_lab.astype(float)),
                pixel_count=pixel_count,
                prominence_percentage=prominence_pct,
                cluster_id=cluster_id,
                confidence=0.9  # K-means inherently has high confidence
            )
            clusters.append(result)

        # Sort by prominence (pixel count)
        clusters.sort(key=lambda c: c.prominence_percentage, reverse=True)

        return clusters[:self.k]

    def _filter_background_pixels(self, pixels: np.ndarray) -> np.ndarray:
        """Remove very dark and light pixels (likely backgrounds)"""
        # Calculate brightness (mean of RGB channels)
        brightness = pixels.mean(axis=1)

        # Keep pixels with moderate brightness (avoid pure white/black backgrounds)
        mask = (brightness >= 20) & (brightness <= 235)

        # If filtering removes too many pixels, be more lenient
        if mask.sum() < len(pixels) * 0.1:
            mask = brightness >= 5

        return pixels[mask]

    @staticmethod
    def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color"""
        return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class AdaptiveColorKMeans(ColorKMeansClustering):
    """K-means with adaptive k selection based on image content"""

    def __init__(self, min_k: int = 5, max_k: int = 20, **kwargs):
        """Initialize adaptive K-means

        Args:
            min_k: Minimum number of clusters
            max_k: Maximum number of clusters
            **kwargs: Additional arguments for ColorKMeansClustering
        """
        super().__init__(**kwargs)
        self.min_k = min_k
        self.max_k = max_k

    def extract_palette_adaptive(self, image: np.ndarray) -> list[ColorClusterResult]:
        """Extract palette with automatically determined k

        Uses elbow method to find optimal k:
        - Lower k: Fewer distinct colors, less detail
        - Higher k: More distinct colors, more detail
        - Optimal k: Where adding more clusters provides diminishing returns
        """
        # Resize for analysis
        if self.resize_for_speed:
            analysis_image = cv2.resize(image, (128, 128), interpolation=cv2.INTER_AREA)
        else:
            analysis_image = image

        pixel_data = analysis_image.reshape(-1, 3).astype(np.float32)

        # Elbow method: find where additional clusters provide diminishing returns
        inertias = []
        k_values = range(self.min_k, self.max_k + 1)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.1)

        for k in k_values:
            _, _, centers = cv2.kmeans(pixel_data, k, None, criteria, 3, cv2.KMEANS_PP_CENTERS)
            # Calculate inertia (sum of squared distances from each point to its center)
            distances = np.min(
                cv2.norm(pixel_data[:, np.newaxis] - centers, axis=2, norm=cv2.NORM_L2),
                axis=1
            )
            inertia = np.sum(distances ** 2)
            inertias.append(inertia)

        # Find elbow point (where second derivative is highest)
        second_derivative = np.diff(np.diff(inertias))
        if len(second_derivative) > 0:
            elbow_idx = np.argmax(second_derivative) + self.min_k + 1
            optimal_k = min(elbow_idx, self.max_k)
        else:
            optimal_k = self.min_k

        # Set k and extract palette
        self.k = optimal_k
        return self.extract_palette(image)


def calculate_kmeans_histogram(
    image: np.ndarray,
    clusters: list[ColorClusterResult],
    normalize: bool = True
) -> dict[str, float]:
    """Calculate histogram of color distribution

    Args:
        image: Original image
        clusters: Clustering results
        normalize: Normalize to percentages

    Returns:
        Dictionary mapping hex colors to percentage of image
    """
    histogram = {}

    for cluster in clusters:
        if normalize:
            histogram[cluster.hex_color] = cluster.prominence_percentage
        else:
            histogram[cluster.hex_color] = cluster.pixel_count

    return histogram
