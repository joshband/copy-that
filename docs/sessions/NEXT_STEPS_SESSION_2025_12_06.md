# Shadow Extraction Pipeline - Next Steps & Implementation Roadmap

**Date:** 2025-12-06
**Status:** Implementation Complete ✅ Ready for Next Phase
**Branch:** `feat/missing-updates-and-validations` (pushed to remote)
**Commit:** `589c9af` - Complete shadow extraction pipeline implementation

---

## Executive Summary

The shadow extraction pipeline is fully implemented and operationalized. All 8 stages are functional with complete orchestration, artifact persistence, and visualization metadata. The system includes clear integration points for ML models and is ready for the next phase of development.

### What's Complete
✅ Complete 8-stage pipeline with orchestration
✅ All core algorithms (illumination, classical detection, lighting fit, fusion)
✅ Data structures and serialization (JSON + PNG artifacts)
✅ Visual layer metadata for UI rendering
✅ Comprehensive documentation and handoff guides
✅ Clear placeholders for ML model integration

### What's Next
🔵 **Phase 2:** ML Model Integration (DSDNet, MiDaS, IntrinsicNet)
🔵 **Phase 3:** Evaluation Harness & Dataset Pipeline
🔵 **Phase 4:** Frontend UI Components (8-tile visualization)
🔵 **Phase 5:** API Endpoints & Integration
🔵 **Phase 6:** Production Optimization & Deployment

---

## Phase 2: ML Model Integration (2-3 Days)

### Objective
Replace placeholder functions with production-grade ML models for shadow detection, depth estimation, and intrinsic decomposition.

### Deliverables

#### 2.1 Shadow Detection Model (DSDNet/BDRAR)
**Files to modify:** `src/copy_that/shadowlab/pipeline.py:run_shadow_model()`

**Integration steps:**
1. Install model dependencies:
   ```bash
   pip install timm torch torchvision
   # For specific model: pip install git+https://github.com/jinyeun/BDRAR.git
   ```

2. Implement model loading and inference:
   ```python
   def run_shadow_model(rgb: np.ndarray) -> np.ndarray:
       """Load DSDNet/BDRAR and run shadow detection."""
       import torch
       from torchvision import transforms

       # Load pre-trained model
       device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
       model = load_pretrained_shadow_model(device)
       model.eval()

       # Preprocess
       transform = transforms.Compose([
           transforms.ToTensor(),
           transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225])
       ])

       # Inference
       with torch.no_grad():
           tensor = transform(Image.fromarray((rgb * 255).astype(np.uint8)))
           tensor = tensor.unsqueeze(0).to(device)
           output = model(tensor)

       # Post-process
       shadow_mask = torch.sigmoid(output).squeeze().cpu().numpy()
       return shadow_mask.astype(np.float32)
   ```

3. **Models to test:**
   - **DSDNet:** Fast, ~0.1s per image, 87% accuracy
   - **BDRAR:** More accurate, ~0.3s, 92% accuracy
   - **ShadowNet:** Good balance, ~0.15s, 89% accuracy
   - **Choose:** DSDNet for speed, BDRAR for accuracy

4. **Testing:**
   - Create unit test: `backend/tests/shadowlab/test_shadow_model.py`
   - Test on 10-20 sample images from ISTD dataset
   - Validate output shape, range [0, 1], and convergence

#### 2.2 Depth Estimation (MiDaS v3)
**Files to modify:** `src/copy_that/shadowlab/pipeline.py:run_midas_depth()`

**Integration steps:**
1. Install MiDaS:
   ```bash
   pip install timm torch torchvision
   # MiDaS usually available via torch.hub
   ```

2. Implement depth estimation:
   ```python
   def run_midas_depth(rgb: np.ndarray) -> np.ndarray:
       """Estimate depth using MiDaS v3 (large or small)."""
       import torch

       device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
       model_type = "DPT_Large"  # Options: DPT_Large, DPT_Hybrid, MiDaS_small
       midas = torch.hub.load("intel-isl/MiDaS", model_type).to(device)
       midas.eval()

       # Prepare input
       h, w = rgb.shape[:2]
       midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
       transform = midas_transforms.dpt_transform

       input_batch = transform(Image.fromarray((rgb * 255).astype(np.uint8))).to(device)

       # Inference
       with torch.no_grad():
           depth = midas(input_batch)
           depth = torch.nn.functional.interpolate(
               depth.unsqueeze(1), size=(h, w),
               mode="bicubic", align_corners=False
           ).squeeze()

       # Normalize
       depth_np = depth.cpu().numpy()
       depth_normalized = (depth_np - depth_np.min()) / (depth_np.max() - depth_np.min())
       return depth_normalized.astype(np.float32)
   ```

