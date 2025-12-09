# Token Graph Data Model Architecture - 2025-12-09

**Session:** Frontend Architecture Deep Dive
**Focus:** Token graph as the single source of truth for all token data
**Goal:** Ensure consistent graph-based representation across all features

---

## 🎯 Core Principle: Tokens as a Graph

**Philosophy:** Design tokens are not flat lists - they form a **directed graph** with relationships:

- **Aliases:** `{color.primary}` → references another token
- **Composition:** Shadows reference colors, Typography references fonts
- **Hierarchies:** Spacing scales reference base units
- **Dependencies:** Component tokens depend on primitive tokens

---

## 📊 Current Token Graph Implementation

### Token Graph Store (Zustand)

**Location:** `src/store/tokenGraphStore.ts`

```typescript
export interface TokenGraphState {
  loaded: boolean

  // Token collections (nodes)
  colors: UiColorToken[]
  spacing: UiSpacingToken[]
  shadows: UiShadowToken[]
  typography: UiTypographyToken[]
  layout: UiTokenBase<unknown>[]

  // Metadata
  typographyRecommendation?: {
    styleAttributes?: Record<string, string | number>
    confidence?: number | null
  }

  // Operations
  load: (projectId: number) => Promise<void>

  // Legacy adapters (for backwards compatibility)
  legacyColors: () => Array<...>
  legacySpacing: () => Array<...>
  legacyColorExtras: () => Record<...>
}
```

---

## 🔗 Token Node Types (Graph Nodes)

### Base Token Interface

```typescript
export interface UiTokenBase<T> {
  id: string                    // Node identifier
  category: TokenCategory       // Node type
  raw: T                        // W3C token data
}
```

### Color Token (Node with Alias Edges)

```typescript
export interface UiColorToken extends UiTokenBase<W3CColorToken> {
  category: 'color'
  isAlias: boolean              // Is this node an alias?
  aliasTargetId?: string        // Edge: points to target token
}
```

**Graph representation:**
```
color.primary (#FF0000)
         ↑
         │ alias edge
         │
color.button (#FF0000) [isAlias=true, aliasTargetId="color.primary"]
```

### Spacing Token (Node with Base Multiplier)

```typescript
export interface UiSpacingToken extends UiTokenBase<W3CSpacingToken> {
  category: 'spacing'
  baseId?: string               // Edge: points to base unit
  multiplier?: number           // Multiplier relationship
}
```

**Graph representation:**
```
spacing.base (8px)
         ↑
         │ base edge (multiplier=2)
         │
spacing.medium (16px) [baseId="spacing.base", multiplier=2]
```

### Shadow Token (Node with Color Dependencies)

```typescript
export interface UiShadowToken extends UiTokenBase<W3CShadowToken> {
  category: 'shadow'
  referencedColorIds: string[]  // Edges: depends on color tokens
}
```

**Graph representation:**
```
color.shadow (#000000)
         ↑
         │ color reference edge
         │
shadow.card [referencedColorIds=["color.shadow"]]
```

### Typography Token (Multi-Edge Node)

```typescript
export interface UiTypographyToken extends UiTokenBase<WCTypographyToken> {
  category: 'typography'
  referencedColorId?: string    // Edge: text color
  fontFamilyTokenId?: string    // Edge: font family
  fontSizeTokenId?: string      // Edge: font size
}
```

**Graph representation:**
```
color.text (#333333)  font.sans ("Inter")  spacing.md (16px)
         ↑                  ↑                     ↑
         └──────────────────┴─────────────────────┘
                            │
                   typography.body
                   [referencedColorId, fontFamilyTokenId, fontSizeTokenId]
```

---

## 🚨 Current Issues with Graph Usage

### Issue #1: Competing Data Models

**Problem:** 3 different token representations in the codebase

| Store | Location | Format | Graph Support |
|-------|----------|--------|---------------|
| **tokenGraphStore** | `store/tokenGraphStore.ts` | Graph nodes with edges | ✅ Yes |
| **tokenStore (legacy)** | `store/tokenStore.ts` | Flat array | ❌ No |
| **Local component state** | Various components | Ad-hoc | ❌ No |

**Example of confusion:**
```typescript
// App.tsx uses both!
const graphColors = useTokenGraphStore((s) => s.colors)  // Graph model
const legacyColors = useTokenStore((s) => s.tokens)      // Flat model

// Which one should components use?
```

**Impact:**
- ❌ Components don't know which store to use
- ❌ Graph relationships lost when using flat store
- ❌ Duplicated state synchronization logic

---

### Issue #2: Graph Relationships Not Visualized

**Problem:** Token dependencies hidden from users

