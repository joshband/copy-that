# Test Images

Drop images here to test the shadow pipeline.

## Usage

```bash
# Process all images in this folder
uv run python scripts/process_test_images.py

# Process a specific image
uv run python scripts/process_test_images.py test_images/my_image.jpg
```

## Output

Results are saved to `test_images_output/`:
- `{image_name}/` - Per-image results
  - `shadow_tokens.json` - Extracted shadow tokens
  - `artifacts/` - Stage outputs (PNG files)
  - `comparison.png` - Side-by-side visualization

## Supported Formats

- JPG, JPEG, PNG, WEBP, BMP, TIFF
