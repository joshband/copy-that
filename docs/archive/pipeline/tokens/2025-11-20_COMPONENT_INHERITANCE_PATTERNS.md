# Component Inheritance Patterns & Trait Composition

> Production-ready component architecture for token-driven design systems with trait-based specialization.

**Version**: 1.0 | **Last Updated**: November 2025 | **Status**: Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [Three-Tier Inheritance Model](#three-tier-inheritance-model)
4. [Trait Composition Pattern](#trait-composition-pattern)
5. [Model-View Separation](#model-view-separation)
6. [Token Injection & Dependency Management](#token-injection--dependency-management)
7. [React Adapter Pattern](#react-adapter-pattern)
8. [Testing Strategies](#testing-strategies)
9. [Performance Optimization](#performance-optimization)
10. [Accessibility Best Practices](#accessibility-best-practices)
11. [Factory Pattern](#factory-pattern)
12. [Complete Code Examples](#complete-code-examples)
13. [Integration with Token System](#integration-with-token-system)

---

## Overview

This guide documents the **component inheritance patterns** and **trait composition strategies** recommended by the UI Designer and Component Architect agents for building scalable, maintainable component libraries driven by extracted design tokens.

### Key Design Decisions

**✅ Approved Patterns**:
- **Trait Composition**: Mix and match behaviors via interfaces (not deep inheritance)
- **Model-View Separation**: Business logic separate from React views
- **Token Injection**: Design tokens as constructor dependencies
- **TypeScript**: Type safety across model, view, and trait layers
- **Shallow Hierarchy**: Maximum 2-3 inheritance levels

**❌ Anti-Patterns to Avoid**:
- Deep inheritance chains (4+ levels)
- Tightly coupled view logic
- Hard-coded style values
- Inheritance for specialization (use traits instead)

### Architecture Grade

**Overall Score**: A (9/10)

**Component Architect Evaluation**:
- ✅ Composition over inheritance
- ✅ Single responsibility principle
- ✅ Type safety with TypeScript
- ✅ Clear separation of concerns
- ⚠️ Needs: Comprehensive testing, API documentation, sensible defaults

**UI Designer Evaluation**:
- ✅ Design tokens as single source of truth
- ✅ Accessibility-first design
- ✅ Performance optimization ready
- ⚠️ Needs: WCAG validation, focus indicators, touch target validation

---

## Architecture Principles

### 1. Composition Over Inheritance

**Component Architect Principle**:
> "Build complex UIs from simple, composable parts. Inheritance creates tight coupling; composition enables flexibility."

**Implementation**:
```typescript
// ❌ BAD: Deep inheritance for specialization
class Button extends UIElement {}
class ThemedButton extends Button {}
class AWSUIButton extends ThemedButton {}
class AWSUIButtonGlowing extends AWSUIButton {}
class AWSUIButtonGlowingDark extends AWSUIButtonGlowing {}
class AWSUIButtonGlowingDarkCompact extends AWSUIButtonGlowingDark {}

// ✅ GOOD: Shallow hierarchy + trait composition
class UIButton extends UIElement {}
class AWSUIButton extends UIButton {}
class AWSUIButtonSpecialized extends AWSUIButton
  implements GlowTrait, DarkModeTrait, CompactTrait {}
```

### 2. Single Responsibility

**Component Architect Principle**:
> "Each component does one thing well."

**Implementation**:
```typescript
// ✅ Separate concerns
class UIButton {
  // Handles: click events, disabled state, loading state
}

interface GlowTrait {
  // Handles: glow effects, animation
}

interface DarkModeTrait {
  // Handles: dark theme colors
}

interface CompactTrait {
  // Handles: spacing, sizing
}
```

### 3. Design Tokens as Single Source of Truth

**UI Designer Principle**:
> "Design tokens define colors, typography, spacing, shadows as the single source of truth."

**Implementation**:
```typescript
// ✅ Token-driven styling
class AWSUIButton {
  constructor(private tokens: BaseDesignTokens) {}

  getBackgroundColor(): string {
    return this.tokens.colors.primary; // From extracted tokens
  }

  getPadding(): string {
    return `${this.tokens.spacing.sm}px ${this.tokens.spacing.md}px`;
  }
}
```

### 4. Accessibility First

**UI Designer Principle**:
> "WCAG 2.1 AA compliance minimum (AAA where possible). Color contrast: 4.5:1 for normal text, 3:1 for large text. Touch targets: 44x44px minimum."

**Implementation**:
```typescript
class UIButton {
  validateAccessibility(): AccessibilityReport {
    return {
      contrastRatio: this.getContrastRatio(),
      touchTargetSize: this.getTouchTargetSize(),
      hasAriaLabel: this.hasAriaLabel(),
      keyboardNavigable: this.isKeyboardNavigable()
    };
  }
}
```

---

## Three-Tier Inheritance Model

### Tier 1: Generic (Abstract Base)

**Purpose**: Cross-platform primitives, no visual styling

**Location**: `@design-system/core`

**Example**:
```typescript
// packages/core/src/UIElement.ts
export abstract class UIElement {
  protected id: string;
  protected disabled: boolean = false;
  protected visible: boolean = true;

  abstract render(): void;
  abstract getAccessibilityInfo(): AccessibilityInfo;

  setDisabled(disabled: boolean): void {
    this.disabled = disabled;
  }

  getId(): string {
    return this.id;
  }
}

// packages/core/src/UIButton.ts
export abstract class UIButton extends UIElement {
  protected label: string;
  protected onClick: (() => void) | null = null;

  setLabel(label: string): void {
    this.label = label;
  }

  setOnClick(handler: () => void): void {
    this.onClick = handler;
  }

  protected handleClick(): void {
    if (!this.disabled && this.onClick) {
      this.onClick();
    }
  }

  // Abstract methods for children to implement
  abstract getBackgroundColor(): string;
  abstract getPadding(): string;
  abstract getBorderRadius(): string;
}
```

### Tier 2: Themed (Style-Specific)

**Purpose**: Apply design tokens from specific style library

**Location**: `@analog-whimsy/ui`, `@brutalist-console/ui`, `@minimal-glass/ui`

**Example**:
```typescript
// packages/analog-whimsy/src/AWSUIButton.ts
import { UIButton } from '@design-system/core';
import { BaseDesignTokens } from '@design-system/core/types';

export class AWSUIButton extends UIButton {
  constructor(protected tokens: BaseDesignTokens) {
    super();
  }

  getBackgroundColor(): string {
    return this.disabled
      ? this.tokens.colors.neutral400
      : this.tokens.colors.primary;
  }

  getPadding(): string {
    return `${this.tokens.spacing.sm}px ${this.tokens.spacing.md}px`;
  }

  getBorderRadius(): string {
    return `${this.tokens.borderRadius.md}px`;
  }

  getShadow(): string {
    return this.tokens.shadows.md;
  }

  getMaterial(): MaterialProperties | undefined {
    return this.tokens.materials?.['enamel-gloss'];
  }

  render(): void {
    const bgColor = this.getBackgroundColor();
    const padding = this.getPadding();
    const borderRadius = this.getBorderRadius();
    const shadow = this.getShadow();

    // Platform-specific rendering
    console.log(`Render button: ${this.label}`, {
      bgColor, padding, borderRadius, shadow
    });
  }

  getAccessibilityInfo(): AccessibilityInfo {
    return {
      role: 'button',
      label: this.label,
      disabled: this.disabled,
      contrastRatio: this.calculateContrastRatio()
    };
  }

  private calculateContrastRatio(): number {
    // Calculate WCAG contrast ratio
    const bgColor = this.getBackgroundColor();
    const textColor = this.tokens.colors.neutral50;
    return calculateWCAGContrast(bgColor, textColor);
  }
}
```

### Tier 3: Specialized (Trait-Based)

**Purpose**: Add optional behaviors via trait composition

**Location**: Same package as themed components

**Example**:
```typescript
// packages/analog-whimsy/src/traits/GlowTrait.ts
export interface GlowTrait {
  glowIntensity: number;
  glowColor: string;
  enableGlow(intensity: number): void;
  disableGlow(): void;
  getGlowStyle(): string;
}

// packages/analog-whimsy/src/traits/DarkModeTrait.ts
export interface DarkModeTrait {
  isDarkMode: boolean;
  enableDarkMode(): void;
  disableDarkMode(): void;
  getDarkModeColors(): { bg: string; fg: string };
}

// packages/analog-whimsy/src/traits/CompactTrait.ts
export interface CompactTrait {
  isCompact: boolean;
  enableCompact(): void;
  disableCompact(): void;
  getCompactPadding(): string;
}

// packages/analog-whimsy/src/AWSUIButtonSpecialized.ts
export class AWSUIButtonSpecialized extends AWSUIButton
  implements GlowTrait, DarkModeTrait, CompactTrait {

  // GlowTrait implementation
  glowIntensity: number = 0;
  glowColor: string = '';

  enableGlow(intensity: number): void {
    this.glowIntensity = intensity;
    this.glowColor = this.tokens.colors.accent || this.tokens.colors.primary;
  }

  disableGlow(): void {
    this.glowIntensity = 0;
  }

  getGlowStyle(): string {
    if (this.glowIntensity === 0) return '';
    return `0 0 ${this.glowIntensity * 10}px ${this.glowColor}`;
  }

  // DarkModeTrait implementation
  isDarkMode: boolean = false;

  enableDarkMode(): void {
    this.isDarkMode = true;
  }

  disableDarkMode(): void {
    this.isDarkMode = false;
  }

  getDarkModeColors(): { bg: string; fg: string } {
    // Use dark theme variant from tokens
    return {
      bg: this.tokens.colors.neutral900,
      fg: this.tokens.colors.neutral50
    };
  }

  // CompactTrait implementation
  isCompact: boolean = false;

  enableCompact(): void {
    this.isCompact = true;
  }

  disableCompact(): void {
    this.isCompact = false;
  }

  getCompactPadding(): string {
    const baseSpacing = this.tokens.spacing.sm;
    return `${baseSpacing * 0.5}px ${baseSpacing}px`;
  }

  // Override base methods to incorporate traits
  getBackgroundColor(): string {
    if (this.isDarkMode) {
      return this.getDarkModeColors().bg;
    }
    return super.getBackgroundColor();
  }

  getPadding(): string {
    if (this.isCompact) {
      return this.getCompactPadding();
    }
    return super.getPadding();
  }

  getShadow(): string {
    const baseShadow = super.getShadow();
    const glowShadow = this.getGlowStyle();

    if (glowShadow) {
      return `${baseShadow}, ${glowShadow}`;
    }
    return baseShadow;
  }
}
```

---

## Trait Composition Pattern

### Why Traits Over Inheritance?

**Problem**: Deep inheritance chains become brittle and inflexible.

```typescript
// ❌ Inheritance explosion
class ButtonGlowing extends Button {}
class ButtonGlowingDark extends ButtonGlowing {}
class ButtonGlowingDarkCompact extends ButtonGlowingDark {}
class ButtonGlowingDarkCompactAnimated extends ButtonGlowingDarkCompact {}
// 16 combinations = 16 classes!
```

**Solution**: Traits allow infinite combinations with shallow hierarchy.

```typescript
// ✅ Trait composition
class ButtonSpecialized extends Button
  implements GlowTrait, DarkModeTrait, CompactTrait, AnimatedTrait {}

// Configure at instantiation
const btn = new ButtonSpecialized(tokens);
btn.enableGlow(0.8);
btn.enableDarkMode();
btn.enableCompact();
btn.enableAnimation('spring');
// 16 combinations = 1 class!
```

### Available Traits

#### Visual Traits

**GlowTrait** - Adds glow/outer shadow effects
```typescript
interface GlowTrait {
  glowIntensity: number;        // 0.0 - 1.0
  glowColor: string;            // Hex color
  enableGlow(intensity: number): void;
  disableGlow(): void;
  getGlowStyle(): string;       // CSS box-shadow
}
```

**GradientTrait** - Applies gradient backgrounds
```typescript
interface GradientTrait {
  gradientStops: Array<{ color: string; position: number }>;
  gradientAngle: number;        // 0-360 degrees
  enableGradient(stops: GradientStop[], angle?: number): void;
  disableGradient(): void;
  getGradientStyle(): string;   // CSS linear-gradient
}
```

**MaterialTrait** - Applies material properties (gloss, roughness, metalness)
```typescript
interface MaterialTrait {
  material: MaterialProperties;
  applyMaterial(material: MaterialProperties): void;
  getMaterialStyle(): CSSProperties;
}
```

#### Theme Traits

**DarkModeTrait** - Dark theme variant
```typescript
interface DarkModeTrait {
  isDarkMode: boolean;
  enableDarkMode(): void;
  disableDarkMode(): void;
  getDarkModeColors(): { bg: string; fg: string; border: string };
}
```

**MonochromaticTrait** - Single-color variant
```typescript
interface MonochromaticTrait {
  baseColor: string;
  enableMonochromatic(baseColor: string): void;
  disableMonochromatic(): void;
  getMonochromaticPalette(): ColorScale;
}
```

**HighContrastTrait** - WCAG AAA high-contrast
```typescript
interface HighContrastTrait {
  isHighContrast: boolean;
  enableHighContrast(): void;
  disableHighContrast(): void;
  getHighContrastColors(): { bg: string; fg: string };
  validateWCAGAAA(): boolean;
}
```

#### Layout Traits

**CompactTrait** - Reduced spacing/sizing
```typescript
interface CompactTrait {
  isCompact: boolean;
  enableCompact(): void;
  disableCompact(): void;
  getCompactPadding(): string;
  getCompactFontSize(): number;
}
```

**SpaciousTrait** - Increased spacing/sizing
```typescript
interface SpaciousTrait {
  isSpacious: boolean;
  enableSpacious(): void;
  disableSpacious(): void;
  getSpaciousPadding(): string;
  getSpaciousFontSize(): number;
}
```

#### Interaction Traits

**AnimatedTrait** - Motion/transitions
```typescript
interface AnimatedTrait {
  animationType: 'spring' | 'linear' | 'ease' | 'bounce';
  animationDuration: number;    // milliseconds
  enableAnimation(type: string, duration?: number): void;
  disableAnimation(): void;
  getTransitionStyle(): string;
}
```

**HapticTrait** - Haptic feedback
```typescript
interface HapticTrait {
  hapticStrength: 'light' | 'medium' | 'heavy';
  enableHaptic(strength: string): void;
  disableHaptic(): void;
  triggerHaptic(): void;
}
```

**TooltipTrait** - Hover tooltips
```typescript
interface TooltipTrait {
  tooltipText: string;
  tooltipPosition: 'top' | 'right' | 'bottom' | 'left';
  setTooltip(text: string, position?: string): void;
  showTooltip(): void;
  hideTooltip(): void;
}
```

### Trait Implementation Example

```typescript
// Real-world usage: Button with 4 traits
import { AWSUIButton } from '@analog-whimsy/ui';
import {
  GlowTrait,
  DarkModeTrait,
  CompactTrait,
  AnimatedTrait
} from '@analog-whimsy/ui/traits';

class CTAButton extends AWSUIButton
  implements GlowTrait, DarkModeTrait, CompactTrait, AnimatedTrait {

  // GlowTrait
  glowIntensity = 0;
  glowColor = '';
  enableGlow(intensity: number) { /* ... */ }
  disableGlow() { /* ... */ }
  getGlowStyle() { /* ... */ }

  // DarkModeTrait
  isDarkMode = false;
  enableDarkMode() { /* ... */ }
  disableDarkMode() { /* ... */ }
  getDarkModeColors() { /* ... */ }

  // CompactTrait
  isCompact = false;
  enableCompact() { /* ... */ }
  disableCompact() { /* ... */ }
  getCompactPadding() { /* ... */ }

  // AnimatedTrait
  animationType = 'spring';
  animationDuration = 200;
  enableAnimation(type, duration) { /* ... */ }
  disableAnimation() { /* ... */ }
  getTransitionStyle() { /* ... */ }

  // Combine all traits in render
  render(): void {
    const styles = {
      background: this.getBackgroundColor(),
      padding: this.getPadding(),
      boxShadow: this.getShadow(),
      transition: this.getTransitionStyle()
    };
    // Render with combined styles
  }
}

// Usage
const ctaButton = new CTAButton(analogWhimsyTokens);
ctaButton.setLabel('Get Started');
ctaButton.enableGlow(0.8);
ctaButton.enableDarkMode();
ctaButton.enableCompact();
ctaButton.enableAnimation('spring', 300);
ctaButton.render();
```

---

## Model-View Separation

### Architecture Pattern

**Component Architect Principle**:
> "Separate business logic from presentation. Models handle state and behavior; views handle rendering."

```
┌─────────────────────────────────────────┐
│           TypeScript Models             │
│  (Business logic, state, validation)    │
│  ┌─────────────────────────────────┐   │
│  │ UIButton (abstract base)        │   │
│  │ ├─ AWSUIButton (themed)         │   │
│  │ └─ AWSUIButtonSpecialized       │   │
│  │    (+ GlowTrait, DarkModeTrait) │   │
│  └─────────────────────────────────┘   │
└─────────────────┬───────────────────────┘
                  │ Token injection
                  │
┌─────────────────▼───────────────────────┐
│          React Adapter Views            │
│    (Thin wrappers, no business logic)   │
│  ┌─────────────────────────────────┐   │
│  │ <AWSButton /> component         │   │
│  │ ├─ Instantiates AWSUIButton     │   │
│  │ ├─ Passes props to model        │   │
│  │ └─ Renders using model state    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Benefits

1. **Platform Agnostic Models**: TypeScript models work in React, Vue, Angular, vanilla JS
2. **Testable Logic**: Unit test models without React dependencies
3. **Type Safety**: Full TypeScript support across layers
4. **Reusable Views**: Thin views are easy to refactor/replace

### Example: Button Model

```typescript
// packages/analog-whimsy/src/models/AWSUIButton.ts
import { UIButton } from '@design-system/core';
import { BaseDesignTokens } from '@design-system/core/types';

export class AWSUIButton extends UIButton {
  private tokens: BaseDesignTokens;
  private variant: 'primary' | 'secondary' | 'ghost' = 'primary';
  private size: 'sm' | 'md' | 'lg' = 'md';
  private loading: boolean = false;

  constructor(tokens: BaseDesignTokens) {
    super();
    this.tokens = tokens;
  }

  // Configuration methods
  setVariant(variant: 'primary' | 'secondary' | 'ghost'): void {
    this.variant = variant;
  }

  setSize(size: 'sm' | 'md' | 'lg'): void {
    this.size = size;
  }

  setLoading(loading: boolean): void {
    this.loading = loading;
  }

  // Style computation (business logic)
  getBackgroundColor(): string {
    if (this.disabled) return this.tokens.colors.neutral400;
    if (this.variant === 'primary') return this.tokens.colors.primary;
    if (this.variant === 'secondary') return this.tokens.colors.secondary;
    return 'transparent'; // ghost
  }

  getPadding(): string {
    const spacing = this.tokens.spacing;
    if (this.size === 'sm') return `${spacing.xs}px ${spacing.sm}px`;
    if (this.size === 'lg') return `${spacing.md}px ${spacing.lg}px`;
    return `${spacing.sm}px ${spacing.md}px`; // md
  }

  getFontSize(): number {
    if (this.size === 'sm') return this.tokens.typography.fontSize.sm;
    if (this.size === 'lg') return this.tokens.typography.fontSize.lg;
    return this.tokens.typography.fontSize.base;
  }

  getBorderRadius(): string {
    return `${this.tokens.borderRadius.md}px`;
  }

  // State queries
  isDisabled(): boolean {
    return this.disabled || this.loading;
  }

  isLoading(): boolean {
    return this.loading;
  }

  // Render method (platform-agnostic)
  render(): void {
    console.log('Render button model', {
      label: this.label,
      variant: this.variant,
      size: this.size,
      disabled: this.isDisabled(),
      loading: this.loading
    });
  }

  // Accessibility
  getAccessibilityInfo(): AccessibilityInfo {
    return {
      role: 'button',
      label: this.label,
      disabled: this.isDisabled(),
      ariaLive: this.loading ? 'polite' : 'off',
      ariaLabel: this.loading ? `${this.label} (loading)` : this.label
    };
  }
}
```

### Example: Button View (React)

```typescript
// packages/analog-whimsy-react/src/components/AWSButton.tsx
import React, { useMemo } from 'react';
import { AWSUIButton } from '@analog-whimsy/ui';
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
  const tokens = useTokens(); // Get tokens from context

  // Instantiate model (memoized)
  const buttonModel = useMemo(() => {
    const model = new AWSUIButton(tokens);
    model.setVariant(variant);
    model.setSize(size);
    return model;
  }, [tokens, variant, size]);

  // Update model state
  buttonModel.setLabel(label);
  buttonModel.setDisabled(disabled);
  buttonModel.setLoading(loading);
  if (onClick) {
    buttonModel.setOnClick(onClick);
  }

  // Get computed styles from model
  const styles: React.CSSProperties = {
    backgroundColor: buttonModel.getBackgroundColor(),
    padding: buttonModel.getPadding(),
    fontSize: `${buttonModel.getFontSize()}px`,
    borderRadius: buttonModel.getBorderRadius(),
    cursor: buttonModel.isDisabled() ? 'not-allowed' : 'pointer',
    opacity: buttonModel.isDisabled() ? 0.5 : 1,
    border: 'none',
    fontFamily: tokens.typography.fontFamily.base,
    fontWeight: tokens.typography.fontWeight.medium,
    color: tokens.colors.neutral50,
    transition: 'all 0.2s ease'
  };

  // Get accessibility info from model
  const a11y = buttonModel.getAccessibilityInfo();

  return (
    <button
      className={className}
      style={styles}
      disabled={buttonModel.isDisabled()}
      onClick={() => !buttonModel.isDisabled() && onClick?.()}
      role={a11y.role}
      aria-label={a11y.ariaLabel}
      aria-live={a11y.ariaLive}
      aria-disabled={buttonModel.isDisabled()}
    >
      {buttonModel.isLoading() ? (
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

### Testing Strategy

**Model Tests** (No React dependencies):
```typescript
// packages/analog-whimsy/src/models/__tests__/AWSUIButton.test.ts
import { AWSUIButton } from '../AWSUIButton';
import { mockTokens } from '../../__mocks__/tokens';

describe('AWSUIButton Model', () => {
  let button: AWSUIButton;

  beforeEach(() => {
    button = new AWSUIButton(mockTokens);
  });

  test('should return primary color for primary variant', () => {
    button.setVariant('primary');
    expect(button.getBackgroundColor()).toBe(mockTokens.colors.primary);
  });

  test('should be disabled when loading', () => {
    button.setLoading(true);
    expect(button.isDisabled()).toBe(true);
  });

  test('should calculate correct padding for size', () => {
    button.setSize('lg');
    const expected = `${mockTokens.spacing.md}px ${mockTokens.spacing.lg}px`;
    expect(button.getPadding()).toBe(expected);
  });

  test('should provide correct accessibility info', () => {
    button.setLabel('Submit');
    button.setLoading(true);
    const a11y = button.getAccessibilityInfo();

    expect(a11y.role).toBe('button');
    expect(a11y.ariaLabel).toBe('Submit (loading)');
    expect(a11y.ariaLive).toBe('polite');
    expect(a11y.disabled).toBe(true);
  });
});
```

**View Tests** (React Testing Library):
```typescript
// packages/analog-whimsy-react/src/components/__tests__/AWSButton.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { AWSButton } from '../AWSButton';
import { TokenProvider } from '../../providers/TokenProvider';
import { mockTokens } from '../../__mocks__/tokens';

describe('AWSButton Component', () => {
  const renderButton = (props = {}) => {
    return render(
      <TokenProvider tokens={mockTokens}>
        <AWSButton label="Click me" {...props} />
      </TokenProvider>
    );
  };

  test('should render with label', () => {
    renderButton();
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  test('should call onClick when clicked', () => {
    const handleClick = jest.fn();
    renderButton({ onClick: handleClick });

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('should not call onClick when disabled', () => {
    const handleClick = jest.fn();
    renderButton({ onClick: handleClick, disabled: true });

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).not.toHaveBeenCalled();
  });

  test('should show loading state', () => {
    renderButton({ loading: true });
    expect(screen.getByLabelText(/loading/i)).toBeInTheDocument();
  });
});
```

---

## Token Injection & Dependency Management

### Constructor Injection Pattern

**Best Practice**: Inject tokens through constructor for explicit dependencies.

```typescript
// ✅ GOOD: Explicit token dependency
class AWSUIButton extends UIButton {
  constructor(private tokens: BaseDesignTokens) {
    super();
  }

  getBackgroundColor(): string {
    return this.tokens.colors.primary; // Clear dependency
  }
}

// ❌ BAD: Global token access
class AWSUIButton extends UIButton {
  getBackgroundColor(): string {
    return globalTokens.colors.primary; // Hidden dependency
  }
}
```

### Token Provider Pattern (React)

```typescript
// packages/analog-whimsy-react/src/providers/TokenProvider.tsx
import React, { createContext, useContext } from 'react';
import { BaseDesignTokens } from '@design-system/core/types';

const TokenContext = createContext<BaseDesignTokens | null>(null);

export interface TokenProviderProps {
  tokens: BaseDesignTokens;
  children: React.ReactNode;
}

export const TokenProvider: React.FC<TokenProviderProps> = ({
  tokens,
  children
}) => {
  return (
    <TokenContext.Provider value={tokens}>
      {children}
    </TokenContext.Provider>
  );
};

export const useTokens = (): BaseDesignTokens => {
  const tokens = useContext(TokenContext);
  if (!tokens) {
    throw new Error('useTokens must be used within TokenProvider');
  }
  return tokens;
};
```

### Usage in Application

```typescript
// App.tsx
import React from 'react';
import { TokenProvider } from '@analog-whimsy-react/providers';
import { analogWhimsyTokens } from '@analog-whimsy/ui';
import { AWSButton } from '@analog-whimsy-react/components';

export const App: React.FC = () => {
  return (
    <TokenProvider tokens={analogWhimsyTokens}>
      <div className="app">
        <AWSButton
          label="Get Started"
          variant="primary"
          size="lg"
          onClick={() => console.log('Clicked!')}
        />
      </div>
    </TokenProvider>
  );
};
```

### Dynamic Token Switching

```typescript
// Support theme switching at runtime
const [currentTheme, setCurrentTheme] = useState<'light' | 'dark'>('light');

const tokens = currentTheme === 'light'
  ? analogWhimsyTokens
  : analogWhimsyDarkTokens;

return (
  <TokenProvider tokens={tokens}>
    <button onClick={() => setCurrentTheme(t => t === 'light' ? 'dark' : 'light')}>
      Toggle Theme
    </button>
    <AWSButton label="Styled Button" />
  </TokenProvider>
);
```

---

## React Adapter Pattern

### Thin View Wrapper

**Component Architect Principle**:
> "Views should be thin adapters. All business logic belongs in models."

```typescript
// ✅ GOOD: Thin view (30 lines)
export const AWSButton: React.FC<AWSButtonProps> = (props) => {
  const tokens = useTokens();
  const model = useMemo(() => new AWSUIButton(tokens), [tokens]);

  // Sync props to model
  model.setLabel(props.label);
  model.setDisabled(props.disabled || false);

  // Render using model state
  return (
    <button style={getStylesFromModel(model)} onClick={props.onClick}>
      {props.label}
    </button>
  );
};

// ❌ BAD: Fat view with business logic (100+ lines)
export const AWSButton: React.FC<AWSButtonProps> = (props) => {
  // 50 lines of style calculation
  // 30 lines of state management
  // 20 lines of event handlers
  return <button>...</button>;
};
```

### Sensible Defaults

**Component Architect Principle**:
> "Provide reasonable default values for optional props."

```typescript
export interface AWSButtonProps {
  label: string;                                    // Required
  variant?: 'primary' | 'secondary' | 'ghost';      // Optional, default: 'primary'
  size?: 'sm' | 'md' | 'lg';                        // Optional, default: 'md'
  disabled?: boolean;                               // Optional, default: false
  loading?: boolean;                                // Optional, default: false
  onClick?: () => void;                             // Optional
  className?: string;                               // Optional, default: ''
}

export const AWSButton: React.FC<AWSButtonProps> = ({
  label,
  variant = 'primary',   // ✅ Sensible default
  size = 'md',           // ✅ Sensible default
  disabled = false,      // ✅ Sensible default
  loading = false,       // ✅ Sensible default
  onClick,
  className = ''
}) => {
  // Component logic
};
```

### Prop Interface Design

**Component Architect Principle**:
> "Create clear, intuitive, and type-safe prop interfaces."

```typescript
// ✅ GOOD: Clear, type-safe props
interface AWSSliderProps {
  value: number;                    // Current value
  min: number;                      // Minimum value
  max: number;                      // Maximum value
  step?: number;                    // Step increment (default: 1)
  onChange: (value: number) => void; // Value change handler
  label?: string;                   // Accessible label
  disabled?: boolean;               // Disabled state
  orientation?: 'horizontal' | 'vertical'; // Slider direction
}

// ❌ BAD: Unclear, any-typed props
interface AWSSliderProps {
  config: any;          // What's in config?
  handler: Function;    // What parameters? What return type?
  options?: any;        // Unclear purpose
}
```

---

## Testing Strategies

### Component Architect Recommendations

**Three-Layer Testing Pyramid**:
1. **Unit Tests** (70%): Model logic, pure functions
2. **Integration Tests** (20%): Component interactions
3. **Visual Regression Tests** (10%): Storybook snapshots

### 1. Unit Tests (Model Layer)

**Focus**: Business logic, state management, calculations

```typescript
// AWSUIButton.test.ts
describe('AWSUIButton', () => {
  let button: AWSUIButton;
  let tokens: BaseDesignTokens;

  beforeEach(() => {
    tokens = mockTokens;
    button = new AWSUIButton(tokens);
  });

  describe('Variant styles', () => {
    test('primary variant uses primary color', () => {
      button.setVariant('primary');
      expect(button.getBackgroundColor()).toBe(tokens.colors.primary);
    });

    test('secondary variant uses secondary color', () => {
      button.setVariant('secondary');
      expect(button.getBackgroundColor()).toBe(tokens.colors.secondary);
    });

    test('ghost variant uses transparent background', () => {
      button.setVariant('ghost');
      expect(button.getBackgroundColor()).toBe('transparent');
    });
  });

  describe('Size calculations', () => {
    test('small size uses correct padding', () => {
      button.setSize('sm');
      expect(button.getPadding()).toBe(`${tokens.spacing.xs}px ${tokens.spacing.sm}px`);
    });

    test('large size uses correct font size', () => {
      button.setSize('lg');
      expect(button.getFontSize()).toBe(tokens.typography.fontSize.lg);
    });
  });

  describe('State management', () => {
    test('loading state disables button', () => {
      button.setLoading(true);
      expect(button.isDisabled()).toBe(true);
    });

    test('disabled prop overrides loading', () => {
      button.setDisabled(true);
      button.setLoading(false);
      expect(button.isDisabled()).toBe(true);
    });
  });

  describe('Accessibility', () => {
    test('provides correct ARIA attributes', () => {
      button.setLabel('Submit Form');
      button.setLoading(true);
      const a11y = button.getAccessibilityInfo();

      expect(a11y.role).toBe('button');
      expect(a11y.ariaLabel).toContain('loading');
      expect(a11y.ariaLive).toBe('polite');
      expect(a11y.disabled).toBe(true);
    });
  });
});
```

### 2. Integration Tests (View Layer)

**Focus**: User interactions, event handling, prop changes

```typescript
// AWSButton.test.tsx
describe('AWSButton Component', () => {
  test('renders with all variants', () => {
    const { rerender } = render(<AWSButton label="Test" variant="primary" />);
    expect(screen.getByText('Test')).toBeInTheDocument();

    rerender(<AWSButton label="Test" variant="secondary" />);
    expect(screen.getByText('Test')).toBeInTheDocument();

    rerender(<AWSButton label="Test" variant="ghost" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  test('handles click events', () => {
    const handleClick = jest.fn();
    render(<AWSButton label="Click me" onClick={handleClick} />);

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('prevents clicks when disabled', () => {
    const handleClick = jest.fn();
    render(<AWSButton label="Disabled" disabled onClick={handleClick} />);

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).not.toHaveBeenCalled();
  });

  test('shows loading spinner', () => {
    const { rerender } = render(<AWSButton label="Submit" />);
    expect(screen.queryByLabelText(/loading/i)).not.toBeInTheDocument();

    rerender(<AWSButton label="Submit" loading />);
    expect(screen.getByLabelText(/loading/i)).toBeInTheDocument();
  });

  test('applies custom className', () => {
    const { container } = render(
      <AWSButton label="Test" className="custom-class" />
    );
    expect(container.querySelector('.custom-class')).toBeInTheDocument();
  });
});
```

### 3. Visual Regression Tests (Storybook)

**Focus**: Visual appearance, theme variations, responsive design

```typescript
// AWSButton.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { AWSButton } from './AWSButton';
import { TokenProvider } from '../providers/TokenProvider';
import { analogWhimsyTokens } from '@analog-whimsy/ui';

const meta: Meta<typeof AWSButton> = {
  title: 'Components/AWSButton',
  component: AWSButton,
  decorators: [
    (Story) => (
      <TokenProvider tokens={analogWhimsyTokens}>
        <Story />
      </TokenProvider>
    )
  ],
  parameters: {
    layout: 'centered'
  },
  tags: ['autodocs']
};

export default meta;
type Story = StoryObj<typeof AWSButton>;

// Default state
export const Primary: Story = {
  args: {
    label: 'Primary Button',
    variant: 'primary',
    size: 'md'
  }
};

// All variants
export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '16px' }}>
      <AWSButton label="Primary" variant="primary" />
      <AWSButton label="Secondary" variant="secondary" />
      <AWSButton label="Ghost" variant="ghost" />
    </div>
  )
};

// All sizes
export const AllSizes: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
      <AWSButton label="Small" size="sm" />
      <AWSButton label="Medium" size="md" />
      <AWSButton label="Large" size="lg" />
    </div>
  )
};

// States
export const States: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '16px' }}>
      <AWSButton label="Default" />
      <AWSButton label="Disabled" disabled />
      <AWSButton label="Loading" loading />
    </div>
  )
};

// Visual regression test
export const VisualRegressionGrid: Story = {
  render: () => (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
      {['primary', 'secondary', 'ghost'].map(variant =>
        ['sm', 'md', 'lg'].map(size =>
          <AWSButton
            key={`${variant}-${size}`}
            label={`${variant}-${size}`}
            variant={variant as any}
            size={size as any}
          />
        )
      )}
    </div>
  ),
  parameters: {
    chromatic: { disableSnapshot: false }
  }
};
```

### Test Coverage Goals

**Component Architect Standards**:
- Unit tests: 90%+ coverage
- Integration tests: 80%+ coverage
- Visual regression: All component states documented

```json
// jest.config.js
{
  "coverageThreshold": {
    "global": {
      "statements": 90,
      "branches": 85,
      "functions": 90,
      "lines": 90
    }
  }
}
```

---

## Performance Optimization

### UI Designer Recommendations

**Performance Budget**:
- Bundle size: < 50KB per component (gzipped)
- First paint: < 100ms
- Interaction response: < 16ms (60 FPS)

### 1. React.memo for Pure Components

```typescript
// ✅ Memoize expensive components
export const AWSButton = React.memo<AWSButtonProps>(({
  label,
  variant,
  size,
  onClick
}) => {
  // Component logic
}, (prevProps, nextProps) => {
  // Custom comparison for optimization
  return (
    prevProps.label === nextProps.label &&
    prevProps.variant === nextProps.variant &&
    prevProps.size === nextProps.size &&
    prevProps.disabled === nextProps.disabled
  );
});
```

### 2. useMemo for Model Instantiation

```typescript
export const AWSButton: React.FC<AWSButtonProps> = (props) => {
  const tokens = useTokens();

  // ✅ Memoize model creation (expensive)
  const buttonModel = useMemo(() => {
    return new AWSUIButton(tokens);
  }, [tokens]);

  // Cheap prop updates (no re-instantiation)
  buttonModel.setLabel(props.label);
  buttonModel.setVariant(props.variant || 'primary');

  return <button>...</button>;
};
```

### 3. useCallback for Event Handlers

```typescript
export const AWSButton: React.FC<AWSButtonProps> = ({ onClick, ...props }) => {
  // ✅ Memoize callback to prevent child re-renders
  const handleClick = useCallback(() => {
    if (!props.disabled && !props.loading) {
      onClick?.();
    }
  }, [onClick, props.disabled, props.loading]);

  return <button onClick={handleClick}>...</button>;
};
```

### 4. Code Splitting

```typescript
// ✅ Lazy load heavy components
const AWSButtonSpecialized = React.lazy(() =>
  import('./AWSButtonSpecialized')
);

export const App: React.FC = () => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AWSButtonSpecialized label="Advanced Button" />
    </Suspense>
  );
};
```

### 5. Bundle Optimization

```typescript
// packages/analog-whimsy-react/package.json
{
  "sideEffects": false, // Enable tree-shaking
  "exports": {
    "./components/AWSButton": "./src/components/AWSButton.tsx",
    "./components/AWSSlider": "./src/components/AWSSlider.tsx"
  }
}

// Import only what you need
import { AWSButton } from '@analog-whimsy-react/components/AWSButton';
// ❌ Don't import entire library
// import { AWSButton } from '@analog-whimsy-react'; // imports everything!
```

### 6. Virtual Scrolling for Lists

```typescript
// Use react-window for long lists of components
import { FixedSizeList } from 'react-window';

const ButtonList: React.FC = () => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <AWSButton label={`Button ${index}`} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={1000}
      itemSize={50}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
};
```

---

## Accessibility Best Practices

### UI Designer WCAG 2.1 Standards

**Required Compliance**:
- AA minimum (AAA where possible)
- Color contrast: 4.5:1 (normal text), 3:1 (large text ≥18px)
- Touch targets: 44×44px minimum (mobile)
- Keyboard navigation: Full support
- Screen readers: ARIA attributes

### 1. Color Contrast Validation

```typescript
class AWSUIButton extends UIButton {
  validateAccessibility(): AccessibilityReport {
    const bgColor = this.getBackgroundColor();
    const fgColor = this.getForegroundColor();
    const contrastRatio = calculateWCAGContrast(bgColor, fgColor);

    return {
      contrastRatio,
      wcagAA: contrastRatio >= 4.5,
      wcagAAA: contrastRatio >= 7.0,
      wcagAALarge: contrastRatio >= 3.0,
      recommendation: contrastRatio < 4.5
        ? `Increase contrast to ${4.5}:1 minimum`
        : 'Passes WCAG AA'
    };
  }
}

// Usage
const button = new AWSUIButton(tokens);
const a11yReport = button.validateAccessibility();
if (!a11yReport.wcagAA) {
  console.warn('Button fails WCAG AA:', a11yReport.recommendation);
}
```

### 2. Touch Target Sizing

```typescript
class AWSUIButton extends UIButton {
  getTouchTargetSize(): { width: number; height: number } {
    const padding = this.getPadding();
    const fontSize = this.getFontSize();

    // Calculate total dimensions
    const [verticalPadding, horizontalPadding] = padding.split(' ').map(parseFloat);
    const height = fontSize + verticalPadding * 2;
    const width = fontSize * 6 + horizontalPadding * 2; // Estimate

    return { width, height };
  }

  validateTouchTarget(): boolean {
    const { width, height } = this.getTouchTargetSize();
    const minSize = 44; // iOS Human Interface Guidelines

    if (width < minSize || height < minSize) {
      console.warn(`Touch target too small: ${width}×${height}px (min: ${minSize}×${minSize}px)`);
      return false;
    }
    return true;
  }
}
```

### 3. Keyboard Navigation

```typescript
export const AWSButton: React.FC<AWSButtonProps> = (props) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Space or Enter activates button
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      props.onClick?.();
    }
  };

  return (
    <button
      onClick={props.onClick}
      onKeyDown={handleKeyDown}
      tabIndex={props.disabled ? -1 : 0} // Remove from tab order when disabled
      aria-disabled={props.disabled}
    >
      {props.label}
    </button>
  );
};
```

### 4. ARIA Attributes

```typescript
class AWSUIButton extends UIButton {
  getAccessibilityInfo(): AccessibilityInfo {
    return {
      role: 'button',
      label: this.label,
      disabled: this.isDisabled(),

      // Live regions for dynamic content
      ariaLive: this.loading ? 'polite' : 'off',
      ariaAtomic: this.loading ? 'true' : 'false',

      // Descriptive labels
      ariaLabel: this.loading
        ? `${this.label} (loading)`
        : this.label,

      // Pressed state for toggle buttons
      ariaPressed: this.pressed ? 'true' : 'false',

      // Expanded state for dropdown buttons
      ariaExpanded: this.expanded ? 'true' : 'false',
      ariaHaspopup: this.hasPopup ? 'true' : 'false'
    };
  }
}

// React view
export const AWSButton: React.FC<AWSButtonProps> = (props) => {
  const model = useButtonModel(props);
  const a11y = model.getAccessibilityInfo();

  return (
    <button
      role={a11y.role}
      aria-label={a11y.ariaLabel}
      aria-disabled={a11y.disabled}
      aria-live={a11y.ariaLive}
      aria-atomic={a11y.ariaAtomic}
      aria-pressed={a11y.ariaPressed}
      aria-expanded={a11y.ariaExpanded}
      aria-haspopup={a11y.ariaHaspopup}
    >
      {props.label}
    </button>
  );
};
```

### 5. Focus Indicators

```typescript
// CSS for focus indicators (UI Designer requirement)
const getFocusStyle = (tokens: BaseDesignTokens): string => {
  return `
    outline: 3px solid ${tokens.colors.primary};
    outline-offset: 2px;
  `;
};

export const AWSButton: React.FC<AWSButtonProps> = (props) => {
  const tokens = useTokens();

  const styles: React.CSSProperties = {
    // Base styles
    ...getBaseStyles(tokens),

    // Focus visible (not on mouse click)
    '&:focus-visible': {
      outline: `3px solid ${tokens.colors.primary}`,
      outlineOffset: '2px'
    },

    // Remove default focus ring
    '&:focus': {
      outline: 'none'
    }
  };

  return <button style={styles}>{props.label}</button>;
};
```

### 6. Screen Reader Announcements

```typescript
// Use live regions for dynamic updates
export const AWSButton: React.FC<AWSButtonProps> = (props) => {
  const [announcement, setAnnouncement] = useState('');

  const handleClick = () => {
    props.onClick?.();

    // Announce action to screen readers
    setAnnouncement(`${props.label} activated`);
    setTimeout(() => setAnnouncement(''), 1000);
  };

  return (
    <>
      <button onClick={handleClick}>
        {props.label}
      </button>

      {/* Hidden live region for screen readers */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        style={{
          position: 'absolute',
          left: '-10000px',
          width: '1px',
          height: '1px',
          overflow: 'hidden'
        }}
      >
        {announcement}
      </div>
    </>
  );
};
```

---

## Factory Pattern

### Simplified Component Creation

**Component Architect Principle**:
> "Factories abstract complexity and provide convenient creation methods."

```typescript
// packages/analog-whimsy/src/factories/ButtonFactory.ts
import { AWSUIButton } from '../models/AWSUIButton';
import { AWSUIButtonSpecialized } from '../models/AWSUIButtonSpecialized';
import { BaseDesignTokens } from '@design-system/core/types';

export class ButtonFactory {
  constructor(private tokens: BaseDesignTokens) {}

  // Basic button
  createButton(label: string): AWSUIButton {
    const button = new AWSUIButton(this.tokens);
    button.setLabel(label);
    return button;
  }

  // Primary CTA
  createPrimaryCTA(label: string): AWSUIButton {
    const button = this.createButton(label);
    button.setVariant('primary');
    button.setSize('lg');
    return button;
  }

  // Secondary button
  createSecondary(label: string): AWSUIButton {
    const button = this.createButton(label);
    button.setVariant('secondary');
    return button;
  }

  // Ghost button
  createGhost(label: string): AWSUIButton {
    const button = this.createButton(label);
    button.setVariant('ghost');
    return button;
  }

  // Specialized button with traits
  createGlowingButton(label: string, glowIntensity: number = 0.8): AWSUIButtonSpecialized {
    const button = new AWSUIButtonSpecialized(this.tokens);
    button.setLabel(label);
    button.enableGlow(glowIntensity);
    return button;
  }

  // Dark mode button
  createDarkModeButton(label: string): AWSUIButtonSpecialized {
    const button = new AWSUIButtonSpecialized(this.tokens);
    button.setLabel(label);
    button.enableDarkMode();
    return button;
  }

  // Compact button for dense UIs
  createCompactButton(label: string): AWSUIButtonSpecialized {
    const button = new AWSUIButtonSpecialized(this.tokens);
    button.setLabel(label);
    button.enableCompact();
    return button;
  }

  // Full-featured specialized button
  createFeatureButton(
    label: string,
    options: {
      glow?: boolean;
      glowIntensity?: number;
      darkMode?: boolean;
      compact?: boolean;
      animated?: boolean;
    } = {}
  ): AWSUIButtonSpecialized {
    const button = new AWSUIButtonSpecialized(this.tokens);
    button.setLabel(label);

    if (options.glow) {
      button.enableGlow(options.glowIntensity || 0.8);
    }
    if (options.darkMode) {
      button.enableDarkMode();
    }
    if (options.compact) {
      button.enableCompact();
    }
    if (options.animated) {
      button.enableAnimation('spring', 300);
    }

    return button;
  }
}

// Usage
const factory = new ButtonFactory(analogWhimsyTokens);

const primaryButton = factory.createPrimaryCTA('Get Started');
const glowingButton = factory.createGlowingButton('Hover Me', 1.0);
const compactButton = factory.createCompactButton('More');

const specialButton = factory.createFeatureButton('Advanced', {
  glow: true,
  glowIntensity: 0.9,
  darkMode: true,
  animated: true
});
```

### React Hook Factory

```typescript
// packages/analog-whimsy-react/src/hooks/useButtonFactory.ts
import { useMemo } from 'react';
import { ButtonFactory } from '@analog-whimsy/ui';
import { useTokens } from './useTokens';

export const useButtonFactory = () => {
  const tokens = useTokens();

  return useMemo(() => {
    return new ButtonFactory(tokens);
  }, [tokens]);
};

// Usage in components
export const MyComponent: React.FC = () => {
  const factory = useButtonFactory();

  const primaryButton = factory.createPrimaryCTA('Get Started');
  const compactButton = factory.createCompactButton('More Options');

  return (
    <div>
      <AWSButton model={primaryButton} />
      <AWSButton model={compactButton} />
    </div>
  );
};
```

---

## Complete Code Examples

### Example 1: Button Component (Complete)

**File Structure**:
```
packages/analog-whimsy/
├── src/
│   ├── models/
│   │   ├── AWSUIButton.ts              # Model (business logic)
│   │   └── AWSUIButtonSpecialized.ts   # Specialized with traits
│   ├── traits/
│   │   ├── GlowTrait.ts
│   │   ├── DarkModeTrait.ts
│   │   └── CompactTrait.ts
│   ├── factories/
│   │   └── ButtonFactory.ts
│   └── __tests__/
│       └── AWSUIButton.test.ts

packages/analog-whimsy-react/
├── src/
│   ├── components/
│   │   └── AWSButton.tsx               # React view
│   ├── hooks/
│   │   ├── useTokens.ts
│   │   └── useButtonFactory.ts
│   └── __tests__/
│       └── AWSButton.test.tsx
```

**Complete Implementation** (see previous sections for full code).

### Example 2: Slider Component

```typescript
// packages/analog-whimsy/src/models/AWSUISlider.ts
import { UISlider } from '@design-system/core';
import { BaseDesignTokens } from '@design-system/core/types';

export class AWSUISlider extends UISlider {
  private tokens: BaseDesignTokens;
  private value: number = 0;
  private min: number = 0;
  private max: number = 100;
  private step: number = 1;
  private orientation: 'horizontal' | 'vertical' = 'horizontal';

  constructor(tokens: BaseDesignTokens) {
    super();
    this.tokens = tokens;
  }

  setValue(value: number): void {
    this.value = Math.min(Math.max(value, this.min), this.max);
  }

  setRange(min: number, max: number): void {
    this.min = min;
    this.max = max;
  }

  setStep(step: number): void {
    this.step = step;
  }

  setOrientation(orientation: 'horizontal' | 'vertical'): void {
    this.orientation = orientation;
  }

  getTrackColor(): string {
    return this.tokens.colors.neutral300;
  }

  getThumbColor(): string {
    return this.disabled ? this.tokens.colors.neutral400 : this.tokens.colors.primary;
  }

  getActiveTrackColor(): string {
    return this.tokens.colors.primary;
  }

  getThumbSize(): number {
    return 20; // pixels
  }

  getTrackHeight(): number {
    return 4; // pixels
  }

  getValuePercentage(): number {
    return ((this.value - this.min) / (this.max - this.min)) * 100;
  }

  render(): void {
    console.log('Render slider', {
      value: this.value,
      percentage: this.getValuePercentage(),
      orientation: this.orientation
    });
  }

  getAccessibilityInfo(): AccessibilityInfo {
    return {
      role: 'slider',
      ariaValueMin: this.min,
      ariaValueMax: this.max,
      ariaValueNow: this.value,
      ariaOrientation: this.orientation,
      disabled: this.disabled
    };
  }
}

// packages/analog-whimsy-react/src/components/AWSSlider.tsx
import React, { useMemo, useCallback } from 'react';
import { AWSUISlider } from '@analog-whimsy/ui';
import { useTokens } from '../hooks/useTokens';

export interface AWSSliderProps {
  value: number;
  min: number;
  max: number;
  step?: number;
  onChange: (value: number) => void;
  orientation?: 'horizontal' | 'vertical';
  label?: string;
  disabled?: boolean;
}

export const AWSSlider: React.FC<AWSSliderProps> = ({
  value,
  min,
  max,
  step = 1,
  onChange,
  orientation = 'horizontal',
  label,
  disabled = false
}) => {
  const tokens = useTokens();

  const sliderModel = useMemo(() => {
    const model = new AWSUISlider(tokens);
    model.setRange(min, max);
    model.setStep(step);
    model.setOrientation(orientation);
    return model;
  }, [tokens, min, max, step, orientation]);

  sliderModel.setValue(value);
  sliderModel.setDisabled(disabled);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(e.target.value);
    onChange(newValue);
  }, [onChange]);

  const a11y = sliderModel.getAccessibilityInfo();

  const trackStyle: React.CSSProperties = {
    width: orientation === 'horizontal' ? '200px' : `${sliderModel.getTrackHeight()}px`,
    height: orientation === 'horizontal' ? `${sliderModel.getTrackHeight()}px` : '200px',
    backgroundColor: sliderModel.getTrackColor(),
    borderRadius: `${tokens.borderRadius.full}px`,
    position: 'relative'
  };

  const activeTrackStyle: React.CSSProperties = {
    width: orientation === 'horizontal' ? `${sliderModel.getValuePercentage()}%` : '100%',
    height: orientation === 'horizontal' ? '100%' : `${sliderModel.getValuePercentage()}%`,
    backgroundColor: sliderModel.getActiveTrackColor(),
    borderRadius: `${tokens.borderRadius.full}px`,
    position: 'absolute',
    [orientation === 'horizontal' ? 'left' : 'bottom']: 0
  };

  const thumbStyle: React.CSSProperties = {
    width: `${sliderModel.getThumbSize()}px`,
    height: `${sliderModel.getThumbSize()}px`,
    backgroundColor: sliderModel.getThumbColor(),
    borderRadius: '50%',
    position: 'absolute',
    [orientation === 'horizontal' ? 'left' : 'bottom']: `calc(${sliderModel.getValuePercentage()}% - ${sliderModel.getThumbSize() / 2}px)`,
    [orientation === 'horizontal' ? 'top' : 'right']: '50%',
    transform: orientation === 'horizontal' ? 'translateY(-50%)' : 'translateX(50%)',
    cursor: disabled ? 'not-allowed' : 'pointer',
    boxShadow: tokens.shadows.sm
  };

  return (
    <div>
      {label && <label>{label}</label>}
      <div style={trackStyle}>
        <div style={activeTrackStyle} />
        <div style={thumbStyle} />
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={handleChange}
          disabled={disabled}
          role={a11y.role}
          aria-valuemin={a11y.ariaValueMin}
          aria-valuemax={a11y.ariaValueMax}
          aria-valuenow={a11y.ariaValueNow}
          aria-orientation={a11y.ariaOrientation}
          aria-label={label}
          style={{
            position: 'absolute',
            width: '100%',
            height: '100%',
            opacity: 0,
            cursor: disabled ? 'not-allowed' : 'pointer'
          }}
        />
      </div>
    </div>
  );
};
```

### Example 3: Audio Plugin Knob

```typescript
// packages/analog-whimsy/src/models/AWSUIKnob.ts
import { UIControl } from '@design-system/core';
import { BaseDesignTokens } from '@design-system/core/types';

export class AWSUIKnob extends UIControl {
  private tokens: BaseDesignTokens;
  private value: number = 0;
  private min: number = 0;
  private max: number = 1;
  private diameter: number = 60;
  private startAngle: number = -135; // degrees
  private endAngle: number = 135;   // degrees

  constructor(tokens: BaseDesignTokens) {
    super();
    this.tokens = tokens;
  }

  setValue(value: number): void {
    this.value = Math.min(Math.max(value, this.min), this.max);
  }

  setDiameter(diameter: number): void {
    this.diameter = diameter;
  }

  getKnobColor(): string {
    return this.tokens.colors.neutral800;
  }

  getIndicatorColor(): string {
    return this.tokens.colors.primary;
  }

  getValueAngle(): number {
    const percentage = (this.value - this.min) / (this.max - this.min);
    const angleRange = this.endAngle - this.startAngle;
    return this.startAngle + (angleRange * percentage);
  }

  getMaterial(): MaterialProperties | undefined {
    // Use extracted material tokens
    return this.tokens.materials?.['brushed-metal'];
  }

  render(): void {
    const material = this.getMaterial();
    console.log('Render knob', {
      value: this.value,
      angle: this.getValueAngle(),
      material: material?.optical.gloss
    });
  }

  getAccessibilityInfo(): AccessibilityInfo {
    return {
      role: 'slider',
      ariaValueMin: this.min,
      ariaValueMax: this.max,
      ariaValueNow: this.value,
      ariaLabel: this.label || 'Rotary control',
      disabled: this.disabled
    };
  }
}
```

---

## Integration with Token System

### Token Flow Diagram

```
┌──────────────────────────────────────┐
│   Image Upload (UI Screenshot)       │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  Extraction System (30+ Extractors)  │
│  ├─ Foundation (colors, spacing)     │
│  ├─ Component (buttons, inputs)      │
│  └─ VisualStyle (materials, lighting)│
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│     Design Tokens (JSON/TypeScript)  │
│  {                                    │
│    colors: { primary: "#F15925" },   │
│    spacing: { md: 16 },              │
│    materials: { "enamel-gloss": {} } │
│  }                                    │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  Component Models (TypeScript)       │
│  class AWSUIButton {                 │
│    constructor(tokens) {}            │
│    getBackgroundColor() {            │
│      return this.tokens.colors.primary│
│    }                                  │
│  }                                    │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│     React Views (Thin Adapters)      │
│  <AWSButton label="Click" />         │
└──────────────────────────────────────┘
```

### Complete Integration Example

```typescript
// 1. Extract tokens from image
import { extractTokens } from './extractors';

const image = await loadImage('screenshot.png');
const tokens: BaseDesignTokens = await extractTokens(image);

// 2. Save to database
await saveStyleLibrary({
  name: 'My App Theme',
  package_name: '@my-app/theme',
  tokens: tokens
});

// 3. Generate component library
import { ButtonFactory } from '@my-app/theme';

const factory = new ButtonFactory(tokens);
const primaryButton = factory.createPrimaryCTA('Get Started');

// 4. Use in React app
import { TokenProvider } from '@my-app/theme-react';
import { AWSButton } from '@my-app/theme-react/components';

export const App = () => (
  <TokenProvider tokens={tokens}>
    <AWSButton label="Get Started" variant="primary" size="lg" />
  </TokenProvider>
);
```

---

## Summary

### Key Takeaways

**Architecture**:
- ✅ Three-tier inheritance (Generic → Themed → Specialized)
- ✅ Trait composition for infinite variants
- ✅ Model-view separation for platform agnosticism
- ✅ Token injection for explicit dependencies

**Best Practices**:
- ✅ Composition over inheritance
- ✅ TypeScript for type safety
- ✅ Comprehensive testing (unit, integration, visual)
- ✅ WCAG 2.1 AA accessibility minimum
- ✅ Performance optimization (memoization, code splitting)

**Component Architect Grade**: A (9/10)
**UI Designer Grade**: A (9/10)

### Next Steps

1. **Create starter repository** with example components
2. **Add Storybook** for interactive documentation
3. **Implement performance monitoring** (bundle size, render times)
4. **Set up CI/CD** with automated accessibility tests
5. **Generate additional components** (Input, Card, Modal, Navigation)

---

**Related Documentation**:
- [Token System Overview](TOKEN_SYSTEM.md)
- [Design Libraries Guide](DESIGN_LIBRARIES_GUIDE.md)
- [Generator & Export Guide](GENERATOR_EXPORT_GUIDE.md)
- [Token Schema Guide](TOKEN_SCHEMA_GUIDE.md)

**Last Updated**: 2025-11-11 | **Version**: 1.0 | **Status**: Complete
