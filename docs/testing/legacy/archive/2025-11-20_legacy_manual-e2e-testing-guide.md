# Manual E2E Testing Guide - Copy That

## Prerequisites
- ✅ Frontend running on `http://localhost:4000`
- ✅ Backend running on `http://localhost:8000`
- ✅ Database initialized with SQLite

## Full E2E Workflow Test

### 1. Project Creation & Management
**Objective**: Verify project CRUD operations work end-to-end

**Steps**:
1. Navigate to `http://localhost:4000`
2. Create a new project
   - [ ] Click "New Project" button
   - [ ] Enter project name: "Manual E2E Test Project"
   - [ ] Enter description: "Testing color extraction workflow"
   - [ ] Click "Create"
   - [ ] ✅ Verify: Project appears in project list with ID and timestamp

3. Update the project
   - [ ] Click project to edit
   - [ ] Change name to "Updated Manual E2E Test"
   - [ ] Click "Save"
   - [ ] ✅ Verify: Project name updates immediately

4. View project details
   - [ ] Click on project name
   - [ ] ✅ Verify: Project details panel opens
   - [ ] ✅ Verify: Shows creation date and update timestamp

---

### 2. Color Token Extraction & Display
**Objective**: Verify complete color extraction pipeline

**Steps**:
1. Upload test image (use any standard image file)
   - [ ] Click "Upload Image" in project
   - [ ] Select an image file from your computer
   - [ ] Set max colors to 10
   - [ ] Click "Extract Colors"
   - [ ] ⏳ Wait for extraction to complete (2-10 seconds depending on image)

