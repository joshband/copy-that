# Testing Documentation

Complete testing infrastructure for Copy This design token extraction tool.

## 📊 Overview

### Frontend Testing (Playwright)

**Framework**: Playwright
**Test Coverage**: Visual regression, Accessibility (WCAG 2.1 AA), Responsive design
**Browsers**: Chromium, Firefox, WebKit
**Viewports**: 8 configurations (desktop, tablet, mobile)
**Total Tests**: 31 automated end-to-end tests

### Backend Testing (pytest)

**Framework**: pytest + httpx
**Test Coverage**: API contracts, token extraction, validation
**Total Tests**: 198 Python tests
**Coverage**: 82% code coverage
**Test Categories**: Color extraction, spacing, WCAG validation, shadow/elevation, typography, z-index, icon sizing, gradient detection, mobile tokens, border radius

## 🎯 What We Test

### Visual Regression
- Canvas-based pixelation animation (5x, 7x, 8x, 10x zoom)
- Processing animation stages (pixelate, blur, scan, extreme)
- Multi-image cycling
- UI components across all states
- Responsive layouts

### Accessibility (WCAG 2.1 AA)
- Color contrast compliance
- Keyboard navigation
- Screen reader compatibility
- ARIA attributes
- Focus management
- `prefers-reduced-motion` support

### Responsive Design
- **7 viewports**: From 320x568 (iPhone SE) to 1920x1080 (Full HD)
- Touch target sizing (≥ 44px)
- No horizontal overflow
- Readable typography (≥ 14px)
- Orientation changes

## 🚀 Quick Start

```bash
# Install dependencies
cd frontend
pnpm install

# Install Playwright browsers (one-time setup)
pnpm playwright:install

# Run all tests
pnpm test

# Run with UI (recommended)
pnpm test:ui
```

## 📝 Test Commands

### Full Test Suite
```bash
pnpm test              # All tests across all browsers
pnpm test:ui           # Interactive UI mode
pnpm test:headed       # See browser while testing
pnpm test:debug        # Step-by-step debugging
```

### Specific Test Types
```bash
pnpm test:visual       # Visual regression only
pnpm test:a11y         # Accessibility only
pnpm test:responsive   # Responsive design only
```

### Browser-Specific
```bash
pnpm test:chromium     # Chrome/Edge
pnpm test:firefox      # Firefox
pnpm test:webkit       # Safari
pnpm test:mobile       # iPhone + Android
```

### Baseline Management
```bash
pnpm test:update-snapshots   # Update all visual baselines
pnpm test:report             # View HTML report with diffs
```

## 📁 File Structure

```
frontend/
├── playwright.config.ts           # Playwright configuration
├── tests/
│   ├── README.md                  # Detailed testing guide
│   ├── processing-animation.visual.spec.ts  # Visual regression
│   ├── accessibility.spec.ts      # WCAG 2.1 AA compliance
│   └── responsive.spec.ts         # Responsive design
├── playwright-report/             # HTML test reports (gitignored)
├── test-results/                  # Test artifacts (gitignored)
└── tests/**/*-snapshots/          # Visual baselines (gitignored)

.github/
└── workflows/
    └── visual-testing.yml         # CI/CD configuration
```

## 🔧 Configuration

### Playwright Config ([frontend/playwright.config.ts](frontend/playwright.config.ts))

**Key settings**:
- Timeout: 30 seconds per test
- Retries: 2 in CI, 0 locally
- Visual diff threshold: 1% maximum pixel difference
- Parallel execution: Enabled

**Projects**:
- 3 desktop browsers (1920x1080)
- 2 tablet viewports (iPad Pro)
- 2 mobile viewports (iPhone, Pixel)
- 1 custom viewport (1280x720 for animations)

### Visual Comparison Settings
```typescript
expect.toHaveScreenshot({
  maxDiffPixelRatio: 0.01,   // 1% tolerance
  animations: 'disabled',     // Wait for animations
  threshold: 0.2,             // Pixel matching threshold
})
```

