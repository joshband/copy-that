# Copy That: Generative UI System Architecture

**Date:** 2025-12-10
**Primary Purpose:** Ingest visual designs (Midjourney, Figma, etc.) → Extract design tokens → Generate production-ready code for ANY framework
**Status:** Vision document + implementation roadmap

---

## Core Premise

**Copy That is an AI-powered visual → code generator that uses design tokens as the intermediate representation (IR).**

```
Midjourney UI Image
    ↓
┌─────────────────────────────────────┐
│   CV/ML Token Extraction (Frontend) │  ← Fast, local analysis (ms)
│   - Colors (K-means)                │
│   - Spacing (SAM segmentation)      │
│   - Typography (CLIP)               │
│   - Layout (bbox, positioning)      │
└──────────┬──────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│      TokenGraph (Graph IR)          │  ← Central data structure
│   - Tokens + Relationships          │
│   - Semantic meaning                │
│   - Aliasing, composition           │
└──────────┬──────────────────────────┘
           ↓
        (AI Enrichment - optional, async)
        Claude analysis for semantic naming,
        design patterns, accessibility
           ↓
┌─────────────────────────────────────┐
│   Generator Module (Pick One)       │
│   ├─ React Generator                │
│   ├─ Tauri Generator                │
│   ├─ JUCE Generator                 │
│   ├─ Flutter Generator              │
│   ├─ Figma Generator                │
│   └─ W3C Export                     │
└──────────┬──────────────────────────┘
           ↓
    Production-Ready Code
```

---

## Your Historical Architecture (What Worked)

You had a **3-layer async/streaming approach** that was excellent:

```
Layer 1: Frontend (Fast, Local) - ms
├─ WebGL/Canvas rendering
├─ K-means color extraction
├─ SAM segmentation (quantized model)
├─ CLIP embeddings (onnx.js)
├─ Real-time progress visualization
└─ Results displayed immediately

Layer 2: Backend (Async Fallback) - seconds
├─ AI analysis (Claude)
├─ Semantic naming
├─ Design pattern recognition
├─ Accessibility analysis
└─ Enrichment only (doesn't block UI)

Layer 3: Code Generation (Can be offline)
├─ TokenGraph → Generator
├─ Multiple format outputs
└─ User downloads code
```

**Key insight:** User sees results in **milliseconds** (frontend CV), enrichment is **optional async**, generation is **on-demand**.

---

## Current Problem: Gap Between Vision & Code

The issue is the implementation moved to **backend-first** approach:

```
CURRENT (Wrong Direction):
Image Upload → Backend (wait...) → Response → Display
└─ User waits seconds for AI analysis before seeing anything
└─ Slow, blocking, bad UX

ORIGINAL (Correct):
Image Upload
├─ Frontend: K-means colors (ms) + display
├─ Frontend: SAM spacing (ms) + display
├─ Frontend: CLIP typography (ms) + display
├─ Backend: Claude semantic analysis (async)
│  └─ Updates display when ready
└─ Generation: On-demand (React/Tauri/etc.)
```

---

## Regenerated Architecture for YOUR System

### Layer 1: Visual Input (Any Source)

```
Supported Inputs:
├─ Midjourney renders (PNG/JPG)
├─ Figma exports
├─ Screenshots
├─ Hand-drawn mockups
├─ Existing app screenshots
└─ Any UI image
```

### Layer 2: Frontend CV Analysis (Client-Side, Streaming)

**These run instantly in browser. No backend needed for initial visualization.**

```typescript
// frontend/src/pages/design/ImageUpload.tsx
async function analyzeImage(imageFile: File) {
  // LAYER 1: Display image immediately
  preview.src = URL.createObjectURL(imageFile);

  // LAYER 2A: Extract colors (K-means, ~50ms)
  const colorExtractor = new ColorExtractor();
  for await (const color of colorExtractor.extractStream(image)) {
    addColorSwatch(color);  // Display as found
  }

  // LAYER 2B: Detect spacing (SAM, ~100ms)
  const spacingDetector = new SpacingDetector();
  for await (const spacing of spacingDetector.detectStream(image)) {
    drawSpacingRuler(spacing);  // Display as found
  }

  // LAYER 2C: Identify typography (CLIP, ~80ms)
  const typographyAnalyzer = new TypographyAnalyzer();
  for await (const typo of typographyAnalyzer.analyzeStream(image)) {
    addTypographyCard(typo);  // Display as found
  }

  // All done in ~300ms. User sees complete initial UI token library.
  return { colors, spacing, typography };
}
```

**Key: Streaming results means user sees results appearing in real-time, not waiting for batch completion.**

### Layer 3: TokenGraph (In-Memory Store)

The frontend stores everything in a **reactive TokenGraph**:

```typescript
// frontend/src/store/tokenGraphStore.ts (Zustand)
interface TokenGraphStore {
  // Graph state
  tokens: Map<string, Token>           // All tokens
  relations: TokenRelation[]           // Relationships
  selectedTokens: Set<string>          // UI selection

  // Operations
  addToken(token: Token): void
  addRelation(from: string, type: RelationType, to: string): void
  resolveAlias(tokenId: string): Token
  getTokensByType(type: TokenType): Token[]

  // UI State
  isLoading: boolean
  analysisProgress: number             // 0-100%
  selectedTab: "colors" | "spacing" | "typography" | "layout"

  // Export
  async generateCode(framework: "react" | "tauri" | "flutter"): Promise<string>
}
```

**This store can work entirely offline after initial frontend analysis.**

### Layer 4: Backend AI Enrichment (Async, Non-Blocking)

When user clicks a button or after initial analysis completes, **optional** backend enrichment:

```python
# backend/services/enrichment_service.py
class TokenEnrichmentService:
    """Optional: Enrich tokens with semantic meaning"""

    async def enrich_tokens(self, graph: TokenGraph) -> EnrichedTokenGraph:
        """Non-blocking enrichment - user already has basic tokens"""

        tasks = [
            self.analyze_semantics(graph),      # What is this color for?
            self.detect_design_patterns(graph),  # Material Design? Custom?
            self.analyze_accessibility(graph),   # WCAG compliance
            self.suggest_ramps(graph),           # Generate scales
        ]

        for task in asyncio.as_completed(tasks):
            enriched = await task
            emit_update(enriched)  # WebSocket update to frontend

        return enriched_graph
```

**User doesn't wait for this. Their tokens are already usable.**

### Layer 5: Code Generators (Framework-Specific)

**Pick ONE generator based on desired output:**

```
Generators:
├─ src/copy_that/generators/react/
│  └─ Generates React components + hooks + contexts
├─ src/copy_that/generators/tauri/
│  └─ Generates Tauri + Rust backend
├─ src/copy_that/generators/juce/
│  └─ Generates JUCE C++ audio UI
├─ src/copy_that/generators/flutter/
│  └─ Generates Flutter Dart widgets
├─ src/copy_that/generators/figma/
│  └─ Generates Figma components + library
└─ src/copy_that/generators/w3c/
   └─ Exports W3C design tokens
```

**Each generator:**
- Takes TokenGraph as input
- Returns production-ready code
- Can be run server-side or client-side

---

## Concrete Example: Midjourney Image → React App

### Step 1: User Uploads Image (Instant Feedback)

```typescript
// Frontend immediately shows:
// ✓ 8 colors extracted (with swatches)
// ✓ Spacing grid identified
// ✓ Typography detected (heading, body)
// ✓ Layout detected (sidebar, main, footer)
```

### Step 2: TokenGraph Built Locally

```python
Token(
  id="color/primary",
  type=TokenType.COLOR,
  value="#3498DB",
  attributes={
    "wcag_contrast": 4.5,
    "temperature": "cool",
    "harmony": "complementary",
    "usage": ["buttons", "links", "highlights"]
  }
)

Token(
  id="spacing/md",
  type=TokenType.SPACING,
  value=16,
  attributes={
    "semantic_role": "medium",
    "usage": ["component padding", "element gaps"]
  }
)
```

### Step 3: User Clicks "Generate React Code"

```typescript
// On frontend or backend
const generator = new ReactGenerator();
const code = await generator.generate(tokenGraph);

// Output:
// ├─ colors.ts (CSS variables)
// ├─ spacing.ts (responsive grid)
// ├─ typography.ts (font scales)
// ├─ Layout.tsx (main structure)
// ├─ Header.tsx (responsive header)
// ├─ Sidebar.tsx (navigation)
// ├─ Main.tsx (content area)
// ├─ styles.module.css (generated styles)
// └─ hooks.ts (custom hooks)
```

### Step 4: User Downloads & Runs

```bash
$ npm install
$ npm run dev
# App runs immediately with extracted design tokens!
```

---

## Why This Works Better Than Alternatives

| Approach | Speed | Accuracy | Customization | Cost |
|----------|-------|----------|----------------|------|
| **Copy That (TokenGraph)** | ms (CV) | Good | Excellent | Low |
| Figma plugin | Slow | Perfect | Limited | Medium |
| Manual Figma design | Very slow | Perfect | Perfect | High |
| Custom Transformer | Slow | Medium | Limited | High |
| Hand-coded | Very slow | Perfect | Perfect | Very high |

---

## Technical Stack (Recommended)

### Frontend (Client-Side)
- **CV Models:**
  - K-means: Native JS implementation (< 100KB)
  - SAM: ONNX.js quantized model (memory-efficient)
  - CLIP: ONNX.js embeddings (parallel processing)

- **Streaming:**
  - Web Workers (background processing)
  - ReadableStream (progressive results)
  - Zustand (state management)

- **Code Generation:**
  - Handlebars (template-based generation)
  - Prettier (code formatting)
  - Tree-sitter (AST parsing)

### Backend (Async Enrichment Only)
- **FastAPI** (async, streaming responses)
- **Claude API** (semantic analysis)
- **Pydantic** (validation)
- **WebSockets** (real-time updates)