2. Verify color extraction results
   - [ ] ✅ Colors display in grid/list format
   - [ ] ✅ Each color shows:
     - Hex code (e.g., #FF5733)
     - RGB format
     - Color name
     - Confidence score (0.0 - 1.0)
     - Harmony type (if available)
   - [ ] ✅ Color count matches max_colors setting

3. Verify color details
   - [ ] Click on individual color card
   - [ ] ✅ Verify color details panel shows:
     - Full hex/RGB/HSL/HSV values
     - Design intent (if extracted)
     - Harmony information
     - WCAG contrast ratios
     - Accessibility compliance (AA/AAA)
     - Color temperature
     - Saturation level

4. Verify educational components (if enabled)
   - [ ] Scroll through color visualization panels
   - [ ] ✅ Verify harmony visualizer displays color wheel
   - [ ] ✅ Verify accessibility calculator shows contrast ratios
   - [ ] ✅ Verify color narrative explains color properties

---

### 3. Multiple Image Batch Processing
**Objective**: Verify batch extraction handles multiple images

**Steps**:
1. Upload multiple images
   - [ ] Click "Add More Images"
   - [ ] Select 2-3 additional images
   - [ ] Click "Extract All"
   - [ ] ⏳ Wait for batch processing

2. Verify batch results
   - [ ] ✅ All images are processed
   - [ ] ✅ Colors from each image are aggregated
   - [ ] ✅ Total color count reflects all images
   - [ ] ✅ Confidence scores account for multiple sources

---

### 4. Color Token Management
**Objective**: Verify color token CRUD operations

**Steps**:
1. Create manual color token
   - [ ] Click "Add Color Manually"
   - [ ] Fill in form:
     - Hex: #0066FF
     - Name: Primary Blue
     - Design Intent: primary
     - Harmony: analogous
     - Confidence: 0.95
   - [ ] Click "Add"
   - [ ] ✅ Verify: Color appears in collection

2. Retrieve colors
   - [ ] Click on project colors
   - [ ] ✅ Verify: All extracted + manual colors displayed
   - [ ] ✅ Verify: Sort/filter options work

3. Update color properties
   - [ ] Click on color to edit
   - [ ] Change design intent
   - [ ] Click "Save"
   - [ ] ✅ Verify: Changes persist

4. Delete color
   - [ ] Click on color
   - [ ] Click "Delete"
   - [ ] Confirm deletion
   - [ ] ✅ Verify: Color removed from list

---

### 5. Data Persistence
**Objective**: Verify data survives browser refresh and multiple sessions

**Steps**:
1. Create test data (project + colors)
   - [ ] Create project with test colors
   - [ ] Verify colors display

2. Refresh browser
   - [ ] Press F5 or Cmd+R
   - [ ] ✅ Verify: Project and colors still visible
   - [ ] ✅ Verify: All data preserved

3. Close and reopen browser
   - [ ] Close browser tab/window
   - [ ] Wait 5 seconds
   - [ ] Open new tab and navigate to `localhost:4000`
   - [ ] ✅ Verify: Project still accessible
   - [ ] ✅ Verify: Colors still present

---

### 6. API Integration Verification
**Objective**: Verify backend API endpoints work correctly

**Steps**:
1. Check API status
   - [ ] Open new terminal tab
   - [ ] Run: `curl http://localhost:8000/api/v1/status | jq`
   - [ ] ✅ Verify: Returns status JSON with "operational" status

2. Test project endpoint
   - [ ] Run: `curl http://localhost:8000/api/v1/projects | jq`
   - [ ] ✅ Verify: Returns list of projects

3. Test color endpoint
   - [ ] Run: `curl 'http://localhost:8000/api/v1/projects/1/colors' | jq`
   - [ ] ✅ Verify: Returns color tokens for project

4. Test color creation
   - [ ] Create curl POST request with color data
   - [ ] ✅ Verify: Color created successfully (201 response)

---

### 7. Error Handling & Edge Cases
**Objective**: Verify graceful error handling

**Steps**:
1. Test invalid project ID
   - [ ] Navigate to `http://localhost:4000/projects/99999`
   - [ ] ✅ Verify: Shows "Project not found" error

2. Test upload without image
   - [ ] Click "Extract Colors" without selecting image
   - [ ] ✅ Verify: Shows validation error

3. Test invalid form data
   - [ ] Try to create color with invalid hex code
   - [ ] ✅ Verify: Shows validation error with hint

4. Test empty project
   - [ ] Create new project without images
   - [ ] ✅ Verify: Shows "No colors extracted" message

---

### 8. Performance & Responsiveness
**Objective**: Verify performance meets requirements

**Steps**:
1. Response time - Image upload
   - [ ] Upload 5MB image
   - [ ] Start timer
   - [ ] ⏳ Wait for extraction complete
   - [ ] ✅ Verify: Completes in <30 seconds
   - [ ] ✅ Verify: UI remains responsive (no freezing)

2. Response time - Color display
   - [ ] Upload image with 20+ colors
   - [ ] ✅ Verify: Colors display within 2 seconds
   - [ ] ✅ Verify: Smooth rendering (no jank)

3. Batch processing efficiency
   - [ ] Upload 5 images
   - [ ] ⏳ Time batch processing
   - [ ] ✅ Verify: Completes in reasonable time
   - [ ] ✅ Verify: No memory leaks (check DevTools)

---

## Accessibility Testing

### 1. Keyboard Navigation
- [ ] Tab through all controls
- [ ] ✅ Verify: Tab order makes sense
- [ ] ✅ Verify: Can submit forms with Enter

### 2. Color Contrast
- [ ] Use browser DevTools accessibility checker
- [ ] ✅ Verify: All text meets WCAG AA standards
- [ ] ✅ Verify: Color names don't rely on color alone

### 3. Screen Reader
- [ ] Test with browser screen reader
- [ ] ✅ Verify: Form labels read correctly
- [ ] ✅ Verify: Color values announced clearly

---

## TypeScript & Type Safety Testing

### 1. Type Checking
```bash
# Run type check
pnpm type-check

# ✅ Verify: 0 TypeScript errors
```

### 2. Component Props
- [ ] Open React DevTools
- [ ] Verify all component props are correctly typed
- [ ] ✅ Verify: No "any" types in color-related components

---

## Testing Checklist Summary

### Frontend (UI)
- [ ] Projects CRUD operations
- [ ] Color extraction displays correctly
- [ ] Color details panel shows all fields
- [ ] Batch processing works
- [ ] Data persists across page refreshes
- [ ] Error messages display properly
- [ ] UI responsive on different screen sizes
- [ ] Accessibility features work
- [ ] Type safety (0 TypeScript errors)

### Backend (API)
- [ ] Status endpoint responds
- [ ] Projects endpoint lists/creates
- [ ] Colors endpoint retrieves/creates
- [ ] Color token validation works
- [ ] Database persistence verified
- [ ] Error responses properly formatted

### Performance
- [ ] Image upload < 30 seconds
- [ ] Color display < 2 seconds
- [ ] No memory leaks
- [ ] Smooth UI interactions

### Integration
- [ ] Full E2E workflow succeeds
- [ ] Frontend ↔ Backend communication works
- [ ] Database ↔ API integration verified
- [ ] Cross-browser compatibility (test in Chrome, Safari, Firefox)

---

## Test Data References

### Sample Images for Testing
- **Simple colors**: Solid color backgrounds
- **Complex colors**: Photos with many colors (landscape, portrait)
- **Edge cases**: B&W images, very small images, large high-res images

### Sample Test Colors
```json
{
  "hex": "#FF5733",
  "rgb": "rgb(255, 87, 51)",
  "hsl": "hsl(11, 100%, 60%)",
  "name": "Coral Red",
  "design_intent": "error",
  "confidence": 0.95,
  "harmony": "complementary"
}
```

---

## Troubleshooting

### Frontend not loading
- [ ] Check `http://localhost:4000` is accessible
- [ ] Check browser console for errors (F12)
- [ ] Run `pnpm dev` to restart frontend

### Backend not responding
- [ ] Check `http://localhost:8000/api/v1/status`
- [ ] Check backend logs
- [ ] Run `python -m uvicorn src.copy_that.interfaces.api.main:app --reload`

### Database issues
- [ ] Check SQLite database exists at `./copy_that.db`
- [ ] Run migrations: `python -m alembic upgrade head`

### Colors not displaying
- [ ] Check browser Network tab for API errors
- [ ] Verify color tokens in database: `sqlite3 copy_that.db "SELECT * FROM color_tokens;"`

---

## Notes for QA Team

**Version**: v0.3.2
**Status**: Production Ready (CSS Styling Complete)
**Last Updated**: 2025-11-20

**Known Limitations**:
- Batch processing limited to 50 images per session
- Max 100 colors per image extraction
- SQLite for dev/test only (Neon PostgreSQL for production)

**Next Testing Phase**:
- Load testing with 50+ images
- Integration with production database
- Performance optimization validation
