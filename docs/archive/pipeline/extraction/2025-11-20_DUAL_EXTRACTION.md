# Dual CV+AI Extraction Guide

> **Status update (2025-11-05)**: AI enhancement is optional and currently disabled by default in production. Follow this guide only when OpenAI credentials are configured.

**Version**: v2.2
**Status**: Beta

---

## Overview

The dual extraction system runs **both** Computer Vision (CV) and AI methods in parallel, then cross-validates and merges results for maximum confidence and quality.

### Architecture

```
Image → [CV Extract (required)] → Precise values
           ↓
       [AI Extract (optional)] → Semantic understanding
           ↓
       [Cross-Validate] → High confidence when both agree
           ↓
       [Merge Results] → Best of both worlds
```

---

## Quick Start

### 1. CV-Only Mode (Default) - FREE

No AI API key needed. Fast, precise, zero cost.

```bash
# Standard extraction (CV only)
make ingest

# Or explicitly
python extractors/build_style_guide.py assets/refs > style_guide.json
```

**Output**:
```json
{
  "palette": {
    "primary": "#F15925"
  }
}
```

---

### 2. Dual Mode (CV + AI) - ~$0.02-0.05/image

Requires OpenAI API key. Adds semantic naming and validation.

**Setup**:
```bash
# Set OpenAI API key
export OPENAI_API_KEY="sk-..."

# Enable dual extraction
export AI_ENABLED=true

# Run extraction
make ingest
```

**Output**:
```json
{
  "palette": {
    "primary": {
      "hex": "#F15925",                # CV (precise)
      "name": "molten-copper",          # AI (semantic)
      "confidence": 0.95,               # Both agree
      "validated": true                 # Cross-validated
    }
  },
  "validation_summary": {
    "validated": 5,
    "conflicts": 0,
    "cv_only": 2,
    "overall_confidence": 0.92
  }
}
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (none) | OpenAI API key (required for AI) |
| `AI_ENABLED` | `false` | Enable dual CV+AI extraction |
| `AI_MODE` | `validate` | AI mode: `validate`, `enhance`, `full` |
| `AI_CONFIDENCE` | `0.7` | Minimum confidence threshold (0-1) |

### AI Modes

**1. `validate` (Default)** - Cross-validation only
- CV extracts tokens
- AI validates results
- Flags conflicts
- **Cost**: ~$0.01-0.02/image

**2. `enhance`** - Semantic enhancement
- CV extracts + AI adds names/context
- Cross-validation
- Merge results
- **Cost**: ~$0.02-0.03/image

**3. `full`** - Complete dual extraction
- Both methods extract independently
- Full cross-validation
- Component detection
- Style analysis
- **Cost**: ~$0.03-0.05/image

---

## Examples

### Example 1: Basic Dual Extraction

```bash
export OPENAI_API_KEY="sk-..."
export AI_ENABLED=true
python extractors/build_style_guide.py assets/refs > style_guide.json
```

**Result**:
- CV finds colors precisely
- AI names them semantically
- Cross-validation ensures quality

---

### Example 2: Validation Mode (Budget-Friendly)

```bash
export OPENAI_API_KEY="sk-..."
export AI_ENABLED=true
export AI_MODE=validate  # Only validate, don't extract
make ingest
```

**Benefits**:
- Lowest AI cost (~$0.01/image)
- Error detection
- Confidence scoring
- Fallback to CV if AI fails

---

### Example 3: CV-Only Fallback

If AI fails or API key is missing, automatically falls back to CV:

```bash
# No API key set
make ingest
```

**Output**:
```
ℹ️  AI enhancement not available - using CV only (this is normal)
✅ Extraction complete (CV-only mode)
```

---

## Benefits of Dual Extraction

### 1. Higher Confidence

| Method | Confidence |
|--------|-----------|
| CV only | ~70-80% |
| AI only | ~75-85% |
| **Both agree** | **~95%** ✨ |

### 2. Error Detection

**CV Errors Caught by AI**:
- Compression artifacts detected as colors
- Measurement noise
- Edge detection mistakes

**AI Errors Caught by CV**:
- Hallucinated colors
- Imprecise measurements
- Misidentifications

### 3. Completeness

- CV finds precise pixel values
- AI finds contextual elements
- Together: More complete token extraction

### 4. Semantic Enrichment

**CV Output**:
```json
{"primary": "#F15925"}
```

**Dual Output**:
```json
{
  "primary": {
    "hex": "#F15925",
    "name": "molten-copper",
    "context": "Retro audio equipment warmth",
    "mood": "energetic, industrial",
    "validated": true
  }
}
```

---

## Cost Analysis

### CV-Only (Default)
- **Cost**: $0
- **Speed**: <500ms/image
- **Quality**: Precise measurements
- **Best for**: Production, budget-conscious, offline

### Dual (AI Enhancement)
- **Cost**: $0.01-0.05/image
- **Speed**: 2-5 seconds/image
- **Quality**: Precise + Semantic
- **Best for**: Professional projects, design systems, client work

### ROI Calculation

**Project**: 20 reference images

**CV-Only**:
- Cost: $0
- Manual naming: 45min × $100/hr = $75
- **Total**: $75

**Dual**:
- Cost: 20 × $0.03 = $0.60
- Manual naming: 5min × $100/hr = $8
- **Total**: $8.60

**Savings**: $66.40 per project + better quality

---

## Troubleshooting

### "AI enhancement not available"

This is **normal** if:
- No `OPENAI_API_KEY` set
- `AI_ENABLED=false`
- No internet connection

**Solution**: The system will automatically use CV-only mode (works perfectly!).

### "AI extraction failed: API error"

**Cause**: API rate limit, network issue, or invalid key

**Behavior**: Automatically falls back to CV-only

**Log**:
```
⚠️  AI extraction failed: API timeout. Falling back to CV-only.
✅ Extraction complete (CV-only mode)
```

### Low Confidence Warnings

If `overall_confidence < 0.7`:
```
⚠️  Token confidence 0.65 below threshold 0.7
```

**Causes**:
- CV and AI disagree on many tokens
- Image quality issues
- Design inconsistencies

**Solution**: Review flagged conflicts manually

---

## Best Practices

### 1. Use CV-Only for Development
```bash
make ingest  # Fast, free, reliable
```

### 2. Use Dual for Production
```bash
export AI_ENABLED=true
make ingest  # High quality, validated
```

### 3. Start with Validate Mode
```bash
export AI_MODE=validate  # Cheapest AI option
```

### 4. Review Conflicts
Check `validation_summary.conflicts` in output:
```json
{
  "validation_summary": {
    "conflicts": 2,  // ← Review these
    "validated": 8
  }
}
```

---

## API Key Setup

### Option 1: Environment Variable (Temporary)
```bash
export OPENAI_API_KEY="sk-..."
make ingest AI_ENABLED=true
```

### Option 2: .env File (Permanent)
```bash
# extractors/.env
OPENAI_API_KEY=sk-...
AI_ENABLED=true
AI_MODE=validate
```

### Option 3: Shell Config (Global)
```bash
# ~/.zshrc or ~/.bashrc
export OPENAI_API_KEY="sk-..."
```

**Security**: Never commit API keys to git! Add `.env` to `.gitignore`.

---

## Advanced Usage

### Custom Confidence Threshold
```bash
export AI_CONFIDENCE=0.85  # Higher threshold = stricter validation
make ingest AI_ENABLED=true
```

### Disable Caching
```python
# extractors/ai/config.py
self.enable_caching = False  # Always call AI (higher cost)
```

### Cost Limiting
```python
# extractors/ai/config.py
self.max_cost_per_image = 0.02  # Max $0.02/image
```

---

## Integration Examples

### With Backend API
```python
# backend/routers/extraction.py
from extractors.build_style_guide import extract_with_ai