**Missing visualizations:**
- Which colors are aliases?
- Which spacing tokens derive from base?
- Which shadows use which colors?
- Which typography tokens reference what?

**Current state:**
```typescript
// User sees flat list
colors: [
  { id: 'color.primary', hex: '#FF0000' },
  { id: 'color.button', hex: '#FF0000' },  // Same color, but why?
]

// Graph relationships hidden!
// color.button → alias → color.primary
```

---

### Issue #3: No Graph Query API

**Problem:** Components directly access arrays instead of querying graph

```typescript
// ❌ Current: Direct array access (no graph traversal)
const primaryColor = colors.find(c => c.id === 'color.primary')
const aliases = colors.filter(c => c.aliasTargetId === 'color.primary')

// ✅ Desired: Graph query API
const primaryColor = tokenGraph.getNode('color.primary')
const aliases = tokenGraph.getAliases('color.primary')
const dependencies = tokenGraph.getDependencies('shadow.card')
```

---

### Issue #4: W3C Token References Not Resolved

**Problem:** `{color.primary}` references stored as strings, not resolved

**Current:**
```typescript
// W3C token with reference
{
  "$type": "shadow",
  "$value": {
    "color": "{color.primary}",  // ❌ String reference
    "offsetX": "4px"
  }
}
```

**Desired:**
```typescript
// Resolved token with graph node
{
  id: "shadow.card",
  referencedColorIds: ["color.primary"],  // ✅ Resolved to node ID
  resolvedColor: "#FF0000"                // ✅ Resolved value
}
```

---

## 🎯 Proposed Graph-First Architecture

### 1. Single Source of Truth: Token Graph

```typescript
// New unified graph API
interface TokenGraph {
  // Node access
  getNode(id: string): TokenNode | null
  getNodes(category: TokenCategory): TokenNode[]
  getAllNodes(): TokenNode[]

  // Edge traversal
  getAliases(tokenId: string): TokenNode[]
  getDependencies(tokenId: string): TokenNode[]
  getDependents(tokenId: string): TokenNode[]

  // Graph queries
  getRootTokens(): TokenNode[]              // Tokens with no dependencies
  getLeafTokens(): TokenNode[]              // Tokens with no dependents
  getTokenPath(fromId: string, toId: string): TokenNode[]

  // Graph operations
  resolveAlias(tokenId: string): TokenNode  // Follow alias chain
  resolveReferences(token: TokenNode): TokenNode  // Resolve all {refs}

  // Graph analysis
  hasCycle(): boolean
  getStronglyConnectedComponents(): TokenNode[][]
  getTopologicalSort(): TokenNode[]
}
```

### 2. Feature Components Use Graph API

```typescript
// ✅ Color feature uses graph
function ColorPalette() {
  const graph = useTokenGraph()
  const colors = graph.getNodes('color')

  return colors.map(color => {
    const aliases = graph.getAliases(color.id)
    const dependents = graph.getDependents(color.id)

    return (
      <ColorCard
        color={color}
        aliases={aliases}
        usedBy={dependents}  // Shows which shadows/typography use this color
      />
    )
  })
}
```

### 3. Graph Visualization Components

```typescript
// New shared component
function TokenGraphVisualizer({ tokenId }: { tokenId: string }) {
  const graph = useTokenGraph()
  const node = graph.getNode(tokenId)
  const dependencies = graph.getDependencies(tokenId)
  const dependents = graph.getDependents(tokenId)

  return (
    <GraphView>
      <CenterNode token={node} />
      <DependencyEdges tokens={dependencies} />
      <DependentEdges tokens={dependents} />
    </GraphView>
  )
}
```

---

## 📐 Graph Data Model Best Practices

### Rule #1: Always Use Graph Store

❌ **Bad: Local state with flat arrays**
```typescript
function ColorList() {
  const [colors, setColors] = useState<ColorToken[]>([])  // ❌ Flat

  useEffect(() => {
    fetch('/api/colors').then(data => setColors(data))
  }, [])
}
```

✅ **Good: Graph store with relationships**
```typescript
function ColorList() {
  const graph = useTokenGraph()
  const colors = graph.getNodes('color')  // ✅ Graph-aware

  // Graph relationships available
  colors.forEach(color => {
    const aliases = graph.getAliases(color.id)
  })
}
```

### Rule #2: Resolve References Before Display

❌ **Bad: Show unresolved references**
```typescript
<ShadowCard shadow={shadow} />
// User sees: color: "{color.primary}"  ❌ Confusing
```

✅ **Good: Resolve references in UI**
```typescript
const resolvedShadow = graph.resolveReferences(shadow)
<ShadowCard shadow={resolvedShadow} />
// User sees: color: "#FF0000" (Primary)  ✅ Clear
```

### Rule #3: Show Graph Relationships in UI

