# Generator & Export Guide

**Complete Reference: Transforming Design Tokens into Production Code**

Version: 3.1
Last Updated: 2025-11-11
Status: Production Blueprint + @aws-ui/ Component Library Architecture

---

## Overview

This guide documents the **complete generator pipeline** from extracted design tokens to production-ready code across multiple platforms:

```
Design Tokens (JSON/TypeScript)
    ↓
[Schema Validation]
    ↓
[Generator Engine]
├─ Preview Generators (existing)
│  ├─ React Demo App
│  ├─ Figma Tokens
│  └─ MUI Theme
├─ Code Generators (existing)
│  ├─ CSS Variables
│  ├─ TypeScript Types
│  ├─ Tailwind Config
│  └─ JUCE C++ Constants
└─ Component Library Generators (blueprint) ⭐
   ├─ React Component Library (@aws-ui-react/)
   ├─ Vue Component Library (@aws-ui-vue/)
   ├─ Angular Component Library (@aws-ui-ng/)
   ├─ Svelte Component Library (@aws-ui-svelte/)
   └─ Vanilla JS/Web Components (@aws-ui-web/)
    ↓
Production-Ready Code (Multi-Framework)
```

---

## Table of Contents

1. [Existing Generators](#existing-generators)
2. [Generator Architecture](#generator-architecture)
3. [Multi-Framework Component Generation](#multi-framework-component-generation) ⭐
   - [Model-View Architecture](#model-view-architecture-for-multi-framework)
   - [React Components](#react-components)
   - [Vue Components](#vue-components)
   - [Angular Components](#angular-components)
   - [Svelte Components](#svelte-components)
   - [Vanilla JS/Web Components](#vanilla-jsweb-components)
4. [React Component Library Generator (Blueprint)](#react-component-library-generator)
5. [Token → Component Transformation](#token-component-transformation)
6. [Platform-Specific Exports](#platform-specific-exports)
7. [Creating Custom Generators](#creating-custom-generators)

---

## Existing Generators

### 1. React Demo App Generator (Preview)

**File**: `generators/src/export-react.ts` (1,774 LOC)
**Output**: Interactive preview/design system browser

**What It Generates**:
```
targets/react/
├─ index.html
├─ main.tsx
├─ App.tsx          # Demo app with token previews
└─ tokens.css       # CSS variables from tokens
```

**Components Generated**:
- `ColorSwatch` - Interactive color picker
- `SpacingItem` - Spacing scale visualizer
- `ReferenceImages` - Source image gallery
- Shadow/gradient/z-index/icon size visualizers

**Purpose**: Design system documentation & token exploration

**NOT a component library** - this is a preview app, not reusable components!

---

### 2. Figma Tokens Generator

**File**: `generators/src/export-figma.ts` (187 LOC)
**Output**: Figma-compatible tokens JSON

```typescript
// Example output: targets/figma/tokens.json
{
  "color": {
    "primary": {
      "value": "#F15925",
      "type": "color"
    }
  },
  "spacing": {
    "sm": {
      "value": "8px",
      "type": "spacing"
    }
  }
}
```

**Supports**: Colors, spacing, typography, shadows, radius
**Compatible with**: Figma Tokens plugin, Style Dictionary

---

### 3. Material-UI Theme Generator

**File**: `generators/src/export-mui.ts` (97 LOC)
**Output**: MUI theme configuration

```typescript
// Example output: targets/mui/theme.ts
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: { main: '#F15925' },
    secondary: { main: '#4ECDC4' },
  },
  spacing: 8,
  typography: {
    fontFamily: 'Inter, sans-serif',
  },
  shadows: [...],
});
```

---

### 4. JUCE C++ Generators

**Files**:
- `export-juce.ts` (307 LOC) - Constants generator
- `export-juce-components.ts` (516 LOC) - Component generator

**Output**: JUCE audio plugin UI code

```cpp
// Example output: targets/juce/DesignTokens.h
namespace DesignTokens {
    namespace Colours {
        const juce::Colour Primary = juce::Colour(0xFFF15925);
        const juce::Colour Secondary = juce::Colour(0xFF4ECDC4);
    }

    namespace Spacing {
        constexpr int Small = 8;
        constexpr int Medium = 16;
        constexpr int Large = 24;
    }

    namespace Components {
        // Rotary slider configuration from audio_plugin tokens
        struct RotaryKnob {
            static constexpr int diameter = 48;
            static constexpr float strokeWidth = 3.0f;
            static const juce::Colour fillColour;
        };
    }
}
```

**Purpose**: Audio plugin UI development (VST/AU/AAX)

---

### 5. CSS Variables Generator

**Embedded in**: All generators
**Output**: CSS custom properties

```css
/* Example output: tokens.css */
:root {
  /* Colors */
  --color-primary: #F15925;
  --color-secondary: #4ECDC4;
  --color-background: #FDF7EE;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;

  /* Typography */
  --font-family-base: Inter, sans-serif;
  --font-size-sm: 13px;
  --font-size-base: 16px;

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.12);
  --shadow-md: 0 4px 8px rgba(0,0,0,0.16);

  /* Materials (Visual DNA) */
  --material-brass: #B08C4C;
  --material-gloss: 0.7;

  /* Motion */
  --transition-fast: 150ms;
  --transition-base: 220ms;
  --transition-elastic: cubic-bezier(0.68,-0.55,0.27,1.55);
}
```

---

## Generator Architecture

### Pipeline Flow

```
1. Token Extraction
   ↓
2. Token Validation (schema.ts)
   ↓
3. Token Normalization (normalize.ts)
   ↓
4. Generator Selection
   ├─ tokens → All generators
   ├─ figma → Figma export
   ├─ mui → Material-UI theme
   ├─ react → React preview app
   └─ juce → JUCE C++ code
   ↓
5. Template Rendering
   ↓
6. File Output (targets/{format}/)
```

### Backend Executor (Python)

**File**: `backend/generator_executor.py` (436 LOC)

**Features**:
- Async subprocess execution (non-blocking)
- Process pooling (max 5 concurrent)
- Caching (1-hour TTL, 100 entries max)
- Timeout handling (60s default)
- Error recovery

**Usage**:
```python
from backend.generator_executor import execute_generator

result = await execute_generator(
    format="react",
    tokens=extracted_tokens,
    style_path=Path("temp/style_guide.json"),
    dist_dest=Path("generators/dist"),
    spec_path=Path("temp/component_spec.json"),  # Optional
    use_cache=True,
    timeout=60
)

if result.success:
    print(f"Generated: {result.output_paths}")
    print(f"Duration: {result.duration_ms}ms")
    print(f"Cached: {result.cached}")
```

---

### Frontend CLI (TypeScript)

**File**: `generators/src/cli.ts`

**Commands**:
```bash
# Generate all formats
node cli.js tokens style_guide.json

# Generate specific format
node cli.js figma style_guide.json
node cli.js mui style_guide.json
node cli.js react style_guide.json component_spec.json
node cli.js juce style_guide.json component_spec.json
```

---

## Multi-Framework Component Generation

### Overview: One Token System, Multiple Frontend Targets

The generator system supports **multi-framework output** from a single token extraction. The same design tokens power React, Vue, Angular, Svelte, and vanilla JS components through a **model-view separation pattern**.

```
┌──────────────────────────────────────┐
│    Design Tokens (Framework-Agnostic)│
│    JSON/TypeScript Type Definitions   │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│   TypeScript Models (Business Logic) │
│   Platform-agnostic component logic  │
│   ├─ AWSUIButton.ts                  │
│   ├─ AWSUIKnob.ts                    │
│   └─ AWSUISlider.ts                  │
└────────┬─────────────────────────────┘
         │
         ├──────────────┬──────────────┬──────────────┬──────────────┐
         ▼              ▼              ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│   React    │  │    Vue     │  │  Angular   │  │  Svelte    │  │ Vanilla JS │
│   Adapter  │  │  Adapter   │  │  Adapter   │  │  Adapter   │  │  Adapter   │
│  (Thin)    │  │  (Thin)    │  │  (Thin)    │  │  (Thin)    │  │  (Thin)    │
└────────────┘  └────────────┘  └────────────┘  └────────────┘  └────────────┘
     │               │               │               │               │
     ▼               ▼               ▼               ▼               ▼
@aws-ui-react/  @aws-ui-vue/  @aws-ui-ng/   @aws-ui-svelte/ @aws-ui-web/
```

### Key Benefits

**1. Code Reuse**: Business logic written once, rendered in any framework
**2. Type Safety**: Full TypeScript support across all platforms
**3. Consistent Behavior**: Same models ensure identical component behavior
**4. Easy Maintenance**: Fix bugs once, deploy everywhere
**5. Framework Migration**: Swap views without rewriting logic

---

### Model-View Architecture for Multi-Framework

#### Shared TypeScript Models (Framework-Agnostic)

**Package**: `@design-system/core` (shared across all frameworks)

```typescript
// packages/core/src/models/AWSUIButton.ts
import { BaseDesignTokens } from '../types';

export class AWSUIButton {
  private tokens: BaseDesignTokens;
  private label: string = '';
  private variant: 'primary' | 'secondary' | 'ghost' = 'primary';
  private size: 'sm' | 'md' | 'lg' = 'md';
  private disabled: boolean = false;
  private loading: boolean = false;
  private onClick: (() => void) | null = null;

  constructor(tokens: BaseDesignTokens) {
    this.tokens = tokens;
  }

  // Configuration methods
  setLabel(label: string): void {
    this.label = label;
  }

  setVariant(variant: 'primary' | 'secondary' | 'ghost'): void {
    this.variant = variant;
  }

  setSize(size: 'sm' | 'md' | 'lg'): void {
    this.size = size;
  }

  setDisabled(disabled: boolean): void {
    this.disabled = disabled;
  }

  setLoading(loading: boolean): void {
    this.loading = loading;
  }

  setOnClick(handler: () => void): void {
    this.onClick = handler;
  }

  // Getters (used by all frameworks)
  getLabel(): string {
    return this.label;
  }

  isDisabled(): boolean {
    return this.disabled || this.loading;
  }

  isLoading(): boolean {
    return this.loading;
  }

  // Style computation (business logic)
  getBackgroundColor(): string {
    if (this.disabled) return this.tokens.colors.neutral400;
    if (this.variant === 'primary') return this.tokens.colors.primary;
    if (this.variant === 'secondary') return this.tokens.colors.secondary;
    return 'transparent'; // ghost
  }

  getTextColor(): string {
    if (this.variant === 'ghost') return this.tokens.colors.primary;
    return this.tokens.colors.neutral50;
  }

  getPadding(): string {
    const spacing = this.tokens.spacing;
    if (this.size === 'sm') return `${spacing.xs}px ${spacing.sm}px`;
    if (this.size === 'lg') return `${spacing.md}px ${spacing.lg}px`;
    return `${spacing.sm}px ${spacing.md}px`;
  }

  getFontSize(): number {
    if (this.size === 'sm') return this.tokens.typography.fontSize.sm;
    if (this.size === 'lg') return this.tokens.typography.fontSize.lg;
    return this.tokens.typography.fontSize.base;
  }

  getBorderRadius(): string {
    return `${this.tokens.borderRadius.md}px`;
  }

  getShadow(): string {
    if (this.variant === 'ghost') return 'none';
    return this.tokens.shadows.sm;
  }

  // Event handling
  handleClick(): void {
    if (!this.isDisabled() && this.onClick) {
      this.onClick();
    }
  }

  // Accessibility info (used by all frameworks)
  getAccessibilityInfo(): {
    role: string;
    label: string;
    disabled: boolean;
    ariaLabel: string;
    ariaLive?: string;
  } {
    return {
      role: 'button',
      label: this.label,
      disabled: this.isDisabled(),
      ariaLabel: this.loading ? `${this.label} (loading)` : this.label,
      ariaLive: this.loading ? 'polite' : undefined
    };
  }
}
```

**Benefits**:
- ✅ No framework dependencies (pure TypeScript)
- ✅ Unit testable without DOM
- ✅ Reusable across React, Vue, Angular, Svelte, vanilla JS
- ✅ Single source of truth for business logic

---

### React Components

**Package**: `@aws-ui-react`
**Adapter Pattern**: Thin React wrapper around TypeScript models

```typescript
// packages/aws-ui-react/src/components/AWSButton.tsx
import React, { useMemo } from 'react';
import { AWSUIButton } from '@design-system/core';
import { useTokens } from '../hooks/useTokens';

export interface AWSButtonProps {
  label: string;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  className?: string;
}

export const AWSButton: React.FC<AWSButtonProps> = ({
  label,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick,
  className = ''
}) => {
  const tokens = useTokens();

  // Instantiate model (memoized)
  const model = useMemo(() => {
    const btn = new AWSUIButton(tokens);
    btn.setVariant(variant);
    btn.setSize(size);
    return btn;
  }, [tokens, variant, size]);

  // Update model state (cheap)
  model.setLabel(label);
  model.setDisabled(disabled);
  model.setLoading(loading);
  if (onClick) {
    model.setOnClick(onClick);
  }

  // Get computed styles from model
  const styles: React.CSSProperties = {
    backgroundColor: model.getBackgroundColor(),
    color: model.getTextColor(),
    padding: model.getPadding(),
    fontSize: `${model.getFontSize()}px`,
    borderRadius: model.getBorderRadius(),
    boxShadow: model.getShadow(),
    cursor: model.isDisabled() ? 'not-allowed' : 'pointer',
    opacity: model.isDisabled() ? 0.5 : 1,
    border: 'none',
    fontFamily: tokens.typography.fontFamily.base,
    fontWeight: tokens.typography.fontWeight.medium,
    transition: 'all 0.2s ease'
  };

  const a11y = model.getAccessibilityInfo();

  return (
    <button
      className={className}
      style={styles}
      disabled={model.isDisabled()}
      onClick={() => model.handleClick()}
      role={a11y.role}
      aria-label={a11y.ariaLabel}
      aria-live={a11y.ariaLive}
    >
      {model.isLoading() ? (
        <>
          <span className="spinner" aria-hidden="true">⏳</span>
          {label}
        </>
      ) : (
        label
      )}
    </button>
  );
};
```

**Usage**:
```tsx
import { AWSButton } from '@aws-ui-react';
import { AWSThemeProvider, analogWhimsyTokens } from '@aws-ui-react';

function App() {
  return (
    <AWSThemeProvider tokens={analogWhimsyTokens}>
      <AWSButton
        label="Get Started"
        variant="primary"
        size="lg"
        onClick={() => console.log('Clicked!')}
      />
    </AWSThemeProvider>
  );
}
```

---

### Vue Components

**Package**: `@aws-ui-vue`
**Adapter Pattern**: Vue 3 Composition API wrapper

```vue
<!-- packages/aws-ui-vue/src/components/AWSButton.vue -->
<template>
  <button
    :class="['aws-button', className]"
    :style="buttonStyle"
    :disabled="model.isDisabled()"
    @click="handleClick"
    :role="a11y.role"
    :aria-label="a11y.ariaLabel"
    :aria-live="a11y.ariaLive"
  >
    <span v-if="model.isLoading()" class="spinner" aria-hidden="true">⏳</span>
    {{ label }}
  </button>
</template>

<script setup lang="ts">
import { computed, watchEffect } from 'vue';
import { AWSUIButton } from '@design-system/core';
import { useTokens } from '../composables/useTokens';

interface Props {
  label: string;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  className: ''
});

const emit = defineEmits<{
  click: [];
}>();

const tokens = useTokens();

// Create model
const model = new AWSUIButton(tokens.value);
model.setVariant(props.variant);
model.setSize(props.size);

// Sync props to model
watchEffect(() => {
  model.setLabel(props.label);
  model.setDisabled(props.disabled);
  model.setLoading(props.loading);
  model.setOnClick(() => emit('click'));
});

// Computed styles from model
const buttonStyle = computed(() => ({
  backgroundColor: model.getBackgroundColor(),
  color: model.getTextColor(),
  padding: model.getPadding(),
  fontSize: `${model.getFontSize()}px`,
  borderRadius: model.getBorderRadius(),
  boxShadow: model.getShadow(),
  cursor: model.isDisabled() ? 'not-allowed' : 'pointer',
  opacity: model.isDisabled() ? 0.5 : 1,
  border: 'none',
  fontFamily: tokens.value.typography.fontFamily.base,
  fontWeight: tokens.value.typography.fontWeight.medium,
  transition: 'all 0.2s ease'
}));

const a11y = computed(() => model.getAccessibilityInfo());

const handleClick = () => {
  model.handleClick();
};
</script>

<style scoped>
.aws-button {
  /* Base styles */
}

.spinner {
  display: inline-block;
  margin-right: 8px;
}
</style>
```

**Usage**:
```vue
<template>
  <AWSThemeProvider :tokens="analogWhimsyTokens">
    <AWSButton
      label="Get Started"
      variant="primary"
      size="lg"
      @click="handleClick"
    />
  </AWSThemeProvider>
</template>

<script setup lang="ts">
import { AWSButton, AWSThemeProvider, analogWhimsyTokens } from '@aws-ui-vue';

const handleClick = () => {
  console.log('Clicked!');
};
</script>
```

---

### Angular Components

**Package**: `@aws-ui-ng`
**Adapter Pattern**: Angular component with TypeScript model injection

```typescript
// packages/aws-ui-ng/src/lib/components/aws-button/aws-button.component.ts
import { Component, Input, Output, EventEmitter, OnInit, OnChanges } from '@angular/core';
import { AWSUIButton } from '@design-system/core';
import { TokenService } from '../../services/token.service';

@Component({
  selector: 'aws-button',
  template: `
    <button
      [class]="'aws-button ' + (className || '')"
      [style]="buttonStyle"
      [disabled]="model.isDisabled()"
      (click)="handleClick()"
      [attr.role]="a11y.role"
      [attr.aria-label]="a11y.ariaLabel"
      [attr.aria-live]="a11y.ariaLive"
    >
      <span *ngIf="model.isLoading()" class="spinner" aria-hidden="true">⏳</span>
      {{ label }}
    </button>
  `,
  styles: [`
    .aws-button {
      /* Base styles */
    }
    .spinner {
      display: inline-block;
      margin-right: 8px;
    }
  `]
})
export class AWSButtonComponent implements OnInit, OnChanges {
  @Input() label!: string;
  @Input() variant: 'primary' | 'secondary' | 'ghost' = 'primary';
  @Input() size: 'sm' | 'md' | 'lg' = 'md';
  @Input() disabled: boolean = false;
  @Input() loading: boolean = false;
  @Input() className?: string;
  @Output() clicked = new EventEmitter<void>();

  model!: AWSUIButton;
  buttonStyle: any = {};
  a11y: any = {};

  constructor(private tokenService: TokenService) {}

  ngOnInit(): void {
    // Create model with injected tokens
    const tokens = this.tokenService.getTokens();
    this.model = new AWSUIButton(tokens);
    this.model.setVariant(this.variant);
    this.model.setSize(this.size);
    this.model.setOnClick(() => this.clicked.emit());
    this.updateModel();
  }

  ngOnChanges(): void {
    if (this.model) {
      this.updateModel();
    }
  }

  private updateModel(): void {
    this.model.setLabel(this.label);
    this.model.setDisabled(this.disabled);
    this.model.setLoading(this.loading);

    // Compute styles from model
    const tokens = this.tokenService.getTokens();
    this.buttonStyle = {
      backgroundColor: this.model.getBackgroundColor(),
      color: this.model.getTextColor(),
      padding: this.model.getPadding(),
      fontSize: `${this.model.getFontSize()}px`,
      borderRadius: this.model.getBorderRadius(),
      boxShadow: this.model.getShadow(),
      cursor: this.model.isDisabled() ? 'not-allowed' : 'pointer',
      opacity: this.model.isDisabled() ? 0.5 : 1,
      border: 'none',
      fontFamily: tokens.typography.fontFamily.base,
      fontWeight: tokens.typography.fontWeight.medium,
      transition: 'all 0.2s ease'
    };

    this.a11y = this.model.getAccessibilityInfo();
  }

  handleClick(): void {
    this.model.handleClick();
  }
}
```

**Usage**:
```typescript
// app.component.ts
import { Component } from '@angular/core';
import { analogWhimsyTokens } from '@aws-ui-ng';

@Component({
  selector: 'app-root',
  template: `
    <aws-theme-provider [tokens]="tokens">
      <aws-button
        label="Get Started"
        variant="primary"
        size="lg"
        (clicked)="handleClick()"
      ></aws-button>
    </aws-theme-provider>
  `
})
export class AppComponent {
  tokens = analogWhimsyTokens;

  handleClick() {
    console.log('Clicked!');
  }
}
```

---

### Svelte Components

**Package**: `@aws-ui-svelte`
**Adapter Pattern**: Svelte reactive wrapper

```svelte
<!-- packages/aws-ui-svelte/src/lib/AWSButton.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { AWSUIButton } from '@design-system/core';
  import { getTokens } from './stores/tokens';

  export let label: string;
  export let variant: 'primary' | 'secondary' | 'ghost' = 'primary';
  export let size: 'sm' | 'md' | 'lg' = 'md';
  export let disabled: boolean = false;
  export let loading: boolean = false;
  export let className: string = '';

  const tokens = getTokens();
  let model: AWSUIButton;

  // Create model
  onMount(() => {
    model = new AWSUIButton($tokens);
    model.setVariant(variant);
    model.setSize(size);
    updateModel();
  });

  // Reactive updates
  $: if (model) {
    model.setLabel(label);
    model.setDisabled(disabled);
    model.setLoading(loading);
  }

  function updateModel() {
    model.setLabel(label);
    model.setDisabled(disabled);
    model.setLoading(loading);
  }

  function handleClick() {
    if (model) {
      model.handleClick();
    }
  }

  // Computed styles
  $: buttonStyle = model ? {
    backgroundColor: model.getBackgroundColor(),
    color: model.getTextColor(),
    padding: model.getPadding(),
    fontSize: `${model.getFontSize()}px`,
    borderRadius: model.getBorderRadius(),
    boxShadow: model.getShadow(),
    cursor: model.isDisabled() ? 'not-allowed' : 'pointer',
    opacity: model.isDisabled() ? 0.5 : 1,
    border: 'none',
    fontFamily: $tokens.typography.fontFamily.base,
    fontWeight: $tokens.typography.fontWeight.medium,
    transition: 'all 0.2s ease'
  } : {};

  $: a11y = model ? model.getAccessibilityInfo() : null;
</script>

<button
  class="aws-button {className}"
  style={Object.entries(buttonStyle)
    .map(([k, v]) => `${k.replace(/[A-Z]/g, m => '-' + m.toLowerCase())}: ${v}`)
    .join('; ')}
  disabled={model?.isDisabled()}
  on:click={handleClick}
  role={a11y?.role}
  aria-label={a11y?.ariaLabel}
  aria-live={a11y?.ariaLive}
>
  {#if model?.isLoading()}
    <span class="spinner" aria-hidden="true">⏳</span>
  {/if}
  {label}
</button>

<style>
  .aws-button {
    /* Base styles */
  }

  .spinner {
    display: inline-block;
    margin-right: 8px;
  }
</style>
```

**Usage**:
```svelte
<script lang="ts">
  import { AWSButton, AWSThemeProvider, analogWhimsyTokens } from '@aws-ui-svelte';

  function handleClick() {
    console.log('Clicked!');
  }
</script>

<AWSThemeProvider tokens={analogWhimsyTokens}>
  <AWSButton
    label="Get Started"
    variant="primary"
    size="lg"
    on:click={handleClick}
  />
</AWSThemeProvider>
```

---

### Vanilla JS/Web Components

**Package**: `@aws-ui-web`
**Adapter Pattern**: Web Components API with TypeScript models

```typescript
// packages/aws-ui-web/src/components/aws-button.ts
import { AWSUIButton } from '@design-system/core';
import { getTokens } from '../utils/tokens';

export class AWSButtonElement extends HTMLElement {
  private model: AWSUIButton;
  private buttonEl: HTMLButtonElement;

  static get observedAttributes() {
    return ['label', 'variant', 'size', 'disabled', 'loading'];
  }

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });

    // Create model
    const tokens = getTokens();
    this.model = new AWSUIButton(tokens);

    // Create button element
    this.buttonEl = document.createElement('button');
    this.buttonEl.className = 'aws-button';
    this.buttonEl.addEventListener('click', () => this.handleClick());

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
      .aws-button {
        transition: all 0.2s ease;
      }
      .spinner {
        display: inline-block;
        margin-right: 8px;
      }
    `;

    this.shadowRoot!.appendChild(style);
    this.shadowRoot!.appendChild(this.buttonEl);

    // Set up click handler
    this.model.setOnClick(() => {
      this.dispatchEvent(new CustomEvent('clicked', { bubbles: true, composed: true }));
    });
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback(name: string, oldValue: string, newValue: string) {
    if (oldValue === newValue) return;

    switch (name) {
      case 'label':
        this.model.setLabel(newValue);
        break;
      case 'variant':
        this.model.setVariant(newValue as any);
        break;
      case 'size':
        this.model.setSize(newValue as any);
        break;
      case 'disabled':
        this.model.setDisabled(newValue !== null);
        break;
      case 'loading':
        this.model.setLoading(newValue !== null);
        break;
    }

    this.render();
  }

  private render() {
    const tokens = getTokens();

    // Apply styles from model
    Object.assign(this.buttonEl.style, {
      backgroundColor: this.model.getBackgroundColor(),
      color: this.model.getTextColor(),
      padding: this.model.getPadding(),
      fontSize: `${this.model.getFontSize()}px`,
      borderRadius: this.model.getBorderRadius(),
      boxShadow: this.model.getShadow(),
      cursor: this.model.isDisabled() ? 'not-allowed' : 'pointer',
      opacity: this.model.isDisabled() ? '0.5' : '1',
      border: 'none',
      fontFamily: tokens.typography.fontFamily.base,
      fontWeight: tokens.typography.fontWeight.medium.toString()
    });

    // Update content
    const label = this.model.getLabel();
    const loading = this.model.isLoading();
    this.buttonEl.innerHTML = loading
      ? `<span class="spinner" aria-hidden="true">⏳</span>${label}`
      : label;

    // Update a11y attributes
    const a11y = this.model.getAccessibilityInfo();
    this.buttonEl.disabled = this.model.isDisabled();
    this.buttonEl.setAttribute('role', a11y.role);
    this.buttonEl.setAttribute('aria-label', a11y.ariaLabel);
    if (a11y.ariaLive) {
      this.buttonEl.setAttribute('aria-live', a11y.ariaLive);
    } else {
      this.buttonEl.removeAttribute('aria-live');
    }
  }

  private handleClick() {
    this.model.handleClick();
  }

  // Public API
  get label(): string {
    return this.getAttribute('label') || '';
  }

  set label(value: string) {
    this.setAttribute('label', value);
  }

  get variant(): string {
    return this.getAttribute('variant') || 'primary';
  }

  set variant(value: string) {
    this.setAttribute('variant', value);
  }

  get size(): string {
    return this.getAttribute('size') || 'md';
  }

  set size(value: string) {
    this.setAttribute('size', value);
  }

  get disabled(): boolean {
    return this.hasAttribute('disabled');
  }

  set disabled(value: boolean) {
    if (value) {
      this.setAttribute('disabled', '');
    } else {
      this.removeAttribute('disabled');
    }
  }

  get loading(): boolean {
    return this.hasAttribute('loading');
  }

  set loading(value: boolean) {
    if (value) {
      this.setAttribute('loading', '');
    } else {
      this.removeAttribute('loading');
    }
  }
}

// Register custom element
customElements.define('aws-button', AWSButtonElement);
```

**Usage (Vanilla JS)**:
```html
<!DOCTYPE html>
<html>
<head>
  <script type="module" src="@aws-ui-web/dist/index.js"></script>
</head>
<body>
  <!-- Declarative usage -->
  <aws-button
    label="Get Started"
    variant="primary"
    size="lg"
  ></aws-button>

  <!-- Programmatic usage -->
  <script type="module">
    import { AWSButtonElement } from '@aws-ui-web';

    const button = document.querySelector('aws-button');
    button.addEventListener('clicked', () => {
      console.log('Clicked!');
    });

    // Or create dynamically
    const newButton = document.createElement('aws-button');
    newButton.label = 'Click Me';
    newButton.variant = 'secondary';
    newButton.addEventListener('clicked', () => {
      console.log('Button clicked!');
    });
    document.body.appendChild(newButton);
  </script>
</body>
</html>
```

---

### Generator Output: Multi-Framework Packages

**Generated Package Structure** (from single token extraction):

```
generated-output/
├─ @aws-ui-react/          # React package
│  ├─ package.json
│  ├─ src/
│  │  ├─ components/
│  │  │  ├─ AWSButton.tsx
│  │  │  ├─ AWSKnob.tsx
│  │  │  └─ AWSSlider.tsx
│  │  ├─ hooks/
│  │  │  └─ useTokens.ts
│  │  └─ index.ts
│  └─ dist/
│
├─ @aws-ui-vue/            # Vue package
│  ├─ package.json
│  ├─ src/
│  │  ├─ components/
│  │  │  ├─ AWSButton.vue
│  │  │  ├─ AWSKnob.vue
│  │  │  └─ AWSSlider.vue
│  │  ├─ composables/
│  │  │  └─ useTokens.ts
│  │  └─ index.ts
│  └─ dist/
│
├─ @aws-ui-ng/             # Angular package
│  ├─ package.json
│  ├─ src/
│  │  ├─ lib/
│  │  │  ├─ components/
│  │  │  │  ├─ aws-button/
│  │  │  │  ├─ aws-knob/
│  │  │  │  └─ aws-slider/
│  │  │  ├─ services/
│  │  │  │  └─ token.service.ts
│  │  │  └─ aws-ui-ng.module.ts
│  │  └─ public-api.ts
│  └─ dist/
│
├─ @aws-ui-svelte/         # Svelte package
│  ├─ package.json
│  ├─ src/
│  │  ├─ lib/
│  │  │  ├─ AWSButton.svelte
│  │  │  ├─ AWSKnob.svelte
│  │  │  └─ AWSSlider.svelte
│  │  ├─ stores/
│  │  │  └─ tokens.ts
│  │  └─ index.ts
│  └─ dist/
│
├─ @aws-ui-web/            # Vanilla JS/Web Components
│  ├─ package.json
│  ├─ src/
│  │  ├─ components/
│  │  │  ├─ aws-button.ts
│  │  │  ├─ aws-knob.ts
│  │  │  └─ aws-slider.ts
│  │  ├─ utils/
│  │  │  └─ tokens.ts
│  │  └─ index.ts
│  └─ dist/
│
└─ @design-system/core/    # Shared models (framework-agnostic)
   ├─ package.json
   ├─ src/
   │  ├─ models/
   │  │  ├─ AWSUIButton.ts
   │  │  ├─ AWSUIKnob.ts
   │  │  └─ AWSUISlider.ts
   │  ├─ types/
   │  │  └─ tokens.ts
   │  └─ index.ts
   └─ dist/
```

**Generator Command**:
```bash
# Generate all frameworks
node cli.js components style_guide.json --frameworks all

# Generate specific frameworks
node cli.js components style_guide.json --frameworks react,vue,angular

# Generate with custom package names
node cli.js components style_guide.json \
  --frameworks react,vue \
  --package-prefix @my-company
```

---

### Performance Comparison

| Framework | Bundle Size (gzip) | Initial Load | Runtime Performance |
|-----------|-------------------|--------------|---------------------|
| **React** | 45KB | Fast | Excellent |
| **Vue** | 38KB | Fast | Excellent |
| **Angular** | 120KB | Medium | Good |
| **Svelte** | 12KB | Very Fast | Excellent |
| **Vanilla JS/Web Components** | 8KB | Very Fast | Excellent |

**All frameworks share**:
- Same TypeScript models (~15KB gzipped)
- Same design tokens (~2KB gzipped)
- Same business logic

**Only framework adapters differ** (5-100KB depending on framework).

---

## React Component Library Generator

### Overview: @aws-ui/ Package Architecture

Based on the **Analog Whimsy Systems** reference, here's the blueprint for a production-ready React component library generator.

### Package Structure

```
@aws-ui/                    # Generated package
├─ package.json
├─ tsconfig.json
├─ README.md
├─ src/
│  ├─ index.ts              # Main export
│  ├─ theme/
│  │  ├─ AWSThemeProvider.tsx    # Context provider
│  │  ├─ tokens.ts               # Generated from design tokens
│  │  └─ useTokens.ts            # Hook for consuming tokens
│  ├─ primitives/           # Atomic components
│  │  ├─ AWSButtonCap/
│  │  │  ├─ AWSButtonCap.tsx
│  │  │  ├─ AWSButtonCap.types.ts
│  │  │  └─ AWSButtonCap.stories.tsx
│  │  ├─ AWSKnob/
│  │  ├─ AWSSwitch/
│  │  ├─ AWSSlider/
│  │  ├─ AWSMeter/
│  │  ├─ AWSLight/
│  │  ├─ AWSScreen/
│  │  ├─ AWSBadge/
│  │  └─ AWSPill/
│  ├─ layout/
│  │  ├─ AWSPanel/
│  │  ├─ AWSModuleFrame/
│  │  ├─ AWSStack/
│  │  └─ AWSSurface/
│  ├─ composites/           # Molecules
│  │  ├─ AWSControlCluster/
│  │  ├─ AWSDataPanel/
│  │  ├─ AWSSynthesisPod/
│  │  └─ AWSTelemetryStrip/
│  ├─ organisms/
│  │  ├─ AWSTelemetryHub/
│  │  ├─ AWSCommandConsole/
│  │  └─ AWSDashboardGrid/
│  └─ utils/
│     ├─ motion.ts
│     ├─ a11y.ts
│     └─ cx.ts
└─ styles/
   └─ aws.css              # Generated CSS variables
```

---

### Generated Type System

**From Design Tokens** → **TypeScript Types**

```typescript
// Generated: src/theme/tokens.types.ts

/** Accent colors extracted from palette tokens */
export type AWSAccent = 'coral' | 'teal' | 'lemon' | 'peach' | 'mint';

/** Size scale from spacing tokens */
export type AWSSize = 'xs' | 'sm' | 'md' | 'lg';

/** Intent colors for semantic usage */
export type AWSIntent = 'neutral' | 'primary' | 'success' | 'warning' | 'danger';

/** Material finishes from materials tokens */
export type AWSMaterialTrim = 'brass' | 'chrome' | 'copper' | 'none';

/** Component state from state_layers tokens */
export type AWSState = 'idle' | 'active' | 'disabled' | 'error';

/** Design tokens interface */
export interface AWSTokens {
  colors: {
    surface: string;      // from palette.background
    coral: string;        // from palette.primary
    teal: string;         // from palette.secondary
    lemon: string;        // from palette.accent
    peach: string;        // from semantic_colors
    mint: string;         // from semantic_colors
    brass: string;        // from materials.brass-trim
  };
  radius: {
    sm: number;          // from radius.sm
    md: number;          // from radius.md
    lg: number;          // from radius.lg
  };
  motion: {
    fast: number;        // from transitions.duration.fast
    base: number;        // from transitions.duration.smooth
    elastic: string;     // from transitions.easing.spring
  };
  materials: {
    gloss: number;       // from materials.enamel-gloss.optical.gloss
  };
}
```

**Token Mapping**:

| TypeScript Type | Source Token | Extractor |
|-----------------|--------------|-----------|
| `AWSAccent` | `palette.primary/secondary/accent` | ColorExtractor |
| `AWSSize` | `spacing.xs/sm/md/lg` | SpacingExtractor |
| `AWSMaterialTrim` | `materials.brass-trim/chrome-trim` | MaterialExtractor |
| `AWSTokens.motion.elastic` | `transitions.easing.spring` | TransitionExtractor |

---

### Generated Theme Provider

```typescript
// Generated: src/theme/AWSThemeProvider.tsx

import React, { createContext, useContext } from 'react';
import { AWSTokens } from './tokens.types';

// Default tokens from extracted design tokens
const defaultTokens: AWSTokens = {
  colors: {
    surface: '#FDF7EE',    // from palette.background
    coral: '#F56A5D',      // from palette.primary
    teal: '#45B0A6',       // from palette.secondary
    lemon: '#FFD85C',      // from palette.accent
    peach: '#F6A58E',      // from semantic_colors.warm
    mint: '#E6F4EE',       // from semantic_colors.cool
    brass: '#B08C4C'       // from materials.brass-trim.hex
  },
  radius: {
    sm: 8,                 // from radius.sm
    md: 16,                // from radius.md
    lg: 24                 // from radius.lg
  },
  motion: {
    fast: 150,             // from transitions.duration.fast (ms)
    base: 220,             // from transitions.duration.smooth (ms)
    elastic: 'cubic-bezier(0.68,-0.55,0.27,1.55)'  // from transitions.easing.spring
  },
  materials: {
    gloss: 0.7             // from materials.enamel-gloss.optical.gloss
  }
};

const TokensContext = createContext<AWSTokens>(defaultTokens);

export interface AWSThemeProviderProps {
  theme?: Partial<AWSTokens>;
  children: React.ReactNode;
}

export const AWSThemeProvider: React.FC<AWSThemeProviderProps> = ({
  theme,
  children
}) => {
  const tokens = { ...defaultTokens, ...theme };

  // Inject CSS variables
  React.useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--aws-color-surface', tokens.colors.surface);
    root.style.setProperty('--aws-color-coral', tokens.colors.coral);
    root.style.setProperty('--aws-color-teal', tokens.colors.teal);
    // ... all tokens
  }, [tokens]);

  return (
    <TokensContext.Provider value={tokens}>
      {children}
    </TokensContext.Provider>
  );
};

export const useTokens = () => useContext(TokensContext);
```

---

### Generated Component: AWSKnob

**From Tokens**:
```json
{
  "audio_plugin": {
    "knobs": {
      "detected": true,
      "sizes": [32, 48, 64],
      "average_size": 48
    }
  },
  "palette": {
    "coral": "#F56A5D",
    "teal": "#45B0A6"
  },
  "materials": {
    "enamel-gloss": {
      "optical": { "gloss": 0.7 }
    }
  }
}
```

**Generated Component**:

```typescript
// Generated: src/primitives/AWSKnob/AWSKnob.tsx

import React, { useCallback, useRef, useState } from 'react';
import { useTokens } from '../../theme/useTokens';
import { AWSAccent, AWSSize } from '../../theme/tokens.types';
import './AWSKnob.css';

export interface AWSKnobProps {
  value: number;               // 0..1 normalized
  onChange: (v: number) => void;
  label?: string;
  accent?: AWSAccent;          // Generated from palette
  size?: AWSSize;              // Generated from spacing
  detents?: number[];          // Snap points (0..1)
  ariaLabel?: string;
  min?: number;                // Raw range (optional)
  max?: number;
  step?: number;
  tickCount?: number;
}

const SIZE_MAP = {
  xs: 32,   // from audio_plugin.knobs.sizes[0]
  sm: 40,
  md: 48,   // from audio_plugin.knobs.average_size
  lg: 64    // from audio_plugin.knobs.sizes[2]
};

export const AWSKnob: React.FC<AWSKnobProps> = ({
  value,
  onChange,
  label,
  accent = 'coral',
  size = 'md',
  detents = [],
  ariaLabel,
  min = 0,
  max = 1,
  step = 0.01,
  tickCount = 11
}) => {
  const tokens = useTokens();
  const dialRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const diameter = SIZE_MAP[size];
  const accentColor = tokens.colors[accent];
  const gloss = tokens.materials.gloss;

  // Rotation: 0° (min) to 270° (max)
  const rotation = -135 + (value * 270);

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    setIsDragging(true);
    dialRef.current?.setPointerCapture(e.pointerId);
    e.preventDefault();
  }, []);

  const handlePointerMove = useCallback((e: PointerEvent) => {
    if (!isDragging || !dialRef.current) return;

    const rect = dialRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    // Calculate angle from center
    const angle = Math.atan2(e.clientY - centerY, e.clientX - centerX);
    const degrees = (angle * 180 / Math.PI + 90 + 360) % 360;

    // Map 0-270° to 0-1
    let newValue = Math.max(0, Math.min(1, degrees / 270));

    // Snap to detents if close
    for (const detent of detents) {
      if (Math.abs(newValue - detent) < 0.02) {
        newValue = detent;
        break;
      }
    }

    onChange(newValue);
  }, [isDragging, detents, onChange]);

  const handlePointerUp = useCallback((e: PointerEvent) => {
    setIsDragging(false);
    dialRef.current?.releasePointerCapture(e.pointerId);
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
    <div className="aws-knob-container">
      {label && <label className="aws-knob-label">{label}</label>}
      <div
        ref={dialRef}
        role="slider"
        aria-label={ariaLabel || label}
        aria-valuemin={min}
        aria-valuemax={max}
        aria-valuenow={min + value * (max - min)}
        tabIndex={0}
        className="aws-knob"
        style={{
          '--knob-size': `${diameter}px`,
          '--knob-color': accentColor,
          '--knob-gloss': gloss,
          '--knob-rotation': `${rotation}deg`
        } as React.CSSProperties}
        onPointerDown={handlePointerDown}
        onKeyDown={(e) => {
          if (e.key === 'ArrowUp' || e.key === 'ArrowRight') {
            onChange(Math.min(1, value + step));
            e.preventDefault();
          } else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') {
            onChange(Math.max(0, value - step));
            e.preventDefault();
          }
        }}
      >
        {/* Tick marks */}
        <div className="aws-knob-ticks">
          {Array.from({ length: tickCount }).map((_, i) => (
            <div
              key={i}
              className="aws-knob-tick"
              style={{
                transform: `rotate(${-135 + (i / (tickCount - 1)) * 270}deg)`
              }}
            />
          ))}
        </div>

        {/* Dial */}
        <div className="aws-knob-dial">
          <div className="aws-knob-indicator" />
        </div>
      </div>
    </div>
  );
};
```

**Generated CSS**:

```css
/* Generated: src/primitives/AWSKnob/AWSKnob.css */

.aws-knob-container {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;  /* from spacing.xs */
}

.aws-knob-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--aws-color-surface);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.aws-knob {
  position: relative;
  width: var(--knob-size);
  height: var(--knob-size);
  border-radius: 50%;
  background: var(--knob-color);
  cursor: grab;
  user-select: none;
  touch-action: none;

  /* Enamel gloss effect - from materials.enamel-gloss */
  box-shadow:
    inset 0 1px 3px rgba(255,255,255,var(--knob-gloss)),
    0 2px 8px rgba(0,0,0,0.15),
    0 4px 16px rgba(0,0,0,0.1);

  /* Elastic transition - from transitions.easing.spring */
  transition: transform 220ms cubic-bezier(0.68,-0.55,0.27,1.55);
}

.aws-knob:active {
  cursor: grabbing;
}

.aws-knob:focus-visible {
  outline: 2px solid var(--aws-color-coral);
  outline-offset: 4px;
}

.aws-knob-ticks {
  position: absolute;
  inset: 0;
}

.aws-knob-tick {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2px;
  height: 6px;
  background: rgba(0,0,0,0.3);
  transform-origin: center calc(var(--knob-size) / 2);
  margin-left: -1px;
  margin-top: calc(var(--knob-size) / -2 + 2px);
}

.aws-knob-dial {
  position: absolute;
  inset: 8%;  /* from spacing */
  background: rgba(0,0,0,0.1);
  border-radius: 50%;
  transform: rotate(var(--knob-rotation));
}

.aws-knob-indicator {
  position: absolute;
  top: 8%;
  left: 50%;
  width: 3px;
  height: 30%;
  background: rgba(255,255,255,0.9);
  border-radius: 2px;  /* from radius.sm */
  transform: translateX(-50%);
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

/* Responsive sizing */
@media (prefers-reduced-motion: reduce) {
  .aws-knob {
    transition: none;
  }
}
```

---

### Generated Storybook Story

```typescript
// Generated: src/primitives/AWSKnob/AWSKnob.stories.tsx

import type { Meta, StoryObj } from '@storybook/react';
import { AWSKnob } from './AWSKnob';
import { AWSThemeProvider } from '../../theme/AWSThemeProvider';
import { useState } from 'react';

const meta: Meta<typeof AWSKnob> = {
  title: 'Primitives/AWSKnob',
  component: AWSKnob,
  decorators: [
    (Story) => (
      <AWSThemeProvider>
        <div style={{ padding: '40px', background: '#1a1a1a' }}>
          <Story />
        </div>
      </AWSThemeProvider>
    )
  ],
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof AWSKnob>;

export const Default: Story = {
  render: () => {
    const [value, setValue] = useState(0.5);
    return <AWSKnob value={value} onChange={setValue} label="Cutoff" />;
  }
};

export const AllAccents: Story = {
  render: () => {
    const [value, setValue] = useState(0.42);
    return (
      <div style={{ display: 'flex', gap: '24px' }}>
        <AWSKnob value={value} onChange={setValue} label="Coral" accent="coral" />
        <AWSKnob value={value} onChange={setValue} label="Teal" accent="teal" />
        <AWSKnob value={value} onChange={setValue} label="Lemon" accent="lemon" />
        <AWSKnob value={value} onChange={setValue} label="Peach" accent="peach" />
        <AWSKnob value={value} onChange={setValue} label="Mint" accent="mint" />
      </div>
    );
  }
};

export const AllSizes: Story = {
  render: () => {
    const [value, setValue] = useState(0.7);
    return (
      <div style={{ display: 'flex', gap: '24px', alignItems: 'flex-end' }}>
        <AWSKnob value={value} onChange={setValue} label="XS" size="xs" />
        <AWSKnob value={value} onChange={setValue} label="SM" size="sm" />
        <AWSKnob value={value} onChange={setValue} label="MD" size="md" />
        <AWSKnob value={value} onChange={setValue} label="LG" size="lg" />
      </div>
    );
  }
};

export const WithDetents: Story = {
  render: () => {
    const [value, setValue] = useState(0.5);
    return (
      <AWSKnob
        value={value}
        onChange={setValue}
        label="Resonance"
        detents={[0, 0.25, 0.5, 0.75, 1.0]}
        tickCount={5}
      />
    );
  }
};

export const AccessibilityTest: Story = {
  render: () => {
    const [value, setValue] = useState(0.3);
    return (
      <AWSKnob
        value={value}
        onChange={setValue}
        label="Filter Cutoff"
        ariaLabel="Filter cutoff frequency control"
        min={20}
        max={20000}
        step={10}
      />
    );
  },
  parameters: {
    a11y: {
      config: {
        rules: [
          { id: 'color-contrast', enabled: true },
          { id: 'label', enabled: true },
        ],
      },
    },
  },
};
```

---

## Token → Component Transformation

### Mapping Rules

| Token Category | Component Props | Example Transformation |
|----------------|-----------------|------------------------|
| **Colors** (`palette`) | `accent?: AWSAccent` | `palette.primary` → `AWSAccent = 'coral'` |
| **Spacing** (`spacing`) | `size?: AWSSize` | `spacing.sm/md/lg` → `AWSSize = 'xs'\|'sm'\|'md'\|'lg'` |
| **Materials** (`materials`) | `trim?: AWSMaterialTrim` | `materials.brass-trim` → `trim="brass"` |
| **Transitions** (`transitions`) | `motion.elastic` | `transitions.easing.spring` → `cubic-bezier(...)` |
| **Audio Plugin** (`audio_plugin.knobs`) | Component sizing | `knobs.average_size` → `SIZE_MAP.md = 48` |
| **Component** (`button`) | Component variants | `button.primary` → `variant="primary"` |

### Extraction → Type Generation Flow

```typescript
// 1. Extract tokens
const tokens = {
  palette: {
    primary: "#F56A5D",    // Coral
    secondary: "#45B0A6",  // Teal
    accent: "#FFD85C"      // Lemon
  }
};

// 2. Generate TypeScript types
type AWSAccent = 'coral' | 'teal' | 'lemon';  // From palette keys

// 3. Generate theme tokens
const themeTokens = {
  colors: {
    coral: tokens.palette.primary,
    teal: tokens.palette.secondary,
    lemon: tokens.palette.accent
  }
};

// 4. Use in components
<AWSKnob accent="coral" />  // Type-safe!
```

---

## Platform-Specific Exports

### CSS Variables Export

**Used By**: All web platforms
**Format**: CSS custom properties

```css
:root {
  /* Foundation Tokens */
  --color-primary: #F56A5D;
  --color-secondary: #4ECDC4;
  --space-sm: 8px;
  --space-md: 16px;
  --radius-sm: 4px;
  --radius-md: 8px;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.12);

  /* Visual DNA Tokens */
  --material-brass: #B08C4C;
  --material-gloss: 0.7;
  --lighting-warmth: 0.65;

  /* Motion Tokens */
  --transition-fast: 150ms;
  --transition-elastic: cubic-bezier(0.68,-0.55,0.27,1.55);
}
```

---

### TypeScript Types Export

```typescript
export interface DesignTokens {
  palette: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
  };
  spacing: {
    xs: number;
    sm: number;
    md: number;
    lg: number;
    xl: number;
  };
  radius: {
    sm: number;
    md: number;
    lg: number;
    full: number;
  };
  // ... all token types
}
```

---

### Tailwind Config Export

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#F56A5D',
        secondary: '#4ECDC4',
        accent: '#FFD85C',
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
      },
      borderRadius: {
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
      },
      transitionTimingFunction: {
        'elastic': 'cubic-bezier(0.68,-0.55,0.27,1.55)',
      }
    }
  }
}
```

---

## Creating Custom Generators

### Generator Template Structure

```typescript
// generators/src/export-custom.ts

import fs from 'fs';
import path from 'path';

export interface CustomGeneratorOptions {
  tokens: any;              // Extracted design tokens
  outputPath: string;       // Output directory
  packageName?: string;     // e.g., "@company/design-system"
  framework?: 'react' | 'vue' | 'svelte';
}

export async function generateCustomPackage(
  options: CustomGeneratorOptions
): Promise<void> {
  const { tokens, outputPath, packageName = '@company/ui', framework = 'react' } = options;

  // 1. Create package structure
  fs.mkdirSync(`${outputPath}/src`, { recursive: true });
  fs.mkdirSync(`${outputPath}/styles`, { recursive: true });

  // 2. Generate package.json
  const packageJson = {
    name: packageName,
    version: '1.0.0',
    main: 'dist/index.js',
    types: 'dist/index.d.ts',
    dependencies: framework === 'react' ? { 'react': '^18.0.0' } : {}
  };
  fs.writeFileSync(
    `${outputPath}/package.json`,
    JSON.stringify(packageJson, null, 2)
  );

  // 3. Generate theme tokens
  const tokenTypes = generateTokenTypes(tokens);
  fs.writeFileSync(`${outputPath}/src/tokens.types.ts`, tokenTypes);

  // 4. Generate components
  if (tokens.audio_plugin?.knobs) {
    const knobComponent = generateKnobComponent(tokens, framework);
    fs.writeFileSync(`${outputPath}/src/Knob.tsx`, knobComponent);
  }

  // 5. Generate CSS variables
  const cssVars = generateCSSVariables(tokens);
  fs.writeFileSync(`${outputPath}/styles/tokens.css`, cssVars);
}

function generateTokenTypes(tokens: any): string {
  const accentColors = Object.keys(tokens.palette || {})
    .filter(k => !['background', 'text'].includes(k))
    .map(k => `'${k}'`)
    .join(' | ');

  return `export type Accent = ${accentColors || "'primary'"};
export type Size = 'xs' | 'sm' | 'md' | 'lg';

export interface DesignTokens {
  colors: Record<string, string>;
  spacing: Record<string, number>;
  // ... more types
}`;
}

function generateKnobComponent(tokens: any, framework: string): string {
  if (framework === 'react') {
    return `import React from 'react';

export interface KnobProps {
  value: number;
  onChange: (v: number) => void;
  size?: 'xs' | 'sm' | 'md' | 'lg';
}

export const Knob: React.FC<KnobProps> = ({ value, onChange, size = 'md' }) => {
  // Generated component logic
  return <div className="knob">...</div>;
};`;
  }
  // ... Vue, Svelte implementations
  return '';
}

function generateCSSVariables(tokens: any): string {
  let css = ':root {\n';

  if (tokens.palette) {
    Object.entries(tokens.palette).forEach(([key, value]) => {
      css += `  --color-${key}: ${value};\n`;
    });
  }

  if (tokens.spacing) {
    Object.entries(tokens.spacing).forEach(([key, value]) => {
      css += `  --space-${key}: ${value}px;\n`;
    });
  }

  css += '}\n';
  return css;
}
```

---

## Generator Performance

### Caching Strategy

**Backend Cache** (Python):
- SHA256 hash of (format + tokens + spec)
- 1-hour TTL
- 100 entries max
- LRU eviction

**Performance Gains**:
- Cache hit: < 10ms
- Cache miss: 500ms - 5s (depending on generator)

### Parallel Execution

```python
# Run multiple generators in parallel
await asyncio.gather(
    execute_generator("figma", tokens, ...),
    execute_generator("mui", tokens, ...),
    execute_generator("react", tokens, ...),
)
# Total time: max(generator_times) instead of sum(generator_times)
```

---

## Related Documentation

- [Complete Token-Extractor Mapping](COMPLETE_TOKEN_EXTRACTOR_MAPPING.md) - CV libraries, AI models, methods
- [Extractor-to-Token Type Table](EXTRACTOR_TO_TOKEN_TYPE_TABLE.md) - Which extractors produce which tokens
- [Token Schema Guide](TOKEN_SCHEMA_GUIDE.md) - Complete token schemas
- [Token Variations Guide](TOKEN_VARIATIONS_GUIDE.md) - Multi-variant system
- [Storytelling Framework](STORYTELLING_FRAMEWORK.md) - Token naming and narratives

---

**Last Updated**: 2025-11-11
**Version**: 3.1
**Status**: Production Blueprint + @aws-ui/ Architecture Reference