3. **Model variants:**
   - **DPT_Large:** Best quality, ~1.5s/image, needs 12GB VRAM
   - **DPT_Hybrid:** Good balance, ~0.8s/image, needs 8GB VRAM
   - **MiDaS_small:** Fast, ~0.3s/image, needs 2GB VRAM
   - **Choose:** DPT_Hybrid for balance

4. **Testing:**
   - Unit test: `backend/tests/shadowlab/test_midas_depth.py`
   - Validate: depth map shape, range [0, 1], smooth gradients
   - Compare with classical depth (plane-fitting) - should be better

#### 2.3 Intrinsic Decomposition (IntrinsicNet/CGIntrinsics)
**Files to modify:** `src/copy_that/shadowlab/pipeline.py:run_intrinsic()`

**Integration steps:**
1. Install dependencies:
   ```bash
   pip install torch torchvision
   # Clone IntrinsicNet: git clone https://github.com/zmurez/IntrinsicNet.git
   ```

2. Implement intrinsic decomposition:
   ```python
   def run_intrinsic(rgb: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
       """Decompose image into reflectance and shading."""
       import torch

       device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
       model = load_intrinsic_model(device)

       # Prepare input
       h, w = rgb.shape[:2]
       tensor = torch.from_numpy(rgb).permute(2, 0, 1).unsqueeze(0).float().to(device)

       # Inference
       with torch.no_grad():
           reflectance, shading = model(tensor)

       # Post-process
       reflectance = reflectance.squeeze().permute(1, 2, 0).cpu().numpy()
       shading = shading.squeeze().cpu().numpy()

       return reflectance, shading
   ```

3. **Evaluation:**
   - Validate: reflectance is color-preserving (bright areas meaningful)
   - Validate: shading matches lighting estimation
   - Validate: reflectance × shading ≈ original RGB

4. **Testing:**
   - Unit test: `backend/tests/shadowlab/test_intrinsic.py`
   - Visual inspection: Is reflectance realistic? Is shading smooth?
   - Pixel-level verification: rgb_reconstructed ≈ reflectance × shading

### Deliverable Structure
```
src/copy_that/shadowlab/
├── pipeline.py (updated with 3 ML models)
├── models/
│   ├── __init__.py
│   ├── shadow_model.py      (NEW - DSDNet/BDRAR wrapper)
│   ├── depth_model.py       (NEW - MiDaS wrapper)
│   └── intrinsic_model.py   (NEW - IntrinsicNet wrapper)
└── tests/
    ├── test_shadow_model.py     (NEW)
    ├── test_depth_model.py      (NEW)
    └── test_intrinsic_model.py  (NEW)
```

### Success Criteria
- [ ] All 3 models load and run without errors
- [ ] Output shapes match expected (h, w), (h, w), (h, w, 3)
- [ ] All outputs in valid ranges: [0, 1]
- [ ] Pipeline end-to-end test succeeds on 10 images
- [ ] No GPU OOM errors with 8GB VRAM
- [ ] Processing time < 5s per image (DPT_Hybrid + DSDNet + IntrinsicNet)

---

## Phase 3: Evaluation Harness & Dataset Pipeline (2-3 Days)

### Objective
Create infrastructure to evaluate shadow extraction quality and build a dataset from Midjourney images.

### Deliverables

#### 3.1 Evaluation Metrics
**New file:** `src/copy_that/shadowlab/eval.py`

