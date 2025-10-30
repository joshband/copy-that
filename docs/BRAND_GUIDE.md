# GenUI: Visual DNA → Design Systems
## Visual UI Brand Guide

---

## 1. Brand Overview

### Application Name & Tagline
**GenUI: Visual DNA → Design Systems**
*Transform visual inspiration into production-ready component libraries*

### Mission and Purpose
GenUI is a web-based tool that transforms visual inspiration (reference images) into production-ready component libraries. It extracts visual DNA, detects patterns, creates style rules, and generates UI components through an intelligent, multi-phase pipeline.

### Target Audience
- **UI/UX Designers** seeking to rapidly prototype design systems from visual references
- **Frontend Developers** needing consistent component libraries
- **Design System Architects** building scalable design foundations
- **Product Teams** translating design inspiration into actionable components

### Brand Personality
- **Intelligent**: Automated analysis and pattern recognition
- **Progressive**: Step-by-step guided workflow
- **Modern**: Clean, contemporary aesthetic
- **Trustworthy**: Reliable, consistent results
- **Empowering**: Transforms inspiration into production-ready assets
- **Precise**: Data-driven design decisions

---

## 2. Color Palette

### Color Philosophy

GenUI uses **two distinct color systems** that serve different purposes:

1. **Application Colors**: Standardized colors for the GenUI web application interface (purple gradient brand identity)
2. **Generative Colors**: Dynamically extracted colors from reference images to create cinematic, emotionally resonant design systems

---

### 2.1 Application Colors (GenUI Interface)

**Purpose**: Used throughout the GenUI web application for branding, navigation, controls, and interface elements.

#### Purple Gradient (Brand Identity)
```css
/* Primary Gradient */
linear-gradient(135deg, #667eea 0%, #764ba2 100%)

/* Individual Colors */
#667eea  /* Purple Blue */
rgb(102, 126, 234)
hsl(229, 76%, 66%)

#764ba2  /* Deep Purple */
rgb(118, 75, 162)
hsl(270, 37%, 46%)
```

**Usage**: Header backgrounds, progress bars, step indicators (running state), primary buttons, accent strips, brand elements

