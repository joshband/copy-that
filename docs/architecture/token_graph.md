# Token Graph Architecture

This document summarizes the lightweight token graph used by the CV-first control panel pipeline.

## Core Concepts

- **Token model (`core/tokens/model.py`)** – Minimal dataclass storing `id`, `type`, `value`, `attributes`, `relations`, and `meta`. All downstream systems operate on these normalized records.
- **Repositories (`core/tokens/repository.py`)** – `TokenRepository` describes CRUD + relation helpers; `InMemoryTokenRepository` is used for orchestration tests and the panel pipeline.
- **Adapters (`core/tokens/adapters/w3c.py`)** – Converts from repository contents to W3C Design Tokens JSON and vice versa so every export path flows through the same contract.

## CV + Layout Tooling

- **Preprocessing (`cv_pipeline/preprocess.py`)** – Loads an image, normalizes EXIF orientation, downsamples to <=1024px, and returns both Pillow + OpenCV views.
- **Primitive detection (`cv_pipeline/primitives.py`)** – Finds circles, rectangles, and lines via OpenCV. These feed the classifier.
- **Control classifier (`cv_pipeline/control_classifier.py`)** – Maps primitive geometry to semantic control types (knob/button/fader/etc.) via heuristics while staying model-ready.
- **Layout graph (`layout/layout_graph.py`)** – Wraps classifier instances into `ControlNode`s grouped by inferred rows/columns for downstream analysis.
- **Layout metrics (`layout/metrics.py`)** – Provides density/variance/regularity metrics that guide typography choices.

## Typography Layer

- **Recommender (`typography/recommender.py`)** – Inspects layout metrics, chooses a descriptor (classification, case style, sample families, etc.), and emits typography tokens that reference existing color tokens through `make_typography_token`.

## Panel Pipeline (`src/pipeline/panel_to_tokens.py`)

`process_panel_image(path)` orchestrates the full flow:

1. Preprocess image once (Pillow + OpenCV views).
2. Use `CVColorExtractor` to populate color tokens (`token/color/panel/**`).
3. Detect primitives → classify controls → build `PanelGraph`.
4. Compute layout metrics and feed them to the typography recommender.
5. Persist typography tokens referencing the detected color IDs.
6. Export all tokens via the W3C adapter. The resulting JSON includes `color` and `typography` sections and stays compatible with downstream tooling.

This architecture keeps extractors modular (colors, controls, typography), shares preprocessing work, and ensures every consumer interacts with a consistent token graph instead of bespoke dicts.

## Current Flow (Mermaid)

```mermaid
flowchart TD
    subgraph API
        COLORS[colors.py]
        SPACING[spacing.py]
        SESSIONS[sessions.py]
    end

    subgraph Mappers
        MAP[Token mappers<br/>(ORM -> Token)]
    end

    subgraph TokenGraph
        REPO[TokenRepository<br/>(InMemory/DB-backed)]
        ADAPTERS[Adapters<br/>W3C/custom]
    end

    subgraph CV
        PRE[cv_pipeline.preprocess]
        PRIMS[cv_pipeline.primitives]
        CV_COLOR[CV color extractor]
        CV_SPACING[CV spacing extractor]
    end

    API --> MAP --> REPO --> ADAPTERS
    CV_COLOR --> REPO
    CV_SPACING --> REPO
    PRE --> CV_COLOR
    PRE --> CV_SPACING
    PRIMS --> CV_SPACING

    subgraph Legacy
        LEGACY[copy_that.tokens.* (deprecated stubs)]
    end
    LEGACY -. to be removed after migration .- API
```

Legacy `copy_that.tokens.*` helpers are currently stubbed for compatibility and will be removed once all API/generator usages are migrated to the token graph and mappers.
