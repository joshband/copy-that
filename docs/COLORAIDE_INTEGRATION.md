# ColorAide Integration Across Color Pipeline

## Overview

ColorAide is integrated throughout the color token extraction pipeline as the **authoritative color science library**. It provides industry-standard algorithms for perceptual color analysis and harmony detection.

---

## Pipeline Integration Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTRACTION PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  IMAGE INPUT                                                    │
│      ↓                                                           │
│  Claude Sonnet 4.5 (Vision Analysis)                           │
│      ↓                                                           │
│  Raw Hex Colors → AIColorExtractor                             │
│      ↓                                                           │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  COLORAIDE PROCESSING LAYER                             │  │
│  │  (color_utils.py & color_extractor.py)                  │  │
│  │                                                          │  │
│  │  ├─ color_utils.compute_all_properties()               │  │
│  │  │  ├─ is_neutral_color() [ColorAide.achromatic()]     │  │
│  │  │  ├─ calculate_delta_e() [ColorAide.delta_e()]       │  │
│  │  │  ├─ calculate_wcag_contrast() [ColorAide.luminance()]│ │
│  │  │  └─ is_color_in_gamut() [ColorAide.gamut()]         │  │
│  │  │                                                      │  │
│  │  └─ color_extractor._parse_color_response()            │  │
│  │     └─ get_color_harmony() [ColorAide.hsl.hue]         │  │
│  │                                                          │  │
│  └─────────────────────────────────────────────────────────┘  │
│      ↓                                                           │
│  ColorToken (Pydantic) with all ColorAide-computed fields      │
│      ↓                                                           │
│  DATABASE STORAGE (color_tokens table)                         │
│      ↓                                                           │
│  API RESPONSE (ColorTokenResponse)                             │
│      ↓                                                           │
│  FRONTEND (React - future Zod validation)                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer-by-Layer Integration

### 1. **Schema Layer** (Pydantic Model)
**File:** `src/copy_that/application/color_extractor.py:19-74`

```python
class ColorToken(BaseModel):
    # ColorAide-generated fields
    is_neutral: Optional[bool]              # From achromatic()
    wcag_contrast_on_white: Optional[float] # From luminance()
    wcag_contrast_on_black: Optional[float] # From luminance()
    wcag_aa_compliant_text: Optional[bool]  # From luminance() + contrast calc
    wcag_aaa_compliant_text: Optional[bool] # From luminance() + contrast calc
    wcag_aa_compliant_normal: Optional[bool] # From luminance() + contrast calc
    wcag_aaa_compliant_normal: Optional[bool]# From luminance() + contrast calc
    delta_e_to_dominant: Optional[float]    # From delta_e()
    harmony: Optional[str]                  # From hsl.hue analysis
```

**Metadata Tracking:**
```python
extraction_metadata: Optional[dict]
# Example: {
#   "is_neutral": "color_utils.is_neutral_color",
#   "wcag_contrast_on_white": "color_utils.calculate_wcag_contrast",
#   "harmony": "color_utils.get_color_harmony"
# }
```

---

### 2. **Database Layer** (SQLAlchemy Model)
**File:** `src/copy_that/domain/models.py:67-135`

```python
class ColorToken(Base):
    __tablename__ = "color_tokens"

    # All ColorAide-computed fields stored as columns
    is_neutral: Mapped[Optional[bool]]
    wcag_contrast_on_white: Mapped[Optional[float]]
    wcag_contrast_on_black: Mapped[Optional[float]]
    wcag_aa_compliant_text: Mapped[Optional[bool]]
    wcag_aaa_compliant_text: Mapped[Optional[bool]]
    wcag_aa_compliant_normal: Mapped[Optional[bool]]
    wcag_aaa_compliant_normal: Mapped[Optional[bool]]
    delta_e_to_dominant: Mapped[Optional[float]]
    harmony: Mapped[Optional[str]]
    extraction_metadata: Mapped[Optional[str]]  # JSON: tool attribution
```

**Persistence:** All ColorAide-computed properties are stored in `color_tokens` table with full attribution in `extraction_metadata`.

---

### 3. **Extraction Layer** (ColorAide Integration)
**File:** `src/copy_that/application/color_utils.py`

#### Function Overview

