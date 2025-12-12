# Mood Board Generation Specification

## Overview

Copy That generates AI-curated mood boards that translate extracted design tokens into rich visual narratives. Mood boards bridge raw token data (colors, typography, spacing) with cultural context, material DNA, and aesthetic movements.

## Mood Board Types

### 1. Material-Focused Mood Boards

**Purpose:** Capture the physical, tactile, and surface qualities of a design system.

**Visual DNA:**
- Anodized aluminum surfaces (brushed, matte, polished)
- Resin/enamel swirls and fluid patterns
- Glass globes and translucent indicators
- Tactile polymers and soft-touch materials
- CRT oscilloscope glows and phosphor traces
- Metallic finishes (gold, brass, chrome, gunmetal)
- Synesthetic gradients and color blending
- Physical controls (knobs, sliders, buttons)

**Key Characteristics:**
- Emphasis on texture and materiality
- Physical object photography
- Depth and dimensionality
- Surface reflections and light interaction
- Tactile qualities visible in imagery

**Example Themes:**
- "Retro-Futurism" - Playful tactile controls meet Yves Klein blue
- "Analog Warmth" - Brushed metal meets resin swirls
- "Synesthetic Hardware" - Glass globes and gradient fields

**DALL-E Prompt Focus:**
```
- "anodized aluminum surface with brushed metal texture"
- "resin and enamel fluid patterns with swirls"
- "glass globe indicator with internal glow"
- "tactile control panel with physical knobs and buttons"
- "CRT oscilloscope screen with phosphor glow"
- "metallic surfaces with gradient reflections"
```

---

### 2. Typography-Focused Mood Boards

**Purpose:** Establish typographic systems, grid structures, and graphic language for UI controls.

**Visual DNA:**
- Swiss typographic rigor (grid systems, baseline logic)
- Industrial panel typography (frequency markings, mode labels)
- Geometric sans-serif type systems
- Asymmetric composition and modular layouts
- Technical signage and control labels
- Play/stop glyphs and interface icons
- Tuning numerics and measurement scales
- Baseline grids and modular spacing

**Key Characteristics:**
- Emphasis on letterforms and hierarchy
- Grid systems and alignment
- Icon and glyph systems
- Technical/industrial lettering
- Typographic compositions as focal point

**Example Themes:**
- "Swiss Industrial" - Grid systems meet control panel labels
- "Geometric Discipline" - Bold sans-serif with modular rhythm
- "Technical Poetry" - Frequency markings and typographic rigor

**DALL-E Prompt Focus:**
```
- "Swiss grid system with bold sans-serif typography and geometric shapes"
- "Industrial control panel with frequency markings and technical labels"
- "Modular typographic composition with baseline grid visible"
- "Geometric letterforms on industrial blue and gold background"
- "Technical signage with play controls and measurement scales"
- "Asymmetric layout with bold typography and iconic glyphs"
```

**Reference Elements:**
- Grid overlays (visible baseline grids, modular units)
- Technical labels ("245 Hz", "FM/AM", "FREQUENCY", "GAIN")
- Control glyphs (play, stop, left/right arrows, waveforms)
- Typeface specimens (alphabet displays, letter variations)
- Measurement scales and numeric systems
- Icon sets and pictograms

---

### 3. Color-Focused Mood Boards *(Future)*

**Purpose:** Explore color relationships, harmonies, and chromatic narratives.

**Visual DNA:**
- Color field paintings
- Gradient studies
- Chromatic progressions
- Color blocking and contrast
- Atmospheric color studies

---

### 4. Spatial-Focused Mood Boards *(Future)*

**Purpose:** Demonstrate spacing systems, rhythm, and compositional balance.

**Visual DNA:**
- Architectural spacing
- Whitespace studies
- Rhythmic patterns
- Compositional balance
- Geometric relationships

---

## Technical Implementation

### API Request Format

```json
{
  "colors": [
    {
      "hex": "#2171B5",
      "name": "IKB Blue",
      "temperature": "cool",
      "saturation_level": "vivid",
      "hue_family": "blue"
    }
  ],
  "focus_type": "material",  // Options: "material", "typography", "color", "spatial"
  "num_variants": 2,
  "include_images": true,
  "num_images_per_variant": 4
}
```

### Claude Prompt Structure

#### Base Prompt (All Types)
```
You are an expert design curator and art historian. Analyze these extracted
design tokens and generate {num_variants} distinct mood board themes.

Focus Type: {focus_type}
{focus_type_specific_guidance}

Color Data:
{color_summary}

Generate {num_variants} mood board variants, each with:
1. Theme Name - Evocative and specific to {focus_type}
2. Subtitle - One-line essence
3. Tags - 4-6 descriptive tags
4. Visual Elements - 3-4 descriptions focusing on {focus_type} characteristics
5. Aesthetic References - 2-3 cultural/artistic movements
6. Dominant Colors - 3-4 hex colors from palette
7. Vibe - One word overall feeling
```

#### Material-Specific Guidance
```
MATERIAL FOCUS GUIDANCE:
- Emphasize physical surfaces, textures, and tactile qualities
- Reference materials: anodized aluminum, resin, glass, metal finishes
- Consider light interaction, reflections, and depth
- Think about physical controls and three-dimensional objects
- Visual elements should describe MATERIALS and SURFACES
- Example visual elements:
  * "Brushed aluminum surfaces with circular grain"
  * "Resin swirls with fluid gradient transitions"
  * "Glass spheres with internal phosphor glow"
  * "Tactile polymer buttons with matte finish"
```

