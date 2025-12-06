"""
Advanced shadow analysis features.

This module provides enhanced capabilities beyond the core pipeline:
- Multi-light source fitting (2-3 dominant lights)
- CLIP-based shadow style embeddings
- LLaVA-based natural language shadow descriptions
"""

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


# ============================================================================
# Multi-Light Source Fitting
# ============================================================================


@dataclass
class LightSource:
    """Represents a single light source."""

    direction: np.ndarray  # Unit vector (3,)
    intensity: float  # Relative intensity 0-1
    azimuth_deg: float
    elevation_deg: float
    contribution: float  # How much of shading this light explains

    def to_dict(self) -> dict[str, Any]:
        return {
            "direction": self.direction.tolist(),
            "intensity": self.intensity,
            "azimuth_deg": self.azimuth_deg,
            "elevation_deg": self.elevation_deg,
            "contribution": self.contribution,
        }


@dataclass
class MultiLightResult:
    """Result of multi-light source fitting."""

    lights: list[LightSource]
    residual_error: float  # Unexplained variance
    total_explained: float  # Total variance explained (0-1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lights": [light.to_dict() for light in self.lights],
            "residual_error": self.residual_error,
            "total_explained": self.total_explained,
            "num_lights": len(self.lights),
        }


def fit_multi_light_sources(
    normals: np.ndarray,
    shading: np.ndarray,
    max_lights: int = 3,
    min_contribution: float = 0.1,
) -> MultiLightResult:
    """
    Fit multiple directional light sources to the shading field.

    Uses iterative residual fitting:
    1. Fit first dominant light
    2. Compute residual shading
    3. Fit next light to residual
    4. Repeat until max_lights or residual < threshold

    Args:
        normals: (H, W, 3) unit normal vectors
        shading: (H, W) shading map [0, 1]
        max_lights: Maximum number of lights to fit
        min_contribution: Minimum contribution threshold for a light

    Returns:
        MultiLightResult with fitted lights
    """
    h, w = normals.shape[:2]

    # Convert shading to grayscale if needed
    if shading.ndim == 3:
        shading_gray = np.mean(shading, axis=2)
    else:
        shading_gray = shading.copy()

    # Normalize shading to 0-1
    shading_norm = shading_gray.astype(np.float32)
    if shading_norm.max() > 1.0:
        shading_norm = shading_norm / shading_norm.max()

    # Reshape for linear algebra
    N = normals.reshape(-1, 3)  # (H*W, 3)
    S = shading_norm.reshape(-1)  # (H*W,)

    lights = []
    residual = S.copy()
    total_variance = np.var(S)
    explained_variance = 0.0

    for i in range(max_lights):
        # Fit light to residual
        try:
            L = np.linalg.lstsq(N, residual, rcond=None)[0]
        except np.linalg.LinAlgError:
            break

        # Normalize direction
        L_norm = np.linalg.norm(L)
        if L_norm < 1e-8:
            break
        L_dir = L / L_norm

        # Compute this light's contribution
        predicted = np.clip(N @ L_dir, 0, 1) * L_norm
        contribution = np.var(predicted) / (total_variance + 1e-8)

        # Stop if contribution too small
        if contribution < min_contribution:
            break

        # Convert to angles
        azimuth_deg, elevation_deg = _light_dir_to_angles(L_dir)

        # Create light source
        light = LightSource(
            direction=L_dir,
            intensity=float(L_norm),
            azimuth_deg=azimuth_deg,
            elevation_deg=elevation_deg,
            contribution=float(contribution),
        )
        lights.append(light)

        # Update residual
        residual = residual - predicted
        explained_variance += contribution

        logger.debug(
            f"Light {i + 1}: azimuth={azimuth_deg:.1f}°, "
            f"elevation={elevation_deg:.1f}°, contribution={contribution:.1%}"
        )

    # Compute final residual error
    residual_error = float(np.var(residual) / (total_variance + 1e-8))

    return MultiLightResult(
        lights=lights,
        residual_error=residual_error,
        total_explained=float(explained_variance),
    )


