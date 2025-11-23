# Session 1: Preprocessing Pipeline

**Can Run in Parallel with Sessions 2-5**

## Branch
```bash
git checkout -b claude/preprocessing-pipeline-{SESSION_ID}
```

## Mission
Implement PreprocessingAgent: download, validate, resize, enhance, cache images.

## Owned Files

Create these files:
- `src/copy_that/pipeline/preprocessing/__init__.py`
- `src/copy_that/pipeline/preprocessing/agent.py`
- `src/copy_that/pipeline/preprocessing/downloader.py`
- `src/copy_that/pipeline/preprocessing/validator.py`
- `src/copy_that/pipeline/preprocessing/enhancer.py`
- `tests/unit/pipeline/preprocessing/test_agent.py`
- `tests/unit/pipeline/preprocessing/test_validator.py`
- `tests/unit/pipeline/preprocessing/test_downloader.py`

## Priority Tasks

### IMMEDIATE - Security Critical

#### 1. ImageValidator with SSRF Protection
- Block private IPs: 10.x, 172.16.x, 192.168.x, 127.x
- Block metadata endpoints: 169.254.169.254
- Validate magic bytes (PNG, JPEG, WebP, GIF)
- Enforce 10MB size limit
- **TESTS FIRST**

#### 2. ImageDownloader (Async)
- httpx AsyncClient
- 30s timeout
- Retry with exponential backoff
- **TESTS FIRST**

### HIGH

#### 3. ImageEnhancer
- Resize maintaining aspect ratio
- CLAHE contrast enhancement
- Fix EXIF orientation
- Convert to WebP
- **TESTS FIRST**

#### 4. PreprocessingAgent
- Orchestrate: validate → download → enhance
- Return ProcessedImage with metadata
- **TESTS FIRST**

## Exit Criteria
- [ ] SSRF protection blocks all private IPs
- [ ] All tests written BEFORE implementation
- [ ] 100% coverage on security code

## Commit Message
```
feat: implement preprocessing pipeline with SSRF protection
```

## Auto-Execute
1. Create branch
2. Write security tests FIRST
3. Implement
4. Commit and push
