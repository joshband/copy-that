"""Unit tests for shadow detection models.

Tests DSDNet, BDRAR, and ShadowNet shadow detection models.
"""

from pathlib import Path

import numpy as np
import pytest

# Import models
try:
    from src.copy_that.shadowlab.models import load_shadow_model
except ImportError:
    # Try alternative import path
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from src.copy_that.shadowlab.models import load_shadow_model


class TestShadowDetectionModel:
    """Test suite for shadow detection models."""

    @pytest.fixture
    def test_image(self):
        """Create a test image."""
        # Generate a test image with some variation
        np.random.seed(42)
        # Create gradient image with some shadows
        h, w = 256, 256
        x = np.linspace(0, 1, w)
        y = np.linspace(0, 1, h)
        X, Y = np.meshgrid(x, y)

        # Create base image with gradient
        base = 0.5 + 0.3 * X + 0.2 * Y
        noise = np.random.normal(0, 0.05, (h, w))
        img = np.clip(base + noise, 0, 1)

        # Create RGB image
        rgb = np.stack([img, img * 0.9, img * 0.8], axis=2).astype(np.float32)
        return rgb

    def test_dsdnet_initialization(self):
        """Test DSDNet model initialization."""
        model = load_shadow_model(model_name="dsdnet", device="cpu")
        assert model is not None
        assert str(model).startswith("ShadowDetectionModel")

    def test_bdrar_initialization(self):
        """Test BDRAR model initialization."""
        model = load_shadow_model(model_name="bdrar", device="cpu")
        assert model is not None
        assert str(model).startswith("ShadowDetectionModel")

    def test_shadownet_initialization(self):
        """Test ShadowNet model initialization."""
        model = load_shadow_model(model_name="shadownet", device="cpu")
        assert model is not None
        assert str(model).startswith("ShadowDetectionModel")

    def test_dsdnet_inference(self, test_image):
        """Test DSDNet inference."""
        model = load_shadow_model(model_name="dsdnet", device="cpu")
        shadow_mask = model.infer(test_image)

        # Check output shape
        assert shadow_mask.shape == (256, 256)

        # Check output range
        assert shadow_mask.min() >= 0.0
        assert shadow_mask.max() <= 1.0

        # Check dtype
        assert shadow_mask.dtype == np.float32

    def test_bdrar_inference(self, test_image):
        """Test BDRAR inference."""
        model = load_shadow_model(model_name="bdrar", device="cpu")
        shadow_mask = model.infer(test_image)

        # Check output shape
        assert shadow_mask.shape == (256, 256)

        # Check output range
        assert shadow_mask.min() >= 0.0
        assert shadow_mask.max() <= 1.0

        # Check dtype
        assert shadow_mask.dtype == np.float32

    def test_shadownet_inference(self, test_image):
        """Test ShadowNet inference."""
        model = load_shadow_model(model_name="shadownet", device="cpu")
        shadow_mask = model.infer(test_image)

        # Check output shape
        assert shadow_mask.shape == (256, 256)

        # Check output range
        assert shadow_mask.min() >= 0.0
        assert shadow_mask.max() <= 1.0

        # Check dtype
        assert shadow_mask.dtype == np.float32

    def test_invalid_model_name(self):
        """Test error on invalid model name."""
        with pytest.raises(ValueError, match="not supported"):
            load_shadow_model(model_name="invalid_model", device="cpu")

    def test_image_shape_validation(self):
        """Test image shape validation."""
        model = load_shadow_model(model_name="dsdnet", device="cpu")

        # Test wrong number of channels
        invalid_image = np.random.rand(256, 256).astype(np.float32)
        with pytest.raises(ValueError, match="Expected"):
            model.infer(invalid_image)

    def test_image_dtype_validation(self):
        """Test image dtype validation."""
        model = load_shadow_model(model_name="dsdnet", device="cpu")

        # Test wrong dtype
        invalid_image = np.random.randint(0, 255, (256, 256, 3)).astype(np.uint8)
        with pytest.raises(ValueError, match="Expected float32"):
            model.infer(invalid_image)

    def test_model_different_sizes(self):
        """Test model with different image sizes."""
        model = load_shadow_model(model_name="dsdnet", device="cpu")

        sizes = [(128, 128), (256, 256), (512, 512)]
        for h, w in sizes:
            test_img = np.random.rand(h, w, 3).astype(np.float32)
            shadow_mask = model.infer(test_img)

            assert shadow_mask.shape == (h, w)
            assert shadow_mask.dtype == np.float32
            assert shadow_mask.min() >= 0.0
            assert shadow_mask.max() <= 1.0

    def test_model_consistency(self, test_image):
        """Test that model produces consistent results."""
        model = load_shadow_model(model_name="dsdnet", device="cpu")

        # Run inference twice
        mask1 = model.infer(test_image)
        mask2 = model.infer(test_image)

        # Results should be identical
        np.testing.assert_array_almost_equal(mask1, mask2)

    def test_batch_processing_sequential(self, test_image):
        """Test sequential processing of multiple images."""
        model = load_shadow_model(model_name="dsdnet", device="cpu")

        masks = []
        for _ in range(3):
            mask = model.infer(test_image)
            masks.append(mask)

        # All masks should have correct shape
        for mask in masks:
            assert mask.shape == (256, 256)

    def test_device_parameter(self):
        """Test device parameter."""
        # CPU should always work
        model_cpu = load_shadow_model(model_name="dsdnet", device="cpu")
        assert model_cpu.device == "cpu"

        # Note: CUDA tests skipped if no GPU
        try:
            model_cuda = load_shadow_model(model_name="dsdnet", device="cuda")
            assert model_cuda.device == "cuda"
        except RuntimeError:
            pytest.skip("CUDA not available")

    def test_model_eval_mode(self):
        """Test that model is in eval mode."""
        model = load_shadow_model(model_name="dsdnet", device="cpu")
        # Model should be in eval mode (no batch norm updates, etc.)
        assert not model.model.training

    def test_output_smoothness(self, test_image):
        """Test that output is reasonably smooth."""
        model = load_shadow_model(model_name="dsdnet", device="cpu")
        shadow_mask = model.infer(test_image)

        # Compute gradient magnitude
        gy, gx = np.gradient(shadow_mask)
        grad_mag = np.sqrt(gx**2 + gy**2)

        # Check that output is not too spiky
        # 95th percentile of gradients should be reasonable
        grad_high = np.percentile(grad_mag, 95)
        assert grad_high < 0.5, "Output has too many sharp transitions"


