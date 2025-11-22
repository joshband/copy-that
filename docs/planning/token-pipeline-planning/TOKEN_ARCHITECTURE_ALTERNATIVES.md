# Token Architecture Alternatives: Loosely Coupled Parallel Processing

**Version:** 1.0 | **Date:** 2025-11-22 | **Status:** Architectural Exploration

This document explores architectural alternatives to the factory pattern for a token system that requires:
- Loose coupling between token types
- Parallel execution with independent instances
- Atomic token instances with multiple instantiations
- Relationship management across token types
- Flexibility and extensibility

---

## Problem Statement

The factory pattern, while providing code reuse, creates coupling through:
- Shared base classes
- Central registry
- Synchronized pipeline orchestration
- Tight inheritance hierarchies

**What we actually need:**
- Tokens that can run independently and in parallel
- Multiple instances of the same token type processing simultaneously
- Relationships between tokens (color influences typography, spacing relates to grid)
- Atomic operations that can fail independently
- Horizontal scalability

---

## Architectural Alternatives

### Option 1: Actor Model

Each token type is an independent **actor** with its own mailbox, state, and behavior.

```
┌─────────────────────────────────────────────────────────┐
│                    ACTOR SYSTEM                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Color   │  │ Spacing  │  │Typography│              │
│  │  Actor   │  │  Actor   │  │  Actor   │              │
│  │ Instance │  │ Instance │  │ Instance │              │
│  │    1     │  │    1     │  │    1     │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │             │             │                     │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐              │
│  │  Color   │  │ Spacing  │  │Typography│              │
│  │  Actor   │  │  Actor   │  │  Actor   │              │
│  │ Instance │  │ Instance │  │ Instance │              │
│  │    2     │  │    2     │  │    2     │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                          │
│  Message Bus (async, non-blocking)                      │
└─────────────────────────────────────────────────────────┘
```