| Function | ColorAide Method | Purpose | Line |
|----------|------------------|---------|------|
| `is_neutral_color()` | `.achromatic()` | Grayscale detection | 260-268 |
| `is_color_in_gamut()` | `.gamut()` | sRGB displayability | 272-278 |
| `calculate_wcag_contrast()` | `.luminance()` | Contrast ratio (WCAG 2.1) | 282-297 |
| `calculate_delta_e()` | `.delta_e()` | Perceptual distance (CIEDE2000) | 399-417 |
| `get_color_harmony()` | `.convert("hsl")["hue"]` | Color harmony classification | 420-479 |

#### ColorAide Capabilities Used

1. **Perceptual Uniformity** (Delta-E)
   - Industry standard: CIEDE2000
   - Used for: Color similarity detection, palette merging, nearest-color matching
   - Threshold-based: ΔE < 2 (barely noticeable), < 5 (similar), < 15 (distinct)

2. **Luminance Calculation** (WCAG 2.1)
   - Accurate relative luminance using relative luminosity formula
   - Used for: Contrast ratio calculation, WCAG AA/AAA compliance checking
   - Replaces manual gamma correction (ColorAide handles all color space conversions)

3. **Achromatic Detection**
   - Detects colors with zero saturation (true grayscale)
   - Used for: Neutral color classification
   - Better algorithm than simple saturation checks

4. **Gamut Mapping** (sRGB)
   - Validates colors displayable in standard sRGB color space
   - Used for: Color validity checking before storage
   - Future: Support for wide-gamut spaces (P3, Rec2020)

5. **HSL Conversion**
   - Perceptually-correct hue angle extraction
   - Used for: Color harmony analysis (complementary, analogous, triadic, etc.)

---

### 4. **Extraction Workflow** (AIColorExtractor)
**File:** `src/copy_that/application/color_extractor.py:237-354`

**Workflow in `_parse_color_response()`:**

```python
for hex_code in response_text.findall(r"#[0-9A-Fa-f]{6}"):
    # Step 1: Compute all ColorAide-based properties
    all_properties, extraction_metadata = \
        color_utils.compute_all_properties_with_metadata(
            hex_code,
            dominant_colors[:3]  # For Delta-E and harmony
        )

    # Step 2: Calculate harmony using ColorAide hue analysis
    harmony = color_utils.get_color_harmony(
        hex_code,
        dominant_colors[:3]
    )

    # Step 3: Build ColorToken with all ColorAide-computed fields
    color_token = ColorToken(
        hex=hex_code,
        rgb=f"rgb{rgb}",
        # ColorAide fields from step 1:
        wcag_contrast_on_white=all_properties.get("wcag_contrast_on_white"),
        wcag_contrast_on_black=all_properties.get("wcag_contrast_on_black"),
        wcag_aa_compliant_text=all_properties.get("wcag_aa_compliant_text"),
        is_neutral=all_properties.get("is_neutral"),
        delta_e_to_dominant=all_properties.get("delta_e_to_dominant"),
        # ColorAide field from step 2:
        harmony=harmony,
        # Metadata tracking (for provenance):
        extraction_metadata=extraction_metadata  # Maps each field to ColorAide function
    )
```

---

### 5. **API Layer** (FastAPI Schema)
**File:** `src/copy_that/interfaces/api/schemas.py:36-92`

```python
class ColorTokenResponse(BaseModel):
    # All ColorAide-computed fields exposed in API
    wcag_contrast_on_white: Optional[float]
    wcag_contrast_on_black: Optional[float]
    wcag_aa_compliant_text: Optional[bool]
    wcag_aaa_compliant_text: Optional[bool]
    wcag_aa_compliant_normal: Optional[bool]
    wcag_aaa_compliant_normal: Optional[bool]
    colorblind_safe: Optional[bool]
    is_neutral: Optional[bool]
    delta_e_to_dominant: Optional[float]
    harmony: Optional[str]
    extraction_metadata: Optional[dict]  # Documents ColorAide provenance
```