#### Typography-Specific Guidance
```
TYPOGRAPHY FOCUS GUIDANCE:
- Emphasize typographic systems, grids, and letterforms
- Reference design movements: Swiss Design, Bauhaus, International Style
- Consider grid systems, baseline alignment, modular rhythm
- Think about technical labels, control glyphs, measurement scales
- Visual elements should describe TYPE SYSTEMS and GRAPHIC LANGUAGE
- Example visual elements:
  * "Bold geometric sans-serif with tight letter spacing"
  * "Industrial panel labels with technical numerics"
  * "Modular grid system with visible baseline"
  * "Icon set with play/stop/pause glyphs"
```

### DALL-E Prompt Variations

#### Material Variations
```python
material_variations = [
    "anodized aluminum surface with brushed metal texture and {colors}",
    "resin and enamel fluid patterns with swirling {colors}",
    "glass globe with internal glow using {colors}",
    "tactile control panel with physical knobs in {colors}",
    "CRT oscilloscope phosphor glow effect with {colors}",
    "metallic surfaces with gradient reflections of {colors}",
]
```

#### Typography Variations
```python
typography_variations = [
    "Swiss grid system with bold sans-serif typography using {colors}",
    "Industrial control panel with frequency markings and labels in {colors}",
    "Modular typographic composition with visible baseline grid, {colors}",
    "Geometric letterforms on technical background, {colors}",
    "Technical signage with control glyphs and measurement scales, {colors}",
    "Asymmetric layout with bold typography and icons, {colors}",
]
```

---

## Visual Examples

### Material-Focused Examples

**Example 1: Retro-Futurist Hardware**
- Theme: "Analog Synth Aesthetic"
- Materials: Brushed gold knobs, IKB blue anodized case, glass indicators
- Visual Elements:
  - Circular brushed metal knobs with radial grain
  - Translucent glass buttons with internal LED glow
  - Resin panel with swirling blue-yellow marble effect
  - Matte polymer surface with tactile grip texture

**Example 2: Material Palette**
- Theme: "Tactile Modernism"
- Materials: Chrome, teal glass, butter yellow enamel
- Visual Elements:
  - Polished chrome dials with reflective surfaces
  - Teal glass panels with light diffusion
  - Yellow enamel coating with smooth glossy finish
  - Matte blue polymer housing with soft-touch feel

---

### Typography-Focused Examples

**Example 1: Swiss Industrial**
- Theme: "Grid + Glyph Systems"
- Typography: Bold geometric sans, technical labels, modular grid
- Visual Elements:
  - "TYPOGRAPHY" in bold caps on structured grid
  - Frequency markings: "20 60 70 10" with measurement scale
  - Control glyphs: play, pause, LR indicators
  - Alphabet specimen showing letterform variations

**Example 2: Technical Interface**
- Theme: "Analog Panel Language"
- Typography: Industrial labels, icon set, numeric systems
- Visual Elements:
  - "INTERFACE" header with technical labeling style
  - Mode labels: "FM/AM", "GAIN", "FREQUENCY"
  - Waveform graphics and oscilloscope traces
  - Geometric icon set for controls and navigation

**Example 3: Typographic Rigor**
- Theme: "Bauhaus Geometry"
- Typography: Modular layout, bold sans, alphabetic display
- Visual Elements:
  - Full alphabet specimen (A-Z) in bold geometric sans
  - Grid-based composition with color blocking
  - Technical numerics: "245 Hz", "AE 035"
  - Geometric shapes integrated with letterforms

---

## Implementation Checklist

- [x] Create MOOD_BOARD_SPECIFICATION.md
- [ ] Update MoodBoardGenerator to accept `focus_type` parameter
- [ ] Add material-specific Claude prompt guidance
- [ ] Add typography-specific Claude prompt guidance
- [ ] Update DALL-E prompt variations for each focus type
- [ ] Add frontend UI to select mood board focus type
- [ ] Test material-focused generation with retro-futurist images
- [ ] Test typography-focused generation with Swiss design palette
- [ ] Document example themes for each focus type
- [ ] Add mood board type selector to API endpoint

---

## Future Enhancements

1. **Multi-Focus Boards** - Combine material + typography in single board
2. **Custom Focus Types** - User-defined focus areas (e.g., "motion", "sound")
3. **Reference Image Upload** - Analyze reference images to guide generation
4. **Style Transfer** - Apply reference image style to generated boards
5. **Interactive Refinement** - User feedback loop to tune board aesthetics
6. **Board Variants** - Generate multiple sub-variants within each focus type
7. **Export Formats** - PDF, Pinterest board, Figma frame exports

---

## Success Metrics

- **Material Boards:** Generated images show clear physical textures and surfaces
- **Typography Boards:** Grid systems and letterforms are prominent and legible
- **Cultural Accuracy:** References are authentic and relevant to palette
- **Visual Cohesion:** All images in a board share aesthetic DNA
- **Token Integration:** Boards meaningfully reflect extracted token data

---

## Notes

- Material and Typography focus types are **complementary** - a design system needs both
- Generated images should respect the color palette (use dominant_colors in prompts)
- Claude should generate distinct themes between variants (avoid repetition)
- DALL-E prompts should be specific enough to avoid generic abstract art
- Consider user's design domain (audio plugins, UI kits, branding) when generating themes