**Accessibility**: Provides sufficient contrast against white text (4.51:1 for #667eea, 7.32:1 for #764ba2)

#### Success Green
```css
#4CAF50
rgb(76, 175, 80)
hsl(122, 39%, 49%)
```

**Usage**: Completed states, checkmarks, success indicators, save buttons, completion rings

#### Pink Gradient (Accent)
```css
/* Dice/Random Generator */
linear-gradient(135deg, #f093fb 0%, #f5576c 100%)
```

**Usage**: Special action buttons (dice/random generator), playful interactions

#### Background Colors

```css
#f8f9fa  /* Light Gray - Primary Background */
#ffffff  /* White - Card Backgrounds */
#f8f9ff  /* Light Purple Tint - Upload Area */
#eef0ff  /* Light Purple - Upload Hover */
#e0e5ff  /* Medium Purple - Upload Dragover */
```

#### Text Colors

```css
#2c3e50  /* Primary Text - Dark Blue Gray (12.63:1 AAA) */
#333333  /* Secondary Dark Text (12.63:1 AAA) */
#666666  /* Tertiary Text - Medium Gray (5.74:1 AA) */
#999999  /* Light Text - Hints & Placeholders */
#555555  /* Activity Log Text */
```

#### Border & Neutral Colors

```css
#e0e0e0  /* Light Gray - Borders & Dividers */
#f0f0f0  /* Button Background - Secondary */
#cccccc  /* Disabled State */
#888888  /* Disabled Text */
```

---

### 2.2 Generative Color System (Extracted from Visual Analysis)

**Purpose**: Dynamically extracted colors from reference images to create cohesive, emotionally resonant design systems for generated UI components.

#### Color Extraction Architecture

GenUI analyzes reference images and constructs a **full-spectrum color system** with four tiers:

**Tier 1: Primary Brand Color** (1 color)
**Tier 2: Primary Palette** (5-8 colors)
**Tier 3: Secondary Palette - Dark Shades** (4-6 colors)
**Tier 4: Secondary Palette - Light Shades** (4-6 colors)
**Tier 5: Monochromatic Foundation** (blacks, grays, whites)

---

#### Tier 1: Primary Brand Color

```python
# Extracted as the most dominant, saturated color from reference images
primary_brand_color = extract_dominant_color(reference_images)

# Example from red-themed design:
primary_brand = {
    'hex': '#cc3333',
    'rgb': (204, 51, 51),
    'hsl': (0, 60%, 50%),
    'role': 'Primary brand identity, CTAs, key UI elements'
}
```

**Characteristics**:
- Most saturated, prominent color in the visual analysis
- Used for primary buttons, links, key interactive elements
- Applied more frequently than any other color
- Establishes brand recognition and emotional tone

**Usage Frequency**: 40-50% of colored UI elements

---

#### Tier 2: Primary Palette (Cinematic Color Spectrum)

```python
# Extracted to provide tonal variation, emotion, and contrast
# 5-8 complementary colors from analyzed content
primary_palette = extract_primary_palette(reference_images, count=7)

# Example from red-themed industrial design:
primary_palette = [
    {'hex': '#f9acb6', 'rgb': (249, 172, 182), 'role': 'Soft accents, backgrounds'},
    {'hex': '#d5b9b1', 'rgb': (213, 185, 177), 'role': 'Warm neutrals, surfaces'},
    {'hex': '#d63443', 'rgb': (214, 52, 67),   'role': 'Strong accents, emphasis'},
    {'hex': '#f7f0e6', 'rgb': (247, 240, 230), 'role': 'Light backgrounds, cards'},
    {'hex': '#8d6542', 'rgb': (141, 101, 66),  'role': 'Earth tones, depth'},
    {'hex': '#d6d1be', 'rgb': (214, 209, 190), 'role': 'Neutral surfaces'},
    {'hex': '#19160f', 'rgb': (25, 22, 15),    'role': 'Deep shadows, text'}
]
```

**Extraction Criteria**:
- Colors that provide tonal variation and emotional resonance
- Complementary colors that create visual harmony
- Colors that appear prominently in reference composition
- Range includes warm/cool, light/dark, saturated/muted
- Creates a "cinematic" quality through intentional color relationships

**Color Theory Principles Applied**:
- **Complementary contrast**: Colors opposite on color wheel (e.g., red + teal)
- **Analogous harmony**: Colors adjacent on color wheel (e.g., red, orange, yellow-orange)
- **Triadic balance**: Three colors evenly spaced on color wheel
- **Split-complementary**: Base color + two colors adjacent to its complement
- **Emotional mapping**: Warm colors (energy, passion) vs cool colors (calm, trust)

**Usage Frequency**: 30-40% of colored UI elements (distributed across palette)

---

#### Tier 3: Secondary Palette - Dark Shades

```python
# Darker shades of primary palette for depth, contrast, and tone variation
# Generated algorithmically from primary palette
dark_shades = generate_dark_shades(primary_palette, luminance_reduction=0.3-0.6)

# Example from red-themed design:
dark_shades = [
    {'hex': '#9e0013', 'rgb': (158, 0, 19),   'role': 'Dark emphasis, borders'},
    {'hex': '#8f000b', 'rgb': (143, 0, 11),   'role': 'Darker accents'},
    {'hex': '#750000', 'rgb': (117, 0, 0),    'role': 'Deep backgrounds'},
    {'hex': '#550000', 'rgb': (85, 0, 0),     'role': 'Shadows, depth'},
    {'hex': '#3e0003', 'rgb': (62, 0, 3),     'role': 'Darkest tones'}
]
```

**Generation Algorithm**:
```python
def generate_dark_shades(primary_palette, count=5):
    """Generate darker shades by reducing luminance while preserving hue"""
    dark_shades = []
    for color in primary_palette:
        h, s, l = rgb_to_hsl(color['rgb'])
        # Reduce lightness by 30-60%
        new_lightness = l * (1 - (0.3 + (count * 0.06)))
        # Slightly increase saturation for depth
        new_saturation = min(s * 1.1, 1.0)
        dark_shade = hsl_to_rgb(h, new_saturation, new_lightness)
        dark_shades.append(dark_shade)
    return dark_shades
```

**Usage**:
- Creating depth and visual hierarchy
- Borders, dividers, and subtle contrast
- Text on light backgrounds
- Hover states (darkening effect)
- Establishing dramatic tone or serious emotion
- Shadow colors in layered UI

**Usage Frequency**: 15-20% of colored UI elements

---

#### Tier 4: Secondary Palette - Light Shades

```python
# Lighter shades of primary palette for softness, optimism, and gentle contrast
# Generated algorithmically from primary palette
light_shades = generate_light_shades(primary_palette, luminance_increase=0.3-0.6)

# Example from red-themed design:
light_shades = [
    {'hex': '#ea5048', 'rgb': (234, 80, 72),   'role': 'Bright accents'},
    {'hex': '#ff796b', 'rgb': (255, 121, 107), 'role': 'Soft emphasis'},
    {'hex': '#ff8979', 'rgb': (255, 137, 121), 'role': 'Light backgrounds'},
    {'hex': '#ffa492', 'rgb': (255, 164, 146), 'role': 'Subtle highlights'},
    {'hex': '#ffbca8', 'rgb': (255, 188, 168), 'role': 'Pastel tones'}
]
```

**Generation Algorithm**:
```python
def generate_light_shades(primary_palette, count=5):
    """Generate lighter shades by increasing luminance while preserving hue"""
    light_shades = []
    for color in primary_palette:
        h, s, l = rgb_to_hsl(color['rgb'])
        # Increase lightness by 30-60%
        new_lightness = min(l + (0.3 + (count * 0.06)), 0.95)
        # Reduce saturation slightly for softness
        new_saturation = s * 0.8
        light_shade = hsl_to_rgb(h, new_saturation, new_lightness)
        light_shades.append(light_shade)
    return light_shades
```

**Usage**:
- Shifting tone to softer, more optimistic energy
- Light backgrounds, cards, surfaces
- Subtle accents and highlights
- Hover states (lightening effect)
- Reducing visual weight while maintaining brand
- Creating friendly, approachable mood

**Usage Frequency**: 15-20% of colored UI elements

---

#### Tier 5: Monochromatic Foundation

```python
# Universal neutral colors for text, backgrounds, and structure
monochromatic_foundation = {
    'blacks': [
        {'hex': '#000000', 'rgb': (0, 0, 0),       'role': 'Pure black (sparingly)'},
        {'hex': '#19160f', 'rgb': (25, 22, 15),    'role': 'Near-black with warmth'},
        {'hex': '#1a1a1a', 'rgb': (26, 26, 26),    'role': 'Dark UI backgrounds'},
        {'hex': '#2c2c2c', 'rgb': (44, 44, 44),    'role': 'Dark surfaces'}
    ],
    'grays': [
        {'hex': '#333333', 'rgb': (51, 51, 51),    'role': 'Primary text (light bg)'},
        {'hex': '#555555', 'rgb': (85, 85, 85),    'role': 'Secondary text'},
        {'hex': '#666666', 'rgb': (102, 102, 102), 'role': 'Tertiary text'},
        {'hex': '#888888', 'rgb': (136, 136, 136), 'role': 'Disabled text'},
        {'hex': '#999999', 'rgb': (153, 153, 153), 'role': 'Placeholder text'},
        {'hex': '#cccccc', 'rgb': (204, 204, 204), 'role': 'Disabled states'},
        {'hex': '#e0e0e0', 'rgb': (224, 224, 224), 'role': 'Borders, dividers'},
        {'hex': '#f0f0f0', 'rgb': (240, 240, 240), 'role': 'Light surfaces'},
        {'hex': '#f5f5f5', 'rgb': (245, 245, 245), 'role': 'Background tint'}
    ],
    'whites': [
        {'hex': '#ffffff', 'rgb': (255, 255, 255), 'role': 'Pure white'},
        {'hex': '#fafafa', 'rgb': (250, 250, 250), 'role': 'Off-white'},
        {'hex': '#f8f8f8', 'rgb': (248, 248, 248), 'role': 'Subtle background'}
    ]
}
```

**Usage**: Text, backgrounds, borders, structural elements (always present regardless of color theme)

---

### Color Extraction Process

**Step 1: Image Analysis**
```
Reference Images → K-Means Clustering → Dominant Colors (16-20 clusters)
├─ Extract RGB values from all pixels
├─ Apply k-means clustering (16-20 clusters)
├─ Weight by frequency and saturation
└─ Filter out near-blacks/whites for color palette
```

**Step 2: Primary Brand Color Selection**
```
Dominant Colors → Saturation + Prominence Analysis → Primary Brand Color
├─ Identify most saturated color with highest frequency
├─ Validate against image composition (position, usage)
└─ Select single primary brand color
```

**Step 3: Primary Palette Construction**
```
Dominant Colors → Color Theory Analysis → Primary Palette (5-8 colors)
├─ Apply color harmony rules (complementary, analogous, triadic)
├─ Ensure tonal variation (light, mid, dark tones)
├─ Balance warm and cool colors
├─ Validate emotional resonance
└─ Extract 5-8 complementary colors
```

**Step 4: Secondary Palette Generation**
```
Primary Palette → Shade Generation → Dark Shades + Light Shades
├─ Generate 4-6 darker shades (luminance -30% to -60%)
├─ Generate 4-6 lighter shades (luminance +30% to +60%)
├─ Preserve hue relationships
└─ Validate readability and contrast
```

**Step 5: Contrast Validation**
```
All Colors → WCAG Contrast Checking → Accessibility Validation
├─ Test all text/background combinations
├─ Ensure minimum 4.5:1 for body text (AA)
├─ Ensure minimum 3:1 for large text/UI (AA)
└─ Flag combinations that fail accessibility
```

**Step 6: Usage Distribution**
```
Complete Palette → Usage Frequency Assignment → Component Application
├─ Primary Brand: 40-50%
├─ Primary Palette: 30-40%
├─ Dark Shades: 15-20%
├─ Light Shades: 15-20%
└─ Monochromatic: Always present for structure
```

---

### Color Application Strategy

#### Frequency Hierarchy

**1. Primary Brand Color** (Most Used)
```css
/* Applied to: */
- Primary buttons (background)
- Primary links (text color)
- Active states (borders, highlights)
- Key icons and illustrations
- Brand elements (logos, badges)
```

**Usage**: 40-50% of all colored UI elements

**2. Primary Palette** (Frequently Used)
```css
/* Applied to: */
- Secondary buttons (backgrounds)
- Accent backgrounds (cards, panels)
- Data visualization (charts, graphs)
- Status indicators (info, warning, success)
- Illustrations and imagery
- Gradient combinations
```

**Usage**: 30-40% distributed across palette colors

**3. Dark Shades** (Moderate Use)
```css
/* Applied to: */
- Text on light backgrounds
- Borders and dividers (subtle)
- Hover states (darkening)
- Box shadows and depth
- Dark mode UI (when applicable)
```

**Usage**: 15-20%

**4. Light Shades** (Moderate Use)
```css
/* Applied to: */
- Light backgrounds (cards, sections)
- Hover states (lightening)
- Subtle accents and highlights
- Tinted backgrounds
- Soft overlays
```

**Usage**: 15-20%

**5. Monochromatic Foundation** (Always Present)
```css
/* Applied to: */
- Body text (blacks/grays)
- Page backgrounds (whites/light grays)
- Structural elements (borders, dividers)
- Disabled states (mid grays)
- Secondary UI elements
```

**Usage**: Present throughout for structure and hierarchy

---

### Gradient Usage

**Principle**: Gradients are used ONLY when visual analysis indicates they fit the reference style.

**Detection Criteria**:
```python
def should_use_gradients(reference_images):
    """Determine if gradients fit the visual style"""
    gradient_indicators = {
        'smooth_color_transitions': detect_soft_edges(images),
        'multi_color_surfaces': count_color_transitions(images),
        'depth_through_color': analyze_shading_patterns(images),
        'modern_aesthetic': detect_flat_vs_dimensional(images)
    }
    return gradient_indicators['score'] > 0.6
```

**Gradient Types**:
```css
/* Linear gradients - directional flow */
background: linear-gradient(135deg, #primary 0%, #secondary 100%);

/* Radial gradients - depth and focus */
background: radial-gradient(circle, #primary 0%, #secondary 100%);

/* Multi-stop gradients - complex transitions */
background: linear-gradient(135deg,
    #color1 0%,
    #color2 33%,
    #color3 66%,
    #color4 100%
);
```

**Gradient Application**:
- Backgrounds for depth and dimension
- Buttons for visual interest
- Overlays for emphasis
- Data visualization (heatmaps)
- Only when style analysis supports it

---

### Color Theory Principles

**1. Complementary Contrast**
- Use colors opposite on color wheel
- Creates visual tension and energy
- Example: Red (#cc3333) + Teal (#33cccc)

**2. Analogous Harmony**
- Use colors adjacent on color wheel
- Creates cohesive, harmonious feel
- Example: Red (#cc3333) + Orange (#ff6633) + Pink (#ff3366)

**3. Triadic Balance**
- Use three colors evenly spaced (120°)
- Creates vibrant, balanced palette
- Example: Red, Yellow, Blue

**4. Split-Complementary**
- Base color + two adjacent to complement
- Softer than pure complementary
- Example: Red + Yellow-Green + Blue-Green

**5. Monochromatic Variation**
- Single hue with varying saturation/lightness
- Creates subtle, sophisticated look
- Example: Red → Light Pink → Dark Maroon

**6. 60-30-10 Rule**
- 60% dominant color (primary brand)
- 30% secondary colors (primary palette)
- 10% accent colors (highlights, CTAs)

**7. Emotional Mapping**
- Warm colors (red, orange, yellow): Energy, passion, excitement
- Cool colors (blue, green, purple): Calm, trust, professionalism
- Neutral colors (gray, beige): Balance, sophistication

**8. Saturation Hierarchy**
- Most saturated: CTAs, key interactive elements
- Mid saturation: Supporting UI, backgrounds
- Low saturation: Disabled states, subtle elements

---

### Color Usage Guidelines

#### Generative Color Rules

1. **Primary Dominance**: Primary brand color should appear most frequently (40-50%)
2. **Palette Distribution**: Use all primary palette colors but balance usage (no color >15%)
3. **Shade Moderation**: Dark/light shades are supporting roles (15-20% each)
4. **Monochromatic Foundation**: Always use blacks/grays/whites for text and structure
5. **Saturation Priority**: Most saturated colors for most important UI elements
6. **Contrast Validation**: All text must meet WCAG AA minimum (4.5:1 body, 3:1 large)
7. **Gradient Conditional**: Only use gradients when style analysis indicates appropriateness
8. **Color Theory**: Apply harmonious color relationships from analysis
9. **Emotional Alignment**: Color choices must match intended emotional tone
10. **Accessibility First**: Never sacrifice readability for aesthetic

#### Application Color Rules (GenUI Interface)

1. **Brand Consistency**: Always use purple gradient for GenUI brand elements
2. **Success Indicators**: Green only for completed/success states
3. **Backgrounds**: Light gray (#f8f9fa) for pages, white for cards
4. **Text Hierarchy**: Dark blue-gray (#2c3e50) for primary text, never pure black
5. **Focus States**: Purple gradient at reduced opacity (20-30%)

#### Cross-System Rule

**Never mix application colors with generative colors** - GenUI purple branding stays in the tool interface, extracted colors stay in generated components

---

## 3. Typography

### Typography Philosophy

GenUI uses **two distinct typography systems** that serve different purposes:

1. **Application Typography**: Standardized fonts used consistently across the GenUI application interface itself
2. **Generative Typography**: Dynamic font selection for generated UI components based on visual style analysis

---

### 3.1 Application Typography

**Purpose**: Used throughout the GenUI web application for all interface elements, navigation, controls, and content display.

#### Primary Application Fonts

```css
/* Primary Application Font: ABC Repro */
font-family: 'ABC Repro', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Secondary Application Font: Inter Tight */
font-family: 'Inter Tight', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Monospace (Activity Log, Code Snippets) */
font-family: 'Monaco', 'Courier New', 'Consolas', monospace;
```

**Font Usage Guidelines:**
- **ABC Repro**: Primary for headings, titles, step names, and prominent UI elements
- **Inter Tight**: Secondary for body text, descriptions, labels, and data display
- **Monospace**: Activity logs, technical output, code examples

**Rationale**:
- ABC Repro provides distinctive, modern character ideal for design-focused branding
- Inter Tight offers excellent readability and web optimization for interface text
- System font fallbacks ensure universal compatibility

#### Application Font Sizes

```css
/* Headings (ABC Repro) */
h1: 2.5rem (40px)      /* Main page title "GenUI: Visual DNA → Design Systems" */
h2: 1.5rem (24px)      /* Section headings */
h3: 1.125rem (18px)    /* Subsection headings */
h4: 1rem (16px)        /* Card headings */

/* Body Text (Inter Tight) */
body: 1rem (16px)      /* Base font size */
.subtitle: 1.1rem (17.6px)
.upload-text: 1.3rem (20.8px)
.upload-hint: 0.95rem (15.2px)

/* Small Text (Inter Tight) */
.step-name: 0.9rem (14.4px)
.step-progress: 0.75rem (12px)
.reference-badge: 0.85rem (13.6px)
.result-label: 0.95rem (15.2px)

/* Large Display (ABC Repro) */
.upload-icon: 4rem (64px)     /* Emoji size */
.result-value: 2.5rem (40px)  /* Stat numbers */
.dice-button: 3rem (48px)     /* Large emoji icon */

/* Monospace (Activity Log) */
.activity-log: 0.875rem (14px)
```

#### Application Font Weights

```css
/* ABC Repro Weights */
400  /* Regular - Standard headings */
500  /* Medium - Emphasized headings */
700  /* Bold - Primary headings (h1) */

/* Inter Tight Weights */
400  /* Regular - Body text, labels */
500  /* Medium - Step names, component names */
600  /* Semibold - Buttons, upload text, completed steps */
700  /* Bold - Result values, important data */
```

#### Application Line Heights

```css
/* ABC Repro (Headings) */
h1: 1.2            /* Tight for large display */
h2-h4: 1.3         /* Slightly relaxed for medium headings */

/* Inter Tight (Body) */
body: 1.6          /* Comfortable reading */
.subtitle: 1.4     /* Subheadings */
lists: 1.8         /* List items - extra spacing */
buttons: 1.5       /* Button text */
```

#### Application Letter Spacing

```css
/* ABC Repro */
h1: -0.02em        /* Tighter for large display */
h2-h4: 0           /* Default */

/* Inter Tight */
body: 0            /* Default */
.step-name: 0.01em /* Slightly open for readability */
buttons: 0.02em    /* More open for clarity */
```

---

### 3.2 Generative Typography

**Purpose**: Dynamically selected open-source fonts for generated UI components that match the visual style analysis from reference images.

#### Typography Analysis System

When analyzing reference images, GenUI extracts comprehensive typographic characteristics:

**1. Font Family Selection**
```python
# Analysis extracts style characteristics:
- Serif vs Sans-serif vs Monospace vs Display
- Geometric vs Humanist vs Grotesque
- Modern vs Classic vs Decorative
- Condensed vs Regular vs Extended width

# Dynamic font matching from curated open-source library:
geometric_sans = ['Montserrat', 'Raleway', 'Poppins', 'Quicksand']
humanist_sans = ['Open Sans', 'Lato', 'Source Sans Pro', 'Nunito']
grotesque_sans = ['Work Sans', 'IBM Plex Sans', 'DM Sans']
serif_modern = ['Playfair Display', 'Merriweather', 'Crimson Text']
serif_classic = ['Libre Baskerville', 'EB Garamond', 'Lora']
monospace = ['Roboto Mono', 'Source Code Pro', 'JetBrains Mono']
display = ['Bebas Neue', 'Righteous', 'Fredoka One']
```

**2. Tracking (Letter Spacing)**
```python
# Extracted from reference images:
tracking_values = {
    'very_tight': -0.05em,    # Condensed, dramatic headings
    'tight': -0.02em,         # Refined headings
    'normal': 0,              # Standard body text
    'open': 0.05em,           # Spacious, modern UI
    'very_open': 0.1em        # Architectural, luxury brands
}

# Applied to generated components based on style analysis
```

**3. Leading (Line Height)**
```python
# Extracted spacing ratios from reference layouts:
leading_values = {
    'tight': 1.2,          # Dense information, data tables
    'normal': 1.5,         # Standard UI text
    'relaxed': 1.8,        # Long-form reading
    'loose': 2.0           # Editorial, luxury spacing
}

# Calculated based on context: headings vs body vs UI labels
```

**4. Typesetting & Alignment**
```python
# Pattern detection identifies:
alignment_patterns = {
    'left': 'Standard alignment',
    'center': 'Symmetrical, modern',
    'right': 'Asymmetric, editorial',
    'justify': 'Traditional, formal'
}

# Grid integration:
baseline_grid = True/False  # Detected from reference spacing
text_columns = 1-3          # Multi-column layouts detected
```

**5. Size Hierarchy**
```python
# Extracted scale from reference images:
size_hierarchy = {
    'h1': 2.5-4rem,        # Hero headings
    'h2': 1.75-2.5rem,     # Section headings
    'h3': 1.25-1.75rem,    # Subsection headings
    'body': 1rem,          # Base size (always 16px)
    'small': 0.875rem,     # Labels, captions
    'tiny': 0.75rem        # Metadata
}

# Modular scale detected (e.g., 1.250 Major Third, 1.414 Augmented Fourth)
```

**6. Color Application**
```python
# Text colors extracted from visual DNA:
text_colors = {
    'primary': extracted_dark_color,      # Main body text
    'secondary': extracted_muted_color,   # Supporting text
    'accent': extracted_brand_color,      # Links, emphasis
    'inverse': extracted_light_color      # Text on dark backgrounds
}

# Contrast ratios validated (WCAG AA minimum 4.5:1)
```

**7. Weight Distribution**
```python
# Weight usage patterns detected:
weight_system = {
    'light': 300,          # Large headings, elegant
    'regular': 400,        # Body text
    'medium': 500,         # UI labels, navigation
    'semibold': 600,       # Buttons, emphasis
    'bold': 700,           # Strong headings
    'extrabold': 800       # Display, impact
}

# Usage frequency extracted from reference composition
```

**8. Hierarchy Expression**
```python
# Overall typographic hierarchy style:
hierarchy_styles = {
    'dramatic': {
        'contrast': 'high',      # Large size jumps
        'weight_contrast': 'high' # Bold vs light
    },
    'subtle': {
        'contrast': 'low',       # Similar sizes
        'weight_contrast': 'medium'
    },
    'rhythmic': {
        'scale': 'modular',      # Mathematical scale
        'spacing': 'consistent'  # Regular intervals
    }
}
```

#### Generative Typography Implementation

**Step 1: Visual Analysis**
```
Reference Image → Visual DNA Extraction → Typography Signature
├─ Detect font characteristics (serif/sans/mono)
├─ Measure letter spacing patterns
├─ Calculate line height ratios
├─ Extract size hierarchy scale
├─ Identify weight distribution
└─ Analyze alignment patterns
```

**Step 2: Font Matching**
```
Typography Signature → Open Source Font Library → Best Match
├─ Match style characteristics (geometric, humanist, etc.)
├─ Match weight availability (need 400-700?)
├─ Match character width (condensed, regular, extended)
└─ Validate Google Fonts availability
```

**Step 3: Parametric Application**
```
Matched Font + Extracted Parameters → Generated Components
├─ Apply tracking values to headings/body/UI
├─ Set leading for each text context
├─ Implement size hierarchy scale
├─ Apply weight distribution pattern
├─ Set alignment based on layout grid
└─ Apply extracted text colors with contrast validation
```

#### Open Source Font Library (Curated)

**Sans-Serif Geometric**
- Montserrat (9 weights) - Modern, versatile
- Raleway (18 weights) - Elegant, refined
- Poppins (18 weights) - Friendly, geometric
- Quicksand (7 weights) - Rounded, playful

**Sans-Serif Humanist**
- Open Sans (10 weights) - Neutral, readable
- Lato (10 weights) - Warm, corporate
- Source Sans Pro (12 weights) - Clean, technical
- Nunito (14 weights) - Friendly, rounded

**Sans-Serif Grotesque**
- Work Sans (9 weights) - Industrial, strong
- IBM Plex Sans (14 weights) - Technical, modern
- DM Sans (10 weights) - Minimal, refined

**Serif Modern**
- Playfair Display (12 weights) - Elegant, high contrast
- Merriweather (8 weights) - Readable, friendly
- Crimson Text (12 weights) - Classic, refined

**Serif Classic**
- Libre Baskerville (3 weights) - Traditional, reliable
- EB Garamond (10 weights) - Classic, sophisticated
- Lora (8 weights) - Calligraphic, warm

**Monospace**
- Roboto Mono (14 weights) - Technical, readable
- Source Code Pro (14 weights) - Code-focused
- JetBrains Mono (16 weights) - Developer-focused

**Display**
- Bebas Neue (1 weight) - Bold, impactful
- Righteous (1 weight) - Strong, geometric
- Fredoka One (1 weight) - Playful, rounded

---

### Typography Guidelines

#### Application Typography Rules

1. **Consistency**: Always use ABC Repro for headings, Inter Tight for body text within GenUI app
2. **Hierarchy**: Maintain clear size distinctions (minimum 2px difference between levels)
3. **Readability**: Never use font sizes below 12px (0.75rem) in application interface
4. **Weight Consistency**: Use 600 weight for all interactive elements (buttons, links)
5. **Line Length**: Maximum 75 characters per line for comfortable reading
6. **Emoji Sizing**: Use rem units for consistent emoji scaling across devices
7. **Responsive Scaling**: Font sizes scale proportionally with viewport on mobile devices

#### Generative Typography Rules

1. **Style Fidelity**: Selected fonts must closely match visual characteristics from reference images
2. **Weight Availability**: Ensure selected fonts have all required weights (minimum 400, 600, 700)
3. **Contrast Validation**: All text/background combinations must meet WCAG AA (4.5:1 for body, 3:1 for large text)
4. **Open Source Only**: Only use fonts from Google Fonts or other permissive licenses
5. **Fallback Strategy**: Always provide system font fallbacks for robustness
6. **Performance**: Limit to 2-3 font families per generated design system (max 6 weights total)
7. **Tracking Limits**: Letter spacing should not exceed -0.05em to 0.15em for readability
8. **Leading Constraints**: Line height should stay within 1.2 to 2.2 range based on context

---

## 4. Spacing & Layout

### Spacing Scale (8px Base Unit)

```css
/* Base Unit: 8px */
4px   /* 0.5× - Subtle accents, tight spacing */
8px   /* 1× - Minimum touch target */
10px  /* 1.25× - Small gaps */
12px  /* 1.5× - Component internal spacing */
15px  /* ~2× - Standard gaps */
20px  /* 2.5× - Section padding, card spacing */
25px  /* ~3× - Detail sections */
30px  /* 3.75× - Card padding, major sections */
40px  /* 5× - Large padding, major spacing */
60px  /* 7.5× - Upload area padding */
```

### Container Widths

```css
.container {
    max-width: 1200px;      /* Main content container */
    margin: 0 auto;         /* Center alignment */
}

/* Responsive Breakpoint */
@media (min-width: 768px) {
    /* Increased padding on tablets and desktop */
}
```

### Padding Values

```css
/* Cards */
.main-card: 30px (mobile), 40px (desktop)
.reference-info: 15px
.result-card: 20px
.component-item: 20px

/* Interactive Areas */
.upload-area: 60px 40px (vertical horizontal)
.header: 30px 20px

/* Containers */
.container: 20px
.activity-log: 20px
```

### Margin Values

```css
/* Vertical Rhythm */
header: -20px -20px 30px -20px  /* Negative for full-bleed effect */
.main-card: margin-bottom 30px
.progress-container: 40px 0
.pipeline-steps: 40px 0
.step-content: 40px 0
.btn-group: margin-top 30px

/* Component Spacing */
h1: margin-bottom 10px
.step-circle: margin 0 auto 15px
.step-progress: margin-top 5px
```

### Grid Systems

```css
/* Reference Images Grid */
.references-preview {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

/* Results Grid */
.results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
}

/* Component Showcase */
.component-showcase {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 20px;
}
```

### Spacing Guidelines

1. **Consistency**: Always use multiples of 4px (ideally 8px)
2. **Touch Targets**: Minimum 40x40px for interactive elements (buttons, clickable areas)
3. **Visual Breathing Room**: Minimum 20px between major sections
4. **Card Spacing**: Consistent 30-40px internal padding
5. **Grid Gaps**: 20px standard gap for all grid layouts
6. **Responsive Spacing**: Reduce padding by 25-33% on mobile devices

---

## 5. Components

### Buttons

#### Primary Button
```css
.btn-primary {
    padding: 15px 40px;
    border: none;
    border-radius: 10px;
    font-size: 1.1rem;
    font-weight: 600;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    cursor: pointer;
    transition: all 0.3s;
}

/* Hover State */
.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}

/* Disabled State */
.btn-primary:disabled {
    background: #ccc !important;
    color: #888 !important;
    cursor: not-allowed;
    opacity: 0.6;
}
```

#### Secondary Button
```css
.btn-secondary {
    padding: 15px 40px;
    border: none;
    border-radius: 10px;
    font-size: 1.1rem;
    font-weight: 600;
    background: #f0f0f0;
    color: #333;
    cursor: pointer;
    transition: all 0.3s;
}

/* Hover State */
.btn-secondary:hover {
    background: #e0e0e0;
}
```

#### Special Action Button (Dice)
```css
.dice-button {
    width: 120px;
    height: 120px;
    border-radius: 20px;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    font-size: 3rem;
    border: none;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 10px 30px rgba(245, 87, 108, 0.3);
}

/* Hover State */
.dice-button:hover {
    transform: scale(1.1) rotate(10deg);
}

/* Active State */
.dice-button:active {
    transform: scale(0.95) rotate(-10deg);
}
```

### Cards

#### Main Card
```css
.main-card {
    background: white;
    border-radius: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    padding: 30px; /* 40px on desktop */
    margin-bottom: 30px;
    min-height: 700px;
}
```

#### Reference Card
```css
.reference-card {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s;
}

/* Hover State */
.reference-card:hover {
    transform: translateY(-5px);
}
```

#### Result Card
```css
.result-card {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
```

#### Component Item Card
```css
.component-item {
    background: white;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s;
    cursor: pointer;
}

/* Hover State */
.component-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}
```

### Upload Area

```css
.upload-area {
    border: 3px dashed #667eea;
    border-radius: 15px;
    padding: 60px 40px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    background: #f8f9ff;
}

/* Hover State */
.upload-area:hover {
    background: #eef0ff;
    border-color: #764ba2;
}

/* Dragover State */
.upload-area.dragover {
    background: #e0e5ff;
    border-color: #667eea;
    transform: scale(1.02);
}
```

### Progress Bar

```css
.progress-bar {
    width: 100%;
    height: 40px;
    background: #e0e0e0;
    border-radius: 20px;
    overflow: hidden;
    position: relative;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    transition: width 0.5s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
}
```

### Step Indicators

#### Pipeline Steps Container
```css
.pipeline-steps {
    display: flex;
    justify-content: space-between;
    margin: 40px 0;
    position: relative;
}

/* Connection Line */
.pipeline-steps::before {
    content: '';
    position: absolute;
    top: 30px;
    left: 5%;
    right: 5%;
    height: 3px;
    background: #e0e0e0;
    z-index: 0;
}
```

#### Step Circle
```css
.step-circle {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: white;
    border: 3px solid #e0e0e0;
    margin: 0 auto 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    transition: all 0.3s;
    cursor: pointer;
    position: relative;
}
```

#### Step States

**Pending State:**
```css
.step.pending {
    opacity: 0.2;
}

.step.pending .step-circle {
    background: white;
    border: 3px solid #e0e0e0;
    opacity: 0.3;
}
```

**Running State:**
```css
.step.running {
    opacity: 1;
    animation: fadeInOut 2s ease-in-out infinite;
}

.step.running .step-circle {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-color: #764ba2;
    color: white;
    animation: processingPulse 1.2s ease-in-out infinite;
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.4);
}

@keyframes processingPulse {
    0%, 100% {
        transform: scale(1);
        filter: saturate(0.8) brightness(0.9);
        box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
    }
    50% {
        transform: scale(1.05);
        filter: saturate(1.2) brightness(1.1);
        box-shadow: 0 0 25px rgba(102, 126, 234, 0.5);
    }
}
```

**Completed State:**
```css
.step.completed {
    opacity: 1;
}

.step.completed .step-circle {
    background: #667eea;
    border-color: #667eea;
    color: white;
}

/* Green completion ring */
.step.completed .step-circle::after {
    content: '';
    position: absolute;
    top: -5px;
    left: -5px;
    right: -5px;
    bottom: -5px;
    border-radius: 50%;
    border: 3px solid #4CAF50;
    animation: completionRing 0.6s ease-out;
}

@keyframes completionRing {
    0% {
        transform: scale(0.8);
        opacity: 0;
    }
    50% {
        transform: scale(1.1);
        opacity: 1;
    }
    100% {
        transform: scale(1);
        opacity: 1;
    }
}
```

**Active State:**
```css
.step.active .step-circle {
    transform: scale(1.1);
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
}
```

### Activity Log

```css
.activity-log {
    background: white;
    border: 1px solid #e0e0e0;
    border-left: 4px solid #667eea;  /* Accent strip */
    border-radius: 12px;
    padding: 20px;
    margin: 20px 0;
    min-height: 120px;
    max-height: 150px;
    overflow-y: auto;
    font-family: 'Monaco', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.8;
    opacity: 0;
    transition: opacity 0.3s ease;
}

/* Activity message styling */
.activity-message {
    margin-bottom: 5px;
}

.timestamp {
    color: #999;
}

.activity-bullet {
    color: #667eea;
}
```

### Component States Summary

| Component | Default | Hover | Active | Disabled | Focus |
|-----------|---------|-------|--------|----------|-------|
| Primary Button | Purple gradient | Lift + shadow | Scale down | Gray, reduced opacity | Purple glow |
| Secondary Button | Light gray | Darker gray | Scale down | Reduced opacity | Gray outline |
| Card | White, subtle shadow | Lift -5px | - | - | - |
| Upload Area | Purple tint | Darker tint | Scale 1.02 | - | Purple border |
| Step Circle | Gray border | - | Scale 1.1 + glow | Transparent | - |

---

## 6. Iconography

### Icon Style
GenUI uses **emoji icons** for a friendly, universal, and accessible visual language.

### Icon Sizes

```css
.upload-icon: 4rem (64px)
.step-circle emoji: 1.5rem (24px)
.dice-button emoji: 3rem (48px)
```

### Icon Library

| Icon | Unicode | Usage | Context |
|------|---------|-------|---------|
| 🎨 | U+1F3A8 | Main branding | Page title, design system identity |
| 📤 | U+1F4E4 | Upload | File upload area |
| 📸 | U+1F4F8 | Upload step | First pipeline step |
| 🧬 | U+1F9EC | Visual DNA | DNA analysis step |
| 🔍 | U+1F50D | Patterns | Pattern detection step |
| 📋 | U+1F4CB | Rules | Style rules step |
| 🎨 | U+1F3A8 | Generate | Component generation step |
| ✨ | U+2728 | Showcase | Final showcase step |
| 🔄 | U+1F504 | Activity/Restart | Live updates, restart button |
| 🎲 | U+1F3B2 | Random | Random UI generator |
| 💾 | U+1F4BE | Save | Save action |
| 🗑️ | U+1F5D1 | Delete | Discard action |
| 🔬 | U+1F52C | Processing | Analysis in progress |

### Usage Guidelines

1. **Consistency**: Always use the same emoji for the same action/concept
2. **Size**: Use rem units for scalability
3. **Accessibility**: Always pair emojis with text labels (don't use emojis alone)
4. **Color**: Emojis inherit color from parent elements when possible
5. **Fallback**: Ensure text alternatives exist for screen readers
6. **Cultural Awareness**: Emojis render differently across platforms (acceptable variation)

---

## 7. Shadows & Depth

### Shadow Values

```css
/* Elevation Level 1 - Subtle Cards */
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
/* Usage: result-card, activity-log border */

/* Elevation Level 2 - Standard Cards */
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
/* Usage: reference-card, component-item */

/* Elevation Level 3 - Important Cards */
box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
/* Usage: main-card */

/* Elevation Level 4 - Hover States */
box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
/* Usage: component-item:hover */

/* Elevation Level 5 - Prominent Interactive */
box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
/* Usage: btn-primary:hover (colored shadow) */

/* Special - Dice Button */
box-shadow: 0 10px 30px rgba(245, 87, 108, 0.3);
/* Usage: dice-button (colored shadow) */

/* Glow Effects */
box-shadow: 0 0 20px rgba(102, 126, 234, 0.4);
/* Usage: .step.running (pulsing glow) */

box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
/* Usage: .step.active (focus ring) */
```

### Elevation Levels

| Level | Y-offset | Blur | Opacity | Usage |
|-------|----------|------|---------|-------|
| 0 | 0px | 0px | 0 | Flat elements, text |
| 1 | 4px | 12px | 0.08 | Subtle elevation, result cards |
| 2 | 4px | 12px | 0.10 | Standard cards |
| 3 | 4px | 20px | 0.08 | Important containers |
| 4 | 8px | 20px | 0.15 | Hover states |
| 5 | 10px | 25px | 0.30 | Interactive hover (colored) |

### Shadow Guidelines

1. **Y-Axis Only**: Shadows always cast downward (positive Y values)
2. **No X-Offset**: Centered light source (X = 0)
3. **Blur Radius**: 3-5× the Y-offset for natural diffusion
4. **Color**: Use rgba(0, 0, 0, 0.08-0.15) for neutral shadows
5. **Colored Shadows**: Use brand colors (purple, pink) at 0.3-0.4 opacity for special interactions
6. **Hover Transitions**: Increase Y-offset by 4px and blur by 8px on hover
7. **No Inner Shadows**: All shadows are outer (drop shadows)
8. **Glow vs Shadow**: Glow uses 0 offset with blur, shadow uses Y-offset with blur

---

## 8. Border Radius

### Radius Values

```css
/* Component Radius Scale */
6px   /* Small elements - live color swatches */
8px   /* Standard small - images, inner elements, buttons (small) */
10px  /* Standard buttons */
12px  /* Medium cards - reference-card, result-card, component-item, activity-log */
15px  /* Large interactive - upload-area */
20px  /* Extra large - main-card, header, dice-button, progress-bar, reference-badge */

/* Circular */
50%   /* Perfectly round - step-circle, pill badges */
```

### Component Radius Guide

| Component | Radius | Rationale |
|-----------|--------|-----------|
| Main Card | 20px | Large, prominent container |
| Header | 0 0 20px 20px | Top full-bleed, bottom rounded |
| Reference Card | 12px | Medium card |
| Result Card | 12px | Medium card |
| Component Item | 12px | Medium card |
| Button | 10px | Standard interactive |
| Dice Button | 20px | Large, playful interaction |
| Upload Area | 15px | Large interactive zone |
| Progress Bar | 20px | Large, prominent |
| Activity Log | 12px | Medium container |
| Step Circle | 50% | Perfect circle |
| Image Elements | 8px | Subtle rounding |
| Color Swatches | 6-8px | Small elements |
| Reference Badge | 20px | Pill shape |

### Border Radius Guidelines

1. **Consistency**: Use values from the scale only (6, 8, 10, 12, 15, 20px, 50%)
2. **Size Relationship**: Larger elements get larger radius values
3. **Interactive Elements**: Minimum 10px radius for touch targets
4. **Nested Elements**: Inner elements should have radius 2-4px smaller than container
5. **Pill Shapes**: Use 50% radius for badges and tags
6. **Images**: Always round corners (8-12px) to match card aesthetic
7. **Full-Bleed**: Use selective rounding (e.g., 0 0 20px 20px for header)

---

## 9. Animations & Transitions

### Animation Durations

```css
/* Standard Transition */
transition: all 0.3s;
/* Usage: Most hover effects, color changes, size changes */

/* Fast Transition */
transition: all 0.2s;
transition: opacity 0.3s ease;
/* Usage: Quick state changes */

/* Smooth Progress */
transition: width 0.5s ease;
/* Usage: Progress bar fill */

/* Fade-in Animation */
animation: fadeIn 0.5s;
/* Usage: Panel transitions */

/* Processing Pulse */
animation: processingPulse 1.2s ease-in-out infinite;
/* Usage: Active step indicator */

/* Text Pulse */
animation: textPulse 2s ease-in-out infinite;
/* Usage: Running step text */

/* Fade In/Out */
animation: fadeInOut 2s ease-in-out infinite;
/* Usage: Running step container */

/* Completion Ring */
animation: completionRing 0.6s ease-out;
/* Usage: Step completion indicator */

/* Spinner */
animation: spin 1s linear infinite;
/* Usage: Loading indicator */
```

### Easing Functions

```css
ease          /* Default - gradual acceleration and deceleration */
ease-in-out   /* Smooth start and end - used for loops */
ease-out      /* Fast start, slow end - used for entrances */
linear        /* Constant speed - used for spinning */
```

### Animation Definitions

#### Fade In (Panel Entrance)
```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

#### Processing Pulse (Active Step)
```css
@keyframes processingPulse {
    0%, 100% {
        transform: scale(1);
        filter: saturate(0.8) brightness(0.9);
        box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
    }
    50% {
        transform: scale(1.05);
        filter: saturate(1.2) brightness(1.1);
        box-shadow: 0 0 25px rgba(102, 126, 234, 0.5);
    }
}
```

#### Fade In/Out (Breathing Effect)
```css
@keyframes fadeInOut {
    0%, 100% {
        opacity: 0.7;
    }
    50% {
        opacity: 1;
    }
}
```

#### Text Pulse (Loading Text)
```css
@keyframes textPulse {
    0%, 100% {
        opacity: 0.8;
    }
    50% {
        opacity: 1;
    }
}
```

#### Completion Ring (Success Animation)
```css
@keyframes completionRing {
    0% {
        transform: scale(0.8);
        opacity: 0;
    }
    50% {
        transform: scale(1.1);
        opacity: 1;
    }
    100% {
        transform: scale(1);
        opacity: 1;
    }
}
```

#### Spinner (Loading)
```css
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
```

### Interaction Animations

**Button Hover:**
```css
/* Primary Button */
transform: translateY(-2px);
transition: all 0.3s;
```

**Card Hover:**
```css
/* Cards */
transform: translateY(-5px);
transition: transform 0.3s;
```

**Dice Button:**
```css
/* Hover */
transform: scale(1.1) rotate(10deg);

/* Active */
transform: scale(0.95) rotate(-10deg);

transition: all 0.3s;
```

**Upload Area Dragover:**
```css
transform: scale(1.02);
transition: all 0.3s;
```

### Animation Guidelines

1. **Duration**: 0.2-0.3s for most interactions, 0.5s for smooth transitions, 1-2s for ambient loops
2. **Easing**: Use ease-in-out for loops, ease-out for entrances, ease for general interactions
3. **Performance**: Animate transform and opacity only (GPU-accelerated)
4. **Avoid**: Animating width, height, top, left (causes reflows)
5. **Infinite Loops**: Only for processing/loading states, stop when complete
6. **Entrance Animations**: Fade + translateY for natural entrance
7. **Hover Delays**: No delay on hover enter, 0.3s on hover exit
8. **Accessibility**: Respect prefers-reduced-motion media query

```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

---

## 10. Accessibility Guidelines

### Color Contrast Requirements

#### WCAG AA Compliance (Minimum)
- **Normal Text (16px+)**: 4.5:1 contrast ratio
- **Large Text (24px+)**: 3:1 contrast ratio
- **UI Components**: 3:1 contrast ratio

#### Current Contrast Ratios

| Text Color | Background | Ratio | Level | Usage |
|------------|------------|-------|-------|-------|
| #2c3e50 | #ffffff | 12.63:1 | AAA | Primary text |
| #333333 | #ffffff | 12.63:1 | AAA | Secondary text |
| #666666 | #ffffff | 5.74:1 | AA | Tertiary text |
| #999999 | #ffffff | 2.85:1 | Fail | Hints only (large text) |
| #ffffff | #667eea | 4.51:1 | AA | Button text |
| #ffffff | #764ba2 | 7.32:1 | AAA | Button text |
| #4CAF50 | #ffffff | 3.04:1 | AA (Large) | Success icons |

**Issues to Address:**
- Hint text (#999) should only be used for large text (18px+) or non-essential information
- Consider darkening to #888 for better contrast (3.54:1)

### Keyboard Navigation

#### Implemented
```javascript
// Arrow key navigation between steps
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' && !nextBtn.disabled && currentStep < 5) {
        goToStep(currentStep + 1);
    } else if (e.key === 'ArrowLeft' && !prevBtn.disabled && currentStep > 0) {
        goToStep(currentStep - 1);
    }
});
```

#### Requirements
1. **Tab Order**: Logical flow through interactive elements
2. **Arrow Keys**: Navigate between steps (←/→)
3. **Enter/Space**: Activate buttons and clickable elements
4. **Escape**: Close modals or cancel operations (if added)
5. **Skip Links**: Add "Skip to content" for screen reader users

### Focus States

#### Current Implementation
```css
/* Active step indicator */
.step.active .step-circle {
    transform: scale(1.1);
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
}
```

#### Required Improvements
```css
/* All interactive elements should have visible focus */
button:focus,
.upload-area:focus,
.step:focus {
    outline: 3px solid #667eea;
    outline-offset: 2px;
}

/* Don't remove focus indicators */
*:focus {
    outline: 3px solid #667eea;
    outline-offset: 2px;
}
```

### ARIA Labels

#### Currently Missing - Should Add:

```html
<!-- Upload Area -->
<div class="upload-area"
     role="button"
     tabindex="0"
     aria-label="Upload reference images"
     aria-describedby="upload-hint">
    <div class="upload-icon" aria-hidden="true">📤</div>
    <div class="upload-text">Drag & Drop Reference Images</div>
    <div class="upload-hint" id="upload-hint">
        Or click to browse • Max 4 images • PNG, JPG, WebP
    </div>
</div>

<!-- Progress Bar -->
<div class="progress-bar"
     role="progressbar"
     aria-valuenow="50"
     aria-valuemin="0"
     aria-valuemax="100"
     aria-label="Design system generation progress">
    <div class="progress-fill" style="width: 50%">
        <span>50%</span>
    </div>
</div>

<!-- Step Indicators -->
<div class="step completed"
     data-step="0"
     role="button"
     tabindex="0"
     aria-label="Upload step - Completed">
    <div class="step-circle" aria-hidden="true">📸</div>
    <div class="step-name">Upload</div>
    <div class="step-progress" aria-live="polite">✓ 100%</div>
</div>

<!-- Activity Log -->
<div id="activityLog"
     role="log"
     aria-live="polite"
     aria-label="Live processing activity">
    <div>🔄 Live Activity</div>
    <div id="activityMessages"></div>
</div>

<!-- Buttons -->
<button class="btn btn-primary"
        id="startBtn"
        aria-label="Start design system generation">
    Start Generation
</button>

<button class="btn btn-primary"
        id="nextBtn"
        aria-label="Go to next step"
        disabled
        aria-disabled="true">
    Next →
</button>
```

### Screen Reader Considerations

1. **Emoji Labels**: Add `aria-label` to emoji-only elements
2. **Status Updates**: Use `aria-live="polite"` for activity log and progress updates
3. **State Changes**: Announce step completions and status changes
4. **Hidden Elements**: Use `aria-hidden="true"` for decorative emojis
5. **Loading States**: Announce "Loading" or "Processing" states
6. **Error Messages**: Use `role="alert"` for error notifications
7. **Dynamic Content**: Mark activity log with `role="log"`

### Accessibility Checklist

- [ ] Add proper ARIA labels to all interactive elements
- [ ] Ensure all buttons have descriptive labels (not just emojis)
- [ ] Implement visible focus indicators for all focusable elements
- [ ] Add `role="progressbar"` to progress indicators
- [ ] Use `aria-live` for dynamic status updates
- [ ] Ensure color is not the only means of conveying information
- [ ] Add alt text to all images
- [ ] Test with screen readers (NVDA, JAWS, VoiceOver)
- [ ] Verify tab order is logical
- [ ] Ensure touch targets are minimum 44x44px (currently 40x40px buttons)
- [ ] Add skip navigation links
- [ ] Test keyboard navigation
- [ ] Verify contrast ratios meet WCAG AA standards
- [ ] Implement prefers-reduced-motion media query

---

## 11. Brand Voice & Tone

### Voice Characteristics
- **Clear**: Direct, jargon-free language
- **Empowering**: Action-oriented, confidence-building
- **Intelligent**: Data-driven, precise terminology
- **Friendly**: Approachable, conversational (without being casual)
- **Progressive**: Forward-thinking, innovative

### Writing Style for UI Text

#### Headings
- **Action-oriented**: Focus on what the user will accomplish
- **Concise**: Maximum 6-8 words
- **Descriptive**: Clear about the section's purpose

**Examples:**
- ✓ "Visual DNA Analysis"
- ✓ "Design Patterns & Style Board"
- ✓ "Generated Components"
- ✗ "Analysis" (too vague)
- ✗ "The System is Currently Analyzing Your References" (too verbose)

#### Button Text
- **Verb-first**: Start with action verbs
- **Clear outcome**: User knows what will happen
- **Concise**: 1-3 words ideal

**Examples:**
- ✓ "Start Generation"
- ✓ "Next →"
- ✓ "← Previous"
- ✓ "🔄 Start Over"
- ✗ "Click here to begin"
- ✗ "Proceed"

#### Descriptions & Body Text
- **Second person**: Address user as "you"
- **Active voice**: Subject performs the action
- **Sentence case**: Only capitalize first word and proper nouns
- **Brief**: One sentence when possible

**Examples:**
- ✓ "Transform visual inspiration into production-ready component libraries"
- ✓ "Drag & Drop Reference Images"
- ✓ "Or click to browse • Max 4 images • PNG, JPG, WebP"
- ✗ "The system will transform your visual inspiration..."
- ✗ "Images can be dragged and dropped here"

### Error Message Tone

**Principles:**
- **Helpful**: Explain what went wrong and how to fix it
- **Blame-free**: Don't blame the user
- **Specific**: Tell exactly what the issue is
- **Actionable**: Provide clear next steps

**Examples:**
```
✓ "Please upload at least one image to continue"
✗ "Error: No files selected"

✓ "Maximum file size is 10MB. Please choose a smaller image."
✗ "File too large"

✓ "This file type isn't supported. Please upload PNG, JPG, or WebP images."
✗ "Invalid file type"

✓ "Oops! Something went wrong. Please refresh the page and try again."
✗ "Fatal error 500"
```

### Success Message Tone

**Principles:**
- **Celebratory**: Acknowledge accomplishment
- **Specific**: Tell what was completed
- **Guidance**: Suggest next steps when appropriate
- **Brief**: Don't overdo the celebration

**Examples:**
```
✓ "Analysis complete! 24 colors extracted from your references."
✗ "Success"

✓ "Design system generated! You now have 48 production-ready components."
✗ "Task finished"

✓ "Components saved! You can download your library anytime."
✗ "Saved successfully"
```

### Microcopy Guidelines

#### Step Names
- **Single word or short phrase**: Maximum 2 words
- **Noun-based**: Describe the phase
- **Progressive**: Suggest forward motion

**Examples:**
- Upload, Visual DNA, Patterns, Rules, Generate, Showcase

#### Progress Text
- **Percentage**: Show numeric progress
- **Context**: Brief description of current action
- **Status**: Clear state indication

**Examples:**
```
✓ "45% - Detecting patterns..."
✓ "✓ 100%"
✓ "Processing..."
✗ "Please wait"
✗ "Working..."
```

#### Activity Log
- **Timestamped**: Show when action occurred
- **Present tense**: Describe what's happening now
- **Specific**: Name the exact operation

**Examples:**
```
✓ "[10:34:22] ● Analyzing color palette..."
✓ "[10:34:25] ● Extracting typography rules..."
✓ "[10:34:28] ● Generating button components..."
✗ "Processing data"
✗ "Working on step 2"
```

### Content Principles

#### 1. Lead with the Benefit
Start with what the user will accomplish, not how the system works.

**Examples:**
```
✓ "Transform visual inspiration into production-ready component libraries"
✗ "This system analyzes images to create design systems"
```

#### 2. Use Active Voice
Subject performs the action (more direct and engaging).

**Examples:**
```
✓ "We analyzed your references"
✗ "Your references were analyzed"

✓ "Generate a random UI"
✗ "A random UI will be generated"
```

#### 3. Be Conversational, Not Casual
Friendly but professional. Avoid slang.

**Examples:**
```
✓ "Let's create your design system"
✓ "Ready to generate components?"
✗ "Yo, let's do this!"
✗ "Wanna make some components?"
```

#### 4. Avoid Jargon
Use plain language. When technical terms are necessary, provide context.

**Examples:**
```
✓ "Visual DNA: The core colors, shapes, and styles extracted from your references"
✗ "HSL color space decomposition with k-means clustering"
```

#### 5. Show, Don't Tell
Use concrete examples instead of abstract descriptions.

**Examples:**
```
✓ "Max 4 images • PNG, JPG, WebP"
✗ "Multiple supported formats with reasonable limits"
```

---

## 12. Design Principles

### 1. Progressive Disclosure
**Reveal complexity gradually as users need it**

- Show only the current step's content
- Hide completed steps behind navigation
- Reveal details progressively (color swatches → full analysis)
- Don't overwhelm with all options at once

**Example:** The pipeline shows 6 steps but only displays content for the active step.

### 2. Visual Hierarchy
**Guide users' attention through size, color, and spacing**

- Largest: Main heading (h1, 2.5rem)
- Prominent: Primary buttons (gradient background)
- Secondary: Section headings (natural size)
- Tertiary: Labels and hints (smaller, lighter text)

**Example:** Upload area uses size (64px emoji), color (purple), and position (center) to draw attention.

### 3. Feedback & Visibility
**Always show system status and user actions**

- Progress bar shows overall completion
- Step indicators show current phase
- Activity log shows real-time operations
- Hover states confirm interactivity
- Disabled states show unavailable actions

**Example:** Running steps pulse with animation and show percentage progress.

### 4. Consistency & Patterns
**Use the same design elements for the same functions**

- Purple gradient = primary action/brand
- Green = completion/success
- Card elevation = importance level
- 20px gap = standard grid spacing
- Hover lift = interactivity

**Example:** All cards use consistent radius (12-20px) and shadow values.

### 5. Aesthetic-Usability Effect
**Beautiful design feels more usable**

- Smooth animations (0.3s standard)
- Generous whitespace (40px sections)
- Subtle shadows (0.08-0.15 opacity)
- Cohesive color palette (purple gradient)
- Rounded corners (modern aesthetic)

**Example:** Cards lift on hover with smooth transitions, creating a satisfying interaction.

### 6. Recognition Over Recall
**Make options visible, don't require memorization**

- All 6 steps always visible in pipeline
- Emoji icons aid recognition
- Labels accompany all actions
- Current state clearly indicated
- Navigation always present

**Example:** Step indicators show emoji + label + progress, no need to remember what step 3 is.

### 7. Error Prevention
**Prevent errors before they occur**

- Disable "Next" button until step completes
- Limit file uploads to 4 images
- Accept only specific file types
- Dragover state shows drop zone is active
- Confirm destructive actions (restart)

**Example:** Upload area only accepts image files and provides clear format guidance.

### 8. Flexibility & Efficiency
**Support both novice and expert users**

- Linear flow for beginners (Next/Previous buttons)
- Direct navigation for experts (click any step)
- Keyboard shortcuts (Arrow keys)
- Skip ahead to completed steps
- Restart anytime

**Example:** Users can click any completed step to jump directly to it, or use Next/Previous for guided flow.

---

## 13. Code Examples

### CSS Variables Setup
```css
:root {
    /* Colors */
    --color-primary: #667eea;
    --color-primary-dark: #764ba2;
    --color-success: #4CAF50;
    --color-text-primary: #2c3e50;
    --color-text-secondary: #666;
    --color-text-tertiary: #999;
    --color-bg-light: #f8f9fa;
    --color-border: #e0e0e0;

    /* Gradients */
    --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --gradient-accent: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);

    /* Spacing */
    --spacing-xs: 8px;
    --spacing-sm: 12px;
    --spacing-md: 20px;
    --spacing-lg: 30px;
    --spacing-xl: 40px;

    /* Radius */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 20px;

    /* Shadows */
    --shadow-sm: 0 4px 12px rgba(0, 0, 0, 0.08);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 8px 20px rgba(0, 0, 0, 0.15);
    --shadow-primary: 0 10px 25px rgba(102, 126, 234, 0.3);

    /* Transitions */
    --transition-fast: 0.2s;
    --transition-base: 0.3s;
    --transition-slow: 0.5s;
}
```

### Primary Button Component
```css
/* HTML */
<button class="btn btn-primary">
    Start Generation
</button>

/* CSS */
.btn {
    padding: 15px 40px;
    border: none;
    border-radius: var(--radius-md, 10px);
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all var(--transition-base, 0.3s);
    display: inline-block;
}

.btn-primary {
    background: var(--gradient-primary);
    color: white;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-primary);
}

.btn-primary:disabled {
    background: #ccc !important;
    color: #888 !important;
    cursor: not-allowed;
    opacity: 0.6;
}

.btn-primary:focus {
    outline: 3px solid var(--color-primary);
    outline-offset: 2px;
}
```

### Card Component
```css
/* HTML */
<div class="card">
    <h3 class="card-title">Card Title</h3>
    <p class="card-content">Card content goes here...</p>
</div>

/* CSS */
.card {
    background: white;
    border-radius: var(--radius-md, 12px);
    padding: var(--spacing-md, 20px);
    box-shadow: var(--shadow-md);
    transition: transform var(--transition-base);
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-lg);
}

.card-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: var(--spacing-sm, 12px);
}

.card-content {
    color: var(--color-text-secondary);
    line-height: 1.6;
}
```

### Progress Bar Component
```css
/* HTML */
<div class="progress-bar" role="progressbar" aria-valuenow="65" aria-valuemin="0" aria-valuemax="100">
    <div class="progress-fill" style="width: 65%">
        <span class="progress-text">65%</span>
    </div>
</div>

/* CSS */
.progress-bar {
    width: 100%;
    height: 40px;
    background: var(--color-border);
    border-radius: var(--radius-lg);
    overflow: hidden;
    position: relative;
}

.progress-fill {
    height: 100%;
    background: var(--gradient-primary);
    transition: width var(--transition-slow) ease;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
}

.progress-text {
    position: relative;
    z-index: 1;
}
```

### Step Indicator Component
```css
/* HTML */
<div class="step completed" data-step="1" role="button" tabindex="0">
    <div class="step-circle">🧬</div>
    <div class="step-name">Visual DNA</div>
    <div class="step-progress">✓ 100%</div>
</div>

/* CSS */
.step {
    flex: 1;
    text-align: center;
    position: relative;
    z-index: 1;
    transition: opacity 0.5s ease;
}

.step-circle {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: white;
    border: 3px solid var(--color-border);
    margin: 0 auto 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    transition: all var(--transition-base);
    cursor: pointer;
}

/* Completed State */
.step.completed .step-circle {
    background: var(--color-primary);
    border-color: var(--color-primary);
    color: white;
}

.step.completed .step-circle::after {
    content: '';
    position: absolute;
    top: -5px;
    left: -5px;
    right: -5px;
    bottom: -5px;
    border-radius: 50%;
    border: 3px solid var(--color-success);
    animation: completionRing 0.6s ease-out;
}

/* Running State */
.step.running .step-circle {
    background: var(--gradient-primary);
    border-color: var(--color-primary-dark);
    color: white;
    animation: processingPulse 1.2s ease-in-out infinite;
}

.step-name {
    font-size: 0.9rem;
    color: var(--color-text-secondary);
    font-weight: 500;
}

.step.completed .step-name {
    color: var(--color-success);
    font-weight: 600;
}
```

### Upload Area Component
```css
/* HTML */
<div class="upload-area" role="button" tabindex="0" aria-label="Upload reference images">
    <div class="upload-icon" aria-hidden="true">📤</div>
    <div class="upload-text">Drag & Drop Reference Images</div>
    <div class="upload-hint">Or click to browse • Max 4 images • PNG, JPG, WebP</div>
</div>

/* CSS */
.upload-area {
    border: 3px dashed var(--color-primary);
    border-radius: 15px;
    padding: 60px 40px;
    text-align: center;
    cursor: pointer;
    transition: all var(--transition-base);
    background: #f8f9ff;
}

.upload-area:hover {
    background: #eef0ff;
    border-color: var(--color-primary-dark);
}

.upload-area.dragover {
    background: #e0e5ff;
    border-color: var(--color-primary);
    transform: scale(1.02);
}

.upload-icon {
    font-size: 4rem;
    margin-bottom: var(--spacing-md);
}

.upload-text {
    font-size: 1.3rem;
    color: var(--color-primary);
    margin-bottom: var(--spacing-sm, 10px);
    font-weight: 600;
}

.upload-hint {
    color: var(--color-text-tertiary);
    font-size: 0.95rem;
}
```

### Grid Layout Component
```css
/* Responsive Grid for Cards */
.results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: var(--spacing-md, 20px);
    margin-top: var(--spacing-lg);
}

/* Reference Images Grid */
.references-preview {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-md, 20px);
    margin-top: var(--spacing-lg);
}

@media (max-width: 768px) {
    .results-grid,
    .references-preview {
        grid-template-columns: 1fr;
        gap: var(--spacing-sm, 12px);
    }
}
```

### Activity Log Component
```css
/* HTML */
<div class="activity-log" role="log" aria-live="polite" aria-label="Live processing activity">
    <div class="activity-header">
        <span aria-hidden="true">🔄</span> Live Activity
    </div>
    <div class="activity-messages">
        <div class="activity-message">
            <span class="timestamp">[10:34:22]</span>
            <span class="bullet">●</span>
            <span class="message-text">Analyzing color palette...</span>
        </div>
    </div>
</div>

/* CSS */
.activity-log {
    background: white;
    border: 1px solid var(--color-border);
    border-left: 4px solid var(--color-primary);
    border-radius: var(--radius-md);
    padding: var(--spacing-md);
    margin: var(--spacing-md) 0;
    min-height: 120px;
    max-height: 150px;
    overflow-y: auto;
    font-family: 'Monaco', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.8;
    opacity: 0;
    transition: opacity var(--transition-base) ease;
}

.activity-log.visible {
    opacity: 1;
}

.activity-header {
    font-weight: 600;
    color: var(--color-primary);
    margin-bottom: var(--spacing-sm, 10px);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.activity-message {
    margin-bottom: 5px;
    color: #555;
}

.timestamp {
    color: var(--color-text-tertiary);
}

.bullet {
    color: var(--color-primary);
    margin: 0 5px;
}
```

---

## 14. Usage Examples

### Color Swatch Display
```html
<div class="color-palette">
    <h3 class="palette-title">Extracted Color Palette</h3>
    <div class="color-swatches">
        <div class="color-swatch">
            <div class="swatch-color" style="background: hsl(229, 76%, 66%);"></div>
            <div class="swatch-label">Primary</div>
        </div>
        <div class="color-swatch">
            <div class="swatch-color" style="background: hsl(122, 39%, 49%);"></div>
            <div class="swatch-label">Success</div>
        </div>
    </div>
</div>
```

```css
.color-palette {
    margin: var(--spacing-lg) 0;
}

.palette-title {
    margin-bottom: var(--spacing-md);
    color: var(--color-text-primary);
}

.color-swatches {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
}

.color-swatch {
    text-align: center;
}

.swatch-color {
    width: 60px;
    height: 60px;
    border-radius: var(--radius-sm);
    box-shadow: var(--shadow-sm);
}

.swatch-label {
    font-size: 11px;
    margin-top: 5px;
    color: var(--color-text-secondary);
}
```

---

## 15. File Locations

### Source Files
- **Main Application**: `/Users/noisebox/ui-layer-decomposer/web_interface/templates/index.html`
- **Brand Guide**: `/Users/noisebox/ui-layer-decomposer/BRAND_GUIDE.md`

### Related Assets
- **Session Images**: Served via `/api/session/{session_id}/image/{filename}`
- **Component Library**: Generated at runtime in session output directory

---

## 16. Maintenance & Updates

### Version History
- **v1.0** (2025-10-29): Initial brand guide created from Phase 13 implementation

### Review Schedule
- **Quarterly**: Review color contrast ratios and accessibility compliance
- **Biannually**: Update with new component patterns
- **Annually**: Full brand refresh evaluation

### Change Process
1. Propose changes in design review meeting
2. Update this guide with new values
3. Implement changes in codebase
4. Test across all components
5. Document rationale for changes

---

## 17. Resources & Tools

### Design Tools
- **Color Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **WCAG Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/
- **CSS Gradient Generator**: https://cssgradient.io/
- **Shadow Generator**: https://shadows.brumm.af/

### Development References
- **System Font Stack**: https://systemfontstack.com/
- **CSS-Tricks**: https://css-tricks.com/
- **MDN Web Docs**: https://developer.mozilla.org/

### Accessibility Testing
- **WAVE**: https://wave.webaim.org/
- **axe DevTools**: Browser extension for accessibility testing
- **Screen Readers**: NVDA (Windows), JAWS (Windows), VoiceOver (macOS/iOS)

---

## Appendix: Quick Reference

### Color Quick Reference
| Color | Hex | Usage |
|-------|-----|-------|
| Primary Purple | #667eea | Brand, primary actions |
| Deep Purple | #764ba2 | Gradient end, accents |
| Success Green | #4CAF50 | Completions, success |
| Primary Text | #2c3e50 | Headings, body text |
| Secondary Text | #666666 | Labels, descriptions |
| Tertiary Text | #999999 | Hints, placeholders |
| Background | #f8f9fa | Page background |
| Border | #e0e0e0 | Dividers, borders |

### Spacing Quick Reference
| Name | Value | Usage |
|------|-------|-------|
| XS | 8px | Tight spacing |
| SM | 12px | Small gaps |
| MD | 20px | Standard spacing |
| LG | 30px | Section padding |
| XL | 40px | Major spacing |

### Typography Quick Reference
| Element | Size | Weight | Usage |
|---------|------|--------|-------|
| H1 | 40px | 700 | Page title |
| H2 | 24px | 600 | Section heading |
| H3 | 18px | 600 | Subsection |
| Body | 16px | 400 | Body text |
| Small | 12-14px | 400-500 | Labels, hints |

---

## 16. Brand Strategy & Positioning

### Brand Promise
**"Transform any visual inspiration into a complete, production-ready design system in minutes, not months."**

### Value Proposition
GenUI bridges the gap between inspiration and implementation by:
- **Automating** the tedious process of extracting design patterns
- **Democratizing** design system creation for teams of all sizes
- **Accelerating** the design-to-development workflow
- **Ensuring** consistency through data-driven pattern recognition

### Market Positioning

#### Primary Positioning
**"The AI-powered design system generator for modern product teams"**

#### Competitive Differentiation
- **vs Manual Design Systems**: 100x faster with automated extraction
- **vs Design Tokens Tools**: Generates complete components, not just tokens
- **vs Figma/Sketch Plugins**: Works with any visual reference (screenshots, photos, mockups)
- **vs Template Libraries**: Creates unique systems from YOUR inspiration, not generic templates

#### Target Market Segments

1. **Startups & Scale-ups (Primary)**
   - Need: Rapid design system creation without dedicated design system team
   - Pain point: Limited resources, need to move fast
   - Value: Get professional design system in hours vs weeks

2. **Design Agencies (Secondary)**
   - Need: Quickly prototype client design systems from mood boards
   - Pain point: Time-consuming pattern extraction from references
   - Value: Bill more projects with faster turnaround

3. **Enterprise Design Teams (Tertiary)**
   - Need: Modernize legacy systems by extracting patterns from existing UIs
   - Pain point: Manual audit and documentation of patterns
   - Value: Accelerate redesign projects

### Brand Pillars

1. **Intelligence**: AI-powered pattern recognition and smart defaults
2. **Transparency**: Clear, step-by-step process showing exactly what's happening
3. **Empowerment**: Puts professional design system creation in everyone's hands
4. **Quality**: Production-ready output, not rough prototypes
5. **Flexibility**: Works with any visual style, not opinionated templates

---

## 17. Logo Design & Visual Identity

### Current Logo System

#### Primary Logo
```
🎨 GenUI
```

**Components**:
- **Icon**: Artist palette emoji (🎨) represents creativity and design
- **Wordmark**: "GenUI" in system font, bold weight
- **Color**: Purple gradient when possible, white on dark backgrounds

#### Logo Variations

**Full Logo**
```
🎨 GenUI: Visual DNA → Design Systems
```
Use in: Headers, splash screens, documentation headers

**Condensed Logo**
```
🎨 GenUI
```
Use in: Navigation bars, favicons (without emoji), social media

**Icon Only**
```
🎨
```
Use in: App icons, favicons, small spaces

### Logo Usage Guidelines

#### Minimum Sizes
- Full logo: 200px width minimum
- Condensed: 80px width minimum
- Icon only: 32px minimum

#### Clear Space
Maintain space equal to the height of the "G" letter around all sides of the logo

#### Don'ts
- ❌ Don't stretch or distort the logo
- ❌ Don't change the emoji icon
- ❌ Don't use low-contrast backgrounds
- ❌ Don't add effects (drop shadows, outlines, glows)
- ❌ Don't rotate the logo
- ❌ Don't place on busy backgrounds

### Alternative Logo Concepts
(For future brand evolution)

**Concept 1: DNA Helix**
- Visual metaphor for "Visual DNA extraction"
- Modern, scientific feel
- Could be animated

**Concept 2: Abstract Gradient Shape**
- Flowing, organic gradient form
- Represents transformation
- Scalable and distinctive

**Concept 3: Component Grid**
- Grid of UI elements forming larger shape
- Represents component library output
- Technical, precise aesthetic

---

## 18. Photography & Image Analysis

### Photography Philosophy

GenUI uses **two distinct photography approaches**:

1. **Application Photography**: Curated imagery for the GenUI web interface (clean, modern, technology-forward)
2. **Generative Photography Analysis**: Deep analysis of reference image characteristics to inform UI style

---

### 18.1 Application Photography (GenUI Interface Marketing)

**Purpose**: Professional imagery for GenUI marketing, documentation, and interface

#### Aesthetic Direction
- **Clean & Modern**: Bright, airy, minimalist compositions
- **Technology-Forward**: Showing software, screens, and digital tools
- **Human-Centered**: Designers and developers in creative environments
- **Aspirational**: Professional yet approachable

#### Color Treatment
- **Desaturated with Purple Accent**: Reduce saturation by 20%, add purple grade overlay at 10% opacity
- **High Key Lighting**: Bright, evenly lit scenes
- **Clean Backgrounds**: Minimal distractions, solid colors or subtle gradients

#### Technical Specs (Standard)
- Resolution: 2400x1350px minimum (16:9 for heroes)
- Format: WebP with JPG/PNG fallback
- File size: <200KB after optimization
- Color space: sRGB

---

### 18.2 Generative Photography Analysis (Reference Image Processing)

**Purpose**: Extract visual characteristics from reference photography to inform UI style

#### Analysis Dimensions

When analyzing reference photographs, GenUI extracts comprehensive style information:

**1. Lighting Analysis**
```python
lighting_analysis = {
    'quality': 'hard' | 'soft' | 'diffused',
    'direction': 'top' | 'side' | 'back' | 'bottom' | 'ambient',
    'temperature': 'warm' | 'neutral' | 'cool',  # Color temp in Kelvin
    'contrast': 0.0-1.0,  # High contrast = dramatic, low = flat
    'intensity': 'low-key' | 'mid-key' | 'high-key'
}
```

**UI Application**:
- Hard lighting → Sharp shadows, high contrast UI
- Soft lighting → Subtle gradients, soft shadows
- Warm lighting → Warm color palette accents
- Cool lighting → Cool-toned neutrals
- High-key → Light UI themes
- Low-key → Dark UI themes

**2. Composition Analysis**
```python
composition_analysis = {
    'rule_of_thirds': True | False,
    'golden_spiral': True | False,
    'symmetry': 'bilateral' | 'radial' | 'none',
    'leading_lines': detected_lines[],
    'focal_point': (x, y),  # Relative position
    'negative_space': 0.0-1.0,  # Percentage
    'depth_layers': ['foreground', 'midground', 'background']
}
```

**UI Application**:
- Rule of thirds → Grid-based layouts
- Golden spiral → Organic, flowing layouts
- Symmetry → Centered, balanced UI
- Asymmetry → Dynamic, off-center layouts
- Negative space % → UI density (high negative = sparse, low = dense)

**3. Focus & Depth Analysis**
```python
depth_analysis = {
    'depth_of_field': 'shallow' | 'deep',
    'focal_plane': 'foreground' | 'midground' | 'background',
    'bokeh_quality': 'circular' | 'hexagonal' | 'octagonal' | 'none',
    'blur_intensity': 0.0-1.0,
    'layering_depth': number_of_perceivable_layers
}
```

**UI Application**:
- Shallow DOF → Layered UI with blur effects, modal emphasis
- Deep DOF → Flat UI, everything in focus
- Bokeh presence → Gradient backgrounds, soft out-of-focus elements
- Layering → Z-index hierarchy, card-based layouts

**4. Texture & Detail Analysis**
```python
texture_analysis = {
    'grain': 'fine' | 'medium' | 'coarse' | 'none',
    'surface_quality': 'smooth' | 'rough' | 'glossy' | 'matte',
    'detail_density': 0.0-1.0,  # High = intricate, low = minimal
    'noise_level': 0.0-1.0,
    'sharpness': 0.0-1.0
}
```

**UI Application**:
- Film grain → Subtle texture overlays on backgrounds
- Smooth surfaces → Clean, flat UI elements
- Rough textures → Textured backgrounds, material patterns
- High detail → Detailed illustrations, realistic renderings
- Low detail → Minimalist, flat design

**5. Subject & Style Analysis**
```python
subject_analysis = {
    'subject_type': 'human' | 'product' | 'environment' | 'abstract',
    'photography_style': 'portrait' | 'landscape' | 'macro' | 'architectural' | 'product' | 'editorial',
    'mood': 'dramatic' | 'serene' | 'energetic' | 'mysterious' | 'playful',
    'era': 'vintage' | 'modern' | 'retro' | 'futuristic',
    'realism': 'photorealistic' | 'stylized' | 'abstract'
}
```

**UI Application**:
- Portrait style → Human-centered UI, profile emphasis
- Architectural → Grid-based, structural layouts
- Macro → Detail-focused, zoom interactions
- Product → Clean product cards, showcase layouts
- Vintage → Sepia tones, film grain effects
- Futuristic → Glassy effects, neon accents

**6. Post-Processing Analysis**
```python
post_processing = {
    'filters': ['sepia', 'b&w', 'split-tone', 'cross-process'],
    'vignette': 0.0-1.0,
    'clarity': -1.0 to 1.0,  # Negative = soft, positive = crisp
    'vibrance': 0.0-1.0,
    'selective_color': detected_color_grades[]
}
```

**UI Application**:
- Vignette → Darkened page edges, focus on center
- Soft clarity → Softer UI elements, gentle transitions
- High clarity → Sharp, crisp UI, high contrast
- Color grading → Applied to UI backgrounds and accents

---

### Photography Description Mining

**Principle**: Reference images are analyzed and described in depth. These descriptions are stored and mined for interface usage.

#### Analysis Process

**Step 1: Image Description Generation**
```python
def generate_image_description(reference_image):
    """Generate comprehensive description of reference image"""
    description = {
        'composition': describe_composition(image),
        'lighting': describe_lighting(image),
        'color_story': describe_colors(image),
        'mood': describe_emotional_tone(image),
        'style': describe_photographic_style(image),
        'subjects': identify_and_describe_subjects(image),
        'textures': describe_surface_qualities(image),
        'depth': describe_spatial_depth(image),
        'technical': analyze_technical_specs(image)
    }
    return description
```

**Example Description Storage**:
```json
{
    "reference_id": "img_001",
    "description": {
        "composition": "Rule of thirds with strong leading lines from industrial piping. Subject occupies left third. Significant negative space on right provides breathing room. Low camera angle creates imposing perspective.",
        "lighting": "Hard directional light from upper left creates dramatic shadows. High contrast ratio (~8:1). Warm color temperature (~3200K) suggests industrial/tungsten lighting. Deep shadows preserve detail.",
        "color_story": "Dominated by saturated reds (#cc3333 primary). Warm earth tones (#8d6542, #d5b9b1) provide complementary support. Near-black shadows (#19160f) create depth. Minimal desaturated tones for industrial authenticity.",
        "mood": "Industrial, powerful, mechanical. Conveys precision and engineering. Serious, professional tone. Slight warmth prevents coldness.",
        "style": "Industrial/product photography. Sharp focus throughout (deep DOF). Minimal post-processing. Emphasis on form and material quality. Documentary aesthetic.",
        "subjects": "Industrial control panel with circular dial/knob. Metal construction with wear patterns. Functional, utilitarian design. Authentic aging and patina.",
        "textures": "Brushed metal surfaces. Glossy enamel paint on dial. Subtle wear and scratches. Matte industrial coating. Visible grain structure in metal.",
        "depth": "Three distinct layers: foreground control (sharp), midground housing (sharp), background environment (soft blur). Shallow depth creates dimensional separation.",
        "technical": "High sharpness. Minimal noise. Wide aperture (~f/2.8) for shallow DOF. Natural light supplemented by tungsten. Medium format sensor characteristics."
    },
    "ui_implications": {
        "layout": "Asymmetric grid, emphasize left-aligned content, preserve negative space",
        "color": "Use extracted reds as primary, earths as accents, near-blacks for text",
        "shadows": "Use hard shadows with defined edges, maintain ~8:1 contrast",
        "elements": "Circular controls (knobs, dials), industrial materials (metal textures)",
        "typography": "Bold, mechanical fonts. High contrast weights. Utilitarian feel.",
        "depth": "Layer UI elements with distinct z-index, use blur for background",
        "mood": "Professional, serious, functional UI. Minimal playfulness.",
        "interactions": "Mechanical movements (rotation, sliding). Precise, tactile feedback."
    }
}
```

**Step 2: Description Mining**
```python
def mine_description_for_ui(description_json):
    """Extract actionable UI decisions from image description"""
    ui_rules = {
        'grid_system': extract_grid_from_composition(description),
        'color_palette': extract_colors_from_color_story(description),
        'shadow_system': extract_shadows_from_lighting(description),
        'interaction_style': extract_interactions_from_subjects(description),
        'typography_tone': extract_type_mood(description),
        'animation_intensity': extract_energy_from_mood(description),
        'texture_application': extract_materials(description),
        'spatial_hierarchy': extract_depth_layers(description)
    }
    return ui_rules
```

**Step 3: Application to Generated UI**
```python
# Apply mined rules to component generation
generated_button = create_button(
    colors=ui_rules['color_palette'],
    shadow=ui_rules['shadow_system'],
    corners=ui_rules['geometric_style'],
    texture=ui_rules['texture_application'],
    hover_animation=ui_rules['animation_intensity']
)
```

---

### Photography-Informed UI Elements

#### Realistic UI Elements from Photography

When reference photography indicates realism, apply photographic techniques to UI:

**1. Photographic Lighting on UI**
```css
/* Simulating directional light source */
.realistic-button {
    background: linear-gradient(135deg,
        var(--primary-light) 0%,
        var(--primary) 50%,
        var(--primary-dark) 100%);
    box-shadow:
        inset 1px 1px 0 rgba(255,255,255,0.3),  /* Highlight */
        inset -1px -1px 0 rgba(0,0,0,0.2),     /* Shadow */
        2px 2px 4px rgba(0,0,0,0.3);            /* Cast shadow */
}
```

**2. Photographic Depth of Field**
```css
/* Blur background layers like camera bokeh */
.background-layer {
    filter: blur(12px);
    opacity: 0.6;
}

.midground-layer {
    filter: blur(4px);
    opacity: 0.8;
}

.foreground-layer {
    filter: none;
    opacity: 1;
}
```

**3. Film Grain & Texture**
```css
/* Apply subtle grain like film photography */
.textured-background::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image: url('data:image/svg+xml,...'); /* Noise pattern */
    opacity: 0.03;
    mix-blend-mode: overlay;
}
```

---

## 19. Illustration Style Guide

### Illustration Aesthetic

**Style Direction**: **Flat Design 2.0 with Gradient Accents**

#### Characteristics
- **Simplified forms**: Geometric, clean shapes
- **Gradient fills**: Using brand purple gradient
- **Isometric when appropriate**: 3D elements in isometric view
- **Minimal detail**: Focus on clarity over realism
- **Consistent stroke**: 2-3px uniform stroke weight
- **Rounded corners**: 4-8px border radius on all shapes

### Color Application in Illustrations

#### Primary Palette
- Purple gradient (#667eea → #764ba2) for main subjects
- Light grey (#f8f9fa) for backgrounds and secondary elements
- Success green (#4CAF50) for positive elements
- White for highlights and details

#### Shading Technique
- **Gradient overlay**: 45° angle, 10% opacity difference
- **No hard shadows**: Use gradients for depth
- **Soft highlights**: 20% white overlay on top edges

### Illustration Categories

#### 1. Hero Illustrations (Landing Page)
**Purpose**: Communicate key value propositions visually

**Example Concepts**:
- **"Upload & Transform"**: Reference images flowing into component grid
- **"Visual DNA Extraction"**: Magnifying glass over image revealing color swatches and patterns
- **"Instant Design System"**: Components assembling like building blocks

**Technical Specs**:
- Size: 800x600px at 2x (1600x1200px exported)
- Format: SVG preferred, PNG at 2x fallback
- Viewport: -50 padding on all sides for safe area
- Export: Optimize SVG, compress PNG

#### 2. Empty States
**Purpose**: Friendly, encouraging messages when no content exists

**Style**:
- Centered, max 300x300px
- Mono-color gradient or simple line art
- Accompanied by short, actionable text

**Example Empty States**:
- **No references uploaded**: Upload icon with upward arrow, purple gradient
- **No results yet**: Processing icon (spinning gear), animated
- **Error state**: Friendly alert icon, soft red accent

#### 3. Spot Illustrations (Icons, Features)
**Purpose**: Small, recognizable icons for features and steps

**Style**:
- 48x48px base size (export at 96x96px for 2x)
- 2px stroke, rounded caps
- Single color or simple gradient
- Consistent visual weight

**Current Icon Set** (Expand as needed):
- Upload: 📤 (Cloud upload)
- Visual DNA: 🧬 (DNA helix)
- Patterns: 🔍 (Magnifying glass)
- Rules: 📋 (Checklist)
- Generate: 🎨 (Palette)
- Showcase: ✨ (Sparkles)

#### 4. Process Diagrams
**Purpose**: Explain workflows and technical concepts

**Style**:
- **Flowcharts**: Rounded rectangles with 12px radius
- **Arrows**: Curved with 2px stroke, rounded arrowheads
- **Node colors**: Alternate between purple gradient and light grey
- **Labels**: 14px, medium weight, #2c3e50

**Layout**:
- Left-to-right or top-to-bottom flow
- Consistent spacing (40px between nodes)
- Alignment to 8px grid

### Illustration Tools & Resources

**Recommended Tools**:
- **Figma**: Primary tool for vector illustrations
- **Illustrator**: For complex illustrations
- **Affinity Designer**: Cost-effective alternative

**Resources**:
- **unDraw**: Free illustrations to customize with brand colors
- **Humaaans**: Mix-and-match character illustrations
- **Blush**: Curated illustration libraries

### Illustration Don'ts
- ❌ No clip art or generic icons
- ❌ No inconsistent styles mixed together
- ❌ No overly complex or detailed illustrations
- ❌ No realistic illustrations mixed with flat style
- ❌ No off-brand colors

---

## 20. UI Expression & Interaction Patterns

### Micro-interactions

#### Button Hover States
```css
/* Lift and glow on hover */
button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    transition: all 0.2s ease;
}
```

**Purpose**: Provide immediate feedback that element is interactive

#### Loading States
```css
/* Skeleton pulse */
@keyframes skeleton-loading {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

.skeleton {
    animation: skeleton-loading 1.5s ease-in-out infinite;
}
```

**When to use**: Any content that takes >500ms to load

#### Success Confirmation
```css
/* Checkmark animation */
@keyframes checkmark {
    0% {
        transform: scale(0) rotate(-45deg);
        opacity: 0;
    }
    50% {
        transform: scale(1.1) rotate(-45deg);
        opacity: 1;
    }
    100% {
        transform: scale(1) rotate(-45deg);
        opacity: 1;
    }
}
```

**Duration**: 600ms
**Timing**: cubic-bezier(0.68, -0.55, 0.265, 1.55) (bounce)

### Transition Patterns

#### Page Transitions
```css
/* Fade and slide */
.page-enter {
    opacity: 0;
    transform: translateY(20px);
}

.page-enter-active {
    opacity: 1;
    transform: translateY(0);
    transition: all 300ms ease-out;
}
```

#### Modal/Dialog Appearance
```css
/* Backdrop fade + content scale */
.modal-backdrop {
    animation: fade-in 200ms ease-out;
}

.modal-content {
    animation: scale-up 300ms cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scale-up {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}
```

### Interaction Feedback Patterns

#### 1. **Optimistic UI Updates**
Update UI immediately, rollback if action fails
```javascript
// Show success state immediately
updateUI(optimisticState);

// Async action
try {
    await saveData();
} catch {
    // Rollback on failure
    updateUI(previousState);
    showErrorToast();
}
```

#### 2. **Progressive Disclosure**
Reveal complexity gradually
- Start with simple options
- "Advanced settings" collapsed by default
- Inline expansion instead of new pages

#### 3. **Contextual Help**
- Tooltips on hover (500ms delay)
- Inline help text in muted color
- "?" icon for detailed help overlays

#### 4. **Bulk Actions**
- Select multiple items with checkboxes
- Action bar appears at bottom with count
- Confirm destructive actions

### State Expressions

| State | Visual Treatment | Duration |
|-------|------------------|----------|
| **Loading** | Skeleton pulse + spinner | Continuous |
| **Success** | Green checkmark + fade to normal | 2s |
| **Error** | Red border + shake animation | 400ms shake |
| **Warning** | Yellow border + icon | Persistent |
| **Processing** | Purple pulse + progress % | Until complete |
| **Disabled** | 50% opacity + no-cursor | N/A |

---

## 21. Advanced Layout Systems

### Responsive Grid System

#### Breakpoints
```css
/* Mobile-first approach */
$breakpoints: (
  xs: 0,      /* 0-575px: Mobile portrait */
  sm: 576px,  /* 576-767px: Mobile landscape */
  md: 768px,  /* 768-991px: Tablet portrait */
  lg: 992px,  /* 992-1199px: Tablet landscape */
  xl: 1200px, /* 1200+px: Desktop */
  xxl: 1400px /* 1400+px: Large desktop */
);
```

#### Container Widths
```css
.container {
    width: 100%;
    padding-right: 20px;
    padding-left: 20px;
    margin-right: auto;
    margin-left: auto;
}

@media (min-width: 576px) { .container { max-width: 540px; } }
@media (min-width: 768px) { .container { max-width: 720px; } }
@media (min-width: 992px) { .container { max-width: 960px; } }
@media (min-width: 1200px) { .container { max-width: 1140px; } }
```

#### Grid Columns
```css
/* 12-column grid */
.row {
    display: flex;
    flex-wrap: wrap;
    margin-right: -15px;
    margin-left: -15px;
}

.col-md-6 {
    flex: 0 0 50%;
    max-width: 50%;
    padding: 0 15px;
}
```

### Layout Patterns

#### 1. **Dashboard Layout**
```
┌─────────────────────────────────┐
│  Header (60px fixed)            │
├──────┬──────────────────────────┤
│ Side │  Main Content            │
│ Nav  │  (scrollable)            │
│ 240px│                          │
│      │                          │
└──────┴──────────────────────────┘
```

#### 2. **Wizard/Stepper Layout** (Current GenUI)
```
┌─────────────────────────────────┐
│  Progress Bar                   │
│  [=====>            ] 40%       │
├─────────────────────────────────┤
│  Step Indicators                │
│  ○ ● ○ ○ ○ ○                   │
├─────────────────────────────────┤
│  Content Area                   │
│  (dynamic per step)             │
│                                 │
├─────────────────────────────────┤
│  [← Previous]  [Next →]         │
└─────────────────────────────────┘
```

#### 3. **Gallery Grid Layout**
```css
.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    padding: 20px;
}
```

### Spacing Scale Application

#### Component Internal Spacing
```css
.card {
    padding: 20px;          /* MD spacing */
}

.card-header {
    margin-bottom: 12px;    /* SM spacing */
}

.card-section {
    margin-top: 30px;       /* LG spacing */
}
```

#### Page-Level Spacing
```css
section {
    padding-top: 60px;
    padding-bottom: 60px;
}

section + section {
    padding-top: 40px;      /* Reduce when sections stack */
}
```

---

## 22. Application-Specific Guidelines

### Web Application (Primary)

#### Browser Support
- Chrome/Edge: Last 2 versions
- Firefox: Last 2 versions
- Safari: Last 2 versions
- Mobile browsers: iOS Safari 13+, Chrome Mobile

#### Performance Targets
- First Contentful Paint: <1.5s
- Time to Interactive: <3.5s
- Lighthouse Score: >90

#### Responsive Behavior

**Mobile (< 768px)**
- Stack step indicators vertically
- Full-width cards
- Collapsible sections
- Simplified navigation

**Tablet (768-1199px)**
- 2-column grid for results
- Horizontal step indicators (may scroll)
- Standard card padding

**Desktop (1200px+)**
- 3-4 column grid for results
- Full horizontal step indicators
- Maximum content width: 1200px

### Future: Mobile App Guidelines

#### Platform-Specific Patterns

**iOS**
- Use native navigation patterns (back button, modal sheets)
- Adopt SF Symbols where appropriate
- Follow iOS Human Interface Guidelines
- Haptic feedback on success/error
- Native share sheet for exporting

**Android**
- Material Design 3 components
- Navigation drawer for main menu
- Floating Action Button for primary action
- Snackbar for notifications
- Native share intent

#### App-Specific Components

**Home Screen**
- Recent projects grid
- Quick upload FAB
- Empty state with sample project

**Processing Screen**
- Full-screen step visualization
- Swipe between steps
- Pull to refresh

---

## 23. Motion Design Principles

### Motion Philosophy

GenUI uses **two distinct motion systems**:

1. **Application Motion**: Standardized animations for the GenUI web interface (smooth, professional)
2. **Generative Motion**: Dynamically determined animations based on visual style analysis from reference images

**Core Principle**: "Motion should guide the eye sequentially and respect the visual style of the source imagery."

---

### 23.1 Application Motion (GenUI Interface)

**Purpose**: Consistent, professional animations for the GenUI tool interface

#### Standard Durations
```css
$duration-instant: 100ms;   /* UI feedback */
$duration-fast: 200ms;      /* Hover states */
$duration-normal: 300ms;    /* Content transitions */
$duration-slow: 500ms;      /* Page transitions */
$duration-glacial: 1000ms;  /* Special animations */
```

#### Standard Easing
```css
$ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);     /* Standard */
$ease-out: cubic-bezier(0, 0, 0.2, 1);          /* Decelerating */
$ease-in: cubic-bezier(0.4, 0, 1, 1);           /* Accelerating */
```

#### Performance Rules
- Prefer `transform` and `opacity` (GPU-accelerated)
- Avoid animating `width`, `height`, `top`, `left`
- 60fps minimum (16.67ms per frame)

---

### 23.2 Generative Motion System (Extracted from Visual Analysis)

**Purpose**: Style-appropriate animations for generated UI components based on reference image analysis

---

### Motion Properties & Transforms

GenUI analyzes reference images and applies motion to UI elements using these properties:

#### 1. Position (Translate)
```css
/* Smooth ramped position movements */
transform: translateX(value) translateY(value);
```

**Applications**:
- Sliders smoothly traversing tracks
- Switches flipping between states
- Elements sliding into view
- Sequential cascading layouts

**Extraction from Source**:
- Analyze directional movement in reference (horizontal vs vertical emphasis)
- Detect grid alignment patterns (snap-to positions)
- Identify UI element relationships (connected movements)

#### 2. Opacity (Fade)
```css
opacity: 0-1;
```

**Applications**:
- Indicator lights blinking
- Elements fading in/out
- Soft transitions between states
- Layered depth simulation

**Extraction from Source**:
- Detect transparency usage in reference images
- Analyze lighting contrast (high contrast = sharp cuts, low contrast = fades)
- Identify atmospheric depth cues

#### 3. Scale (Size Change)
```css
transform: scale(value);
```

**Applications**:
- Buttons growing on hover
- Lights turning on (scale + gradient)
- Focus emphasis
- Zoom interactions

**Extraction from Source**:
- Detect size hierarchy in composition
- Analyze emphasis techniques (scale vs color vs position)
- Identify depth perspective (3D scaling)

#### 4. Rotation
```css
transform: rotate(degrees);
```

**Applications**:
- Knobs rotating
- Dials turning
- Loading spinners
- Directional indicators

**Extraction from Source**:
- Identify circular UI elements (knobs, dials, gauges)
- Detect rotational symmetry patterns
- Analyze mechanical vs organic movement

#### 5. Offset (Layering)
```css
transform: translate3d(x, y, z);
box-shadow: multiple offsets;
```

**Applications**:
- Multiple offset drop shadows that move with element
- Parallax depth effects
- 3D layering illusion
- Lighting position indication

**Example**:
```css
/* Slider with dynamic shadow offset indicating light position */
.slider {
    box-shadow:
        2px 2px 4px rgba(0,0,0,0.1),
        4px 4px 8px rgba(0,0,0,0.08),
        6px 6px 12px rgba(0,0,0,0.06);
    transition: box-shadow 0.3s ease;
}

.slider:active {
    box-shadow:
        1px 1px 2px rgba(0,0,0,0.15),
        2px 2px 4px rgba(0,0,0,0.12),
        3px 3px 6px rgba(0,0,0,0.09);
}
```

**Extraction from Source**:
- Detect layering depth in reference composition
- Analyze shadow positions and softness
- Identify lighting direction

#### 6. Cut-On (Instant State Change)
```css
/* No transition, immediate change */
transition: none;
```

**Applications**:
- Digital readouts changing
- Binary state switches (on/off)
- Frame-by-frame animations (GIF assets)
- High-energy, staccato movements

**Extraction from Source**:
- Detect hard edges vs soft transitions
- Analyze digital vs analog aesthetics
- Identify timing rhythm (smooth vs staccato)

#### 7. Weight Change (Visual Mass)
```css
font-weight: change;
filter: blur() brightness() contrast();
```

**Applications**:
- Text emphasis shifting
- Focus/defocus effects
- Depth of field simulation
- Attention direction

**Extraction from Source**:
- Detect focus areas in composition
- Analyze depth of field blur
- Identify hierarchy shifts

#### 8. Combination Animations
Multiple properties animated simultaneously for expressive effects:

```css
/* Example: Light turning on */
@keyframes light-on {
    0% {
        opacity: 0;
        transform: scale(0.8);
        background: radial-gradient(circle, #color1 0%, #color2 0%);
        filter: blur(8px);
    }
    50% {
        opacity: 0.8;
        transform: scale(1.1);
        background: radial-gradient(circle, #color1 30%, #color2 70%);
        filter: blur(4px);
    }
    100% {
        opacity: 1;
        transform: scale(1);
        background: radial-gradient(circle, #color1 60%, #color2 100%);
        filter: blur(0);
    }
}
```

**Applications**:
- Moving gradients + scale (lights, glow effects)
- Position + opacity (smooth entrances)
- Rotation + scale (dynamic emphasis)
- Offset + blur (motion blur effect)

---

### Motion Intensity Levels (Extracted from Style)

GenUI analyzes visual intensity and applies appropriate motion characteristics:

#### Low Intensity (Calm, Professional)
```python
low_intensity_motion = {
    'duration': '500-800ms',
    'easing': 'ease-out',
    'properties': ['position', 'opacity'],
    'movement': 'smooth ramped position movements',
    'characteristics': 'Slow, deliberate, single-direction'
}
```

**Applications**:
- Corporate dashboards
- Financial interfaces
- Medical/healthcare UI
- Minimalist designs

**Example**:
```css
.low-intensity-button {
    transition: transform 0.6s ease-out;
}
.low-intensity-button:hover {
    transform: translateY(-2px);
}
```

#### Medium Intensity (Balanced, Modern)
```python
medium_intensity_motion = {
    'duration': '300-500ms',
    'easing': 'ease-in-out',
    'properties': ['position', 'opacity', 'scale'],
    'movement': 'focus changes, interface transformations, zooms',
    'characteristics': 'Moderate speed, multi-property, controlled'
}
```

**Applications**:
- Standard web applications
- E-commerce interfaces
- Productivity tools
- Content platforms

**Example**:
```css
.medium-intensity-panel {
    transition: transform 0.4s ease-in-out, opacity 0.4s ease-in-out;
}
.medium-intensity-panel.active {
    transform: scale(1.02);
    opacity: 1;
}
```

#### High Intensity (Energetic, Playful)
```python
high_intensity_motion = {
    'duration': '150-300ms',
    'easing': 'ease-in or bounce',
    'properties': ['position', 'scale', 'rotation', 'color'],
    'movement': 'quick cascading motion, staccato sequences',
    'characteristics': 'Fast, multi-element, dramatic'
}
```

**Applications**:
- Gaming interfaces
- Entertainment apps
- Social media platforms
- Creative tools

**Example**:
```css
@keyframes cascade-in {
    0% {
        transform: translateY(-20px) rotate(-5deg) scale(0.8);
        opacity: 0;
    }
    100% {
        transform: translateY(0) rotate(0) scale(1);
        opacity: 1;
    }
}

.high-intensity-item {
    animation: cascade-in 0.25s ease-out;
    animation-delay: calc(var(--index) * 0.05s); /* Stagger */
}
```

---

### Sequential Eye Movement

**Principle**: Animations should guide the audience's eye in sequential order to avoid visual jumping

#### Animation Sequencing Strategies

**1. Staggered Entrance**
```css
/* Elements appear one after another */
.item {
    animation: fade-in-up 0.4s ease-out;
    animation-delay: calc(var(--index) * 0.1s);
    animation-fill-mode: both;
}
```

**2. Directional Flow**
```css
/* Movement indicates reading order: left-to-right, top-to-bottom */
@keyframes flow-in {
    from { transform: translateX(-100px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
```

**3. Scale Hierarchy**
```css
/* Largest/most important animates first */
.primary-element { animation-delay: 0s; }
.secondary-element { animation-delay: 0.2s; }
.tertiary-element { animation-delay: 0.4s; }
```

**4. Radial Expansion**
```css
/* Expand outward from focal point */
.center { animation-delay: 0s; }
.ring-1 { animation-delay: 0.1s; }
.ring-2 { animation-delay: 0.2s; }
```

**Extraction from Source**:
- Analyze visual hierarchy (what draws eye first?)
- Detect reading patterns (left-to-right, center-out, top-down)
- Identify focal points and secondary elements

---

### Animation Implementation Methods

#### Method 1: Frame-by-Frame (GIF/Image Sequence)
**Use When**: Complex, pre-rendered animations that can't be achieved with CSS

```python
# Generate animation frames as PNG sequence
frames = generate_animation_frames(start_state, end_state, frame_count=24)

# Export as GIF
create_gif(frames, duration=1000ms, loop=True)

# Or use as image sequence with JS
display_frame_sequence(frames, fps=24)
```

**Applications**:
- Complex particle effects
- Character animations
- Pre-rendered 3D rotations
- Detailed mechanical movements

**Pros**: Full creative control, consistent across browsers
**Cons**: Larger file size, not scalable, less performant

#### Method 2: Interactive & Dynamic (CSS/JS)
**Use When**: Real-time user interactions require reactive motion

```css
/* CSS Transitions for state changes */
.interactive-slider {
    transform: translateX(0);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* JavaScript for complex interactions */
slider.addEventListener('drag', (e) => {
    const position = calculatePosition(e.clientX);
    slider.style.transform = `translateX(${position}px)`;
    updateShadows(position); // Dynamic shadow offset
});
```

**Applications**:
- Sliders, knobs, switches
- Drag-and-drop interfaces
- Real-time data visualization
- Responsive feedback

**Pros**: Scalable, performant, responsive to user input
**Cons**: Limited to CSS/JS capabilities

---

### Motion Blur

**Principle**: Use motion blur to confidently convey movement and pull viewer attention

```css
/* Subtle motion blur during fast movement */
@keyframes blur-move {
    0% {
        transform: translateX(0);
        filter: blur(0);
    }
    50% {
        transform: translateX(100px);
        filter: blur(4px); /* Peak blur at fastest point */
    }
    100% {
        transform: translateX(200px);
        filter: blur(0);
    }
}
```

**Applications**:
- Fast-moving elements
- Emphasizing speed
- Directing attention to destination
- Creating cinematic quality

**Extraction from Source**:
- Detect motion blur in photography
- Analyze speed of implied movement
- Identify action vs stillness

---

### Color Blocking in Motion

**Principle**: Use 2-3 colors from secondary palettes during animated transitions

```css
/* Color blocking during state transition */
@keyframes color-block-transition {
    0% {
        background: linear-gradient(90deg,
            var(--dark-shade-1) 0%,
            var(--dark-shade-1) 100%);
    }
    50% {
        background: linear-gradient(90deg,
            var(--dark-shade-1) 0%,
            var(--light-shade-1) 50%,
            var(--dark-shade-2) 100%);
    }
    100% {
        background: linear-gradient(90deg,
            var(--light-shade-1) 0%,
            var(--light-shade-1) 100%);
    }
}
```

**Applications**:
- State transitions (off → on)
- Loading indicators
- Progress visualization
- Emotional shifts (calm → alert)

---

### Motion Indicating Depth, Lighting, and Space

#### 1. Depth
```css
/* Parallax layers moving at different speeds */
.layer-background { transform: translateY(calc(scroll * 0.3)); }
.layer-midground { transform: translateY(calc(scroll * 0.6)); }
.layer-foreground { transform: translateY(calc(scroll * 1.0)); }
```

#### 2. Lighting
```css
/* Shadow offset changes indicate light source movement */
.element {
    box-shadow:
        calc(var(--light-x) * 2px)
        calc(var(--light-y) * 2px)
        8px rgba(0,0,0,0.2);
    transition: box-shadow 0.3s ease;
}
```

#### 3. Negative Space
```css
/* Motion reveals negative space */
@keyframes reveal-space {
    from {
        clip-path: inset(0 100% 0 0);
    }
    to {
        clip-path: inset(0 0 0 0);
    }
}
```

#### 4. Shadows
```css
/* Multiple shadow layers create depth */
.layered-shadow {
    box-shadow:
        0 1px 2px rgba(0,0,0,0.12),
        0 2px 4px rgba(0,0,0,0.10),
        0 4px 8px rgba(0,0,0,0.08),
        0 8px 16px rgba(0,0,0,0.06);
}
```

---

### Motion Intensity Based on Mood

**Principle**: Apply motion lightly or heavily depending on extracted mood from source imagery

```python
def determine_motion_intensity(reference_images):
    """Analyze reference images to determine appropriate motion intensity"""
    mood_indicators = {
        'color_saturation': analyze_saturation(images),  # High = energetic
        'contrast': analyze_contrast(images),            # High = dramatic
        'composition_complexity': analyze_complexity(images),  # High = busy
        'lighting': analyze_lighting(images),            # Bright = active
        'subject_energy': detect_movement(images)        # Motion = dynamic
    }

    intensity_score = calculate_weighted_score(mood_indicators)

    if intensity_score > 0.7:
        return 'high'  # Playful, energetic, gaming
    elif intensity_score > 0.4:
        return 'medium'  # Balanced, modern
    else:
        return 'low'  # Professional, calm, minimal
```

**Mood-Based Application**:

| Mood | Motion Intensity | Duration | Properties | Example |
|------|------------------|----------|------------|---------|
| **Playful** | High | 150-300ms | All (position, scale, rotate, color) | Gaming UI, children's apps |
| **Energetic** | High | 200-400ms | Position, scale, opacity, blur | Fitness apps, music players |
| **Professional** | Low | 500-800ms | Position, opacity | Corporate dashboards, finance |
| **Calm** | Low | 600-1000ms | Opacity, position (subtle) | Meditation apps, reading |
| **Modern** | Medium | 300-500ms | Position, scale, opacity | E-commerce, social media |
| **Industrial** | Medium-Low | 400-600ms | Position, rotation (mechanical) | IoT controls, factory UI |
| **Luxury** | Low | 700-1200ms | Opacity, scale (elegant) | Premium brands, jewelry |

---

### Advanced Techniques: Layered Alpha Compositing

**Principle**: Multiple offset layers with alpha channels create realistic depth and lighting

#### Technique 1: Dynamic Multi-Shadow Lighting
```css
.dynamic-lighting-element {
    position: relative;
}

/* Base element */
.dynamic-lighting-element::before {
    content: '';
    position: absolute;
    inset: 0;
    background: var(--element-color);
    border-radius: inherit;
}

/* Shadow layer 1 - Closest */
.dynamic-lighting-element::after {
    content: '';
    position: absolute;
    inset: -2px;
    background: transparent;
    box-shadow:
        calc(var(--light-x) * 1px)
        calc(var(--light-y) * 1px)
        3px rgba(0,0,0,0.15);
    border-radius: inherit;
    transition: box-shadow 0.3s ease;
}

/* JavaScript updates --light-x and --light-y based on interaction */
```

#### Technique 2: Graduating Color Layers for Dynamic Objects
```html
<!-- Multiple divs stacked with alpha transparency -->
<div class="dynamic-object">
    <div class="layer layer-1"></div>  <!-- Darkest -->
    <div class="layer layer-2"></div>  <!-- Mid-dark -->
    <div class="layer layer-3"></div>  <!-- Mid-light -->
    <div class="layer layer-4"></div>  <!-- Lightest -->
</div>
```

```css
.dynamic-object {
    position: relative;
    width: 200px;
    height: 200px;
}

.layer {
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    transition: transform 0.3s ease, opacity 0.3s ease;
}

.layer-1 {
    background: var(--dark-shade-1);
    opacity: 1;
    transform: translate(0, 0);
}

.layer-2 {
    background: var(--dark-shade-2);
    opacity: 0.7;
    transform: translate(2px, 2px);
}

.layer-3 {
    background: var(--light-shade-1);
    opacity: 0.5;
    transform: translate(4px, 4px);
}

.layer-4 {
    background: var(--light-shade-2);
    opacity: 0.3;
    transform: translate(6px, 6px);
}

/* On hover/interaction, layers shift to create 3D illusion */
.dynamic-object:hover .layer-1 { transform: translate(-2px, -2px); }
.dynamic-object:hover .layer-2 { transform: translate(0, 0); }
.dynamic-object:hover .layer-3 { transform: translate(2px, 2px); }
.dynamic-object:hover .layer-4 { transform: translate(4px, 4px); }
```

#### Technique 3: Selling 3D with 2D Layers
```css
/* Simulating 3D button press with 2D offsets */
.button-3d {
    position: relative;
    background: var(--primary-color);
    border: none;
    padding: 15px 30px;
    cursor: pointer;
    transition: transform 0.1s ease, box-shadow 0.1s ease;

    /* Multiple shadow layers */
    box-shadow:
        0 2px 0 var(--dark-shade-1),
        0 4px 0 var(--dark-shade-2),
        0 6px 0 var(--dark-shade-3),
        0 8px 20px rgba(0,0,0,0.2);
}

.button-3d:active {
    transform: translateY(4px);  /* Press down */
    box-shadow:
        0 1px 0 var(--dark-shade-1),
        0 2px 0 var(--dark-shade-2),
        0 3px 10px rgba(0,0,0,0.2);  /* Reduced depth */
}
```

---

### Motion Guidelines

#### Generative Motion Rules

1. **Style Fidelity**: Motion intensity must match mood extracted from reference images
2. **Sequential Flow**: Animate elements in visual hierarchy order (guide the eye)
3. **Performance**: Maintain 60fps minimum, use GPU-accelerated properties
4. **Purposeful Motion**: Every animation serves function (feedback, emphasis, guidance)
5. **Property Combinations**: Use multiple properties for expressive, realistic effects
6. **Layering**: Use alpha compositing for depth, lighting, 3D illusion
7. **Accessibility**: Respect `prefers-reduced-motion` for users with vestibular disorders
8. **Conditional Complexity**: Simple UIs = subtle motion, complex UIs = dynamic motion
9. **Timing Variation**: Vary timing based on intensity (low=slow, high=fast)
10. **Motion Blur**: Use sparingly for emphasis and directional pull

#### Application Motion Rules (GenUI Interface)

1. **Consistency**: Use standardized durations and easing throughout GenUI app
2. **Performance**: GPU-accelerated properties only (transform, opacity)
3. **Subtlety**: Professional, calm motion befitting design tool
4. **Feedback**: All interactions provide visual confirmation
5. **Progressive Enhancement**: Core functionality works without motion

---

### Accessibility Considerations
```css
/* Respect user preferences */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
}
```

---

## 24. Content Strategy & Voice

### Writing Principles

#### 1. **Clarity Over Cleverness**
❌ "We're cooking up your design system!"
✅ "Generating your design system..."

#### 2. **Active Voice**
❌ "Your components have been generated."
✅ "We generated your components."

#### 3. **Concise & Scannable**
- Lead with key information
- Use bullet points
- Break up long paragraphs
- Highlight important terms

#### 4. **Human & Approachable**
❌ "Error 4XX: Invalid parameter"
✅ "Oops! We couldn't process that image. Try a PNG or JPG."

### Content Types

#### Button Labels
**Action-Oriented, Specific**
- ✅ "Generate Design System"
- ✅ "Upload Images"
- ✅ "Export Components"
- ❌ "Submit"
- ❌ "OK"
- ❌ "Continue"

#### Error Messages
**Format**: [What happened] + [Why] + [What to do]

Examples:
```
❌ Upload failed
✅ We couldn't upload your image (file too large).
   Try an image under 10MB.

❌ Invalid input
✅ This doesn't look like a valid image file.
   We support PNG, JPG, and WebP.
```

#### Success Messages
**Format**: [Confirmation] + [What's next]

Examples:
```
✅ Design system generated!
   Click "Download" to get your components.

✅ 4 images uploaded successfully.
   Click "Start Generation" when ready.
```

#### Empty States
**Format**: [Why empty] + [Encouraging action]

Examples:
```
No design system yet
Upload 1-4 reference images to get started.

No components generated
Complete the Visual DNA step to generate components.
```

### Tone Guidelines by Context

| Context | Tone | Example |
|---------|------|---------|
| **Onboarding** | Encouraging, Simple | "Upload your first image to see the magic ✨" |
| **Processing** | Informative, Progressive | "Analyzing patterns... 60% complete" |
| **Success** | Celebratory, Specific | "🎉 Generated 32 components in 12 variations" |
| **Error** | Helpful, Blame-free | "No worries! Let's try a different approach." |
| **Settings** | Technical, Clear | "Maximum upload size: 10MB per image" |

---

**Document maintained by**: GenUI Design Team
**Last updated**: 2025-10-29
**Version**: 2.0 - Comprehensive Brand Guidelines

For questions or suggestions, please contact the design team or open an issue in the project repository.
