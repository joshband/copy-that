# Design Libraries & Multi-Style Inheritance Guide

**Architecture: Parent/Child Style Library System with Token Storage & Schema Mapping**

Version: 3.1
Last Updated: 2025-11-11
Status: Multi-Style Inheritance Architecture

---

## Overview

This guide documents the **multi-style inheritance architecture** where multiple design style libraries inherit from an abstracted parent base, enabling a **design system of design systems**.

**Key Concept**: Each extracted design (like "Analog Whimsy Systems") becomes its own component library, but all libraries share a common base for consistency and interoperability.

```
@design-system/core (Abstract Parent)
├── @analog-whimsy/ui (Child Style 1)
├── @brutalist-console/ui (Child Style 2)
├── @minimal-glass/ui (Child Style 3)
├── @neo-skeuomorph/ui (Child Style 4)
└── ... (infinite extensibility)
```

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Abstract Base Package](#abstract-base-package)
3. [Derived Style Libraries](#derived-style-libraries)
4. [Token Storage & Database](#token-storage-database)
5. [Schema Mapper Integration](#schema-mapper-integration)
6. [Library Loading & Discovery](#library-loading-discovery)
7. [Multi-Style Application](#multi-style-application)

---

## Architecture Overview

### The Design System of Design Systems

**Problem**: Traditional design systems are monolithic (one style for entire product)
**Solution**: Meta-framework where each design extraction creates an independent, interoperable style library

### Three-Tier Architecture

```
┌─────────────────────────────────────────┐
│   @design-system/core (Abstract Base)  │
│   - Base theme provider                 │
│   - Common token types                  │
│   - Abstract component interfaces       │
│   - Shared utilities (motion, a11y, cx) │
└─────────────────────────────────────────┘
                    ↓ extends
┌─────────────────────────────────────────┐
│   Derived Style Libraries (Children)    │
│   - @analog-whimsy/ui                   │
│   - @brutalist-console/ui               │
│   - @minimal-glass/ui                   │
│   - @neo-skeuomorph/ui                  │
└─────────────────────────────────────────┘
                    ↓ consumed by
┌─────────────────────────────────────────┐
│   Applications                          │
│   - Can switch styles at runtime        │
│   - Can mix styles (micro-frontends)    │
│   - Consistent API across all styles   │
└─────────────────────────────────────────┘
```

---

## Abstract Base Package

### Package Structure: `@design-system/core`

```
@design-system/core/
├── package.json
├── tsconfig.json
├── src/
│  ├── index.ts
│  ├── types/
│  │  ├── tokens.types.ts       # Base token interfaces
│  │  ├── component.types.ts    # Base component props
│  │  └── ontology.types.ts     # Design language ontology
│  ├── theme/
│  │  ├── ThemeProvider.tsx     # Abstract base provider
│  │  ├── useTheme.ts           # Theme hook
│  │  └── ThemeContext.tsx      # Context API
│  ├── components/
│  │  ├── base/                 # Abstract base components
│  │  │  ├── BaseButton.tsx
│  │  │  ├── BaseKnob.tsx
│  │  │  ├── BaseSlider.tsx
│  │  │  └── BasePanel.tsx
│  │  └── primitives/           # Unstyled primitives
│  │     ├── Box.tsx
│  │     ├── Stack.tsx
│  │     └── Text.tsx
│  ├── utils/
│  │  ├── motion.ts             # Animation utilities
│  │  ├── a11y.ts               # Accessibility helpers
│  │  ├── cx.ts                 # ClassName combiner
│  │  └── tokens.ts             # Token transformation utilities
│  └── storage/
│     ├── TokenStorage.ts       # Token storage interface
│     ├── LibraryRegistry.ts    # Style library registry
│     └── SchemaMapper.ts       # Schema validation
└── styles/
   └── reset.css                # CSS reset only
```

---

### Base Token Types

```typescript
// @design-system/core/src/types/tokens.types.ts

/** Base token types shared across all style libraries */
export interface BaseDesignTokens {
  // Foundation tokens (required)
  colors: {
    [key: string]: string;  // Hex colors
  };
  spacing: {
    [key: string]: number;  // Pixel values
  };
  typography: {
    families: {
      [key: string]: string;  // Font stack
    };
    sizes: {
      [key: string]: number;  // px or rem
    };
    weights: {
      [key: string]: number;  // 100-900
    };
  };
  radius: {
    [key: string]: number;  // Border radius in px
  };
  shadows: {
    [key: string]: string;  // CSS box-shadow
  };

  // Optional Visual DNA tokens
  materials?: {
    [key: string]: MaterialToken;
  };
  lighting?: LightingToken;
  environment?: EnvironmentToken;
  artistic?: ArtisticToken;

  // Optional Ontology (design language metadata)
  ontology?: DesignLanguageOntology;
}

/** Material properties from MaterialExtractor */
export interface MaterialToken {
  material_class: 'plastic' | 'metal' | 'glass' | 'wood' | 'ceramic' | 'fabric';
  variant: string;
  optical: {
    gloss: number;         // 0-1
    reflectivity: number;  // 0-1
    transmission: number;  // 0-1 (for glass)
  };
  tactile: {
    friction: number;  // 0-1
    warmth: number;    // 0-1
    grain: number;     // 0-1
  };
  finish: 'matte' | 'satin' | 'gloss' | 'mirror';
}

/** Design language ontology from AI extraction */
export interface DesignLanguageOntology {
  name: string;                    // e.g., "Analog Whimsy Systems"
  definition: string;
  stylistic_lineage: string[];
  design_principles: DesignPrinciple[];
  composition: CompositionOntology;
  interaction_metaphor: string;
  narrative_archetype?: NarrativeArchetype;
}

export interface DesignPrinciple {
  name: string;
  rule: string;
  rationale: string;
  visual_manifestation: string;
}
```

---

### Abstract Theme Provider

```typescript
// @design-system/core/src/theme/ThemeProvider.tsx

import React, { createContext, useContext, useState } from 'react';
import { BaseDesignTokens } from '../types/tokens.types';

export interface ThemeContextValue {
  tokens: BaseDesignTokens;
  styleName: string;
  setStyle: (name: string) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export interface BaseThemeProviderProps {
  tokens: BaseDesignTokens;
  styleName: string;
  children: React.ReactNode;
  onStyleChange?: (name: string) => void;
}

export const BaseThemeProvider: React.FC<BaseThemeProviderProps> = ({
  tokens,
  styleName,
  children,
  onStyleChange
}) => {
  const [currentStyle, setCurrentStyle] = useState(styleName);

  const setStyle = (name: string) => {
    setCurrentStyle(name);
    onStyleChange?.(name);
  };

  // Inject CSS variables from tokens
  React.useEffect(() => {
    const root = document.documentElement;

    // Colors
    Object.entries(tokens.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });

    // Spacing
    Object.entries(tokens.spacing).forEach(([key, value]) => {
      root.style.setProperty(`--space-${key}`, `${value}px`);
    });

    // Typography
    Object.entries(tokens.typography.families).forEach(([key, value]) => {
      root.style.setProperty(`--font-${key}`, value);
    });

    // Radius
    Object.entries(tokens.radius).forEach(([key, value]) => {
      root.style.setProperty(`--radius-${key}`, `${value}px`);
    });

    // Materials (optional)
    if (tokens.materials) {
      Object.entries(tokens.materials).forEach(([key, material]) => {
        root.style.setProperty(`--material-${key}-gloss`, String(material.optical.gloss));
      });
    }

    // Store style name
    root.setAttribute('data-style', currentStyle);
  }, [tokens, currentStyle]);

  const value: ThemeContextValue = {
    tokens,
    styleName: currentStyle,
    setStyle
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextValue => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within BaseThemeProvider');
  }
  return context;
};
```

---

### Abstract Base Components

```typescript
// @design-system/core/src/components/base/BaseButton.tsx

import React from 'react';
import { useTheme } from '../../theme/useTheme';

export interface BaseButtonProps {
  variant?: 'primary' | 'secondary' | 'tertiary';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

/**
 * Abstract base button - provides structure, no visual styling.
 * Child style libraries override CSS to apply visual treatment.
 */
export const BaseButton: React.FC<BaseButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  children,
  onClick,
  className = ''
}) => {
  const { tokens, styleName } = useTheme();

  return (
    <button
      className={`base-button base-button--${variant} base-button--${size} ${styleName}-button ${className}`}
      disabled={disabled}
      onClick={onClick}
      style={{
        '--button-color': tokens.colors[variant] || tokens.colors.primary,
        '--button-radius': `${tokens.radius[size] || tokens.radius.md}px`
      } as React.CSSProperties}
    >
      {children}
    </button>
  );
};
```

```typescript
// @design-system/core/src/components/base/BaseKnob.tsx

import React, { useCallback, useRef, useState } from 'react';
import { useTheme } from '../../theme/useTheme';

export interface BaseKnobProps {
  value: number;         // 0-1 normalized
  onChange: (v: number) => void;
  label?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  accent?: string;       // Token color key
  disabled?: boolean;
  className?: string;
}

/**
 * Abstract base knob - provides rotation logic, no visual styling.
 * Child style libraries override CSS for enamel, metallic, glass treatments.
 */
export const BaseKnob: React.FC<BaseKnobProps> = ({
  value,
  onChange,
  label,
  size = 'md',
  accent = 'primary',
  disabled = false,
  className = ''
}) => {
  const { tokens, styleName } = useTheme();
  const dialRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const rotation = -135 + (value * 270);  // 0° to 270°

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    if (disabled) return;
    setIsDragging(true);
    dialRef.current?.setPointerCapture(e.pointerId);
  }, [disabled]);

  const handlePointerMove = useCallback((e: PointerEvent) => {
    if (!isDragging || !dialRef.current) return;

    const rect = dialRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    const angle = Math.atan2(e.clientY - centerY, e.clientX - centerX);
    const degrees = (angle * 180 / Math.PI + 90 + 360) % 360;

    const newValue = Math.max(0, Math.min(1, degrees / 270));
    onChange(newValue);
  }, [isDragging, onChange]);

  const handlePointerUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  React.useEffect(() => {
    if (isDragging) {
      window.addEventListener('pointermove', handlePointerMove);
      window.addEventListener('pointerup', handlePointerUp);
      return () => {
        window.removeEventListener('pointermove', handlePointerMove);
        window.removeEventListener('pointerup', handlePointerUp);
      };
    }
  }, [isDragging, handlePointerMove, handlePointerUp]);

  return (
    <div className={`base-knob-container ${styleName}-knob-container ${className}`}>
      {label && <label className="base-knob-label">{label}</label>}
      <div
        ref={dialRef}
        className={`base-knob base-knob--${size} ${styleName}-knob`}
        role="slider"
        aria-label={label}
        aria-valuemin={0}
        aria-valuemax={1}
        aria-valuenow={value}
        aria-disabled={disabled}
        tabIndex={disabled ? -1 : 0}
        style={{
          '--knob-rotation': `${rotation}deg`,
          '--knob-color': tokens.colors[accent] || tokens.colors.primary,
          '--knob-size': `${tokens.spacing[size] || tokens.spacing.md}px`
        } as React.CSSProperties}
        onPointerDown={handlePointerDown}
      >
        <div className="base-knob-dial" />
      </div>
    </div>
  );
};
```

---

## Derived Style Libraries

### Child Style 1: `@analog-whimsy/ui`

**Package Structure**:
```
@analog-whimsy/ui/
├── package.json        # Depends on @design-system/core
├── src/
│  ├── index.ts         # Re-exports core + overrides
│  ├── theme/
│  │  ├── tokens.ts     # Analog Whimsy specific tokens
│  │  └── AnalogWhimsyProvider.tsx
│  ├── components/
│  │  ├── AWSButton.tsx      # Styled BaseButton
│  │  ├── AWSKnob.tsx        # Styled BaseKnob (enamel gloss)
│  │  ├── AWSPanel.tsx       # Styled BasePanel (brass trim)
│  │  └── AWSMeter.tsx       # New component (analog meter)
│  └── styles/
│     └── analog-whimsy.css  # Visual overrides
```

**Tokens** (from extraction):
```typescript
// @analog-whimsy/ui/src/theme/tokens.ts

import { BaseDesignTokens } from '@design-system/core';

export const analogWhimsyTokens: BaseDesignTokens = {
  colors: {
    coral: '#F56A5D',
    teal: '#45B0A6',
    lemon: '#FFD85C',
    peach: '#F6A58E',
    mint: '#E6F4EE',
    surface: '#FDF7EE',
    brass: '#B08C4C',      // From materials.brass-trim
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32
  },
  typography: {
    families: {
      base: 'Inter, sans-serif',
      mono: 'JetBrains Mono, monospace'
    },
    sizes: {
      sm: 12,
      base: 14,
      lg: 16
    },
    weights: {
      normal: 400,
      medium: 500,
      bold: 700
    }
  },
  radius: {
    sm: 8,
    md: 16,
    lg: 24,
    full: 9999
  },
  shadows: {
    sm: '0 1px 3px rgba(0,0,0,0.12)',
    md: '0 4px 8px rgba(0,0,0,0.16)',
    lg: '0 8px 16px rgba(0,0,0,0.24)'
  },
  materials: {
    'enamel-gloss': {
      material_class: 'plastic',
      variant: 'vintage bakelite',
      optical: {
        gloss: 0.7,
        reflectivity: 0.4,
        transmission: 0.0
      },
      tactile: {
        friction: 0.5,
        warmth: 0.6,
        grain: 0.1
      },
      finish: 'gloss'
    },
    'brass-trim': {
      material_class: 'metal',
      variant: 'brushed brass',
      optical: {
        gloss: 0.6,
        reflectivity: 0.7,
        transmission: 0.0
      },
      tactile: {
        friction: 0.4,
        warmth: 0.3,
        grain: 0.2
      },
      finish: 'satin'
    }
  },
  ontology: {
    name: 'Analog Whimsy Systems',
    definition: 'Multi-sensory interface system merging retro instrumentality, ecological aesthetics, and human-centered tactility',
    stylistic_lineage: [
      'Retro-futurism (1960s NASA)',
      'Mid-century modernism (Braun)',
      'Techno-botanical surrealism'
    ],
    design_principles: [
      {
        name: 'Function-through-Form',
        rule: 'Make affordances explicit',
        rationale: 'Reduce cognitive load by making interactive elements visually obvious',
        visual_manifestation: '3D buttons, shadows, glossy surfaces'
      },
      {
        name: 'Color-driven Cognition',
        rule: 'Warm=action, cool=feedback, neutral=structure',
        rationale: 'Leverage pre-attentive processing',
        visual_manifestation: 'Orange knobs, teal meters, cream panels'
      }
    ],
    composition: {
      layout_paradigm: 'grid-less modular',
      flow_direction: 'vertical stacking with lateral flow',
      architecture_style: 'wall-integrated',
      hierarchy_method: 'color zones and control clustering'
    },
    interaction_metaphor: 'analog',
    narrative_archetype: {
      setting: 'fictional laboratory ecosystem',
      synthesis: 'analog computing + sound synthesis + alchemical instrumentation',
      tone: ['whimsical', 'exploratory', 'humanistic']
    }
  }
};
```

**Styled Components**:
```typescript
// @analog-whimsy/ui/src/components/AWSKnob.tsx

import React from 'react';
import { BaseKnob, BaseKnobProps } from '@design-system/core';
import './AWSKnob.css';  // Analog Whimsy specific styles

export interface AWSKnobProps extends Omit<BaseKnobProps, 'className'> {
  trim?: 'brass' | 'chrome' | 'none';
}

export const AWSKnob: React.FC<AWSKnobProps> = ({
  trim = 'brass',
  ...baseProps
}) => {
  return (
    <BaseKnob
      {...baseProps}
      className={`aws-knob aws-knob--trim-${trim}`}
    />
  );
};
```

**CSS Overrides**:
```css
/* @analog-whimsy/ui/src/styles/analog-whimsy.css */

.analog-whimsy-knob {
  /* Enamel gloss effect from materials.enamel-gloss */
  background: var(--knob-color);
  border-radius: 50%;
  box-shadow:
    inset 0 1px 3px rgba(255,255,255,0.7),  /* Gloss highlight */
    0 2px 8px rgba(0,0,0,0.15),             /* Depth shadow */
    0 4px 16px rgba(0,0,0,0.1);             /* Ambient occlusion */

  /* Tactile skeuomorphism */
  cursor: grab;
  transition: transform 220ms cubic-bezier(0.68,-0.55,0.27,1.55);
}

.analog-whimsy-knob:active {
  cursor: grabbing;
  transform: scale(0.98);  /* Physical press feedback */
}

/* Brass trim variant */
.aws-knob--trim-brass {
  border: 2px solid var(--color-brass);
  box-shadow:
    inset 0 1px 3px rgba(255,255,255,0.7),
    0 0 0 1px rgba(176,140,76,0.3),  /* Brass glow */
    0 2px 8px rgba(0,0,0,0.15);
}

/* Analog Whimsy buttons - pill-shaped with enamel finish */
.analog-whimsy-button {
  border-radius: var(--radius-lg);  /* Pill shape */
  background: var(--button-color);
  box-shadow:
    inset 0 1px 2px rgba(255,255,255,0.5),  /* Top highlight */
    inset 0 -1px 2px rgba(0,0,0,0.1),      /* Bottom shadow */
    0 2px 6px rgba(0,0,0,0.12);            /* Drop shadow */

  /* Typography */
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;

  transition: all 220ms cubic-bezier(0.68,-0.55,0.27,1.55);
}

.analog-whimsy-button:hover {
  transform: translateY(-1px);
  box-shadow:
    inset 0 1px 2px rgba(255,255,255,0.6),
    0 4px 12px rgba(0,0,0,0.16);
}

.analog-whimsy-button:active {
  transform: translateY(0);
  box-shadow:
    inset 0 2px 4px rgba(0,0,0,0.2),
    0 1px 3px rgba(0,0,0,0.12);
}
```

---

### Child Style 2: `@brutalist-console/ui`

**Different Visual Treatment, Same Base**:

```typescript
// @brutalist-console/ui/src/theme/tokens.ts

export const brutalistTokens: BaseDesignTokens = {
  colors: {
    concrete: '#3A3A3A',
    steel: '#808080',
    rust: '#C84C09',
    warning: '#FFD700'
  },
  spacing: {
    xs: 2,   // Tighter spacing
    sm: 4,
    md: 8,
    lg: 16
  },
  typography: {
    families: {
      base: 'IBM Plex Mono, monospace',  // Monospace only
      mono: 'IBM Plex Mono, monospace'
    },
    sizes: {
      sm: 11,
      base: 13,
      lg: 16
    },
    weights: {
      normal: 400,
      medium: 600,
      bold: 700
    }
  },
  radius: {
    sm: 0,    // Sharp corners (brutalism)
    md: 0,
    lg: 0,
    full: 0
  },
  shadows: {
    sm: 'none',  // Brutalism: no soft shadows
    md: '4px 4px 0 rgba(0,0,0,0.8)',  // Hard drop shadows
    lg: '8px 8px 0 rgba(0,0,0,0.9)'
  },
  materials: {
    'raw-concrete': {
      material_class: 'concrete',
      variant: 'unfinished',
      optical: {
        gloss: 0.1,  // Matte
        reflectivity: 0.0,
        transmission: 0.0
      },
      tactile: {
        friction: 0.9,  // Rough
        warmth: 0.3,    // Cold
        grain: 0.8      // Coarse texture
      },
      finish: 'matte'
    }
  },
  ontology: {
    name: 'Brutalist Data Console',
    definition: 'Raw, uncompromising interface celebrating structural honesty and information density',
    stylistic_lineage: [
      'Brutalist architecture (Le Corbusier)',
      'Terminal UIs (Unix, DOS)',
      'Industrial control panels'
    ],
    design_principles: [
      {
        name: 'Structural Honesty',
        rule: 'Expose the underlying system',
        rationale: 'Transparency builds trust',
        visual_manifestation: 'Raw grids, visible borders, monospace typography'
      }
    ],
    composition: {
      layout_paradigm: 'grid-based',
      flow_direction: 'left-right data flow',
      architecture_style: 'layered',
      hierarchy_method: 'size-based + monochrome contrast'
    },
    interaction_metaphor: 'digital',
    narrative_archetype: {
      setting: 'industrial control room',
      synthesis: 'data visualization + command-line interface',
      tone: ['serious', 'utilitarian', 'uncompromising']
    }
  }
};
```

**CSS**:
```css
/* @brutalist-console/ui/src/styles/brutalist.css */

.brutalist-button {
  border-radius: 0;  /* Sharp corners */
  background: var(--button-color);
  border: 2px solid currentColor;
  box-shadow: 4px 4px 0 rgba(0,0,0,0.8);  /* Hard drop shadow */

  font-family: var(--font-mono);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;

  transition: none;  /* No smooth transitions */
}

.brutalist-button:hover {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0 rgba(0,0,0,0.8);
}

.brutalist-button:active {
  transform: translate(4px, 4px);
  box-shadow: none;
}

.brutalist-knob {
  /* Knobs in brutalist style become sliders (no skeuomorphism) */
  width: 100%;
  height: 4px;
  background: var(--color-concrete);
  border: 1px solid var(--color-steel);
  box-shadow: none;
}
```

---

### Child Style 3: `@minimal-glass/ui`

**Glassmorphic Minimal Style**:

```typescript
// @minimal-glass/ui/src/theme/tokens.ts

export const minimalGlassTokens: BaseDesignTokens = {
  colors: {
    glass: 'rgba(255,255,255,0.1)',
    frost: 'rgba(255,255,255,0.05)',
    accent: '#007AFF',
    text: '#FFFFFF'
  },
  spacing: {
    xs: 8,   // Generous spacing
    sm: 16,
    md: 24,
    lg: 32,
    xl: 48
  },
  radius: {
    sm: 12,
    md: 16,
    lg: 20,
    full: 9999
  },
  shadows: {
    sm: '0 4px 16px rgba(0,0,0,0.1)',
    md: '0 8px 32px rgba(0,0,0,0.12)',
    lg: '0 16px 64px rgba(0,0,0,0.16)'
  },
  materials: {
    'frosted-glass': {
      material_class: 'glass',
      variant: 'frosted',
      optical: {
        gloss: 0.3,
        reflectivity: 0.1,
        transmission: 0.9  // High transmission (translucent)
      },
      tactile: {
        friction: 0.2,
        warmth: 0.5,
        grain: 0.05
      },
      finish: 'satin'
    }
  },
  ontology: {
    name: 'Minimal Glass Interface',
    definition: 'Ethereal, depth-aware interface leveraging transparency and blur for spatial hierarchy',
    stylistic_lineage: [
      'Glassmorphism (iOS 7+)',
      'Swiss Minimalism',
      'Japanese Ma (negative space)'
    ],
    design_principles: [
      {
        name: 'Depth through Transparency',
        rule: 'Use blur and transparency to encode hierarchy',
        rationale: 'Layers reveal context without cluttering',
        visual_manifestation: 'Backdrop blur, translucent surfaces, soft shadows'
      }
    ],
    composition: {
      layout_paradigm: 'grid-based',
      flow_direction: 'center-out',
      architecture_style: 'floating',
      hierarchy_method: 'depth-based (blur + opacity)'
    },
    interaction_metaphor: 'gestural',
    narrative_archetype: {
      setting: 'ethereal space',
      synthesis: 'minimalism + depth + light',
      tone: ['serene', 'elegant', 'refined']
    }
  }
};
```

**CSS**:
```css
/* @minimal-glass/ui/src/styles/minimal-glass.css */

.minimal-glass-button {
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: var(--radius-md);
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);

  font-weight: 500;
  color: white;

  transition: all 300ms ease;
}

.minimal-glass-button:hover {
  background: rgba(255,255,255,0.15);
  border-color: rgba(255,255,255,0.3);
  box-shadow: 0 12px 48px rgba(0,0,0,0.15);
}

.minimal-glass-knob {
  background: rgba(255,255,255,0.08);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.15);
  box-shadow:
    inset 0 1px 2px rgba(255,255,255,0.1),
    0 8px 32px rgba(0,0,0,0.08);
}
```

---

## Token Storage & Database

### Storage Architecture

```
Token Storage System
├── File System (Development)
│   └── tokens/{style-name}/
│       ├── tokens.json
│       ├── ontology.json
│       └── metadata.json
├── Database (Production)
│   ├── PostgreSQL
│   │   ├── tokens table
│   │   ├── ontologies table
│   │   └── style_libraries table
│   └── Redis (Cache)
│       └── Token lookup cache
└── Cloud Storage (Assets)
    └── S3/GCS
        ├── Source images
        └── Generated previews
```

---

### Database Schema

```sql
-- Style Libraries Registry
CREATE TABLE style_libraries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) UNIQUE NOT NULL,                -- "analog-whimsy"
  display_name VARCHAR(255) NOT NULL,               -- "Analog Whimsy Systems"
  package_name VARCHAR(255) NOT NULL,               -- "@analog-whimsy/ui"
  version VARCHAR(50) NOT NULL,                     -- "1.0.0"
  parent_package VARCHAR(255) DEFAULT '@design-system/core',

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  created_by VARCHAR(255),

  -- Ontology
  ontology JSONB,                                   -- Design language ontology

  -- Status
  status VARCHAR(50) DEFAULT 'draft',               -- draft, published, archived

  -- Statistics
  download_count INTEGER DEFAULT 0,
  star_count INTEGER DEFAULT 0
);

-- Design Tokens Storage
CREATE TABLE design_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  style_library_id UUID REFERENCES style_libraries(id) ON DELETE CASCADE,

  -- Token data
  tokens JSONB NOT NULL,                            -- Complete token set

  -- Extraction metadata
  source_images TEXT[],                             -- Array of image URLs
  extractors_used TEXT[],                           -- Array of extractor names
  extraction_date TIMESTAMP DEFAULT NOW(),
  extraction_duration_ms INTEGER,

  -- Validation
  schema_version VARCHAR(50) NOT NULL,              -- "3.1"
  validation_status VARCHAR(50) DEFAULT 'valid',    -- valid, invalid, pending
  validation_errors JSONB,

  -- Version control
  version INTEGER NOT NULL,
  is_latest BOOLEAN DEFAULT TRUE,

  -- Indexes
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_style_libraries_name ON style_libraries(name);
CREATE INDEX idx_design_tokens_style ON design_tokens(style_library_id);
CREATE INDEX idx_design_tokens_latest ON design_tokens(style_library_id, is_latest) WHERE is_latest = TRUE;
```

---

### Token Storage Service

```typescript
// backend/services/TokenStorage.ts

import { Pool } from 'pg';
import { BaseDesignTokens, DesignLanguageOntology } from '@design-system/core';

export interface StyleLibrary {
  id: string;
  name: string;
  display_name: string;
  package_name: string;
  version: string;
  parent_package: string;
  ontology: DesignLanguageOntology;
  status: 'draft' | 'published' | 'archived';
  created_at: Date;
}

export class TokenStorageService {
  private pool: Pool;

  constructor(databaseUrl: string) {
    this.pool = new Pool({ connectionString: databaseUrl });
  }

  /**
   * Save extracted tokens as a new style library
   */
  async createStyleLibrary(
    name: string,
    displayName: string,
    tokens: BaseDesignTokens,
    sourceImages: string[],
    extractorsUsed: string[]
  ): Promise<StyleLibrary> {
    const client = await this.pool.connect();

    try {
      await client.query('BEGIN');

      // 1. Create style library entry
      const libraryResult = await client.query(`
        INSERT INTO style_libraries (name, display_name, package_name, ontology, status)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
      `, [
        name,
        displayName,
        `@${name}/ui`,
        JSON.stringify(tokens.ontology || {}),
        'draft'
      ]);

      const library = libraryResult.rows[0];

      // 2. Save tokens
      await client.query(`
        INSERT INTO design_tokens (
          style_library_id, tokens, source_images, extractors_used,
          schema_version, version, is_latest
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
      `, [
        library.id,
        JSON.stringify(tokens),
        sourceImages,
        extractorsUsed,
        '3.1',
        1,
        true
      ]);

      await client.query('COMMIT');
      return library;

    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  /**
   * Load tokens for a style library
   */
  async loadTokens(libraryName: string): Promise<BaseDesignTokens | null> {
    const result = await this.pool.query(`
      SELECT t.tokens
      FROM design_tokens t
      JOIN style_libraries l ON t.style_library_id = l.id
      WHERE l.name = $1 AND t.is_latest = TRUE
    `, [libraryName]);

    if (result.rows.length === 0) return null;
    return result.rows[0].tokens;
  }

  /**
   * List all available style libraries
   */
  async listLibraries(): Promise<StyleLibrary[]> {
    const result = await this.pool.query(`
      SELECT * FROM style_libraries
      WHERE status = 'published'
      ORDER BY created_at DESC
    `);

    return result.rows;
  }

  /**
   * Update tokens (creates new version)
   */
  async updateTokens(
    libraryName: string,
    newTokens: BaseDesignTokens
  ): Promise<void> {
    const client = await this.pool.connect();

    try {
      await client.query('BEGIN');

      // 1. Get library ID
      const libraryResult = await client.query(`
        SELECT id FROM style_libraries WHERE name = $1
      `, [libraryName]);

      if (libraryResult.rows.length === 0) {
        throw new Error(`Library ${libraryName} not found`);
      }

      const libraryId = libraryResult.rows[0].id;

      // 2. Mark current version as not latest
      await client.query(`
        UPDATE design_tokens
        SET is_latest = FALSE
        WHERE style_library_id = $1 AND is_latest = TRUE
      `, [libraryId]);

      // 3. Get next version number
      const versionResult = await client.query(`
        SELECT MAX(version) as max_version
        FROM design_tokens
        WHERE style_library_id = $1
      `, [libraryId]);

      const nextVersion = (versionResult.rows[0].max_version || 0) + 1;

      // 4. Insert new version
      await client.query(`
        INSERT INTO design_tokens (
          style_library_id, tokens, schema_version, version, is_latest
        )
        VALUES ($1, $2, $3, $4, $5)
      `, [
        libraryId,
        JSON.stringify(newTokens),
        '3.1',
        nextVersion,
        true
      ]);

      await client.query('COMMIT');
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }
}
```

---

## Schema Mapper Integration

### Validation & Normalization

```typescript
// backend/schema_mapper/validator.ts

import Ajv from 'ajv';
import { BaseDesignTokens } from '@design-system/core';

const tokenSchema = {
  type: 'object',
  required: ['colors', 'spacing', 'typography', 'radius', 'shadows'],
  properties: {
    colors: {
      type: 'object',
      patternProperties: {
        '^[a-z-]+$': { type: 'string', pattern: '^#[0-9A-Fa-f]{6}$' }
      }
    },
    spacing: {
      type: 'object',
      patternProperties: {
        '^[a-z-]+$': { type: 'number', minimum: 0 }
      }
    },
    materials: {
      type: 'object',
      patternProperties: {
        '^[a-z-]+$': {
          type: 'object',
          required: ['material_class', 'optical', 'tactile', 'finish'],
          properties: {
            material_class: {
              type: 'string',
              enum: ['plastic', 'metal', 'glass', 'wood', 'ceramic', 'fabric']
            },
            optical: {
              type: 'object',
              required: ['gloss', 'reflectivity', 'transmission'],
              properties: {
                gloss: { type: 'number', minimum: 0, maximum: 1 },
                reflectivity: { type: 'number', minimum: 0, maximum: 1 },
                transmission: { type: 'number', minimum: 0, maximum: 1 }
              }
            }
          }
        }
      }
    }
  }
};

export class TokenValidator {
  private ajv: Ajv;

  constructor() {
    this.ajv = new Ajv();
  }

  validate(tokens: unknown): { valid: boolean; errors?: string[] } {
    const validate = this.ajv.compile(tokenSchema);
    const valid = validate(tokens);

    if (!valid) {
      return {
        valid: false,
        errors: validate.errors?.map(err => `${err.instancePath}: ${err.message}`) || []
      };
    }

    return { valid: true };
  }

  /**
   * Normalize tokens to conform to schema
   */
  normalize(tokens: Partial<BaseDesignTokens>): BaseDesignTokens {
    return {
      colors: tokens.colors || {},
      spacing: tokens.spacing || { xs: 4, sm: 8, md: 16, lg: 24 },
      typography: tokens.typography || {
        families: { base: 'sans-serif' },
        sizes: { base: 16 },
        weights: { normal: 400 }
      },
      radius: tokens.radius || { sm: 4, md: 8, lg: 12, full: 9999 },
      shadows: tokens.shadows || { sm: 'none', md: 'none', lg: 'none' },
      materials: tokens.materials,
      lighting: tokens.lighting,
      environment: tokens.environment,
      artistic: tokens.artistic,
      ontology: tokens.ontology
    };
  }
}
```

---

## Library Loading & Discovery

### Dynamic Style Switching

```typescript
// Example: Application with runtime style switching

import React, { useState } from 'react';
import { BaseThemeProvider } from '@design-system/core';
import { analogWhimsyTokens } from '@analog-whimsy/ui';
import { brutalistTokens } from '@brutalist-console/ui';
import { minimalGlassTokens } from '@minimal-glass/ui';

const AVAILABLE_STYLES = {
  'analog-whimsy': analogWhimsyTokens,
  'brutalist-console': brutalistTokens,
  'minimal-glass': minimalGlassTokens
};

export function App() {
  const [currentStyle, setCurrentStyle] = useState('analog-whimsy');
  const tokens = AVAILABLE_STYLES[currentStyle];

  return (
    <BaseThemeProvider tokens={tokens} styleName={currentStyle}>
      <header>
        <h1>Multi-Style Application</h1>
        <select
          value={currentStyle}
          onChange={(e) => setCurrentStyle(e.target.value)}
        >
          <option value="analog-whimsy">Analog Whimsy</option>
          <option value="brutalist-console">Brutalist Console</option>
          <option value="minimal-glass">Minimal Glass</option>
        </select>
      </header>

      <main>
        <BaseButton variant="primary">Click Me</BaseButton>
        <BaseKnob value={0.5} onChange={(v) => console.log(v)} label="Volume" />
      </main>
    </BaseThemeProvider>
  );
}
```

---

## Multi-Style Application

### Use Case: Micro-Frontends with Different Styles

```typescript
// Application shell using different styles for different sections

import { BaseThemeProvider } from '@design-system/core';
import { analogWhimsyTokens } from '@analog-whimsy/ui';
import { brutalistTokens } from '@brutalist-console/ui';

export function Dashboard() {
  return (
    <div className="dashboard">
      {/* Creative section: Analog Whimsy */}
      <BaseThemeProvider tokens={analogWhimsyTokens} styleName="analog-whimsy">
        <section className="creative-tools">
          <h2>Creative Tools</h2>
          {/* Playful, exploratory UI */}
        </section>
      </BaseThemeProvider>

      {/* Data section: Brutalist Console */}
      <BaseThemeProvider tokens={brutalistTokens} styleName="brutalist-console">
        <section className="analytics">
          <h2>Analytics</h2>
          {/* Dense, information-focused UI */}
        </section>
      </BaseThemeProvider>
    </div>
  );
}
```

---

## Related Documentation

- [Generator Export Guide](GENERATOR_EXPORT_GUIDE.md) - How to transform tokens into component libraries
- [Token Ontology Reference](TOKEN_ONTOLOGY_REFERENCE.md) - Design language taxonomy framework
- [Complete Token-Extractor Mapping](COMPLETE_TOKEN_EXTRACTOR_MAPPING.md) - Technical extraction details
- [Token Schema Guide](TOKEN_SCHEMA_GUIDE.md) - Token schemas and examples

---

**Last Updated**: 2025-11-11
**Version**: 3.1
**Status**: Multi-Style Inheritance Architecture

---

## Summary

**Key Insight**: The design system becomes a **meta-framework** where each extracted design can become its own complete component library, but all libraries share a common base for API consistency and interoperability.

**Benefits**:
- **Consistency**: Same base components, APIs, and hooks
- **Flexibility**: Each style library can override visuals completely
- **Extensibility**: Add new styles without breaking existing ones
- **Interoperability**: Mix styles in micro-frontends
- **Maintainability**: Shared utilities and base logic

**Architecture**: Parent (`@design-system/core`) + infinite children (`@{style-name}/ui`)
