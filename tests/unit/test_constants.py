"""Tests for centralized constants module"""

from copy_that.constants import (
    CANNY_THRESHOLD_HIGH,
    CANNY_THRESHOLD_LOW,
    DATABASE_INSERT_BATCH_SIZE,
    DEFAULT_COLOR_CONFIDENCE,
    DEFAULT_DELTA_E_THRESHOLD,
    DEFAULT_EPSILON_CONVERGENCE,
    DEFAULT_EXTRACTION_CONFIDENCE,
    DEFAULT_K_CLUSTERS,
    DEFAULT_MATERIAL_COLOR_TOLERANCE,
    DEFAULT_MAX_CONCURRENT_EXTRACTIONS,
    DEFAULT_MAX_ITERATIONS,
    DOMINANT_COLORS_COUNT,
    GRAYSCALE_CHROMA_THRESHOLD,
    IMAGE_DOWNLOAD_TIMEOUT,
    LIGHTNESS_THRESHOLDS,
    NEUTRAL_COLOR_RGB_DIFF_THRESHOLD,
    OPENAI_MAX_TOKENS,
    OPENAI_TEMPERATURE,
    PASTEL_CHROMA_THRESHOLD,
    PASTEL_LIGHTNESS_THRESHOLD,
    RESIZE_DIMENSION_FOR_SPEED,
    SATURATION_THRESHOLDS,
    VIBRANT_VIBRANCY_THRESHOLD,
    WARM_COOL_TEMPERATURE_THRESHOLD,
    WEB_SAFE_COLOR_STEP,
)


class TestColorAnalysisThresholds:
    """Test color analysis threshold constants"""

    def test_delta_e_threshold_is_jnd(self):
        """Delta-E threshold should be 2.0 for Just Noticeable Difference"""
        assert DEFAULT_DELTA_E_THRESHOLD == 2.0
        assert isinstance(DEFAULT_DELTA_E_THRESHOLD, float)

    def test_grayscale_chroma_threshold(self):
        """Grayscale threshold should be small (near zero chroma)"""
        assert GRAYSCALE_CHROMA_THRESHOLD == 0.05
        assert 0 < GRAYSCALE_CHROMA_THRESHOLD < 0.1


class TestSaturationLightnessThresholds:
    """Test saturation and lightness categorization thresholds"""

    def test_saturation_thresholds_ordered(self):
        """Saturation thresholds should be in ascending order"""
        values = [
            SATURATION_THRESHOLDS["desaturated"],
            SATURATION_THRESHOLDS["muted"],
            SATURATION_THRESHOLDS["moderate"],
            SATURATION_THRESHOLDS["saturated"],
        ]
        assert values == sorted(values)
        assert all(0 <= v <= 1 for v in values)

    def test_lightness_thresholds_ordered(self):
        """Lightness thresholds should be in ascending order"""
        values = [
            LIGHTNESS_THRESHOLDS["very_dark"],
            LIGHTNESS_THRESHOLDS["dark"],
            LIGHTNESS_THRESHOLDS["medium"],
            LIGHTNESS_THRESHOLDS["light"],
        ]
        assert values == sorted(values)
        assert all(0 <= v <= 1 for v in values)


class TestPastelVibrancyConstants:
    """Test pastel and vibrancy detection constants"""

    def test_pastel_thresholds_valid(self):
        """Pastel thresholds should be in valid range"""
        assert 0 < PASTEL_LIGHTNESS_THRESHOLD <= 1
        assert 0 < PASTEL_CHROMA_THRESHOLD < 1
        # Pastels are light and low chroma
        assert PASTEL_LIGHTNESS_THRESHOLD > 0.5

    def test_vibrant_threshold_valid(self):
        """Vibrancy threshold should be positive"""
        assert VIBRANT_VIBRANCY_THRESHOLD > 0
        assert VIBRANT_VIBRANCY_THRESHOLD < 1