```python
class ShadowExtractionEvaluator:
    """Evaluate shadow extraction quality against ground truth."""

    def __init__(self, metrics_config: Dict):
        self.metrics = {
            'iou': IntersectionOverUnion(),          # Mask accuracy
            'mae': MeanAbsoluteError(),               # Pixel-level error
            'bdri': BoundaryDisplacementError(),      # Edge accuracy
            'fmeasure': FMeasure(),                   # F1 score
        }

    def evaluate(self,
                 predicted_mask: np.ndarray,
                 ground_truth_mask: np.ndarray) -> Dict[str, float]:
        """Compute all metrics."""
        return {
            'iou': self.metrics['iou'](predicted, ground_truth),
            'mae': self.metrics['mae'](predicted, ground_truth),
            'bdri': self.metrics['bdri'](predicted, ground_truth),
            'fmeasure': self.metrics['fmeasure'](predicted, ground_truth),
        }
```

#### 3.2 Dataset Pipeline
**New file:** `src/copy_that/shadowlab/dataset.py`

```python
class MidjourneyImageDataset:
    """Load Midjourney images and extract shadows."""

    def __init__(self, image_dir: Path, output_dir: Path):
        self.images = list(Path(image_dir).glob("*.jpg"))
        self.output_dir = output_dir

    def process_all(self) -> List[Dict]:
        """Process all images, return metadata."""
        results = []
        for image_path in tqdm(self.images):
            result = self.process_single(image_path)
            results.append(result)
        return results

    def process_single(self, image_path: Path) -> Dict:
        """Process one image, save artifacts."""
        from copy_that.shadowlab import run_shadow_pipeline

        result = run_shadow_pipeline(str(image_path))

        # Save metadata
        metadata = {
            'image_id': image_path.stem,
            'tokens': result['shadow_token_set']['shadow_tokens'],
            'evaluation': result.get('evaluation_metrics', {}),
            'artifacts': result['artifacts_paths'],
        }

        json_path = self.output_dir / f"{image_path.stem}_metadata.json"
        json_path.write_text(json.dumps(metadata, indent=2))

        return metadata
```

#### 3.3 Batch Processing Script
**New file:** `scripts/process_midjourney_dataset.py`

```python
#!/usr/bin/env python3
"""Process Midjourney dataset through shadow extraction pipeline."""

import argparse
from pathlib import Path
from copy_that.shadowlab.dataset import MidjourneyImageDataset

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_dir", type=Path, help="Directory with Midjourney images")
    parser.add_argument("--output_dir", type=Path, default=Path("./shadows"))
    parser.add_argument("--evaluate", action="store_true")
    args = parser.parse_args()

    # Process dataset
    dataset = MidjourneyImageDataset(args.image_dir, args.output_dir)
    results = dataset.process_all()

    # Generate report
    print(f"\nProcessed {len(results)} images")
    print(f"Results saved to {args.output_dir}")

    if args.evaluate:
        # Generate evaluation report
        pass

if __name__ == "__main__":
    main()
```

### Success Criteria
- [ ] Evaluation metrics computed correctly on 10 test images
- [ ] Dataset pipeline processes 100+ images without errors
- [ ] All artifacts saved (PNG + JSON) in organized structure
- [ ] Processing time < 5 minutes for 100 images
- [ ] Generated report with average metrics and outliers

---

## Phase 4: Frontend UI Components (3-4 Days)

### Objective
Create React components to visualize the 8-stage shadow extraction process interactively.

### Deliverables

#### 4.1 Stage Visualization Component
**New file:** `frontend/src/components/shadowlab/ShadowExtractorViewer.tsx`

```typescript
interface ShadowExtractorViewerProps {
  pipelineResult: ShadowPipelineResult;
  selectedStageId?: string;
}

export function ShadowExtractorViewer({
  pipelineResult,
  selectedStageId,
}: ShadowExtractorViewerProps) {
  const [activeStage, setActiveStage] = useState(selectedStageId || "stage_01");

  return (
    <div className="shadow-extractor-viewer">
      {/* Stage selector - 8 tiles */}
      <StageTileGrid
        stages={pipelineResult.stages}
        activeStage={activeStage}
        onSelectStage={setActiveStage}
      />

      {/* Active stage detail view */}
      <StageDetailView
        stage={pipelineResult.stages[activeStage]}
        visualLayers={pipelineResult.visual_layers}
      />

      {/* Final token display */}
      <ShadowTokenDisplay tokens={pipelineResult.shadow_tokens} />
    </div>
  );
}
```

