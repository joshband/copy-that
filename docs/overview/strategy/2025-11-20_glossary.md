# Copy This - Glossary

> Key terms and concepts used throughout the Copy This documentation

---

## Design System Terms

### Design Token

A design token is a named, platform-agnostic variable that stores visual design attributes (colors, spacing, typography, etc.) in a structured format. Tokens enable consistent design systems across multiple platforms and can be referenced by other tokens.

**Example**: `primary-500: #F15925`

**Categories in Copy This**: Color, spacing, typography, shadows, elevation, z-index, icon sizes, gradients, mobile tokens

### Token Types

#### Primitive Token

Base-level design tokens that contain raw values and are not dependent on other tokens. These form the foundation of the design system.

**Example**: `orange-500: #F15925`, `spacing-md: 16px`

#### Semantic Token

Mid-level tokens that reference primitive tokens and provide meaning/intent to their usage. They describe *what* the token represents rather than *how* it looks.

**Example**: `brand-primary: {orange-500}`, `button-spacing: {spacing-md}`

#### Component Token

High-level tokens specific to UI components that reference semantic or primitive tokens. These are the most specific layer of the token hierarchy.

**Example**: `button-default-bg: {brand-primary}`, `card-padding: {spacing-md}`

### Token Reference System

The hierarchical relationship between token types:
```
Primitive → Semantic → Component → Final Value
orange-500 → brand-primary → button-bg → #F15925
```

---

## System Architecture Terms

### Extractor

A modular Python class that extracts specific design tokens from reference images using computer vision techniques. All extractors inherit from the `TokenExtractor` abstract base class.

**Available Extractors**: ColorExtractor, GradientExtractor, MobileExtractor, SpacingExtractor, ShadowExtractor, TypographyExtractor, ZIndexExtractor, IconSizeExtractor

### Pipeline

The complete workflow from reference image input to production code output:
1. Image upload
2. Token extraction (10 extractors)
3. Validation (WCAG, schema)
4. Normalization
5. Multi-format export

### Generator

A TypeScript module that transforms extracted design tokens into platform-specific code (React components, JUCE headers, Figma tokens, Material-UI themes).

---

## Visual Design Terms

### Ontology

A formal representation of knowledge within a domain, defining concepts, categories, properties, and relationships. In Copy This, the **schema ontology** classifies visual design properties:

- **Art Historical Context**: Movement, era, cultural influences
- **Visual Style**: Rendering treatment, illustration vs. photorealistic
- **Contrast Systems**: Value, color, scale, line weight
- **Spatial Systems**: Grid structure, alignment, whitespace
- **Material Properties**: Surface qualities, wear, tactile attributes

**Purpose**: Enables systematic analysis of design aesthetics beyond color and spacing

### Taxonomy

A hierarchical classification system for organizing design concepts. In Copy This, taxonomies include:

- **Color Families**: Neutral, warm, cool, vibrant, muted
- **Elevation Levels**: 0-5 (flat to highest)
- **Z-Index Layers**: base, dropdown, sticky, fixed, overlay, modal, tooltip

### Color Scale

A progression of shades from lightest to darkest within a color family, typically numbered 50-900. Each primitive color family has 10 shades.

**Example**: `orange-50` (lightest) → `orange-500` (base) → `orange-900` (darkest)

### LAB Color Space

A perceptually uniform color space where distances between colors correspond to human visual perception. Used for accurate color clustering and deduplication.

**Why LAB?**: Unlike RGB, equal distances in LAB space represent equal perceptual color differences (ΔE)

---

## Accessibility Terms

### WCAG (Web Content Accessibility Guidelines)

International standards for web accessibility. Copy This validates color contrast ratios against WCAG AA standards.

**WCAG AA Requirements**:
- Normal text: 4.5:1 contrast ratio
- Large text: 3:1 contrast ratio

### Contrast Ratio

A numeric value representing the luminance difference between two colors, where higher values indicate better readability.

**Example**: Text on Primary: 5.62 (AA compliant ✅)

---

## Computer Vision Terms

### k-means Clustering

An unsupervised machine learning algorithm that groups pixels into k clusters based on color similarity. Copy This uses k=12 clusters for color extraction.

### Edge Detection (Canny)

A computer vision technique that identifies boundaries in images by detecting discontinuities in brightness. Used for spacing and layout analysis.

### Contour Analysis

Detection and measurement of closed curves in images. Used to identify UI components (buttons, icons) and extract sizing information.

---

## Export Formats

### Figma Tokens

JSON format compatible with Figma's design token system, enabling direct import into Figma design files.

### Material-UI Theme

JavaScript object following Material-UI's theme structure for React applications.

### JUCE Headers

C++ header files with `juce::Colour` definitions for audio plugin and desktop application development.

### React Components

Interactive React components demonstrating token usage with live preview capabilities.

---

## Development Terms

### Phase 1 Demo

The original React-based interactive demo (localhost:5173) showing extracted tokens in a standalone visualization.

**Location**: `targets/react/`

### v2.0 Web Application

The full-stack application with FastAPI backend and React frontend for interactive token extraction and editing.

**Ports**: Backend :8000, Frontend :5174

### Job

An asynchronous extraction task tracked in the SQLite database. Jobs have statuses: `pending`, `processing`, `completed`, `failed`.

### Project

A saved collection of design tokens that can be loaded, edited, and exported. Stored in the SQLite database.

---

## File Formats

### style_guide.json

Raw extraction output containing all tokens from all extractors before normalization.

**Location**: Root directory (gitignored)

### tokens.json

Normalized, validated design tokens ready for export.

**Location**: Root directory (gitignored)

### extraction_results/

Directory containing job-specific extraction outputs with timestamps.

**Location**: `backend/extraction_results/` (gitignored)

---

## Testing Terms

### Contract Test

API tests that verify backend endpoints conform to expected input/output schemas.

**Coverage**: 80% backend test coverage

### Integration Test

End-to-end tests validating the complete pipeline from image upload to code export.

**Example**: Upload reference → extract tokens → validate WCAG → export React

### Coverage

Percentage of code executed during testing. Copy This maintains 80% overall coverage.

---

## Related Concepts

### Design System

A collection of reusable components, guided by clear standards, that can be assembled to build applications.

### Style Guide

Visual documentation of design standards including colors, typography, spacing, and component usage patterns.

### Component Library

A collection of pre-built, reusable UI components following a consistent design system.

---

## Quick Reference

| Term | Category | Definition |
|------|----------|------------|
| Token | Core | Platform-agnostic design variable |
| Primitive | Token Type | Base-level token with raw value |
| Semantic | Token Type | Token providing meaning/intent |
| Component | Token Type | Component-specific token |
| Ontology | Visual Design | Formal knowledge representation |
| Taxonomy | Classification | Hierarchical organization system |
| Extractor | Architecture | Computer vision token extraction module |
| Pipeline | Workflow | Complete image → code transformation |
| WCAG | Accessibility | Web accessibility standards |
| LAB | Color Science | Perceptually uniform color space |
| k-means | ML | Color clustering algorithm |

---

**Last Updated**: 2025-11-05 (v2.0 MVP)
