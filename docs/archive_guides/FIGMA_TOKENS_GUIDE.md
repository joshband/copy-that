# Enhanced Figma Tokens Export Guide

## What's New

The Figma export has been enhanced to output **W3C DTCG (Design Tokens Community Group)** format, which is the official standard supported by the **Figma Tokens (Tokens Studio)** plugin.

## Key Improvements

### 1. **W3C DTCG Format**
Every token now includes proper metadata:
```json
{
  "primary": {
    "$value": "#F15925",
    "$type": "color",
    "$description": "Primary brand color"
  }
}
```

### 2. **Semantic Token References Preserved**
Token references like `{orange.500}` are preserved in the export:
```json
{
  "semantic": {
    "brand": {
      "primary": {
        "$value": "{orange.500}",
        "$type": "color"
      }
    }
  }
}
```

When imported into Figma Tokens plugin, these references will be automatically resolved, creating a proper token hierarchy.

### 3. **Proper Token Types**
All tokens are correctly typed:
- **color** - Color values (hex, rgb, hsl)
- **dimension** - Spacing, border radius, breakpoints (with px units)
- **shadow** - Box shadow definitions
- **fontFamily** - Font family names
- **fontWeight** - Font weight values
- **duration** - Animation durations (ms)
- **cubicBezier** - Easing functions

### 4. **Complete Token Coverage**
The export includes:
- ✅ Primitive color scales (orange.50-900, teal.50-900, etc.)
- ✅ Semantic tokens (brand, ui, feedback, text, component)
- ✅ Spacing scale (xs, sm, md, lg, xl, xxl)
- ✅ Border radius (sm, md, lg)
- ✅ Shadows (level0-level5)
- ✅ Typography (family, weights)
- ✅ Animation (duration, easing)
- ✅ Breakpoints (compact, standard, studio, cinema)
- ✅ Grid system (base, margin)

## Export Files

When you export to Figma format, you'll get:

1. **`tokens.json`** - W3C DTCG format (recommended)
2. **`tokens-legacy.json`** - Legacy format for compatibility
3. **`README.md`** - Import instructions

## How to Import into Figma

### Option 1: Figma Tokens Plugin (Recommended)

1. **Install the plugin**
   - Open Figma
   - Go to Plugins → Browse plugins in Community
   - Search for "Tokens Studio for Figma"
   - Click Install

2. **Import your tokens**
   - Open your Figma file
   - Run the plugin: Plugins → Tokens Studio
   - Click **Settings** (gear icon)
   - Click **Import** → **From File**
   - Select your `tokens.json` file
   - Click **Import**

3. **What happens**
   - Color styles are created automatically
   - Semantic tokens reference primitive tokens
   - You can switch themes by toggling token sets
   - Variables are created in Figma's local variables panel

### Option 2: Figma Variables (Native)

1. Open your Figma file
2. Open the **Local variables** panel (right sidebar)
3. Click **Create variable**
4. Choose **Import from JSON**
5. Paste the contents of `tokens.json`
6. Figma will create variable collections

**Note:** Native Figma variables have limited support for token types. The Figma Tokens plugin provides better support for the full DTCG spec.

## Example: Understanding Token References

Your export includes a hierarchical token structure:

```json
{
  "primitive": {
    "orange": {
      "500": {
        "$value": "#F15925",
        "$type": "color"
      }
    }
  },
  "semantic": {
    "brand": {
      "primary": {
        "$value": "{orange.500}",
        "$type": "color"
      }
    }
  }
}
```

**Benefits:**
- Change `orange.500` once, all references update automatically
- Create theme variants by swapping primitive values
- Maintain design system consistency
- Document token relationships

## Token Organization

### Primitive Tokens (Base Layer)
The foundation of your design system:
- `orange.50` through `orange.900`
- `teal.50` through `teal.900`
- `yellow.50` through `yellow.900`
- `red.50` through `red.900`
- `gray.50` through `gray.900`

### Semantic Tokens (Application Layer)
Meaningful names that reference primitives:
- **brand** - Primary, secondary colors and states
- **ui** - Background, surface, border, overlay
- **feedback** - Success, warning, error, info
- **text** - Text colors for different contexts
- **component** - Component-specific tokens (button, slider, etc.)

## Advanced Features

### Creating Theme Variants

1. Export your base theme
2. In Figma Tokens plugin, create a new token set
3. Override primitive values for your new theme
4. Semantic tokens automatically adapt

Example:
```json
// Light theme
"orange": { "500": { "$value": "#F15925", "$type": "color" } }

// Dark theme
"orange": { "500": { "$value": "#FF7043", "$type": "color" } }

// brand.primary references orange.500 in both themes
```

### Using Token References in Design

In the Figma Tokens plugin, you can:
- Apply `brand.primary` to fill colors
- Apply `spacing.md` to auto-layout spacing
- Apply `radius.sm` to corner radius
- Apply `shadow.level2` to effects

All values update automatically when you change the source token.

## Troubleshooting

### Plugin not loading tokens?
- Make sure you're using `tokens.json` (W3C DTCG format)
- Check that the JSON is valid (use a JSON validator)
- Try the legacy format `tokens-legacy.json` if needed

### References not resolving?
- Ensure reference syntax uses curly braces: `{family.shade}`
- Check that the referenced token exists in the primitive layer
- Verify token names don't contain special characters

### Import button grayed out?
- You must have a Figma file open (not just the plugin)
- The file must be editable (not view-only)
- Try restarting the plugin

## Resources

- [Tokens Studio Documentation](https://docs.tokens.studio/)
- [W3C Design Tokens Spec](https://tr.designtokens.org/format/)
- [Figma Variables Guide](https://help.figma.com/hc/en-us/articles/15339657135383-Guide-to-variables-in-Figma)

## Next Steps

1. **Export your design** using the Figma format
2. **Install Figma Tokens plugin** in Figma
3. **Import** your `tokens.json` file
4. **Explore** the token hierarchy in the plugin
5. **Apply tokens** to your designs
6. **Create theme variants** by duplicating token sets

---

**Pro Tip:** Start by applying semantic tokens (like `brand.primary`) rather than primitive tokens (like `orange.500`) to your designs. This makes it easier to create theme variants later!