#### 4.2 Stage Tile Component (8 tiles, one per stage)
**New file:** `frontend/src/components/shadowlab/StageTile.tsx`

```typescript
export function StageTile({
  stage: ShadowStageResult,
  isActive: boolean,
  onClick: () => void,
}) {
  const stageNames = {
    "stage_01": "Input & Preprocessing",
    "stage_02": "Illumination View",
    "stage_03": "Classical Candidates",
    "stage_04": "ML Shadow Mask",
    "stage_05": "Intrinsic Decomposition",
    "stage_06": "Depth & Normals",
    "stage_07": "Lighting Fit",
    "stage_08": "Fusion & Tokens",
  };

  return (
    <div
      className={`stage-tile ${isActive ? "active" : ""}`}
      onClick={onClick}
    >
      <div className="stage-number">{stage.id}</div>
      <div className="stage-name">{stageNames[stage.id]}</div>
      <div className="stage-duration">{stage.duration_ms.toFixed(0)}ms</div>
      <div className="stage-metrics">
        {Object.entries(stage.metrics).map(([k, v]) => (
          <MetricBadge key={k} label={k} value={v} />
        ))}
      </div>
    </div>
  );
}
```

#### 4.3 Visual Layer Renderer
**New file:** `frontend/src/components/shadowlab/VisualLayerViewer.tsx`

```typescript
export function VisualLayerViewer({
  visualLayer: ShadowVisualLayer,
  artifactPath: string,
}) {
  const [opacity, setOpacity] = useState(1);
  const [blendMode, setBlendMode] = useState(visualLayer.render_params.blend_mode);

  return (
    <div className="visual-layer-viewer">
      <img
        src={artifactPath}
        alt={visualLayer.ui.title}
        style={{
          opacity,
          mixBlendMode: blendMode,
        }}
      />

      <div className="layer-controls">
        <label>Opacity: {(opacity * 100).toFixed(0)}%</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={opacity}
          onChange={(e) => setOpacity(parseFloat(e.target.value))}
        />

        <select value={blendMode} onChange={(e) => setBlendMode(e.target.value)}>
          <option>normal</option>
          <option>multiply</option>
          <option>screen</option>
          <option>overlay</option>
        </select>
      </div>
    </div>
  );
}
```

#### 4.4 Integration with API
**Files to modify:** `frontend/src/services/shadowlabService.ts`

```typescript
export class ShadowLabService {
  async extractShadows(imageUrl: string): Promise<ShadowPipelineResult> {
    const response = await fetch('/api/v1/shadowlab/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_url: imageUrl }),
    });

    return response.json();
  }

  async getArtifactPath(imageId: string, artifactId: string): Promise<string> {
    return `/api/v1/shadowlab/artifacts/${imageId}/${artifactId}`;
  }
}
```

### Component Hierarchy
```
ShadowExtractorViewer (main)
├── StageTileGrid (8 tiles)
│   └── StageTile × 8
├── StageDetailView
│   ├── StageMetricsPanel
│   ├── VisualLayerViewer × N
│   └── StageNarrativePanel
└── ShadowTokenDisplay
    ├── TokenCard (coverage, strength, etc.)
    ├── LightingDiagram (azimuth, elevation)
    └── ConsistencyMeter (physics plausibility)
```

### Styling
- Use Tailwind CSS with shadow-extraction-specific color scheme
- Responsive grid: 4 tiles on desktop, 2 on tablet, 1 on mobile
- Smooth transitions between stages
- Live artifact display with layer opacity controls

### Success Criteria
- [ ] All 8 stage tiles render correctly
- [ ] Click tile → detail view updates
- [ ] Visual layers load and display
- [ ] Opacity/blend mode controls work
- [ ] Tokens display with proper formatting
- [ ] No console errors
- [ ] Mobile responsive (tested on 3 breakpoints)

---

## Phase 5: API Endpoints & Backend Integration (2-3 Days)

### Objective
Create FastAPI endpoints to expose shadow extraction pipeline and integrate with existing token platform.

### Deliverables

#### 5.1 Shadow Extraction Endpoint
**New file:** `backend/interfaces/api/shadowlab.py`

