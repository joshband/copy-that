/**
 * Token Type Registry
 *
 * Schema-driven configuration for all token types
 * Enables 80% code reuse across Color, Typography, Spacing, and future token types
 *
 * Pattern: Each token type defines its own tabs, filters, and visual components
 * The UI stays generic and renders based on this registry configuration
 */

import { FC, ComponentType } from 'react';
import { ColorToken } from '../types';

// Import existing color components
import { ColorPrimaryPreview } from '../components/ColorPrimaryPreview';
import { HarmonyVisualizer } from '../components/HarmonyVisualizer';
import { AccessibilityVisualizer } from '../components/AccessibilityVisualizer';
import { ColorNarrative } from '../components/ColorNarrative';

// Placeholder icon components (using simple div for now, can be replaced with proper icons)
const ColorIcon: FC = () => <div>{'🎨'}</div>;
const TypographyIcon: FC = () => <div>{'📝'}</div>;
const SpacingIcon: FC = () => <div>{'📐'}</div>;
const ShadowIcon: FC = () => <div>{'🌑'}</div>;

// Placeholder components for future token types
const PlaceholderComponent: FC<{ label: string }> = ({ label }) => (
  <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
    {label} - Coming Soon
  </div>
);

/**
 * Tab Configuration
 */
export interface TabConfig {
  name: string;
  component: ComponentType<any>;
}

/**
 * Filter Configuration
 */
export interface FilterConfig {
  key: string;
  label: string;
  values: string[];
}

/**
 * Complete Token Type Schema
 */
export interface TokenTypeSchema {
  name: string;
  icon: ComponentType;
  primaryVisual: ComponentType<{ token: Partial<ColorToken> }>;
  formatTabs: TabConfig[];
  playgroundTabs: TabConfig[];
  filters: FilterConfig[];
}

/**
 * Placeholder components for future enhancement
 */
const ColorFormatTab_RGB: FC = () => (
  <PlaceholderComponent label="RGB Format Tab" />
);
const ColorFormatTab_HSL: FC = () => (
  <PlaceholderComponent label="HSL Format Tab" />
);
const ColorFormatTab_Oklch: FC = () => (
  <PlaceholderComponent label="Oklch Format Tab" />
);

const ColorAdjuster: FC = () => (
  <PlaceholderComponent label="Color Adjuster" />
);
const TemperatureVisualizer: FC = () => (
  <PlaceholderComponent label="Temperature Visualizer" />
);
const SaturationVisualizer: FC = () => (
  <PlaceholderComponent label="Saturation Visualizer" />
);

// Typography placeholders
const TypographyVisual: FC<{ token: Partial<ColorToken> }> = ({ token: _token }) => {
  void _token; // Reserved for future use
  return <PlaceholderComponent label="Typography Visual" />;
};
const TypographyFormatTab_Tech: FC = () => (
  <PlaceholderComponent label="Technical Format" />
);
const TypographyFormatTab_Design: FC = () => (
  <PlaceholderComponent label="Design Format" />
);
const TypographyAdjuster: FC = () => (
  <PlaceholderComponent label="Typography Adjuster" />
);
const HierarchyVisualizer: FC = () => (
  <PlaceholderComponent label="Hierarchy Visualizer" />
);

// Spacing placeholders
const SpacingVisual: FC<{ token: Partial<ColorToken> }> = ({ token: _token }) => {
  void _token; // Reserved for future use
  return <PlaceholderComponent label="Spacing Visual" />;
};
const SpacingFormatTab_Pixel: FC = () => (
  <PlaceholderComponent label="Pixel Format" />
);
const SpacingFormatTab_Rem: FC = () => (
  <PlaceholderComponent label="REM Format" />
);
const SpacingAdjuster: FC = () => (
  <PlaceholderComponent label="Spacing Adjuster" />
);

/**
 * Token Type Registry
 *
 * Single source of truth for token type configurations
 * Used by generic components to render type-specific UIs
 */