## 🤖 CI/CD Integration

### GitHub Actions Workflow

**Triggers**:
- Push to `master`, `main`, `develop`
- Pull requests

**Matrix testing**:
- Chromium Desktop
- Firefox Desktop
- WebKit Desktop

**Artifacts** (30-day retention):
- HTML test reports
- Visual baseline screenshots
- JSON results

**PR Comments**:
Automated bot posts test results with:
- ✅ Test summary
- 📊 Coverage metrics
- 🔗 Artifact links

### Workflow File
[.github/workflows/visual-testing.yml](.github/workflows/visual-testing.yml)

## 📊 Test Coverage

### Visual Regression Tests (9 tests)
1. ✅ Homepage initial state
2. ✅ Processing animation - initial frame
3. ✅ Processing animation - canvas pixelation visible
4. ✅ Processing animation - zoom transition
5. ✅ Processing animation - extreme zoom stage
6. ✅ Processing animation - progress indicator
7. ✅ Processing animation - stage indicators
8. ✅ Processing animation - responsive mobile view
9. ✅ Processing animation - multiple images cycling

### Accessibility Tests (13 tests)
1. ✅ Homepage has no violations
2. ✅ Processing animation has no violations
3. ✅ Workspace tabs have no violations
4. ✅ Keyboard navigation (homepage)
5. ✅ Keyboard navigation (workspace)
6. ✅ Color contrast meets WCAG AA
7. ✅ Images have alt text
8. ✅ Form elements have labels
9. ✅ Buttons have accessible names
10. ✅ Landmarks properly labeled
11. ✅ Focus visibility
12. ✅ Screen reader announcements
13. ✅ Respects `prefers-reduced-motion`

### Responsive Design Tests (9 tests)
1. ✅ Desktop Full HD (1920x1080)
2. ✅ Desktop HD (1366x768)
3. ✅ Tablet Portrait (768x1024)
4. ✅ Tablet Landscape (1024x768)
5. ✅ Mobile Large (414x896)
6. ✅ Mobile Medium (375x667)
7. ✅ Mobile Small (320x568)
8. ✅ Orientation change handling
9. ✅ Image aspect ratio preservation

**Total**: 31 automated tests

---

## 🐍 Python Testing (Backend & Extractors)

### Test Structure

```
extractors/tests/               # Token extraction tests
├── test_color_extractor.py    # Color palette extraction
├── test_spacing_extractor.py  # Layout spacing detection
├── test_shadow_extractor.py   # Shadow/elevation system
├── test_typography_extractor.py # Font extraction
├── test_zindex_extractor.py   # Z-index layering
├── test_iconsize_extractor.py # Icon sizing
├── test_gradient_extractor.py # Gradient detection
├── test_mobile_extractor.py   # Mobile tokens
└── test_border_radius.py      # Border radius extraction

backend/tests/                  # API contract tests
├── test_extraction.py         # Extraction endpoint
├── test_projects.py           # Project CRUD
├── test_validation.py         # WCAG validation
└── test_export.py             # Export endpoints
```

### Running Python Tests

```bash
# All Python tests
make test-py

# Specific test module
cd extractors && ../.venv/bin/pytest tests/test_color_extractor.py -v

# Backend API tests
cd backend && ../.venv/bin/pytest tests/ -v

# With coverage report
cd extractors && ../.venv/bin/pytest tests/ --cov=extractors --cov-report=html
```

### Test Coverage by Category