```python
from fastapi import APIRouter, UploadFile, File
from copy_that.shadowlab import run_shadow_pipeline

router = APIRouter(prefix="/shadowlab", tags=["shadowlab"])

@router.post("/extract")
async def extract_shadows(
    project_id: str,
    image_url: Optional[str] = None,
    file: Optional[UploadFile] = File(None),
) -> Dict:
    """Extract shadow tokens from image."""

    # Validate project exists
    project = get_project(project_id)

    # Get image
    if file:
        image_data = await file.read()
        image_path = save_temp_image(image_data)
    else:
        image_path = download_image(image_url)

    # Run pipeline
    result = run_shadow_pipeline(image_path)

    # Save to database
    shadow_tokens = save_shadow_extraction(
        project_id=project_id,
        image_id=generate_uuid(),
        tokens=result['shadow_token_set'],
        artifacts=result['artifacts_paths'],
    )

    return {
        "status": "success",
        "shadow_tokens": shadow_tokens,
        "visual_layers": result['pipeline_results']['visual_layers'],
        "stages": result['pipeline_results']['stages'],
    }

@router.get("/artifacts/{image_id}/{artifact_id}")
async def get_artifact(image_id: str, artifact_id: str) -> FileResponse:
    """Retrieve artifact (PNG/JSON) for a shadow extraction."""
    artifact_path = get_artifact_path(image_id, artifact_id)
    return FileResponse(artifact_path)
```

#### 5.2 Database Schema
**New migration:** `backend/alembic/versions/xxx_add_shadow_tokens.py`

```python
def upgrade():
    op.create_table(
        'shadow_extractions',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('project_id', sa.String, sa.ForeignKey('projects.id')),
        sa.Column('image_id', sa.String),
        sa.Column('coverage', sa.Float),
        sa.Column('mean_strength', sa.Float),
        sa.Column('key_light_direction_json', sa.JSON),
        sa.Column('physics_consistency', sa.Float),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
    )

    op.create_table(
        'shadow_artifacts',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('extraction_id', sa.String, sa.ForeignKey('shadow_extractions.id')),
        sa.Column('artifact_type', sa.String),  # 'rgb', 'illumination', etc.
        sa.Column('artifact_path', sa.String),
        sa.Column('mime_type', sa.String),
    )
```

#### 5.3 Token Platform Integration
**Modify:** `backend/services/token_platform_service.py`

```python
class TokenPlatformService:
    async def extract_all_tokens(self, project_id: str, image_id: str):
        """Extract all token types from image."""

        # Existing: color, spacing, typography
        color_tokens = await self.extract_color_tokens(image_id)
        spacing_tokens = await self.extract_spacing_tokens(image_id)
        typography_tokens = await self.extract_typography_tokens(image_id)

        # NEW: shadow tokens
        shadow_tokens = await self.extract_shadow_tokens(image_id)

        # Merge into unified token graph
        token_graph = TokenGraph()
        token_graph.add_tokens('color', color_tokens)
        token_graph.add_tokens('spacing', spacing_tokens)
        token_graph.add_tokens('typography', typography_tokens)
        token_graph.add_tokens('shadow', shadow_tokens)

        return token_graph

    async def extract_shadow_tokens(self, image_id: str) -> List[ShadowToken]:
        """Extract shadow tokens using shadowlab pipeline."""
        from copy_that.shadowlab import run_shadow_pipeline

        image = get_image(image_id)
        result = run_shadow_pipeline(image.file_path)

        return create_shadow_token_objects(
            image_id=image_id,
            pipeline_result=result,
        )
```

### Success Criteria
- [ ] POST /api/v1/shadowlab/extract returns valid response
- [ ] GET /api/v1/shadowlab/artifacts/{id}/{artifact} returns PNG
- [ ] Database schema created and migrations run
- [ ] Token platform integration test passes
- [ ] API documentation generated (Swagger/OpenAPI)

---

## Phase 6: Production Optimization & Deployment (1-2 Days)

### Objective
Optimize performance, add caching, and prepare for production deployment.

### Key Optimizations

1. **Model Caching**
   - Load models once, reuse across requests
   - Use Redis for artifact caching

2. **Batch Processing**
   - Queue system for large datasets
   - Async task processing with Celery

3. **GPU Optimization**
   - Mixed precision (torch.autocast)
   - Model quantization (int8 for smaller models)
   - Batched inference