class TestAPIConfiguration:
    """Test API configuration constants"""

    def test_image_download_timeout_reasonable(self):
        """Image download timeout should be reasonable (10-60 seconds)"""
        assert 10 <= IMAGE_DOWNLOAD_TIMEOUT <= 60
        assert isinstance(IMAGE_DOWNLOAD_TIMEOUT, int)

    def test_openai_settings_valid(self):
        """OpenAI API settings should be valid"""
        assert OPENAI_MAX_TOKENS > 0
        assert OPENAI_MAX_TOKENS <= 4096  # Reasonable upper bound
        assert 0 <= OPENAI_TEMPERATURE <= 1

    def test_confidence_scores_valid(self):
        """Default confidence scores should be between 0 and 1"""
        assert 0 <= DEFAULT_COLOR_CONFIDENCE <= 1
        assert 0 <= DEFAULT_EXTRACTION_CONFIDENCE <= 1


class TestBatchProcessingConstants:
    """Test batch processing configuration constants"""

    def test_max_concurrent_extractions_valid(self):
        """Max concurrent should be positive and reasonable"""
        assert 1 <= DEFAULT_MAX_CONCURRENT_EXTRACTIONS <= 10
        assert isinstance(DEFAULT_MAX_CONCURRENT_EXTRACTIONS, int)

    def test_database_batch_size_valid(self):
        """Database batch size should be positive and reasonable"""
        assert 10 <= DATABASE_INSERT_BATCH_SIZE <= 1000
        assert isinstance(DATABASE_INSERT_BATCH_SIZE, int)


class TestImageProcessingConstants:
    """Test image processing configuration constants"""

    def test_kmeans_defaults_valid(self):
        """K-means clustering defaults should be valid"""
        assert DEFAULT_K_CLUSTERS > 0
        assert DEFAULT_MAX_ITERATIONS > 0
        assert DEFAULT_EPSILON_CONVERGENCE > 0

    def test_resize_dimension_valid(self):
        """Resize dimension should be reasonable for performance"""
        assert 64 <= RESIZE_DIMENSION_FOR_SPEED <= 512
        assert isinstance(RESIZE_DIMENSION_FOR_SPEED, int)

    def test_canny_thresholds_ordered(self):
        """Canny edge detection thresholds should be ordered"""
        assert CANNY_THRESHOLD_LOW < CANNY_THRESHOLD_HIGH
        assert CANNY_THRESHOLD_LOW > 0

    def test_dominant_colors_count_valid(self):
        """Dominant colors count should be positive"""
        assert DOMINANT_COLORS_COUNT > 0
        assert DOMINANT_COLORS_COUNT <= 20


class TestColorTemperatureConstants:
    """Test color temperature detection constants"""

    def test_warm_cool_threshold_valid(self):
        """Warm/cool temperature threshold should be positive"""
        assert WARM_COOL_TEMPERATURE_THRESHOLD > 0
        # Should be less than max RGB difference (255)
        assert WARM_COOL_TEMPERATURE_THRESHOLD <= 255

    def test_neutral_color_threshold_valid(self):
        """Neutral color threshold should be reasonable"""
        assert 0 < NEUTRAL_COLOR_RGB_DIFF_THRESHOLD <= 50


class TestMaterialDesignConstants:
    """Test Material Design integration constants"""

    def test_material_tolerance_valid(self):
        """Material color tolerance should be reasonable Delta-E"""
        assert DEFAULT_MATERIAL_COLOR_TOLERANCE > 0
        # Should be larger than JND but not too large
        assert DEFAULT_MATERIAL_COLOR_TOLERANCE <= 50

    def test_web_safe_step_valid(self):
        """Web-safe color step should divide 255 evenly"""
        assert WEB_SAFE_COLOR_STEP == 51
        assert 255 % WEB_SAFE_COLOR_STEP == 0


class TestConstantsIntegration:
    """Test that constants work correctly with the codebase"""

    def test_can_import_all_constants(self):
        """All constants should be importable without errors"""
        # If we get here, all imports succeeded
        assert True

    def test_constants_have_correct_types(self):
        """Critical constants should have correct types"""
        assert isinstance(DEFAULT_DELTA_E_THRESHOLD, (int, float))
        assert isinstance(SATURATION_THRESHOLDS, dict)
        assert isinstance(LIGHTNESS_THRESHOLDS, dict)
        assert isinstance(IMAGE_DOWNLOAD_TIMEOUT, (int, float))