def _light_dir_to_angles(L: np.ndarray) -> tuple[float, float]:
    """Convert light direction vector to spherical angles."""
    x, y, z = L[0], L[1], L[2]
    azimuth_rad = np.arctan2(y, x)
    azimuth_deg = float(np.degrees(azimuth_rad) % 360)
    r_xy = np.sqrt(x**2 + y**2)
    elevation_rad = np.arctan2(z, r_xy)
    elevation_deg = float(np.degrees(elevation_rad))
    return azimuth_deg, elevation_deg


# ============================================================================
# CLIP Shadow Style Embeddings
# ============================================================================

# Global cache for CLIP model
_clip_model = None
_clip_processor = None


def _get_clip_model():
    """Load and cache CLIP model."""
    global _clip_model, _clip_processor

    if _clip_model is not None:
        return _clip_model, _clip_processor

    try:
        from transformers import CLIPModel, CLIPProcessor

        model_name = "openai/clip-vit-base-patch32"
        logger.info(f"Loading CLIP model: {model_name}")

        _clip_processor = CLIPProcessor.from_pretrained(model_name)
        _clip_model = CLIPModel.from_pretrained(model_name)
        _clip_model.eval()

        logger.info("CLIP model loaded successfully")
        return _clip_model, _clip_processor

    except ImportError:
        logger.warning("transformers not available for CLIP")
        return None, None
    except Exception as e:
        logger.warning(f"Failed to load CLIP model: {e}")
        return None, None


@dataclass
class ShadowStyleEmbedding:
    """CLIP-based shadow style embedding."""

    embedding: np.ndarray  # (512,) or (768,) depending on model
    style_scores: dict[str, float]  # Similarity to style prompts
    dominant_style: str
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "embedding": self.embedding.tolist(),
            "style_scores": self.style_scores,
            "dominant_style": self.dominant_style,
            "confidence": self.confidence,
        }


# Style prompts for shadow classification
SHADOW_STYLE_PROMPTS = [
    "dramatic cinematic lighting with deep shadows",
    "soft diffuse studio lighting",
    "harsh direct sunlight with sharp shadows",
    "moody low-key lighting",
    "bright high-key lighting with minimal shadows",
    "rim lighting with backlit silhouette",
    "natural outdoor ambient lighting",
    "warm golden hour lighting",
    "cool blue hour lighting",
    "flat even lighting without shadows",
]

SHADOW_STYLE_LABELS = [
    "cinematic",
    "studio_soft",
    "harsh_sunlight",
    "moody_lowkey",
    "highkey",
    "rim_backlit",
    "natural_outdoor",
    "golden_hour",
    "blue_hour",
    "flat_even",
]


def extract_shadow_style_embedding(
    image_rgb: np.ndarray,
    shadow_mask: np.ndarray | None = None,
) -> ShadowStyleEmbedding | None:
    """
    Extract CLIP-based style embedding for shadow characteristics.

    Args:
        image_rgb: RGB image (H, W, 3) uint8
        shadow_mask: Optional shadow mask to focus on shadow regions

    Returns:
        ShadowStyleEmbedding or None if CLIP unavailable
    """
    model, processor = _get_clip_model()
    if model is None:
        logger.warning("CLIP not available, returning None")
        return None

    try:
        import torch
        from PIL import Image

        # Convert to PIL
        if image_rgb.dtype != np.uint8:
            image_rgb = (np.clip(image_rgb, 0, 1) * 255).astype(np.uint8)

        pil_image = Image.fromarray(image_rgb)

        # Process image
        inputs = processor(images=pil_image, return_tensors="pt")

        # Get image embedding
        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
            image_embedding = image_features[0].cpu().numpy()

            # Normalize
            image_embedding = image_embedding / (np.linalg.norm(image_embedding) + 1e-8)

            # Compare to style prompts
            text_inputs = processor(text=SHADOW_STYLE_PROMPTS, return_tensors="pt", padding=True)
            text_features = model.get_text_features(**text_inputs)
            text_embeddings = text_features.cpu().numpy()

            # Normalize text embeddings
            text_embeddings = text_embeddings / (
                np.linalg.norm(text_embeddings, axis=1, keepdims=True) + 1e-8
            )

            # Compute similarities
            similarities = text_embeddings @ image_embedding

        # Create style scores dict
        style_scores = {
            label: float(sim) for label, sim in zip(SHADOW_STYLE_LABELS, similarities)
        }

        # Find dominant style
        best_idx = int(np.argmax(similarities))
        dominant_style = SHADOW_STYLE_LABELS[best_idx]
        confidence = float(similarities[best_idx])

        return ShadowStyleEmbedding(
            embedding=image_embedding,
            style_scores=style_scores,
            dominant_style=dominant_style,
            confidence=confidence,
        )

    except Exception as e:
        logger.warning(f"Failed to extract CLIP embedding: {e}")
        return None


