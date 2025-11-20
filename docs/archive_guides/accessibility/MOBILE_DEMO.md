# 📱 Mobile Demo - Comprehensive Token System

Mobile-optimized visualization of the comprehensive token extraction system, designed specifically for iPhone and mobile devices.

## Features

### 🎨 Visual Token Showcase
- **12 Interactive Categories**: All foundation and comprehensive token categories
- **Touch-Friendly Cards**: Large tap targets optimized for mobile
- **Beautiful Gradients**: Each category has a unique color gradient
- **Smooth Animations**: Native-feeling transitions and interactions

### 📱 Mobile-First Design
- **Responsive Grid**: Adapts from 1 to 3 columns based on screen size
- **Sticky Header**: Navigation stays accessible while scrolling
- **Dark Theme**: Optimized for OLED displays
- **Safe Areas**: Respects iPhone notches and rounded corners

### 🚀 Interactive Navigation
- **Grid View**: Browse all token categories
- **Detail View**: Deep dive into each category
- **Swipe-Friendly**: Natural mobile navigation patterns
- **Quick Actions**: Direct links to extraction tool

## Accessing the Demo

### On Your iPhone

1. **Local Development**:
   ```
   http://localhost:5173/mobile
   ```

2. **On Your Network**:
   - Find your computer's IP: `ipconfig getifaddr en0` (Mac) or `ipconfig` (Windows)
   - Access from iPhone: `http://YOUR_IP:5173/mobile`

3. **Add to Home Screen**:
   - Open in Safari
   - Tap Share button
   - Select "Add to Home Screen"
   - Access like a native app!

### On Desktop
The mobile demo also works great on desktop browsers:
```
http://localhost:5173/mobile
```

## Token Categories

### Foundation Tokens (5)
1. **Colors** - Semantic color tokens with AI-generated names
2. **Spacing** - Layout spacing with usage guidance
3. **Shadows** - Elevation levels with semantic names
4. **Typography** - Type hierarchy with design intent
5. **Radius** - Corner rounding with style intent

### Comprehensive Tokens (7)
6. **Materials** - Material properties (gloss, reflectivity)
7. **Lighting** - Light sources and volumetric effects
8. **Environment** - Scene context and atmosphere
9. **Motion** - Animation durations and easings
10. **Art Style** - Visual treatment and dimensionality
11. **Cinematic** - Camera properties and depth of field
12. **Composites** - Pre-built token combinations

## UI Components

### Grid View
- **Category Cards**: Touch-friendly cards with gradients
- **Foundation Section**: Core design system building blocks
- **Comprehensive Section**: Advanced perceptual properties
- **Stats Grid**: System statistics (15 categories, 3 AI models, 100+ properties)
- **CTA Section**: Call-to-action to try extraction

### Detail View
- **Category Header**: Large icon with gradient background
- **Examples List**: Token naming examples with color dots
- **How It Works**: 3-step process explanation
- **Action Button**: Direct link to extraction tool

## Design System

### Colors
- **Primary Gradient**: `#646cff → #535bf2`
- **Background**: `#0a0a0a → #1a1a2e`
- **Cards**: Unique gradient per category

### Typography
- **Headings**: System font stack, -apple-system, BlinkMacSystemFont
- **Body**: 0.9375rem (15px) for optimal mobile readability
- **Monospace**: Monaco, Courier New for token examples

### Spacing
- **Grid Gap**: 1rem (mobile), 1.5rem (tablet+)
- **Card Padding**: 1.5rem top/bottom, 1rem left/right
- **Section Margin**: 3rem between sections

### Touch Targets
- **Minimum Size**: 44x44px (Apple HIG)
- **Category Cards**: 140px min-height
- **Buttons**: 1rem padding (16px) for comfortable tapping

## Performance

### Optimizations
- **No Images**: Pure CSS gradients and SVG icons
- **Minimal JS**: Static data, no API calls on initial load
- **CSS Animations**: Hardware-accelerated transforms
- **Lazy Loading**: Icons loaded on demand via lucide-react

### Bundle Size
- **Component**: ~8KB (gzipped)
- **CSS**: ~3KB (gzipped)
- **Icons**: ~2KB per icon (lazy loaded)

## Browser Support

### iOS Safari (Primary Target)
- ✅ iOS 14+ fully supported
- ✅ Safe area insets
- ✅ Touch events
- ✅ Add to Home Screen

### Other Mobile Browsers
- ✅ Chrome Mobile
- ✅ Firefox Mobile
- ✅ Edge Mobile
- ✅ Samsung Internet

### Desktop (Bonus)
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Development

### File Structure
```
frontend/src/pages/
├── MobileDemo.tsx      # Main component
└── MobileDemo.css      # Mobile-optimized styles
```

### Running Locally
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173/mobile on your iPhone
```

### Testing on iPhone
1. Start dev server with network access:
   ```bash
   npm run dev -- --host
   ```

2. Find your IP address:
   ```bash
   # Mac
   ipconfig getifaddr en0

   # Windows
   ipconfig
   ```

3. Access from iPhone:
   ```
   http://YOUR_IP:5173/mobile
   ```

## Future Enhancements

### Planned Features
- [ ] Live token extraction preview
- [ ] Swipeable category carousel
- [ ] Haptic feedback on interactions
- [ ] Dark/light mode toggle
- [ ] Share token examples
- [ ] Camera integration for direct photo upload
- [ ] Offline support with Service Worker

### Accessibility
- [ ] VoiceOver optimization
- [ ] Increased contrast mode
- [ ] Larger text support
- [ ] Reduced motion preferences
- [ ] Keyboard navigation

## Related Routes

- `/` - Main extraction interface
- `/mobile` - Mobile demo (this page)
- `/demo` - Foundation tokens demo
- `/demo/comprehensive` - Comprehensive taxonomy showcase
- `/extract/comprehensive` - Interactive extraction tool

## Support

For issues or questions:
- GitHub Issues: [copy-this/issues](https://github.com/joshband/copy-this/issues)
- Tag: `#mobile-demo` `#comprehensive-tokens`

---

Built with ❤️ for mobile-first design token exploration