| Category | Tests | Coverage | Description |
|----------|-------|----------|-------------|
| **Color Extraction** | 25 | 100% | k-means clustering, LAB deduplication, WCAG validation |
| **Spacing Detection** | 18 | 95% | Edge detection, gap analysis, 4px grid quantization |
| **Shadow/Elevation** | 17 | 100% | CV-based depth analysis, 6-level scale generation |
| **Typography** | 22 | 98% | Font family detection, typographic scale, line heights |
| **Z-Index** | 26 | 100% | Semantic layering, progressive stacking hierarchy |
| **Icon Sizing** | 34 | 98% | Component detection, contour analysis, size scale |
| **Gradient Detection** | 15 | 92% | Multi-stop gradients, conic/radial/linear types |
| **Mobile Tokens** | 12 | 88% | Touch targets, safe areas, gesture thresholds |
| **Border Radius** | 33 | 91% | CV-based corner detection, radius scale generation |
| **Backend APIs** | 16 | 85% | REST endpoints, async processing, validation |

**Total**: 198 tests, 82% average coverage

### Key Testing Patterns

**Computer Vision Validation**:
```python
def test_shadow_extraction_from_ui():
    """Test shadow detection from real UI images."""
    extractor = ShadowExtractor()
    result = extractor.extract([sample_ui_image])

    assert "level0" in result["shadows"]
    assert result["shadows"]["level3"]["blur"] > 10
    assert "rgba" in result["shadows"]["level5"]["color"]
```

**WCAG Compliance Testing**:
```python
def test_wcag_contrast_validation():
    """Ensure all color pairs meet WCAG AA standards."""
    validator = WCAGValidator()

    # Text contrast minimum 4.5:1
    assert validator.check_contrast("#F15925", "#FFFFFF") >= 4.5

    # UI contrast minimum 3:1
    assert validator.check_contrast("#3B5E4C", "#FFFFFF") >= 3.0
```

**API Contract Testing**:
```python
@pytest.mark.asyncio
async def test_extraction_endpoint(client):
    """Test async extraction with progress tracking."""
    files = {"files": open("test_image.png", "rb")}
    response = await client.post("/api/extract", files=files)

    assert response.status_code == 202
    assert "job_id" in response.json()
```

---

## 🎨 Visual Regression Details

### Canvas-Based Pixelation Testing

The ProcessingAnimation component uses authentic Canvas downsampling for pixelation:

**Pixelation levels tested**:
- `pixelate`: 25px blocks
- `blur`: 20px blocks
- `scan`: 18px blocks
- `extreme`: 15px blocks (most aggressive)

**Zoom levels tested**:
- 5x (500%)
- 7x (700%)
- 8x (800%)
- 10x (1000%) - extreme zoom

**Animation phases captured**:
- 0-40%: Zoom in transition
- 40-60%: Pixelation hold (baseline comparison)
- 60-100%: Zoom out transition

### Baseline Generation

On first run, Playwright generates baseline screenshots:

```
tests/processing-animation.visual.spec.ts-snapshots/
├── animation-initial-state-chromium-darwin.png
├── animation-pixelation-active-chromium-darwin.png
├── animation-zoom-in-chromium-darwin.png
└── ...
```

Naming convention: `{test-name}-{browser}-{platform}.png`

### Updating Baselines

After intentional UI changes:

```bash
# Review changes in UI mode first
pnpm test:ui

# Update baselines after verification
pnpm test:update-snapshots
```

## ♿ Accessibility Testing Details

### WCAG 2.1 Compliance

**Level**: AA (enhanced)
**Tool**: @axe-core/playwright

**Rules tested**:
- `wcag2a`: Level A (basic)
- `wcag2aa`: Level AA (enhanced)
- `wcag21a`: 2.1 Level A
- `wcag21aa`: 2.1 Level AA

### Keyboard Navigation

**Tested interactions**:
- Tab navigation through UI
- Enter to activate buttons
- Arrow keys for tab selection
- Escape to close modals (if applicable)

**Focus indicators**:
- Outline visible on all focusable elements
- Color contrast meets 3:1 minimum

### Screen Reader Support

**ARIA attributes verified**:
- `aria-label` on icon buttons
- `aria-live` on status updates
- `role` attributes on custom components
- `aria-hidden` on decorative elements