### Generators
- **React:** TypeScript + Vite + Tailwind
- **Tauri:** Rust + SvelteKit
- **Flutter:** Dart 3
- **JUCE:** C++17
- **Figma:** Plugin API

---

## Implementation Phases

### Phase 1: Core Pipeline (Weeks 1-3)
```
✅ Frontend image upload
✅ K-means color extraction (streaming)
✅ SAM spacing detection (streaming)
✅ CLIP typography analysis (streaming)
✅ TokenGraph construction (client-side)
✅ Basic React generator
```

### Phase 2: Enrichment (Weeks 4-5)
```
✅ Backend AI enrichment (async)
✅ WebSocket updates
✅ Semantic naming
✅ Accessibility analysis
```

### Phase 3: Multi-Framework (Weeks 6-8)
```
✅ Tauri generator
✅ Flutter generator
✅ JUCE generator
✅ Figma plugin
```

### Phase 4: Production Ready (Weeks 9-10)
```
✅ Error handling
✅ Edge cases
✅ Performance optimization
✅ Testing & validation
```

---

## Why TokenGraph Is Critical For This

**TokenGraph enables the generator pattern:**

```python
# Generic generator
class BaseGenerator(ABC):
    @abstractmethod
    async def generate(self, graph: TokenGraph) -> CodeOutput:
        pass

# Framework-specific generators
class ReactGenerator(BaseGenerator):
    async def generate(self, graph: TokenGraph) -> ReactCode:
        # Access tokens generically
        colors = graph.get_tokens_by_type(TokenType.COLOR)
        spacing = graph.get_tokens_by_type(TokenType.SPACING)
        typography = graph.get_tokens_by_type(TokenType.TYPOGRAPHY)

        # Generate React
        return ReactCode(colors, spacing, typography)

class FlutterGenerator(BaseGenerator):
    async def generate(self, graph: TokenGraph) -> FlutterCode:
        # Same token access, different output
        colors = graph.get_tokens_by_type(TokenType.COLOR)
        spacing = graph.get_tokens_by_type(TokenType.SPACING)

        # Generate Flutter
        return FlutterCode(colors, spacing)
```

**Without TokenGraph:** Each generator would duplicate token extraction logic
**With TokenGraph:** Tokens extracted once, used by ANY generator

---

## Current State Assessment

**What works:**
- ✅ Image ingestion
- ✅ Color extraction (K-means)
- ✅ FastAPI backend
- ✅ Some W3C export

**What needs rebuilding:**
- ❌ Frontend-first architecture (now backend-first)
- ❌ Streaming analysis (now batch)
- ❌ TokenGraph (described but not implemented)
- ❌ Multi-framework generators (only W3C partial)
- ❌ WebSocket enrichment (no async updates)

---

## Migration Strategy: Return to Frontend-First

### Phase 1: Enable Frontend Streaming (1-2 weeks)

```typescript
// Move K-means to frontend (Web Worker)
// Move SAM to frontend (ONNX.js)
// Move CLIP to frontend (parallel processing)
// Stream results as they complete
// Stop waiting for backend
```

### Phase 2: Build TokenGraph (1 week)

```python
# Implement TokenGraph
# Test graph operations
# Validate composition
```

### Phase 3: Build Generators (2-3 weeks)

```
One at a time:
1. React generator
2. Tauri generator
3. Flutter generator
```

### Phase 4: Optional Backend Enrichment (1 week)

```
Add async Claude analysis
WebSocket updates
Non-blocking enhancement
```

---

## Why This Is Better

**Before (current):**
1. User uploads image
2. Waits for backend analysis (3-5 seconds)
3. Sees tokens
4. Can export to W3C only

**After (your vision):**
1. User uploads image
2. Immediately sees tokens (300ms, frontend CV)
3. Can generate React/Tauri/Flutter instantly
4. Optionally enriches with AI (background)
5. Exports to any format

**User experience:** 16x faster initial response, more output formats, offline capability.

---

## Key Decision: Streaming vs Batch

**Streaming (Recommended):**
```typescript
// User sees results progressively
for await (const color of colorExtractor.extractStream(image)) {
  ui.addColorSwatch(color);  // Display immediately
}
// After ~100ms, all colors visible
```

**Batch (Current):**
```python
colors = colorExtractor.extract_all(image)  # Wait 3-5 seconds
return colors
# User stares at spinner
```

**Streaming gives users feedback and confidence the app is working. Batch makes them think it's broken.**

---

## Questions This Architecture Answers

**Q: Should we do CV on frontend or backend?**
A: Frontend for speed (ms). Backend enrichment is optional, async.

**Q: What about scaling?**
A: Frontend scales infinitely (client hardware). Backend only for optional analysis.

**Q: What about different UI frameworks?**
A: Each gets a generator. Tokens are shared.

**Q: Is TokenGraph overkill?**
A: No. It's essential for multi-framework generation and relationship management.

**Q: Why streaming instead of batch?**
A: UX. Users see something immediately vs waiting for black box.

---

**This is your actual product. The architecture should serve this vision, not generic token libraries.**