# ============================================================================
# LLaVA Shadow Descriptions
# ============================================================================

_llava_model = None
_llava_processor = None


def _get_llava_model():
    """Load and cache LLaVA model."""
    global _llava_model, _llava_processor

    if _llava_model is not None:
        return _llava_model, _llava_processor

    try:
        from transformers import AutoProcessor, LlavaForConditionalGeneration

        # Use smaller LLaVA variant for efficiency
        model_name = "llava-hf/llava-1.5-7b-hf"
        logger.info(f"Loading LLaVA model: {model_name}")

        _llava_processor = AutoProcessor.from_pretrained(model_name)
        _llava_model = LlavaForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
        )

        logger.info("LLaVA model loaded successfully")
        return _llava_model, _llava_processor

    except ImportError:
        logger.warning("transformers not available for LLaVA")
        return None, None
    except Exception as e:
        logger.warning(f"Failed to load LLaVA model: {e}")
        return None, None


@dataclass
class ShadowDescription:
    """Natural language shadow description."""

    description: str
    lighting_summary: str
    shadow_characteristics: str
    mood: str
    model_used: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "lighting_summary": self.lighting_summary,
            "shadow_characteristics": self.shadow_characteristics,
            "mood": self.mood,
            "model_used": self.model_used,
        }


SHADOW_ANALYSIS_PROMPT = """Analyze the lighting and shadows in this image. Provide:
1. A brief description of the overall lighting (1-2 sentences)
2. Shadow characteristics: direction, softness, contrast
3. The mood/atmosphere created by the lighting

Be concise and specific."""


def generate_shadow_description(
    image_rgb: np.ndarray,
    use_llava: bool = True,
) -> ShadowDescription | None:
    """
    Generate natural language description of shadows using LLaVA.

    Args:
        image_rgb: RGB image (H, W, 3) uint8
        use_llava: If True, use LLaVA. If False, use rule-based fallback.

    Returns:
        ShadowDescription or None if generation fails
    """
    if not use_llava:
        return _generate_rule_based_description(image_rgb)

    model, processor = _get_llava_model()
    if model is None:
        logger.info("LLaVA not available, using rule-based fallback")
        return _generate_rule_based_description(image_rgb)

    try:
        import torch
        from PIL import Image

        # Convert to PIL
        if image_rgb.dtype != np.uint8:
            image_rgb = (np.clip(image_rgb, 0, 1) * 255).astype(np.uint8)

        pil_image = Image.fromarray(image_rgb)

        # Prepare prompt
        prompt = f"USER: <image>\n{SHADOW_ANALYSIS_PROMPT}\nASSISTANT:"

        # Process
        inputs = processor(text=prompt, images=pil_image, return_tensors="pt")
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        # Generate
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=200,
                do_sample=False,
            )

        # Decode
        output_text = processor.decode(output_ids[0], skip_special_tokens=True)

        # Extract assistant response
        if "ASSISTANT:" in output_text:
            response = output_text.split("ASSISTANT:")[-1].strip()
        else:
            response = output_text.strip()

        # Parse response into components
        lines = response.split("\n")
        lighting_summary = lines[0] if lines else response
        shadow_chars = lines[1] if len(lines) > 1 else ""
        mood = lines[2] if len(lines) > 2 else ""

        return ShadowDescription(
            description=response,
            lighting_summary=lighting_summary,
            shadow_characteristics=shadow_chars,
            mood=mood,
            model_used="llava-1.5-7b",
        )

    except Exception as e:
        logger.warning(f"LLaVA generation failed: {e}")
        return _generate_rule_based_description(image_rgb)


