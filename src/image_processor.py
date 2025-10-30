"""
Enhanced Image Processing with OpenAI Integration

This module provides advanced image processing capabilities that combine
traditional computer vision with OpenAI's Vision API for intelligent analysis.
"""

import os
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path
import json

import cv2
import numpy as np
from PIL import Image
from skimage import color, filters, feature, measure
from scipy import ndimage

from .openai_vision import OpenAIVisionAnalyzer


class EnhancedImageProcessor:
    """
    Advanced image processor combining CV algorithms with AI-powered analysis.
    """

    def __init__(self, use_openai: bool = True, api_key: Optional[str] = None):
        """
        Initialize the enhanced image processor.

        Args:
            use_openai: Whether to use OpenAI Vision for semantic analysis
            api_key: Optional OpenAI API key
        """
        self.use_openai = use_openai
        self.openai_analyzer = None

        if use_openai:
            try:
                self.openai_analyzer = OpenAIVisionAnalyzer(api_key=api_key)
            except ValueError as e:
                print(f"Warning: OpenAI Vision not available: {e}")
                self.use_openai = False

    def load_image(self, image_path: Union[str, Path]) -> np.ndarray:
        """
        Load image from file path.

        Args:
            image_path: Path to image file

        Returns:
            Image as numpy array (RGB)
        """
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def extract_color_palette(
        self,
        image: np.ndarray,
        n_colors: int = 8,
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Extract color palette using both CV and AI methods.

        Args:
            image: Input image
            n_colors: Number of dominant colors to extract
            use_ai: Whether to use AI for semantic color understanding

        Returns:
            Dictionary with CV-extracted and AI-analyzed colors
        """
        # Traditional CV approach
        pixels = image.reshape(-1, 3)
        from sklearn.cluster import KMeans

        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)

        colors = kmeans.cluster_centers_.astype(int)
        counts = np.bincount(kmeans.labels_)
        percentages = (counts / len(kmeans.labels_)) * 100

        cv_palette = [
            {
                "rgb": tuple(map(int, color)),
                "hex": f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}",
                "percentage": float(pct)
            }
            for color, pct in zip(colors, percentages)
        ]

        result = {"cv_palette": sorted(cv_palette, key=lambda x: x["percentage"], reverse=True)}

        # AI semantic understanding (if enabled)
        if use_ai and self.use_openai and self.openai_analyzer:
            # Save temp image for OpenAI
            temp_path = Path("/tmp/temp_image_analysis.png")
            Image.fromarray(image).save(temp_path)

            try:
                ai_analysis = self.openai_analyzer.extract_design_tokens(temp_path)
                result["ai_color_analysis"] = ai_analysis.get("colors", {})
            except Exception as e:
                print(f"Warning: AI color analysis failed: {e}")

            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()

        return result

    def detect_shapes(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Detect shapes and geometric patterns in the image.

        Args:
            image: Input image

        Returns:
            Dictionary with detected shapes and properties
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Edge detection
        edges = cv2.Canny(gray, 50, 150)

        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        shapes = []
        for contour in contours:
            # Filter small contours
            area = cv2.contourArea(contour)
            if area < 100:
                continue

            # Approximate shape
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)

            # Get bounding box
            x, y, w, h = cv2.boundingRect(approx)

            # Classify shape
            num_vertices = len(approx)
            if num_vertices == 3:
                shape_type = "triangle"
            elif num_vertices == 4:
                aspect_ratio = float(w) / h
                shape_type = "square" if 0.95 <= aspect_ratio <= 1.05 else "rectangle"
            elif num_vertices > 8:
                shape_type = "circle"
            else:
                shape_type = f"polygon-{num_vertices}"

            shapes.append({
                "type": shape_type,
                "vertices": num_vertices,
                "area": float(area),
                "bbox": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                "aspect_ratio": float(w) / h if h > 0 else 0
            })

        return {
            "total_shapes": len(shapes),
            "shapes": shapes,
            "shape_distribution": self._count_shape_types(shapes)
        }

    def _count_shape_types(self, shapes: List[Dict]) -> Dict[str, int]:
        """Count occurrences of each shape type."""
        distribution = {}
        for shape in shapes:
            shape_type = shape["type"]
            distribution[shape_type] = distribution.get(shape_type, 0) + 1
        return distribution

    def analyze_spacing(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze spacing and layout rhythm in the image.

        Args:
            image: Input image

        Returns:
            Dictionary with spacing analysis
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Detect edges
        edges = feature.canny(gray, sigma=2)

        # Find horizontal and vertical spacing patterns
        horizontal_profile = np.sum(edges, axis=1)
        vertical_profile = np.sum(edges, axis=0)

        # Detect gaps (spacing)
        h_gaps = self._detect_gaps(horizontal_profile)
        v_gaps = self._detect_gaps(vertical_profile)

        # Estimate base spacing unit
        if h_gaps or v_gaps:
            all_gaps = h_gaps + v_gaps
            gaps_sorted = sorted(all_gaps)
            base_unit = self._find_base_unit(gaps_sorted)
        else:
            base_unit = None

        return {
            "horizontal_gaps": h_gaps,
            "vertical_gaps": v_gaps,
            "estimated_base_unit": base_unit,
            "avg_horizontal_spacing": float(np.mean(h_gaps)) if h_gaps else None,
            "avg_vertical_spacing": float(np.mean(v_gaps)) if v_gaps else None
        }

    def _detect_gaps(self, profile: np.ndarray, threshold: float = 0.1) -> List[int]:
        """Detect gaps in a 1D profile."""
        mean_val = np.mean(profile)
        threshold_val = mean_val * threshold

        gaps = []
        in_gap = False
        gap_start = 0

        for i, val in enumerate(profile):
            if val < threshold_val and not in_gap:
                in_gap = True
                gap_start = i
            elif val >= threshold_val and in_gap:
                in_gap = False
                gap_size = i - gap_start
                if gap_size > 2:  # Filter very small gaps
                    gaps.append(gap_size)

        return gaps

    def _find_base_unit(self, gaps: List[int]) -> Optional[int]:
        """Find the base spacing unit from gap sizes."""
        if not gaps or len(gaps) < 2:
            return None

        # Use GCD-like approach
        from math import gcd
        from functools import reduce

        # Common multiples likely indicate base unit
        common_divisors = [4, 8, 16]  # Common UI base units
        for divisor in common_divisors:
            if all(gap % divisor == 0 or abs(gap % divisor) <= 2 for gap in gaps[:5]):
                return divisor

        return min(gaps[:3]) if gaps else None

    def detect_corner_radius(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Detect corner radius patterns in UI elements.

        Args:
            image: Input image

        Returns:
            Dictionary with corner radius analysis
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # Detect corners
        corners = cv2.goodFeaturesToTrack(
            edges,
            maxCorners=100,
            qualityLevel=0.01,
            minDistance=10
        )

        if corners is None:
            return {"corner_style": "unknown", "detected_corners": 0}

        # Analyze corner sharpness
        # Sharp corners will have higher curvature
        radii = []
        for corner in corners:
            x, y = corner.ravel()
            x, y = int(x), int(y)

            # Sample region around corner
            if 5 < x < edges.shape[1] - 5 and 5 < y < edges.shape[0] - 5:
                region = edges[y-5:y+5, x-5:x+5]
                edge_density = np.sum(region) / region.size
                radii.append(edge_density)

        if not radii:
            return {"corner_style": "unknown", "detected_corners": 0}

        avg_sharpness = np.mean(radii)

        # Classify corner style
        if avg_sharpness > 0.5:
            style = "sharp"
            estimated_radius = 0
        elif avg_sharpness > 0.3:
            style = "slightly_rounded"
            estimated_radius = 4
        elif avg_sharpness > 0.15:
            style = "rounded"
            estimated_radius = 8
        else:
            style = "heavily_rounded"
            estimated_radius = 16

        return {
            "corner_style": style,
            "estimated_radius_px": estimated_radius,
            "detected_corners": len(corners),
            "avg_sharpness": float(avg_sharpness)
        }

    def comprehensive_analysis(
        self,
        image_path: Union[str, Path],
        include_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Run comprehensive image analysis combining CV and AI.

        Args:
            image_path: Path to image file
            include_ai: Whether to include AI-powered analysis

        Returns:
            Complete analysis results
        """
        print(f"Analyzing image: {image_path}")

        # Load image
        image = self.load_image(image_path)

        results = {
            "image_info": {
                "path": str(image_path),
                "dimensions": {"width": image.shape[1], "height": image.shape[0]},
                "channels": image.shape[2] if len(image.shape) > 2 else 1
            }
        }

        # CV-based analysis
        print("  - Extracting color palette...")
        results["colors"] = self.extract_color_palette(image, use_ai=False)

        print("  - Detecting shapes...")
        results["shapes"] = self.detect_shapes(image)

        print("  - Analyzing spacing...")
        results["spacing"] = self.analyze_spacing(image)

        print("  - Detecting corner styles...")
        results["corners"] = self.detect_corner_radius(image)

        # AI-powered semantic analysis
        if include_ai and self.use_openai and self.openai_analyzer:
            print("  - Running OpenAI Vision analysis...")
            try:
                ai_results = self.openai_analyzer.comprehensive_analysis(image_path)
                results["ai_analysis"] = ai_results
            except Exception as e:
                print(f"    Warning: AI analysis failed: {e}")
                results["ai_analysis"] = {"error": str(e)}

        return results

    def export_results(
        self,
        results: Dict[str, Any],
        output_path: Union[str, Path]
    ) -> None:
        """
        Export analysis results to JSON file.

        Args:
            results: Analysis results dictionary
            output_path: Path to output JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Results exported to: {output_path}")


# Convenience function
def analyze_image(
    image_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    use_openai: bool = True
) -> Dict[str, Any]:
    """
    Convenience function for quick image analysis.

    Args:
        image_path: Path to image file
        output_path: Optional path to save results JSON
        use_openai: Whether to use OpenAI Vision

    Returns:
        Analysis results
    """
    processor = EnhancedImageProcessor(use_openai=use_openai)
    results = processor.comprehensive_analysis(image_path, include_ai=use_openai)

    if output_path:
        processor.export_results(results, output_path)

    return results