4. **Monitoring**
   - Log processing time per stage
   - Track GPU/CPU usage
   - Alert on failures

### Deployment Checklist
- [ ] Load test: 10 requests/sec sustained
- [ ] Memory test: No leaks after 1000 images
- [ ] GPU stability: 24-hour continuous run
- [ ] Edge cases: Handles corrupted/unusual images
- [ ] Documentation: Complete API docs + deployment guide

---

## Implementation Timeline

```
Week 1:
├─ Phase 2: ML Model Integration (Mon-Wed)
├─ Phase 3: Evaluation Harness (Thu-Fri)

Week 2:
├─ Phase 4: Frontend Components (Mon-Wed)
├─ Phase 5: API Endpoints (Thu-Fri)

Week 3:
├─ Phase 6: Production Optimization (Mon-Tue)
└─ Bugfixes & Polish (Wed-Fri)
```

---

## Resource Files

### Reference Documentation
- **SHADOW_PIPELINE_IMPLEMENTATION.md** - Technical architecture
- **SHADOW_EXTRACTION_ROADMAP.md** - 6-phase evolution (Phases 2-6 covered here)
- **SHADOW_PIPELINE_SPEC.md** - Detailed specification

### Code References
- **pipeline.py** - Core implementation with placeholders
- **stages.py** - 8-stage functions
- **orchestrator.py** - Pipeline orchestration

### Testing
- Look at existing test patterns in `backend/tests/` and `frontend/src/tests/`
- Use pytest for backend, vitest for frontend
- Aim for 80%+ coverage

### Model Resources
- **DSDNet:** https://github.com/zhouhao94/DSDNet
- **MiDaS:** https://github.com/isl-org/MiDaS
- **IntrinsicNet:** https://github.com/zmurez/IntrinsicNet
- **ISTD Dataset:** https://github.com/DeepInsight-PeterChen/ShadowDetection (for testing)

---

## Questions & Decision Points

### 1. Model Selection
- **Decision Needed:** Which shadow detection model? (DSDNet vs BDRAR)
- **Impact:** Performance vs accuracy tradeoff
- **Recommendation:** Start with DSDNet (faster), upgrade to BDRAR after testing

### 2. GPU Resource Requirements
- **DPT_Large MiDaS:** 12GB VRAM (~1.5s/image)
- **DPT_Hybrid MiDaS:** 8GB VRAM (~0.8s/image) ← RECOMMENDED
- **MiDaS_small:** 2GB VRAM (~0.3s/image)
- **Combined pipeline:** ~2-3 seconds per image

### 3. Dataset Size
- **Scope:** How many Midjourney images to process initially?
- **Recommendation:** Start with 50-100 for testing, then 1000+ for full evaluation

### 4. Frontend Complexity
- **Simple:** Just display final tokens + main mask
- **Medium:** 8 tiles with stage navigation (RECOMMENDED)
- **Complex:** Interactive blending, layer manipulation, real-time metrics

---

## Success Criteria Summary

### Phase 2
- 3 ML models integrated and tested
- Processing time < 5s per image
- No OOM errors with 8GB VRAM

### Phase 3
- Evaluation metrics computed on dataset
- 100+ images processed successfully
- Generated report with statistics

### Phase 4
- 8-stage visualization interactive
- Mobile responsive
- All layers render correctly

### Phase 5
- API endpoints tested and documented
- Database schema created
- Token platform integration working

### Phase 6
- Load test: 10 req/sec sustained
- No memory leaks after 1000 images
- Production-ready deployment

---

## Notes for Next Session

1. **Model Download:** First action should be downloading pre-trained models (1-2GB)
2. **GPU Setup:** Verify CUDA/torch installation before starting Phase 2
3. **Testing Strategy:** Create test dataset of 20-30 images for validation
4. **API Design:** Finalize endpoint specification before implementing Phase 5
5. **Frontend Design:** Sketch UI mockups before implementing Phase 4

---

## Contact & Questions

If you have questions during implementation:
- Review `SHADOW_PIPELINE_IMPLEMENTATION.md` for technical details
- Check `SHADOW_EXTRACTION_ROADMAP.md` for Phase 2-6 vision
- Reference model documentation links above
- Look at existing patterns in the codebase

Good luck with Phase 2! 🚀
