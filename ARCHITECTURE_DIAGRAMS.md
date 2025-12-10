# Copy That - Architecture Diagrams (Mermaid)

**Purpose:** Visual representation of key architecture concepts

---

## 1. High-Level System Flow: Image → Code

```mermaid
graph LR
    A["📷 UI Image<br/>(Midjourney/Figma)"] -->|Upload| B["Frontend CV<br/>(50ms)"]
    B -->|K-means| C["TokenGraph<br/>(in-memory)"]
    C -->|Display| D["✨ User Sees<br/>Colors/Spacing<br/>Typography"]

    C -->|Optional| E["Backend AI<br/>(async)"]
    E -->|Claude| F["Enriched<br/>TokenGraph"]

    D -->|User clicks| G["Generator<br/>(React/Tauri/Flutter)"]
    F -->|Also feeds| G

    G -->|Produces| H["📦 Production Code<br/>Components + Tokens"]
    H -->|Download| I["🚀 Ready to Use"]

    style A fill:#e1f5ff
    style D fill:#c8e6c9
    style I fill:#fff9c4