**Example API Response:**
```json
{
  "hex": "#FF5733",
  "name": "Sunset Orange",
  "design_intent": "accent",
  "harmony": "complementary",
  "is_neutral": false,
  "wcag_contrast_on_white": 5.2,
  "wcag_contrast_on_black": 2.1,
  "wcag_aa_compliant_text": true,
  "wcag_aaa_compliant_text": false,
  "delta_e_to_dominant": 15.3,
  "extraction_metadata": {
    "harmony": "color_utils.get_color_harmony",
    "wcag_contrast_on_white": "color_utils.calculate_wcag_contrast",
    "is_neutral": "color_utils.is_neutral_color",
    "delta_e_to_dominant": "color_utils.calculate_delta_e"
  }
}
```

---

### 6. **Frontend Layer** (TypeScript - Future)
**File:** `frontend/src/types/generated/color.zod.ts` (to be created)

**Planned Zod Schema Generation:**
```typescript
import { z } from "zod";

const ColorTokenSchema = z.object({
  hex: z.string().regex(/^#[0-9A-Fa-f]{6}$/),
  harmony: z.enum([
    "monochromatic",
    "analogous",
    "complementary",
    "triadic",
    "tetradic",
    "split-complementary"
  ]).nullable(),
  wcag_aa_compliant_text: z.boolean().nullable(),
  wcag_aaa_compliant_text: z.boolean().nullable(),
  is_neutral: z.boolean().nullable(),
  delta_e_to_dominant: z.number().min(0).nullable(),
  extraction_metadata: z.record(z.string()).nullable(),
  // ... other fields
});
```

---

## ColorAide Features Used

| Feature | Status | Use Case |
|---------|--------|----------|
| Delta-E (CIEDE2000) | ✅ **ACTIVE** | Perceptual color distance |
| Luminance (WCAG) | ✅ **ACTIVE** | Contrast ratio calculation |
| Achromatic Detection | ✅ **ACTIVE** | Neutral color classification |
| Gamut Checking (sRGB) | ✅ **ACTIVE** | Color validity |
| HSL Hue Extraction | ✅ **ACTIVE** | Harmony analysis |
| Color Matching | ⏳ **PLANNED** | `.match()` for palette similarity |
| Gamut Mapping | ⏳ **PLANNED** | `.fit()` for wide-gamut support |

---

## Testing Coverage

**ColorAide Integration Tests:** `tests/unit/test_coloraide_integration.py`

```
✅ Delta-E identical colors (0.0)
✅ Delta-E complementary colors (>10.0)
✅ Delta-E is symmetric (a→b = b→a)
✅ WCAG contrast (1:1 to 21:1)
✅ Achromatic detection (black, white, grays)
✅ Gamut checking (sRGB validation)
✅ Harmony calculation (6 harmony types)
```

**Total: 18 tests, 100% passing**

---

## Token Relationship Patterns

### 1. **Palette Harmony**
Colors are analyzed relative to **dominant colors** (top 3 from extraction).
- Harmony ties each color to the broader palette context
- Enables: Palette visualizations, harmony validation, color suggestion

### 2. **Perceptual Similarity (Delta-E)**
- Colors within ΔE < 15: Can be merged/consolidated
- Used for: Duplicate detection, palette reduction, color clustering

### 3. **Accessibility Relationships**
- WCAG contrast links: Target color ↔ Reference background
- References: White (#FFFFFF) and Black (#000000)
- Calculated using ColorAide luminance + standard contrast formula

---

## Architecture Benefits

1. **Single Source of Truth:** All color science goes through ColorAide
2. **Provenance Tracking:** `extraction_metadata` documents which tool computed each field
3. **Reproducibility:** ColorAide functions are deterministic
4. **Extensibility:** Easy to add new ColorAide-based properties
5. **Type Safety:** End-to-end validation (Pydantic → DB → API → Zod)

---

## Future Enhancements

### Medium Priority
- Implement `color_utils.match_palette()` using ColorAide `.match()`
- Add wide-gamut support (P3, Rec2020)
- Palette consistency analysis

### Low Priority
- Color naming using ColorAide's named color database
- Advanced color harmony (quadratic, etc.)
- Historical color palette evolution tracking

---

## References

- **ColorAide Docs:** https://facelessuser.github.io/coloraide/
- **WCAG 2.1 Contrast:** https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum
- **Delta-E (CIEDE2000):** https://en.wikipedia.org/wiki/Color_difference#CIEDE2000
- **Color Harmony Theory:** https://en.wikipedia.org/wiki/Harmony_(color)
