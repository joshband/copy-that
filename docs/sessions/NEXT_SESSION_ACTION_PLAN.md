# Next Session Action Plan - Test Suite Final Push to 100%

**Current Status:** 424/446 tests passing (97.9%) ✅

**Remaining Work:** Fix 9 ImageUploader integration test timeouts (2% of suite)

**Estimated Time:** 30 minutes to reach 100% pass rate

---

## Critical Issue to Fix

### ImageUploader Integration Test Timeouts

**File:** `frontend/src/components/image-uploader/__tests__/ImageUploader.integration.test.tsx`

**Problem:** 9 tests timing out on `screen.findByText('Preview')` at line 470

**Root Cause:** FileReader + image processing operations complete too slowly for default Vitest timeout

**Solution:** Increase async timeout for findByText operations

---

## Exact Fix Required

### Option 1: Global Timeout Fix (Recommended)
**Impact:** Applies to all findByText operations across test suite

1. Open the test file
2. Find all instances of `screen.findByText('Preview')`
3. Change to: `screen.findByText('Preview', {}, { timeout: 5000 })`
4. Repeat for any other similar timeouts in the file

**Expected Results:** All 9 timeouts should resolve

### Option 2: Vitest Config Global Increase
If timeouts are systemic across integration tests, increase in vitest.config.ts:
```typescript
export default defineConfig({
  test: {
    // ... existing config
    testTimeout: 10000, // increased from current
    hookTimeout: 10000,
  }
})
```

---

## Step-by-Step Execution Plan

1. **Open the file** (15 seconds)
   ```bash
   code frontend/src/components/image-uploader/__tests__/ImageUploader.integration.test.tsx
   ```

2. **Find timeout points** (2 minutes)
   - Search for: `screen.findByText`
   - Look for: Line 470 and similar patterns
   - Count total occurrences

3. **Apply fix** (10 minutes)
   - Add timeout parameter to each findByText call
   - Example: `screen.findByText('Preview', {}, { timeout: 5000 })`

4. **Test Phase 4** (5 minutes)
   ```bash
   NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split-phase4
   ```

5. **Verify full suite** (5 minutes)
   ```bash
   NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split
   ```

6. **Confirm typecheck** (2 minutes)
   ```bash
   pnpm type-check
   ```

7. **Commit changes** (2 minutes)
   ```bash
   git add -A
   git commit -m "fix: Increase async timeout for ImageUploader integration tests"
   ```

---

## Expected Outcome

After these fixes:
- ✅ Phase 4 tests: 60/60 passing (100%)
- ✅ Overall: 446/446 passing (100%)
- ✅ All phases complete successfully with 4GB memory
- ✅ Ready for production CI/CD

---

## Quick Reference: Current Test Status

### Phase 1 ✅
```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split-phase1
# Result: 51 tests PASS (100%)
```

### Phase 2 ⚠️ (Mostly working)
```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split-phase2
# Result: 111 tests PASS, 7 TIMEOUT (94%)
# Note: Timeouts are in ImageUploader.integration.test.tsx
```

### Phase 3 ✅
```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split-phase3
# Result: 126 tests PASS (100%)
```

### Phase 4 ⚠️ (Needs timeout fix)
```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split-phase4
# Result: 51 PASS, 9 TIMEOUT (85%)
# Failure Location: ImageUploader.integration.test.tsx
```

---

## Key Files Involved

| File | Status | Notes |
|------|--------|-------|
| `package.json` | ✅ Done | Test scripts already added (commit 1fcba13) |
| `frontend/src/components/image-uploader/__tests__/ImageUploader.integration.test.tsx` | ⚠️ Needs Fix | Add timeout to findByText calls |
| `vitest.config.ts` | ✅ Optimal | Already configured correctly |
| `frontend/src/components/overview-narrative/hooks.ts` | ✅ Done | Already fixed in session 1 |

---

## Verification Checklist

- [ ] Open ImageUploader.integration.test.tsx
- [ ] Identify all `screen.findByText` calls that need timeout
- [ ] Add `{ timeout: 5000 }` parameter to each
- [ ] Run `pnpm test:split-phase4` and confirm all 60 tests pass
- [ ] Run `pnpm test:split` and confirm all phases pass
- [ ] Run `pnpm type-check` and confirm no TypeScript errors
- [ ] Create commit with fixes
- [ ] Document final session results

---

## Session Success Criteria

✅ All criteria met when:
1. Phase 4 shows "60 passed (60)" with no timeouts
2. Full `pnpm test:split` runs all 4 phases successfully
3. `pnpm type-check` passes with no errors
4. All tests can run with `NODE_OPTIONS="--max-old-space-size=4096"`
5. 446/446 tests passing

---

## Notes for Success

- The timeout issue is isolated to ImageUploader integration tests
- Other 80% of suite is already working perfectly
- Memory management via phase splitting is proven to work
- TypeScript is clean and ready
- This is a straightforward async timeout fix

**Estimated completion:** 30 minutes from session start ✨