result = extract_with_ai(
    images=uploaded_files,
    enable_ai=user.has_ai_credits
)
```

### With CI/CD
```yaml
# .github/workflows/extract-tokens.yml
- name: Extract design tokens
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    AI_ENABLED: true
  run: make ingest
```

---

## Comparison: CV vs Dual

| Feature | CV-Only | Dual (CV+AI) |
|---------|---------|--------------|
| **Precision** | ✅ Exact | ✅ Exact (CV value used) |
| **Semantic Names** | ❌ Generic | ✅ Professional |
| **Validation** | ⚠️ None | ✅ Cross-validated |
| **Error Detection** | ❌ | ✅ |
| **Speed** | ✅ <500ms | ⚠️ 2-5s |
| **Cost** | ✅ $0 | ⚠️ ~$0.02-0.05 |
| **Offline** | ✅ Yes | ❌ Requires internet |
| **Quality** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## Future Enhancements (v2.3+)

- [ ] Component-level dual extraction
- [ ] Local AI models (LLaVA, CLIP) for offline AI
- [ ] Batch processing with cost optimization
- [ ] Real-time confidence monitoring in UI
- [ ] AI-powered design system recommendations

---

## Summary

- **CV is required** - Always works, zero cost, precise
- **AI is optional** - Adds semantic understanding, costs $$
- **Both together** - Best quality, high confidence, validated
- **Graceful fallback** - AI fails → automatic CV-only mode

**Recommendation**: Use CV-only for development, dual for production.

---

**Questions?** See [AI Configuration](../../extractors/ai/config.py) or [Dual Extractor](../../extractors/ai/dual_extractor.py)
