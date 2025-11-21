# Export Formats Example

Examples of content returned by `/api/v1/sessions/{session_id}/library/export?format=...`.

## W3C JSON
```json
{
  "color": {
    "brand-primary": { "value": "#FF5733" },
    "brand-accent": { "value": "#0066FF" }
  }
}
```

## CSS Variables
```css
:root {
  --color-brand-primary: #ff5733;
  --color-brand-accent: #0066ff;
}
```

## React (TypeScript)
```ts
export const tokens = {
  colors: {
    brandPrimary: "#FF5733",
    brandAccent: "#0066FF",
  },
} as const;
```

## HTML Demo (snippet)
```html
<div class="color-swatch" style="background:#FF5733">Brand Primary</div>
<div class="color-swatch" style="background:#0066FF">Brand Accent</div>
```

Notes:
- Formats supported: `w3c`, `css`, `react`, `html`.
- For non-color tokens (future), extend generator logic in `src/copy_that/generators/*`.
