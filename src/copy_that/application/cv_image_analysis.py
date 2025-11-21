"""
OpenCV-based image analysis for color extraction.

Provides:
- Histogram analysis
- Color distribution
- Spatial color mapping
- Edge detection for color segmentation
- Histogram equalization
"""


import cv2
import numpy as np


class OpenCVImageAnalysis:
    """OpenCV-based image analysis for color properties"""

    @staticmethod
    def calculate_histogram(image: np.ndarray, bins: int = 256) -> dict[str, np.ndarray]:
        """Calculate color channel histograms

        Args:
            image: RGB image
            bins: Number of histogram bins

        Returns:
            Dictionary with 'r', 'g', 'b', 'h' (hue) histograms
        """
        # Ensure RGB
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)

        histograms = {}

        # RGB histograms
        for i, channel in enumerate(['r', 'g', 'b']):
            hist = cv2.calcHist([image], [i], None, [bins], [0, 256])
            # Normalize
            hist = cv2.normalize(hist, hist).flatten()
            histograms[channel] = hist

        # HSV hue histogram
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        hist_h = cv2.normalize(hist_h, hist_h).flatten()
        histograms['h'] = hist_h

        return histograms

    @staticmethod
    def get_color_distribution(image: np.ndarray) -> dict[str, float]:
        """Get distribution of colors across image

        Returns percentage of image in different hue ranges
        """
        # Convert to HSV
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        if image.shape[2] != 3:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        hue = hsv[:, :, 0]

        # Define hue ranges
        hue_ranges = {
            'red': (0, 30) + (150, 180),  # Red wraps around
            'orange': (11, 25),
            'yellow': (26, 34),
            'green': (35, 77),
            'cyan': (78, 99),
            'blue': (100, 124),
            'magenta': (125, 160),
            'pink': (161, 179),
        }

        distribution = {}
        total_pixels = hue.size

        for hue_name, hue_range in hue_ranges.items():
            if isinstance(hue_range, tuple) and len(hue_range) == 4:
                # Range wraps around (e.g., red)
                mask = (hue >= hue_range[0]) | (hue >= hue_range[2]) & (hue <= hue_range[3])
            else:
                mask = (hue >= hue_range[0]) & (hue <= hue_range[1])

            pixels_in_range = np.sum(mask)
            distribution[hue_name] = (pixels_in_range / total_pixels) * 100

        return distribution

    @staticmethod
    def detect_edges(image: np.ndarray, method: str = 'canny') -> np.ndarray:
        """Detect edges in image for color segmentation

        Args:
            image: Input image
            method: 'canny' or 'sobel'

        Returns:
            Edge map
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        if method == 'canny':
            edges = cv2.Canny(gray, 100, 200)
        elif method == 'sobel':
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            edges = np.sqrt(sobelx**2 + sobely**2).astype(np.uint8)
        else:
            raise ValueError(f"Unknown edge detection method: {method}")

        return edges

    @staticmethod
    def color_quantization(image: np.ndarray, levels: int = 8) -> np.ndarray:
        """Quantize image to fewer color levels

        Useful for simplifying color palettes

        Args:
            image: Input image
            levels: Number of quantization levels per channel

        Returns:
            Quantized image
        """
        # Quantize each channel
        quantized = image.copy().astype(np.float32)

        step = 256 // levels
        for channel in range(3):
            quantized[:, :, channel] = (quantized[:, :, channel] // step) * step

        return quantized.astype(np.uint8)

    @staticmethod
    def histogram_equalization(image: np.ndarray) -> np.ndarray:
        """Apply histogram equalization for better color contrast

        Useful for images with poor contrast
        """
        # Convert to HSV
        if image.shape[2] == 3:
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        else:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Equalize V channel only
        h, s, v = cv2.split(hsv)
        v = cv2.equalizeHist(v)

        # Merge back
        hsv_eq = cv2.merge([h, s, v])

        # Convert back to RGB
        if image.shape[2] == 3:
            equalized = cv2.cvtColor(hsv_eq, cv2.COLOR_HSV2RGB)
        else:
            equalized = cv2.cvtColor(hsv_eq, cv2.COLOR_HSV2BGR)

        return equalized

    @staticmethod
    def get_dominant_color_regions(image: np.ndarray, num_regions: int = 9) -> list[dict]:
        """Divide image into grid and find dominant color in each region

        Returns list of dominant colors with their locations
        """
        h, w = image.shape[:2]
        region_h = h // int(np.sqrt(num_regions))
        region_w = w // int(np.sqrt(num_regions))

        regions = []

        for i in range(int(np.sqrt(num_regions))):
            for j in range(int(np.sqrt(num_regions))):
                y1 = i * region_h
                y2 = min((i + 1) * region_h, h)
                x1 = j * region_w
                x2 = min((j + 1) * region_w, w)

                region = image[y1:y2, x1:x2]

                # Get mean color of region
                mean_color = region.reshape(-1, 3).mean(axis=0).astype(np.uint8)
                hex_color = f"#{mean_color[0]:02X}{mean_color[1]:02X}{mean_color[2]:02X}"

                regions.append({
                    'hex': hex_color,
                    'rgb': tuple(mean_color),
                    'x': x1,
                    'y': y1,
                    'width': x2 - x1,
                    'height': y2 - y1,
                })

        return regions

    @staticmethod
    def calculate_image_properties(image: np.ndarray) -> dict:
        """Calculate overall image color properties

        Returns:
            Dictionary with brightness, saturation, contrast, etc.
        """
        # Ensure RGB
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)

        # Convert to HSV and LAB
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype(np.float32)
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB).astype(np.float32)

        properties = {
            'average_saturation': hsv[:, :, 1].mean() / 255.0,
            'average_brightness': hsv[:, :, 2].mean() / 255.0,
            'average_hue': hsv[:, :, 0].mean(),
            'average_lightness': lab[:, :, 0].mean() / 255.0,
            'saturation_std': hsv[:, :, 1].std() / 255.0,
            'brightness_std': hsv[:, :, 2].std() / 255.0,
            'lightness_std': lab[:, :, 0].std() / 255.0,
            'width': image.shape[1],
            'height': image.shape[0],
            'aspect_ratio': image.shape[1] / image.shape[0] if image.shape[0] > 0 else 1.0,
        }

        return properties