export const tokenTypeRegistry: Record<string, TokenTypeSchema> = {
  color: {
    name: 'Color',
    icon: ColorIcon,
    primaryVisual: ColorPrimaryPreview,
    formatTabs: [
      { name: 'RGB', component: ColorFormatTab_RGB },
      { name: 'HSL', component: ColorFormatTab_HSL },
      { name: 'Oklch', component: ColorFormatTab_Oklch },
    ],
    playgroundTabs: [
      { name: 'Adjuster', component: ColorAdjuster },
      { name: 'Harmony', component: HarmonyVisualizer },
      { name: 'Accessibility', component: AccessibilityVisualizer },
      { name: 'Temperature', component: TemperatureVisualizer },
      { name: 'Saturation', component: SaturationVisualizer },
      { name: 'Education', component: ColorNarrative },
    ],
    filters: [
      {
        key: 'temperature',
        label: 'Temperature',
        values: ['warm', 'neutral', 'cool'],
      },
      {
        key: 'saturation',
        label: 'Saturation',
        values: ['vivid', 'saturated', 'moderate', 'muted', 'desaturated'],
      },
      {
        key: 'lightness',
        label: 'Lightness',
        values: ['very_dark', 'dark', 'medium', 'light', 'very_light'],
      },
      {
        key: 'harmony',
        label: 'Harmony',
        values: [
          'monochromatic',
          'analogous',
          'complementary',
          'split-complementary',
          'triadic',
          'tetradic',
        ],
      },
    ],
  },

  typography: {
    name: 'Typography',
    icon: TypographyIcon,
    primaryVisual: TypographyVisual,
    formatTabs: [
      { name: 'Technical', component: TypographyFormatTab_Tech },
      { name: 'Design', component: TypographyFormatTab_Design },
    ],
    playgroundTabs: [
      { name: 'Adjuster', component: TypographyAdjuster },
      { name: 'Hierarchy', component: HierarchyVisualizer },
      { name: 'Preview', component: PlaceholderComponent },
    ],
    filters: [
      {
        key: 'fontFamily',
        label: 'Font Family',
        values: ['sans-serif', 'serif', 'monospace'],
      },
      {
        key: 'weight',
        label: 'Weight',
        values: ['300', '400', '500', '600', '700', '800'],
      },
      {
        key: 'size',
        label: 'Size Category',
        values: ['small', 'body', 'heading'],
      },
    ],
  },

  spacing: {
    name: 'Spacing',
    icon: SpacingIcon,
    primaryVisual: SpacingVisual,
    formatTabs: [
      { name: 'Pixel', component: SpacingFormatTab_Pixel },
      { name: 'REM', component: SpacingFormatTab_Rem },
    ],
    playgroundTabs: [
      { name: 'Adjuster', component: SpacingAdjuster },
      { name: 'Scale', component: PlaceholderComponent },
      { name: 'Preview', component: PlaceholderComponent },
    ],
    filters: [
      {
        key: 'unit',
        label: 'Unit',
        values: ['px', 'rem', 'em'],
      },
      {
        key: 'range',
        label: 'Range',
        values: ['xs', 'sm', 'md', 'lg', 'xl'],
      },
    ],
  },

  shadow: {
    name: 'Shadow',
    icon: ShadowIcon,
    primaryVisual: PlaceholderComponent as ComponentType<any>,
    formatTabs: [{ name: 'CSS', component: PlaceholderComponent }],
    playgroundTabs: [{ name: 'Adjuster', component: PlaceholderComponent }],
    filters: [
      {
        key: 'elevation',
        label: 'Elevation',
        values: ['subtle', 'medium', 'prominent'],
      },
    ],
  },

  animation: {
    name: 'Animation',
    icon: () => <div>{'✨'}</div>,
    primaryVisual: PlaceholderComponent as ComponentType<any>,
    formatTabs: [{ name: 'Timing', component: PlaceholderComponent }],
    playgroundTabs: [{ name: 'Preview', component: PlaceholderComponent }],
    filters: [
      {
        key: 'type',
        label: 'Type',
        values: ['entrance', 'exit', 'attention'],
      },
    ],
  },
};

/**
 * Helper functions for working with the registry
 */

export function getTokenTypeSchema(tokenType: string): TokenTypeSchema | undefined {
  return tokenTypeRegistry[tokenType];
}

export function isValidTokenType(tokenType: string): boolean {
  return tokenType in tokenTypeRegistry;
}

export function getAllTokenTypes(): string[] {
  return Object.keys(tokenTypeRegistry);
}

export function getFormatTabs(tokenType: string): TabConfig[] {
  const schema = getTokenTypeSchema(tokenType);
  return schema?.formatTabs ?? [];
}

export function getPlaygroundTabs(tokenType: string): TabConfig[] {
  const schema = getTokenTypeSchema(tokenType);
  return schema?.playgroundTabs ?? [];
}

export function getFilters(tokenType: string): FilterConfig[] {
  const schema = getTokenTypeSchema(tokenType);
  return schema?.filters ?? [];
}