❌ **Bad: Hide relationships**
```typescript
<ColorCard color={color} />
// No indication this color is an alias
```

✅ **Good: Visualize relationships**
```typescript
<ColorCard
  color={color}
  isAlias={color.isAlias}
  aliasTarget={graph.getNode(color.aliasTargetId)}
  usedBy={graph.getDependents(color.id)}
/>
// User sees: "Alias of Primary • Used in 3 shadows"
```

### Rule #4: Validate Graph Integrity

```typescript
// On token load, validate graph
function validateTokenGraph(graph: TokenGraph) {
  // Check for cycles
  if (graph.hasCycle()) {
    throw new Error('Token graph contains circular dependencies')
  }

  // Check for broken references
  graph.getAllNodes().forEach(node => {
    node.dependencies.forEach(depId => {
      if (!graph.getNode(depId)) {
        console.warn(`Broken reference: ${node.id} → ${depId}`)
      }
    })
  })
}
```

---

## 🗺️ Migration to Graph-First Architecture

### Phase 1: Enhance Token Graph Store (Week 1)

**Tasks:**
- [ ] Add graph query methods to tokenGraphStore
- [ ] Implement getAliases(), getDependencies(), getDependents()
- [ ] Add reference resolution logic
- [ ] Write tests for graph operations

**Deliverable:** Enhanced TokenGraph API

### Phase 2: Create Graph Hook (Week 1)

```typescript
// New hook for components
export function useTokenGraph() {
  const store = useTokenGraphStore()

  return {
    getNode: (id: string) => { /* ... */ },
    getNodes: (category: TokenCategory) => { /* ... */ },
    getAliases: (id: string) => { /* ... */ },
    getDependencies: (id: string) => { /* ... */ },
    getDependents: (id: string) => { /* ... */ },
    resolveReferences: (token: TokenNode) => { /* ... */ },
  }
}
```

**Tasks:**
- [ ] Create useTokenGraph hook
- [ ] Implement all graph query methods
- [ ] Add memoization for performance
- [ ] Document API with examples

**Deliverable:** `useTokenGraph()` hook ready for features

### Phase 3: Migrate Color Feature to Graph (Week 2)

**Tasks:**
- [ ] Update ColorPalette to use useTokenGraph()
- [ ] Add alias visualization
- [ ] Show "used by" relationships
- [ ] Remove legacy tokenStore usage

**Success Criteria:**
- ✅ Color feature only uses tokenGraphStore
- ✅ Aliases clearly marked in UI
- ✅ Dependencies visualized

### Phase 4: Add Graph Visualizer (Week 3)

**Tasks:**
- [ ] Create TokenGraphVisualizer component
- [ ] Use React Flow or similar library
- [ ] Show nodes and edges
- [ ] Interactive exploration (click to navigate)

**Deliverable:** Visual graph explorer in UI

### Phase 5: Migrate All Features (Week 4-5)

**Migrate in order:**
1. ✅ Color (already done)
2. Spacing
3. Typography
4. Shadows

**Remove:** Legacy tokenStore entirely

### Phase 6: Advanced Graph Features (Week 6)

**Optional enhancements:**
- [ ] Graph search (find tokens by query)
- [ ] Graph diffing (compare before/after)
- [ ] Graph export (for design tools)
- [ ] Graph import (from Figma/Sketch)

---

## 📊 Graph Data Model Benefits

### For Developers

✅ **Single source of truth** - One store, not three
✅ **Type-safe queries** - TypeScript knows graph structure
✅ **Easy refactoring** - Change store, components adapt
✅ **Better testing** - Mock graph, test components

### For Users

✅ **Understand relationships** - See token dependencies
✅ **Find usage** - "Where is this color used?"
✅ **Catch conflicts** - Circular dependencies highlighted
✅ **Better documentation** - Graph shows design system structure

### For Design System

✅ **Enforce consistency** - Aliases ensure single source
✅ **Track changes** - Graph diff shows impact
✅ **Validate integrity** - No broken references
✅ **Scale confidently** - Graph supports 1000s of tokens

---

## 🎯 Next Steps

1. **Review this document** with team
2. **Prioritize graph enhancements** (Phase 1-2)
3. **Migrate color feature first** (Phase 3)
4. **Add visualizer** (Phase 4)
5. **Migrate remaining features** (Phase 5)

---

## 📚 References

- **W3C Design Tokens Spec:** https://design-tokens.github.io/community-group/format/
- **Token References:** https://tr.designtokens.org/format/#aliases-references
- **Graph Theory:** Directed Acyclic Graph (DAG) for token dependencies

---

**Document Version:** 1.0
**Last Updated:** 2025-12-09
**Status:** Ready for Implementation
