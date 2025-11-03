"""
Visual DNA Extractor - Extracts fundamental visual characteristics from UI designs.

This module analyzes reference images to extract the "visual DNA" - the core design
patterns, relationships, and rules that define a design's aesthetic.
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json

import cv2
import numpy as np
from sklearn.cluster import KMeans
from scipy import stats
from collections import Counter


class VisualDNAExtractor:
    """
    Extracts the fundamental visual characteristics that define a design's aesthetic.

    The Visual DNA represents the "why" behind design choices, not just the "what".
    It captures patterns, relationships, and rules that can be used to generate
    new components in the same style.
    """

    def __init__(self):
        """Initialize the Visual DNA extractor."""
        self.scales = [1.0, 0.5, 0.25]  # Multi-scale analysis

    def extract_visual_dna(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract complete visual DNA from an image.

        Args:
            image: Input image as numpy array (RGB)

        Returns:
            Complete visual DNA profile
        """
        print("Extracting Visual DNA...")

        visual_dna = {
            'color_genome': self.extract_color_relationships(image),
            'shape_language': self.extract_shape_patterns(image),
            'texture_signature': self.extract_texture_qualities(image),
            'spatial_rhythm': self.extract_spacing_patterns(image),
            'visual_weight': self.extract_balance_distribution(image),
            'elevation_model': self.extract_depth_patterns(image),
            'corner_style': self.extract_corner_patterns(image),
        }

        # Extract design rules from patterns
        visual_dna['design_rules'] = self.extract_design_rules(visual_dna)

        return visual_dna

    def extract_color_relationships(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract color palette and usage patterns.

        Not just extracting colors, but understanding how they're used together.
        """
        print("  - Analyzing color relationships...")

        # Extract dominant colors
        pixels = image.reshape(-1, 3)
        kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
        kmeans.fit(pixels)

        colors = kmeans.cluster_centers_.astype(int)
        counts = np.bincount(kmeans.labels_)
        percentages = (counts / len(kmeans.labels_)) * 100

        # Sort by prominence
        sorted_indices = np.argsort(percentages)[::-1]
        colors = colors[sorted_indices]
        percentages = percentages[sorted_indices]

        # Analyze color relationships
        palette = []
        for i, (color, pct) in enumerate(zip(colors, percentages)):
            rgb = tuple(map(int, color))
            hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

            # Classify color role based on usage and properties
            role = self._classify_color_role(rgb, pct, i)

            palette.append({
                'rgb': rgb,
                'hex': hex_color,
                'percentage': float(pct),
                'role': role,
                'luminance': self._calculate_luminance(rgb)
            })

        # Detect gradient patterns
        gradients = self._detect_gradient_patterns(image)

        # Calculate color harmony type
        harmony = self._detect_color_harmony(palette)

        return {
            'palette': palette,
            'primary_color': palette[0]['hex'] if palette else '#000000',
            'secondary_color': palette[1]['hex'] if len(palette) > 1 else '#666666',
            'accent_color': self._find_accent_color(palette),
            'gradients': gradients,
            'harmony_type': harmony,
            'saturation_level': self._calculate_avg_saturation(colors)
        }

    def extract_shape_patterns(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze geometric patterns and shape language.
        """
        print("  - Detecting shape patterns...")

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        shapes = []
        aspect_ratios = []

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 100:
                continue

            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
            x, y, w, h = cv2.boundingRect(approx)

            aspect_ratio = float(w) / h if h > 0 else 1.0
            aspect_ratios.append(aspect_ratio)

            # Calculate circularity
            circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0

            shapes.append({
                'vertices': len(approx),
                'area': float(area),
                'aspect_ratio': aspect_ratio,
                'circularity': float(circularity),
                'bbox': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)}
            })

        # Determine dominant shape language
        if aspect_ratios:
            avg_aspect_ratio = np.mean(aspect_ratios)
            if avg_aspect_ratio > 1.5:
                shape_preference = "horizontal"
            elif avg_aspect_ratio < 0.66:
                shape_preference = "vertical"
            else:
                shape_preference = "balanced"
        else:
            shape_preference = "unknown"

        return {
            'total_shapes': len(shapes),
            'shapes': shapes[:20],  # Limit to top 20
            'dominant_aspect_ratio': float(np.mean(aspect_ratios)) if aspect_ratios else 1.0,
            'shape_preference': shape_preference,
            'geometric_style': self._classify_geometric_style(shapes)
        }

    def extract_texture_qualities(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze surface texture and material properties.
        """
        print("  - Analyzing texture qualities...")

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Calculate texture using Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Calculate gradient magnitude
        gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(gx**2 + gy**2).mean()

        # Classify texture type
        if laplacian_var < 100:
            texture_type = "flat"
        elif laplacian_var < 500:
            texture_type = "subtle"
        elif laplacian_var < 1000:
            texture_type = "moderate"
        else:
            texture_type = "textured"

        # Detect noise/grain
        noise_level = self._estimate_noise_level(gray)

        return {
            'texture_variance': float(laplacian_var),
            'gradient_strength': float(gradient_magnitude),
            'texture_type': texture_type,
            'noise_level': noise_level,
            'surface_finish': self._classify_surface_finish(laplacian_var, noise_level)
        }

    def extract_spacing_patterns(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze spacing, rhythm, and grid patterns.
        """
        print("  - Extracting spacing patterns...")

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # Analyze horizontal and vertical spacing
        h_profile = np.sum(edges, axis=1)
        v_profile = np.sum(edges, axis=0)

        h_gaps = self._detect_gaps(h_profile)
        v_gaps = self._detect_gaps(v_profile)

        # Estimate base spacing unit (likely 4px or 8px)
        all_gaps = h_gaps + v_gaps
        base_unit = self._estimate_base_unit(all_gaps)

        return {
            'base_unit': base_unit,
            'horizontal_gaps': h_gaps[:10],
            'vertical_gaps': v_gaps[:10],
            'avg_horizontal_spacing': float(np.mean(h_gaps)) if h_gaps else None,
            'avg_vertical_spacing': float(np.mean(v_gaps)) if v_gaps else None,
            'grid_type': self._detect_grid_type(h_gaps, v_gaps, base_unit)
        }

    def extract_balance_distribution(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze visual weight and balance.
        """
        print("  - Calculating visual weight distribution...")

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        h, w = gray.shape

        # Calculate center of mass
        y_coords, x_coords = np.mgrid[0:h, 0:w]
        total_intensity = gray.sum()

        if total_intensity > 0:
            center_x = (gray * x_coords).sum() / total_intensity
            center_y = (gray * y_coords).sum() / total_intensity
        else:
            center_x, center_y = w / 2, h / 2

        # Calculate weight distribution in quadrants
        mid_x, mid_y = w // 2, h // 2
        quadrants = {
            'top_left': gray[:mid_y, :mid_x].sum(),
            'top_right': gray[:mid_y, mid_x:].sum(),
            'bottom_left': gray[mid_y:, :mid_x].sum(),
            'bottom_right': gray[mid_y:, mid_x:].sum()
        }

        # Normalize
        total = sum(quadrants.values())
        if total > 0:
            quadrants = {k: float(v / total) for k, v in quadrants.items()}

        # Determine balance type
        balance_type = self._classify_balance(quadrants, center_x / w, center_y / h)

        return {
            'center_of_mass': {'x': float(center_x / w), 'y': float(center_y / h)},
            'quadrant_weights': quadrants,
            'balance_type': balance_type
        }

    def extract_depth_patterns(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze depth, elevation, and shadow patterns.
        """
        print("  - Analyzing depth and elevation...")

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Detect shadows using dark regions
        _, dark_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        shadow_percentage = (np.sum(dark_mask) / (dark_mask.size * 255)) * 100

        # Estimate blur/depth of field
        blur_estimate = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Classify elevation style
        if shadow_percentage < 2:
            elevation_style = "flat"
        elif shadow_percentage < 8:
            elevation_style = "subtle"
        elif shadow_percentage < 15:
            elevation_style = "moderate"
        else:
            elevation_style = "dramatic"

        return {
            'shadow_coverage': float(shadow_percentage),
            'elevation_style': elevation_style,
            'blur_estimate': float(blur_estimate),
            'depth_layers': self._estimate_depth_layers(shadow_percentage)
        }

    def extract_corner_patterns(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze corner radius and rounding patterns.
        """
        print("  - Detecting corner patterns...")

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # Detect corners
        corners = cv2.goodFeaturesToTrack(
            edges, maxCorners=100, qualityLevel=0.01, minDistance=10
        )

        if corners is None or len(corners) == 0:
            return {
                'corner_style': 'unknown',
                'estimated_radius': 0,
                'corner_count': 0
            }

        # Analyze corner sharpness
        sharpness_scores = []
        for corner in corners:
            x, y = corner.ravel().astype(int)
            if 5 < x < edges.shape[1] - 5 and 5 < y < edges.shape[0] - 5:
                region = edges[y-5:y+5, x-5:x+5]
                sharpness = np.sum(region) / region.size
                sharpness_scores.append(sharpness)

        if not sharpness_scores:
            avg_sharpness = 0
        else:
            avg_sharpness = np.mean(sharpness_scores)

        # Classify corner style and estimate radius
        if avg_sharpness > 0.5:
            style, radius = "sharp", 0
        elif avg_sharpness > 0.3:
            style, radius = "slightly_rounded", 4
        elif avg_sharpness > 0.15:
            style, radius = "rounded", 8
        else:
            style, radius = "heavily_rounded", 16

        return {
            'corner_style': style,
            'estimated_radius': radius,
            'corner_count': len(corners),
            'avg_sharpness': float(avg_sharpness)
        }

    def extract_design_rules(self, visual_dna: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract actionable design rules from visual DNA patterns.
        """
        print("  - Formulating design rules...")

        rules = {
            'color_rules': {
                'primary': visual_dna['color_genome']['primary_color'],
                'secondary': visual_dna['color_genome']['secondary_color'],
                'accent': visual_dna['color_genome']['accent_color'],
                'use_gradients': len(visual_dna['color_genome']['gradients']) > 0
            },
            'spacing_rules': {
                'base_unit': visual_dna['spatial_rhythm']['base_unit'],
                'grid_type': visual_dna['spatial_rhythm']['grid_type']
            },
            'shape_rules': {
                'corner_radius': visual_dna['corner_style']['estimated_radius'],
                'aspect_preference': visual_dna['shape_language']['shape_preference'],
                'geometric_style': visual_dna['shape_language']['geometric_style']
            },
            'elevation_rules': {
                'style': visual_dna['elevation_model']['elevation_style'],
                'use_shadows': visual_dna['elevation_model']['shadow_coverage'] > 5
            },
            'texture_rules': {
                'surface_finish': visual_dna['texture_signature']['surface_finish'],
                'add_noise': visual_dna['texture_signature']['noise_level'] > 0.1
            }
        }

        return rules

    # Helper methods

    def _classify_color_role(self, rgb: Tuple[int, int, int], percentage: float, index: int) -> str:
        """Classify the role of a color in the design."""
        luminance = self._calculate_luminance(rgb)

        if percentage > 40:
            return "background"
        elif luminance < 50 and percentage > 10:
            return "text"
        elif index == 0 and percentage < 40:
            return "primary"
        elif index == 1:
            return "secondary"
        else:
            return "accent"

    def _calculate_luminance(self, rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance of a color."""
        r, g, b = [x / 255.0 for x in rgb]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def _find_accent_color(self, palette: List[Dict]) -> str:
        """Find the most suitable accent color."""
        for color in palette:
            if color['role'] == 'accent':
                return color['hex']
        # Fallback to third color or primary
        return palette[2]['hex'] if len(palette) > 2 else palette[0]['hex']

    def _detect_gradient_patterns(self, image: np.ndarray) -> List[Dict]:
        """Detect gradient usage in the image."""
        # Simplified gradient detection
        h, w = image.shape[:2]

        gradients = []

        # Check for horizontal gradients
        left_avg = np.mean(image[:, :w//4], axis=(0, 1))
        right_avg = np.mean(image[:, 3*w//4:], axis=(0, 1))
        h_diff = np.linalg.norm(left_avg - right_avg)

        if h_diff > 30:
            gradients.append({
                'type': 'horizontal',
                'strength': float(h_diff),
                'direction': 'left-to-right'
            })

        # Check for vertical gradients
        top_avg = np.mean(image[:h//4, :], axis=(0, 1))
        bottom_avg = np.mean(image[3*h//4:, :], axis=(0, 1))
        v_diff = np.linalg.norm(top_avg - bottom_avg)

        if v_diff > 30:
            gradients.append({
                'type': 'vertical',
                'strength': float(v_diff),
                'direction': 'top-to-bottom'
            })

        return gradients

    def _detect_color_harmony(self, palette: List[Dict]) -> str:
        """Detect the type of color harmony used."""
        if len(palette) < 2:
            return "monochromatic"

        # Simplified harmony detection based on saturation
        saturations = []
        for color in palette[:3]:
            rgb = color['rgb']
            max_c = max(rgb)
            min_c = min(rgb)
            saturation = (max_c - min_c) / max_c if max_c > 0 else 0
            saturations.append(saturation)

        avg_saturation = np.mean(saturations)

        if avg_saturation < 0.1:
            return "monochromatic"
        elif avg_saturation < 0.3:
            return "analogous"
        else:
            return "complementary"

    def _calculate_avg_saturation(self, colors: np.ndarray) -> float:
        """Calculate average saturation of color palette."""
        saturations = []
        for color in colors:
            max_c = max(color)
            min_c = min(color)
            sat = (max_c - min_c) / max_c if max_c > 0 else 0
            saturations.append(sat)
        return float(np.mean(saturations))

    def _classify_geometric_style(self, shapes: List[Dict]) -> str:
        """Classify the overall geometric style."""
        if not shapes:
            return "unknown"

        circularities = [s['circularity'] for s in shapes]
        avg_circularity = np.mean(circularities)

        if avg_circularity > 0.8:
            return "organic"
        elif avg_circularity > 0.5:
            return "soft_geometric"
        else:
            return "geometric"

    def _estimate_noise_level(self, gray: np.ndarray) -> float:
        """Estimate noise/grain level in image."""
        # Use high-pass filter to estimate noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = cv2.absdiff(gray, blurred)
        return float(noise.mean() / 255.0)

    def _classify_surface_finish(self, texture_var: float, noise_level: float) -> str:
        """Classify surface finish type."""
        if texture_var < 100 and noise_level < 0.05:
            return "matte_flat"
        elif texture_var < 100 and noise_level >= 0.05:
            return "matte_textured"
        elif texture_var < 500:
            return "subtle_gloss"
        else:
            return "glossy"

    def _detect_gaps(self, profile: np.ndarray) -> List[int]:
        """Detect spacing gaps in a 1D profile."""
        if len(profile) == 0:
            return []

        mean_val = np.mean(profile)
        threshold = mean_val * 0.1

        gaps = []
        in_gap = False
        gap_start = 0

        for i, val in enumerate(profile):
            if val < threshold and not in_gap:
                in_gap = True
                gap_start = i
            elif val >= threshold and in_gap:
                gap_size = i - gap_start
                if gap_size > 2:
                    gaps.append(gap_size)
                in_gap = False

        return gaps

    def _estimate_base_unit(self, gaps: List[int]) -> int:
        """Estimate the base spacing unit (typically 4px or 8px)."""
        if not gaps or len(gaps) < 2:
            return 8  # Default

        # Common UI base units
        common_units = [4, 8, 16]

        # Find which unit most gaps are multiples of
        best_unit = 8
        best_score = 0

        for unit in common_units:
            score = sum(1 for gap in gaps[:10] if abs(gap % unit) <= 2)
            if score > best_score:
                best_score = score
                best_unit = unit

        return best_unit

    def _detect_grid_type(self, h_gaps: List[int], v_gaps: List[int], base_unit: int) -> str:
        """Detect the type of grid system used."""
        if not h_gaps and not v_gaps:
            return "free_form"

        # Check if gaps are regular
        if h_gaps:
            h_std = np.std(h_gaps) if len(h_gaps) > 1 else 0
            h_regular = h_std < base_unit * 2
        else:
            h_regular = False

        if v_gaps:
            v_std = np.std(v_gaps) if len(v_gaps) > 1 else 0
            v_regular = v_std < base_unit * 2
        else:
            v_regular = False

        if h_regular and v_regular:
            return "strict_grid"
        elif h_regular or v_regular:
            return "flexible_grid"
        else:
            return "free_form"

    def _classify_balance(self, quadrants: Dict[str, float], cx: float, cy: float) -> str:
        """Classify the type of visual balance."""
        # Check if center of mass is near center
        center_tolerance = 0.1
        is_centered = abs(cx - 0.5) < center_tolerance and abs(cy - 0.5) < center_tolerance

        # Check quadrant symmetry
        left_weight = quadrants['top_left'] + quadrants['bottom_left']
        right_weight = quadrants['top_right'] + quadrants['bottom_right']
        weight_diff = abs(left_weight - right_weight)

        if is_centered and weight_diff < 0.1:
            return "symmetric"
        elif weight_diff < 0.2:
            return "asymmetric_balanced"
        else:
            return "asymmetric"

    def _estimate_depth_layers(self, shadow_coverage: float) -> int:
        """Estimate number of elevation layers."""
        if shadow_coverage < 2:
            return 1
        elif shadow_coverage < 8:
            return 2
        elif shadow_coverage < 15:
            return 3
        else:
            return 4
