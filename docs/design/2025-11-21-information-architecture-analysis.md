# Information Architecture & User Flow Analysis
## Copy That Application

**Analysis Date:** November 21, 2025

---

## Executive Summary

Copy That demonstrates a solid foundation for a design token extraction tool with excellent educational components. The token type registry provides good extensibility.

---

## 1. Content Organization

### Information Hierarchy

```
Copy That Application
├── Project (container)
│   ├── Session (batch extraction context)
│   │   ├── Images (source material)
│   │   └── Token Library (aggregated results)
│   └── Tokens (individual color items)
│       ├── Core Properties (hex, rgb, name)
│       ├── Analysis Data (harmony, temperature)
│       └── Accessibility Data (WCAG contrast)
```

### Issues
- `ColorToken` defined locally in 8+ components instead of importing
- Mixed terminology: "extraction" vs "colors"
- Unclear labeling: "Playground" vs "Adjuster" vs "Inspector"

---

## 2. User Flows

### Primary Journey

```
Empty State → Upload Image → Preview → Extract →
Grid Display → Select Token → Inspector → Edit → Export
```

### Dead Ends Identified

1. No export from main App.tsx (only in SessionWorkflow)
2. LearningSidebar exists but not integrated
3. Placeholder tabs show "Coming Soon"
4. BatchImageUploader only in SessionWorkflow

### Missing Flows

1. Token deletion confirmation
2. Undo/redo for edits
3. Save to server (currently local-only)
4. Project management (list, delete, rename)

---

## 3. Component Architecture

### Responsibility Distribution

| Component | Primary Responsibility | Complexity |
|-----------|------------------------|------------|
| App.tsx | Layout orchestration | Low |
| ImageUploader | File handling, API calls | High |
| TokenGrid | List rendering, filtering | Medium |
| TokenCard | Token display, actions | Medium |
| TokenInspectorSidebar | Detail display | Medium |

### Architecture Issues

**High Coupling:**
- ColorDetailPanel directly imports HarmonyVisualizer and AccessibilityVisualizer
- Makes testing and reuse difficult

**Low Cohesion:**
- ImageUploader handles file selection, validation, preview, API calls, streaming
- Should be split into focused components

---

## 4. Mental Model Alignment

### Design Tool Expectations

| Expectation | Implementation | Gap |
|-------------|----------------|-----|
| Undo/Redo | Not implemented | Critical |
| Save/Load projects | Local state only | Major |
| Keyboard shortcuts | Not implemented | Major |
| Multi-select | Not supported | Medium |

### Learning Curve

```
Difficulty Level: Medium-High
Time to First Success: 2-5 minutes
Time to Proficiency: 15-30 minutes
```

---

## 5. Navigation and Wayfinding

### Issues

- No onboarding or tutorial
- No sample data to explore
- Two separate workflows with no navigation between them
- No undo capabilities
- No keyboard navigation support

---

## 6. State Transitions

```
[Initial] → Empty
Empty → FileSelected → Previewing → Extracting
Extracting → Loaded | Error
Loaded → TokenSelected → Editing → TokenSelected
```

---

## 7. Recommendations

### High Priority

| Issue | Recommendation | Effort |
|-------|----------------|--------|
| Duplicate types | Consolidate to single import | Low |
| No undo/redo | Implement command pattern | High |
| Dead-end export | Add export to main App | Medium |
| No delete confirmation | Add modal | Low |

### Medium Priority

| Issue | Recommendation | Effort |
|-------|----------------|--------|
| Split workflows | Unify with routing | High |
| Placeholder features | Implement or remove | Medium |
| No keyboard navigation | Add comprehensive support | Medium |

---

## 8. Implementation Roadmap

### Phase 1: Foundation (1-2 weeks)
1. Consolidate ColorToken types
2. Remove console.log statements
3. Add environment variable for API URL
4. Add delete confirmation modal

### Phase 2: Core UX (2-4 weeks)
1. Add export to main App
2. Implement undo for token edits
3. Add keyboard navigation
4. Integrate LearningSidebar

### Phase 3: Advanced (4-8 weeks)
1. Unify App and SessionWorkflow
2. Complete placeholder features
3. Add onboarding
4. Full undo/redo stack

---

## Conclusion

**Key Strengths:**
- Rich color analysis and accessibility data
- Educational content (HarmonyVisualizer, ColorNarrative)
- Schema-driven component architecture
- Clean Zustand state management

**Critical Improvements:**
1. Consolidate duplicate type definitions
2. Add undo/redo capabilities
3. Unify workflow paradigms
4. Add export to main flow
5. Implement keyboard navigation