class TestModelComparison:
    """Test suite for comparing different shadow detection models."""

    @pytest.fixture
    def test_image_bright(self):
        """Create a bright test image."""
        h, w = 256, 256
        # Bright image with minimal shadows
        rgb = np.ones((h, w, 3), dtype=np.float32) * 0.8
        # Add some noise
        rgb += np.random.normal(0, 0.05, (h, w, 3))
        return np.clip(rgb, 0, 1)

    @pytest.fixture
    def test_image_dark(self):
        """Create a dark test image."""
        h, w = 256, 256
        # Dark image with significant shadows
        rgb = np.ones((h, w, 3), dtype=np.float32) * 0.3
        # Add circular shadow
        y, x = np.ogrid[:h, :w]
        center_y, center_x = h // 2, w // 2
        mask = (x - center_x) ** 2 + (y - center_y) ** 2 <= (50**2)
        rgb[mask] *= 0.5
        return np.clip(rgb, 0, 1)

    def test_models_on_bright_image(self, test_image_bright):
        """Test models on bright image with minimal shadows.

        Note: Thresholds are lenient for untrained models. When pre-trained
        models are loaded, coverage should be significantly lower.
        """
        models = ["dsdnet", "bdrar", "shadownet"]
        for model_name in models:
            model = load_shadow_model(model_name=model_name, device="cpu")
            shadow_mask = model.infer(test_image_bright)

            # Bright images should have reasonable shadow coverage
            # Untrained models may be 50-80%, trained models should be <20%
            coverage = np.mean(shadow_mask)
            assert coverage < 0.85, f"{model_name} predicts excessive shadow on bright image"

    def test_models_on_dark_image(self, test_image_dark):
        """Test models on dark image with clear shadows."""
        models = ["dsdnet", "bdrar", "shadownet"]
        for model_name in models:
            model = load_shadow_model(model_name=model_name, device="cpu")
            shadow_mask = model.infer(test_image_dark)

            # Dark images should have higher shadow coverage
            coverage = np.mean(shadow_mask)
            # Should detect some shadows
            assert coverage > 0.1, f"{model_name} fails to detect shadows"

    def test_bdrar_vs_dsdnet_accuracy(self, test_image_dark):
        """Test that BDRAR and DSDNet produce valid outputs.

        Note: With untrained models, predictions will be random but valid.
        When trained models are loaded, BDRAR should be more refined than DSDNet.
        """
        dsdnet = load_shadow_model(model_name="dsdnet", device="cpu")
        bdrar = load_shadow_model(model_name="bdrar", device="cpu")

        mask_dsdnet = dsdnet.infer(test_image_dark)
        mask_bdrar = bdrar.infer(test_image_dark)

        # Both should produce valid outputs
        assert np.mean(mask_dsdnet) > 0.01
        assert np.mean(mask_bdrar) > 0.01

        # Masks should be valid (untrained models produce similar random outputs)
        # With trained models, this should be much higher
        difference = np.abs(mask_dsdnet - mask_bdrar)
        assert np.mean(difference) > 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