def _generate_rule_based_description(image_rgb: np.ndarray) -> ShadowDescription:
    """Generate a rule-based shadow description as fallback."""
    import cv2

    # Convert to grayscale for analysis
    if image_rgb.ndim == 3:
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_rgb

    # Analyze brightness distribution
    mean_brightness = np.mean(gray)
    std_brightness = np.std(gray)
    dark_fraction = np.mean(gray < 80)
    bright_fraction = np.mean(gray > 175)

    # Determine lighting style
    if dark_fraction > 0.4:
        lighting = "low-key lighting with prominent shadows"
        mood = "dramatic and moody"
    elif bright_fraction > 0.4:
        lighting = "high-key lighting with minimal shadows"
        mood = "bright and airy"
    elif std_brightness > 60:
        lighting = "high-contrast lighting with defined shadows"
        mood = "dynamic and striking"
    else:
        lighting = "balanced lighting with moderate shadows"
        mood = "natural and neutral"

    # Shadow characteristics
    if std_brightness > 70:
        shadow_chars = "Hard shadows with sharp edges, suggesting directional lighting"
    elif std_brightness > 40:
        shadow_chars = "Medium-soft shadows with gradual transitions"
    else:
        shadow_chars = "Soft, diffuse shadows suggesting ambient or overcast lighting"

    description = f"{lighting}. {shadow_chars}. The overall mood is {mood}."

    return ShadowDescription(
        description=description,
        lighting_summary=lighting,
        shadow_characteristics=shadow_chars,
        mood=mood,
        model_used="rule-based",
    )


# ============================================================================
# Combined Advanced Analysis
# ============================================================================


@dataclass
class AdvancedShadowAnalysis:
    """Combined results from all advanced analysis methods."""

    multi_light: MultiLightResult | None
    style_embedding: ShadowStyleEmbedding | None
    description: ShadowDescription | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "multi_light": self.multi_light.to_dict() if self.multi_light else None,
            "style_embedding": self.style_embedding.to_dict() if self.style_embedding else None,
            "description": self.description.to_dict() if self.description else None,
        }


def run_advanced_analysis(
    image_rgb: np.ndarray,
    normals: np.ndarray | None = None,
    shading: np.ndarray | None = None,
    shadow_mask: np.ndarray | None = None,
    enable_clip: bool = True,
    enable_llava: bool = False,  # Disabled by default (heavy)
    max_lights: int = 3,
) -> AdvancedShadowAnalysis:
    """
    Run all advanced shadow analysis methods.

    Args:
        image_rgb: RGB image (H, W, 3)
        normals: Optional surface normals (H, W, 3)
        shading: Optional shading map (H, W)
        shadow_mask: Optional shadow mask
        enable_clip: Enable CLIP style embeddings
        enable_llava: Enable LLaVA descriptions (resource-intensive)
        max_lights: Maximum lights to fit

    Returns:
        AdvancedShadowAnalysis with all results
    """
    # Multi-light fitting
    multi_light = None
    if normals is not None and shading is not None:
        try:
            multi_light = fit_multi_light_sources(normals, shading, max_lights=max_lights)
            logger.info(f"Fitted {len(multi_light.lights)} light sources")
        except Exception as e:
            logger.warning(f"Multi-light fitting failed: {e}")

    # CLIP style embedding
    style_embedding = None
    if enable_clip:
        try:
            style_embedding = extract_shadow_style_embedding(image_rgb, shadow_mask)
            if style_embedding:
                logger.info(f"Dominant style: {style_embedding.dominant_style}")
        except Exception as e:
            logger.warning(f"CLIP embedding failed: {e}")

    # LLaVA description
    description = None
    if enable_llava:
        try:
            description = generate_shadow_description(image_rgb, use_llava=True)
            if description:
                logger.info(f"Description generated via {description.model_used}")
        except Exception as e:
            logger.warning(f"LLaVA description failed: {e}")
    else:
        # Always provide rule-based description
        description = _generate_rule_based_description(image_rgb)

    return AdvancedShadowAnalysis(
        multi_light=multi_light,
        style_embedding=style_embedding,
        description=description,
    )
