"""Unit tests for MiDaS depth estimation model."""

from pathlib import Path

import numpy as np
import pytest

try:
    from src.copy_that.shadowlab.models import load_depth_model
except ImportError:
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from src.copy_that.shadowlab.models import load_depth_model


class TestDepthEstimationModel:
    """Test suite for MiDaS depth estimation."""

    @pytest.fixture
    def test_image(self):
        """Create a test image."""
        np.random.seed(42)
        h, w = 256, 256
        # Create a simple depth-like image
        x = np.linspace(0, 1, w)
        y = np.linspace(0, 1, h)
        X, Y = np.meshgrid(x, y)

        # Create gradient
        base = 0.5 + 0.3 * X + 0.2 * Y
        noise = np.random.normal(0, 0.05, (h, w))
        img = np.clip(base + noise, 0, 1)

        # Create RGB image
        rgb = np.stack([img, img * 0.9, img * 0.8], axis=2).astype(np.float32)
        return rgb

    def test_dpt_large_initialization(self):
        """Test DPT_Large model initialization."""
        # Skip if torch.hub unavailable - loads actual ~1GB model
        pytest.skip("Requires torch.hub, internet access, and ~1GB disk space")

    def test_dpt_hybrid_initialization(self):
        """Test DPT_Hybrid model initialization (RECOMMENDED)."""
        # Skip if torch.hub unavailable
        pytest.skip("Requires torch.hub and internet access")

    def test_midas_small_initialization(self):
        """Test MiDaS_small model initialization."""
        pytest.skip("Requires torch.hub and internet access")

    def test_invalid_model_type(self):
        """Test error on invalid model type."""
        with pytest.raises(ValueError, match="not supported"):
            load_depth_model(model_type="InvalidModel", device="cpu")

    def test_image_shape_validation(self):
        """Test image shape validation."""
        pytest.skip("Requires torch.hub and internet access")

    def test_image_dtype_validation(self):
        """Test image dtype validation."""
        pytest.skip("Requires torch.hub and internet access")

    def test_depth_output_properties(self, test_image):
        """Test general depth output properties."""
        pytest.skip("Requires torch.hub and internet access")


class TestDepthModelOffline:
    """Tests that don't require torch.hub."""

    def test_model_type_validation(self):
        """Test that invalid model types are caught early."""
        valid_types = {"DPT_Large", "DPT_Hybrid", "MiDaS_small"}

        # Import to test validation
        try:
            from src.copy_that.shadowlab.models.depth_model import (
                DepthEstimationModel,
            )
        except ImportError:
            import sys
            from pathlib import Path

            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
            from src.copy_that.shadowlab.models.depth_model import (
                DepthEstimationModel,
            )

        # Valid models should not raise
        for model_type in valid_types:
            model = DepthEstimationModel(model_type=model_type, device="cpu")
            assert model.model_type == model_type

        # Invalid models should raise
        with pytest.raises(ValueError):
            DepthEstimationModel(model_type="InvalidModel", device="cpu")

    def test_device_parameter(self):
        """Test device parameter."""
        try:
            from src.copy_that.shadowlab.models.depth_model import (
                DepthEstimationModel,
            )
        except ImportError:
            import sys
            from pathlib import Path

            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
            from src.copy_that.shadowlab.models.depth_model import (
                DepthEstimationModel,
            )

        model_cpu = DepthEstimationModel(model_type="DPT_Hybrid", device="cpu")
        assert model_cpu.device == "cpu"

        model_cuda = DepthEstimationModel(model_type="DPT_Hybrid", device="cuda")
        assert model_cuda.device == "cuda"

    def test_model_representation(self):
        """Test model string representation."""
        try:
            from src.copy_that.shadowlab.models.depth_model import (
                DepthEstimationModel,
            )
        except ImportError:
            import sys
            from pathlib import Path

            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
            from src.copy_that.shadowlab.models.depth_model import (
                DepthEstimationModel,
            )

        model = DepthEstimationModel(model_type="DPT_Hybrid", device="cpu")
        repr_str = repr(model)
        assert "DepthEstimationModel" in repr_str
        assert "DPT_Hybrid" in repr_str
        assert "cpu" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