**Benefits:**
- Complete isolation between actors
- Natural parallelism
- Fault tolerance (one actor failing doesn't affect others)
- Location transparency (can distribute across machines)

**Implementation (Python with `pykka` or `ray`):**

```python
import ray

@ray.remote
class ColorTokenActor:
    def __init__(self, config):
        self.config = config
        self.state = {}

    async def extract(self, image_data):
        # Completely independent extraction
        result = await self._do_extraction(image_data)
        return result

    async def get_relationships(self, other_token_refs):
        # Query other actors for relationship data
        results = await ray.get([
            ref.get_relationship_data.remote()
            for ref in other_token_refs
        ])
        return self._compute_relationships(results)

# Multiple instances running in parallel
color_actors = [ColorTokenActor.remote(config) for _ in range(5)]
spacing_actors = [SpacingTokenActor.remote(config) for _ in range(5)]

# All extract in parallel
futures = [actor.extract.remote(image) for actor in color_actors + spacing_actors]
results = ray.get(futures)
```

---

### Option 2: Event-Driven Architecture with Message Bus

Tokens communicate via events, completely decoupled.

```
┌─────────────────────────────────────────────────────────┐
│                   EVENT BUS (Redis/Kafka)                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Events: token.extracted, token.aggregated,             │
│          relationship.discovered, export.requested       │
│                                                          │
└────┬──────────────┬──────────────┬──────────────┬───────┘
     │              │              │              │
     ▼              ▼              ▼              ▼
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  Color  │   │ Spacing │   │  Typo   │   │Relation │
│ Service │   │ Service │   │ Service │   │ Service │
└─────────┘   └─────────┘   └─────────┘   └─────────┘
```

**Event Flow:**

```python
# Color service publishes event
await event_bus.publish("token.extracted", {
    "type": "color",
    "instance_id": "color_123",
    "tokens": [...],
    "image_id": "img_456"
})

# Spacing service subscribes and reacts
@event_bus.subscribe("token.extracted")
async def on_token_extracted(event):
    if event["type"] == "color":
        # Spacing can react to color extraction
        await compute_color_spacing_relationship(event)

# Relationship service listens to all extractions
@event_bus.subscribe("token.extracted")
async def on_any_extraction(event):
    await relationship_service.update_graph(event)
```

**Benefits:**
- Zero coupling between services
- Easy to add new token types (just subscribe to events)
- Natural audit trail
- Can scale each service independently

---

### Option 3: Entity-Component-System (ECS)

Separate data (components) from behavior (systems). Tokens are entities with attached components.

```
┌─────────────────────────────────────────────────────────┐
│                     ENTITY REGISTRY                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Entity: token_001                                       │
│  Components:                                             │
│    - ColorComponent { hex: "#FF5733", confidence: 0.95 } │
│    - RelationshipComponent { related_to: [...] }         │
│    - ProvenanceComponent { source_image: "img_1" }       │
│                                                          │
│  Entity: token_002                                       │
│  Components:                                             │
│    - SpacingComponent { value_px: 16, scale: "md" }      │
│    - RelationshipComponent { related_to: [...] }         │
│    - ProvenanceComponent { source_image: "img_1" }       │
│                                                          │
└─────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
       ┌──────────┐   ┌──────────┐   ┌──────────┐
       │Extraction│   │Aggregation│  │Relationship│
       │  System  │   │  System   │  │  System    │
       └──────────┘   └──────────┘   └──────────┘
```

**Implementation:**

```python
class Entity:
    def __init__(self, entity_id):
        self.id = entity_id
        self.components = {}

    def add_component(self, component):
        self.components[type(component).__name__] = component

    def get_component(self, component_type):
        return self.components.get(component_type.__name__)

# Components are pure data
@dataclass
class ColorComponent:
    hex: str
    rgb: tuple
    confidence: float

@dataclass
class SpacingComponent:
    value_px: int
    value_rem: float
    scale: str

@dataclass
class RelationshipComponent:
    related_entities: list[str]
    relationship_types: dict[str, str]

# Systems operate on entities with specific components
class ExtractionSystem:
    async def process(self, entities, world):
        # Process all entities that need extraction
        for entity in entities:
            if entity.has_pending_extraction():
                await self.extract(entity)

class RelationshipSystem:
    async def process(self, entities, world):
        # Find relationships between all entities
        for entity in entities:
            if entity.get_component(RelationshipComponent):
                await self.update_relationships(entity, world)
```

**Benefits:**
- Data and behavior completely separated
- Easy to add new components to existing entities
- Systems can process in parallel
- Very flexible composition

---

### Option 4: Microkernel / Plugin Architecture

Minimal core with plugins that can be loaded/unloaded dynamically.

```
┌─────────────────────────────────────────────────────────┐
│                    MICROKERNEL CORE                      │
│                                                          │
│  - Plugin loader                                         │
│  - Message routing                                       │
│  - Lifecycle management                                  │
│  - Shared state (optional)                              │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ Color   │  │ Spacing │  │  Typo   │  │ Custom  │    │
│  │ Plugin  │  │ Plugin  │  │ Plugin  │  │ Plugin  │    │
│  │         │  │         │  │         │  │         │    │
│  │ v1.2.0  │  │ v1.0.0  │  │ v0.9.0  │  │ v1.0.0  │    │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Plugin Contract:**

```python
class TokenPlugin(Protocol):
    """Minimal contract for token plugins"""

    name: str
    version: str

    async def initialize(self, kernel: Kernel) -> None:
        """Called when plugin loads"""
        ...

    async def extract(self, image_data: bytes) -> list[dict]:
        """Extract tokens from image"""
        ...

    async def aggregate(self, tokens: list[dict]) -> list[dict]:
        """Aggregate and deduplicate"""
        ...

    async def export(self, tokens: list[dict], format: str) -> str:
        """Export to format"""
        ...

    async def get_relationships(self, other_plugins: list[str]) -> dict:
        """Declare relationships with other plugins"""
        ...

    async def shutdown(self) -> None:
        """Called when plugin unloads"""
        ...
```

**Benefits:**
- Hot-reload plugins without restarting
- Version plugins independently
- Minimal core, maximum flexibility
- Easy third-party extensions

---

### Option 5: Saga Pattern with Orchestration

For complex workflows involving multiple token types.

```
┌─────────────────────────────────────────────────────────┐
│                   SAGA ORCHESTRATOR                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Saga: FullDesignSystemExtraction                       │
│                                                          │
│  Step 1: Extract colors (parallel instances)            │
│  Step 2: Extract spacing (parallel instances)           │
│  Step 3: Extract typography (parallel instances)        │
│  Step 4: Compute relationships (depends on 1,2,3)       │
│  Step 5: Aggregate all (depends on 4)                   │
│  Step 6: Export (depends on 5)                          │
│                                                          │
│  Compensation:                                           │
│  - If step 4 fails, retry with cached results           │
│  - If step 5 fails, rollback aggregation                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

```python
class DesignSystemExtractionSaga:
    async def execute(self, image_urls: list[str]):
        # Step 1-3: Parallel extraction
        color_task = self.extract_colors(image_urls)
        spacing_task = self.extract_spacing(image_urls)
        typo_task = self.extract_typography(image_urls)

        try:
            colors, spacings, typos = await asyncio.gather(
                color_task, spacing_task, typo_task
            )
        except ExtractionError as e:
            await self.compensate_extraction(e)
            raise

        # Step 4: Compute relationships
        try:
            relationships = await self.compute_relationships(
                colors, spacings, typos
            )
        except RelationshipError as e:
            # Can still proceed with partial results
            relationships = {}

        # Step 5-6: Aggregate and export
        result = await self.aggregate_and_export(
            colors, spacings, typos, relationships
        )

        return result

    async def compensate_extraction(self, error):
        """Rollback or cleanup on failure"""
        await self.cleanup_partial_results()
        await self.notify_failure(error)
```

---

## Recommended Hybrid Approach

Combine the best of multiple patterns:

### Architecture: Event-Driven Actors with Plugin Loading

```
┌─────────────────────────────────────────────────────────┐
│                    TOKEN RUNTIME                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Plugin Loader (Microkernel)                            │
│  ├── Load token plugins dynamically                     │
│  └── Version management                                 │
│                                                          │
│  Event Bus (Event-Driven)                               │
│  ├── token.extracting, token.extracted                  │
│  ├── relationship.discovered                            │
│  └── export.requested, export.completed                 │
│                                                          │
│  Actor Spawner (Actor Model)                            │
│  ├── Spawn multiple instances per token type            │
│  ├── Load balance across instances                      │
│  └── Fault isolation                                    │
│                                                          │
│  Relationship Graph (Separate Service)                  │
│  ├── Track relationships between all tokens             │
│  ├── Query relationships for export                     │
│  └── Bidirectional links                                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Token Instance Model

```python
@dataclass
class TokenInstance:
    """Atomic, independent token instance"""

    # Identity
    instance_id: str  # Unique per instance
    token_type: str   # "color", "spacing", etc.

    # State
    status: str  # "pending", "extracting", "complete", "failed"
    data: dict   # Token-specific data

    # Provenance
    source_image_id: str
    extraction_timestamp: datetime

    # Relationships (weak references)
    related_instance_ids: list[str]
    relationship_metadata: dict

    # Lifecycle
    created_at: datetime
    updated_at: datetime
    version: int  # For optimistic locking

class TokenInstanceManager:
    """Manages multiple instances of tokens"""

    async def spawn_instance(self, token_type: str, image_id: str) -> str:
        """Spawn a new token instance"""
        instance = TokenInstance(
            instance_id=generate_id(),
            token_type=token_type,
            status="pending",
            source_image_id=image_id,
            ...
        )
        await self.store.save(instance)
        await self.event_bus.publish("token.spawned", instance)
        return instance.instance_id

    async def get_instances(self, token_type: str) -> list[TokenInstance]:
        """Get all instances of a token type"""
        return await self.store.query(token_type=token_type)

    async def link_instances(self, id1: str, id2: str, relationship: str):
        """Create relationship between instances"""
        await self.relationship_graph.link(id1, id2, relationship)
        await self.event_bus.publish("relationship.created", {
            "from": id1, "to": id2, "type": relationship
        })
```

### Parallel Processing Model

```python
class ParallelTokenProcessor:
    """Process multiple token instances in parallel"""

    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.instance_manager = TokenInstanceManager()

    async def process_images(
        self,
        image_urls: list[str],
        token_types: list[str]
    ) -> dict[str, list[TokenInstance]]:
        """
        Process multiple images for multiple token types.

        Each (image, token_type) combination spawns an independent instance.
        All instances process in parallel.
        """

        # Spawn instances for all combinations
        tasks = []
        for image_url in image_urls:
            for token_type in token_types:
                task = self._process_one(image_url, token_type)
                tasks.append(task)

        # Run all in parallel with concurrency control
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Group by token type
        grouped = defaultdict(list)
        for result in results:
            if isinstance(result, TokenInstance):
                grouped[result.token_type].append(result)

        return dict(grouped)

    async def _process_one(
        self,
        image_url: str,
        token_type: str
    ) -> TokenInstance:
        """Process single image for single token type"""
        async with self.semaphore:
            # Spawn instance
            instance_id = await self.instance_manager.spawn_instance(
                token_type, image_url
            )

            # Get plugin for this token type
            plugin = self.plugin_loader.get(token_type)

            # Extract (atomic operation)
            try:
                tokens = await plugin.extract(image_url)

                # Update instance
                instance = await self.instance_manager.update(
                    instance_id,
                    status="complete",
                    data=tokens
                )

                # Publish event
                await self.event_bus.publish("token.extracted", {
                    "instance_id": instance_id,
                    "token_type": token_type,
                    "count": len(tokens)
                })

                return instance

            except Exception as e:
                # Mark as failed (atomic failure)
                await self.instance_manager.update(
                    instance_id,
                    status="failed",
                    error=str(e)
                )
                raise
```

### Relationship Management

```python
class RelationshipGraph:
    """
    Manages relationships between token instances.

    Relationships are:
    - Bidirectional (color -> spacing implies spacing -> color)
    - Typed (influences, derives_from, complements, etc.)
    - Weighted (strength of relationship)
    """

    def __init__(self):
        self.graph = nx.MultiDiGraph()  # NetworkX for graph operations

    async def link(
        self,
        from_id: str,
        to_id: str,
        relationship_type: str,
        weight: float = 1.0,
        metadata: dict = None
    ):
        """Create bidirectional relationship"""
        self.graph.add_edge(
            from_id, to_id,
            type=relationship_type,
            weight=weight,
            metadata=metadata or {}
        )
        # Bidirectional
        self.graph.add_edge(
            to_id, from_id,
            type=f"inverse_{relationship_type}",
            weight=weight,
            metadata=metadata or {}
        )

    async def get_related(
        self,
        instance_id: str,
        relationship_type: str = None,
        max_depth: int = 1
    ) -> list[str]:
        """Get related instances"""
        if max_depth == 1:
            edges = self.graph.edges(instance_id, data=True)
            if relationship_type:
                edges = [e for e in edges if e[2]['type'] == relationship_type]
            return [e[1] for e in edges]
        else:
            # BFS for deeper relationships
            return list(nx.bfs_tree(self.graph, instance_id, depth_limit=max_depth))

    async def get_relationship_strength(
        self,
        from_id: str,
        to_id: str
    ) -> float:
        """Get strength of relationship between two instances"""
        if self.graph.has_edge(from_id, to_id):
            return self.graph.edges[from_id, to_id]['weight']
        return 0.0

# Usage
graph = RelationshipGraph()

# Color token influences typography choices
await graph.link(
    "color_instance_1",
    "typography_instance_1",
    "influences",
    weight=0.8,
    metadata={"reason": "primary color affects heading color"}
)

# Spacing relates to grid system
await graph.link(
    "spacing_instance_1",
    "spacing_instance_2",
    "same_scale",
    weight=1.0,
    metadata={"scale": "8px_system"}
)
```

---

## Implementation Comparison

| Approach | Coupling | Parallelism | Relationships | Complexity |
|----------|----------|-------------|---------------|------------|
| Factory Pattern | High | Medium | Centralized | Low |
| Actor Model | None | Excellent | Message passing | Medium |
| Event-Driven | None | Excellent | Via events | Medium |
| ECS | None | Excellent | Components | Medium |
| Microkernel | Low | Good | Plugin contracts | Low |
| Hybrid | None | Excellent | Graph service | Medium |

---

## Recommendation

For your requirements (loosely coupled, parallel instances, relationships, atomic operations), I recommend the **Hybrid Approach** with:

1. **Plugin Architecture** - Load token types dynamically
2. **Actor-like Instances** - Each extraction is an independent instance
3. **Event Bus** - Communication without coupling
4. **Relationship Graph** - Separate service managing all relationships

This gives you:
- ✅ Zero coupling between token types
- ✅ Unlimited parallel instances
- ✅ Atomic operations with independent failure
- ✅ Bidirectional relationship tracking
- ✅ Easy to add new token types
- ✅ Can distribute across machines

---

## Next Steps

1. **Choose architecture** - Decide on approach
2. **Design instance model** - Define TokenInstance structure
3. **Design relationship model** - Define relationship types
4. **Design event schema** - Define event types and payloads
5. **Implement core runtime** - Plugin loader, event bus, instance manager
6. **Migrate color tokens** - First token type as proof of concept

Would you like me to expand on any of these approaches or create detailed implementation plans for the hybrid architecture?