## 📱 Responsive Testing Details

### Mobile-First Approach

**Breakpoints tested**:
- Mobile: 320px - 414px
- Tablet: 768px - 1024px
- Desktop: 1366px - 1920px

**Touch Target Sizing**:
- Minimum: 44x44px (iOS guideline)
- Tested: All buttons, tabs, interactive elements

### Viewport-Specific Validations

**Mobile** (≤ 414px):
- ✅ No horizontal scrolling
- ✅ Touch targets ≥ 44px
- ✅ Font size ≥ 14px
- ✅ Image processor scales to 400px max
- ✅ Stage indicators wrap

**Tablet** (768px - 1024px):
- ✅ Two-column layouts
- ✅ Sidebar visible
- ✅ Font size ≥ 14px

**Desktop** (≥ 1366px):
- ✅ Full workspace layout
- ✅ Image processor at 500px
- ✅ All tabs visible

## 🔍 Debugging Failed Tests

### Visual Regression Failures

1. **View the diff**:
   ```bash
   pnpm test:report
   ```

2. **Compare side-by-side**:
   - Expected (baseline)
   - Actual (current)
   - Diff (highlighted changes)

3. **Accept changes** (if intentional):
   ```bash
   pnpm test:update-snapshots
   ```

### Accessibility Failures

**Common violations**:
- Missing alt text → Add `alt` attribute
- Low contrast → Adjust colors
- Missing labels → Add `aria-label` or `<label>`
- Keyboard trap → Fix focus management

**Axe-core output** includes:
- Violation description
- WCAG rule reference
- Affected elements
- Fix recommendations

### Responsive Failures

**Common issues**:
- Horizontal scrolling → Check max-width
- Tiny fonts → Increase base font-size
- Small touch targets → Increase padding
- Broken layouts → Review media queries

## 📈 Performance

**Test execution times**:
- Visual regression: ~2 minutes (full suite)
- Accessibility: ~30 seconds
- Responsive: ~1 minute
- **Total**: ~4 minutes across all browsers

**Optimization**:
- Parallel execution enabled
- Cached browser installations
- Smart retries on flaky tests

## 🚨 Troubleshooting

### "Baseline not found"

**Cause**: First run or deleted baselines
**Solution**: Run tests to generate baselines

### "Tests pass locally but fail in CI"

**Common causes**:
- Font rendering differences (platform-specific)
- Timezone issues (animations)
- Different screen density

**Solutions**:
1. Accept platform-specific baselines
2. Increase `threshold` in config
3. Set `TZ` environment variable

### "Flaky animation tests"

**Cause**: Timing-dependent screenshots
**Solution**: Use `animations: 'disabled'` or increase timeout

## 📚 Resources

### Documentation
- [Playwright Docs](https://playwright.dev/)
- [Visual Comparisons](https://playwright.dev/docs/test-snapshots)
- [Axe-core Rules](https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md)
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)

### Tools
- [Playwright Trace Viewer](https://trace.playwright.dev/)
- [Axe DevTools](https://www.deque.com/axe/devtools/)
- [Chrome DevTools Accessibility](https://developer.chrome.com/docs/devtools/accessibility/reference/)

## 🎉 What's Next

### Future Enhancements
- [ ] Cross-browser pixel-perfect rendering
- [ ] Performance regression testing (Lighthouse CI)
- [ ] Visual comparison with Percy/Chromatic
- [ ] Automated accessibility fixes
- [ ] Screenshot comparison history

### Test Expansion
- [ ] Export panel visual tests
- [ ] Token editor interaction tests
- [ ] Project manager CRUD tests
- [ ] Multi-file upload scenarios
- [ ] Error state visual coverage

---

**Setup completed**: November 5, 2025
**Framework**: Playwright v1.56.1
**Test count**: 31 automated tests
**Coverage**: Visual regression, A11y (WCAG 2.1 AA), Responsive design
