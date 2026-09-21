"""
Centralized constants for the copy_that application.

This module contains magic numbers and configuration values that are used
across multiple modules to improve maintainability and consistency.
"""

# =============================================================================
# Color Analysis Thresholds
# =============================================================================

# Delta-E threshold for Just Noticeable Difference (JND)
# Used for color deduplication and similarity detection
DEFAULT_DELTA_E_THRESHOLD = 2.0

# Grayscale detection - colors with chroma below this are considered grayscale
GRAYSCALE_CHROMA_THRESHOLD = 0.05

# =============================================================================
# Saturation/Lightness Categorization
# =============================================================================

# Thresholds for categorizing saturation levels
SATURATION_THRESHOLDS = {
    "desaturated": 0.1,
    "muted": 0.3,
    "moderate": 0.6,
    "saturated": 0.8,  # Above this is "vibrant"
}

# Thresholds for categorizing lightness levels
LIGHTNESS_THRESHOLDS = {
    "very_dark": 0.2,
    "dark": 0.4,
    "medium": 0.6,
    "light": 0.8,  # Above this is "very_light"
}

# =============================================================================
# Pastel and Vibrancy Detection
# =============================================================================

PASTEL_LIGHTNESS_THRESHOLD = 0.8
PASTEL_CHROMA_THRESHOLD = 0.15
VIBRANT_VIBRANCY_THRESHOLD = 0.25

# =============================================================================
# API Configuration
# =============================================================================

# Image download timeout in seconds
IMAGE_DOWNLOAD_TIMEOUT = 30

# OpenAI API settings
OPENAI_MAX_TOKENS = 2000
OPENAI_TEMPERATURE = 0.3

# Default confidence scores
DEFAULT_COLOR_CONFIDENCE = 0.8
DEFAULT_EXTRACTION_CONFIDENCE = 0.85

# =============================================================================
# Batch Processing
# =============================================================================

# Maximum concurrent image processing tasks
DEFAULT_MAX_CONCURRENT_EXTRACTIONS = 3

# Batch size for database inserts
DATABASE_INSERT_BATCH_SIZE = 100

# =============================================================================
# Image Processing (CV/Clustering)
# =============================================================================

# K-means clustering defaults
DEFAULT_K_CLUSTERS = 12
DEFAULT_MAX_ITERATIONS = 100
DEFAULT_EPSILON_CONVERGENCE = 0.1

# Image resize dimensions for faster processing
RESIZE_DIMENSION_FOR_SPEED = 256

# Canny edge detection thresholds
CANNY_THRESHOLD_LOW = 100
CANNY_THRESHOLD_HIGH = 200

# Number of dominant colors to extract
DOMINANT_COLORS_COUNT = 5

# =============================================================================
# Color Temperature Detection
# =============================================================================

# RGB difference threshold for warm/cool temperature detection
WARM_COOL_TEMPERATURE_THRESHOLD = 30

# Maximum RGB channel difference for neutral colors
NEUTRAL_COLOR_RGB_DIFF_THRESHOLD = 20

# =============================================================================
# Material Design Integration
# =============================================================================

# Default tolerance for Material Design color matching
DEFAULT_MATERIAL_COLOR_TOLERANCE = 10.0

# Web-safe color palette step size (255/5)
WEB_SAFE_COLOR_STEP = 51
