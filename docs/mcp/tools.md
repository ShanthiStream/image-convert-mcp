# MCP Tools Reference

The image-convert-mcp server provides two tools for AI agents.

## convert_image_single

Convert a single image to WebP and/or AVIF format.

### When to Use

- Optimizing images for web deployment
- Reducing file sizes for faster page loads
- Converting legacy formats (PNG/JPG/TIFF/BMP) to modern formats

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_path` | string | ✅ | - | Path to input image |
| `output_dir` | string | ❌ | Same as input | Directory for output files |
| `format` | string | ❌ | `"both"` | Output format: `"webp"`, `"avif"`, or `"both"` |
| `webp_quality` | integer | ❌ | 80 | WebP quality (1-100) |
| `avif_quality` | integer | ❌ | 50 | AVIF quality (1-100) |
| `lossless` | boolean | ❌ | false | Enable lossless WebP |
| `max_width` | integer | ❌ | null | Maximum width (maintains aspect ratio) |
| `max_height` | integer | ❌ | null | Maximum height (maintains aspect ratio) |

### Example Usage

```json
{
  "input_path": "/images/photo.png",
  "format": "webp",
  "webp_quality": 80,
  "max_width": 1200
}
```

### Response

```json
{
  "input": "/images/photo.png",
  "webp": "/images/photo.webp"
}
```

---

## convert_image_batch

Convert multiple images in a directory to WebP and/or AVIF format.

### When to Use

- Processing all images in a folder
- Bulk optimization of image libraries
- Converting entire directories at once

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_path` | string | ✅ | - | Directory containing images |
| `output_dir` | string | ❌ | Same as input | Directory for output files |
| `format` | string | ❌ | `"both"` | Output format |
| `webp_quality` | integer | ❌ | 80 | WebP quality (1-100) |
| `avif_quality` | integer | ❌ | 50 | AVIF quality (1-100) |
| `lossless` | boolean | ❌ | false | Enable lossless WebP |
| `max_width` | integer | ❌ | null | Maximum width |
| `max_height` | integer | ❌ | null | Maximum height |
| `workers` | integer | ❌ | CPU count | Parallel workers |

### Performance Tips

- Set `workers=4-8` for optimal performance on most systems
- Default uses all CPU cores
- AVIF encoding is slower than WebP

### Example Usage

```json
{
  "input_path": "/images/gallery/",
  "format": "webp",
  "webp_quality": 80,
  "max_width": 1920,
  "workers": 4
}
```

### Response

```json
[
  {"input": "/images/gallery/photo1.png", "webp": "/images/gallery/photo1.webp"},
  {"input": "/images/gallery/photo2.jpg", "webp": "/images/gallery/photo2.webp"},
  {"input": "/images/gallery/photo3.png", "error": "File too large"}
]
```

---

## Supported Input Formats

- PNG
- JPG / JPEG
- TIFF
- BMP
- WebP

## Quality Guidelines

| Use Case | WebP Quality | AVIF Quality |
|----------|--------------|--------------|
| Web optimization | 80 | 50 |
| Thumbnails | 70 | 40 |
| High quality | 90 | 80 |
| Archival | 95 | 90 |
| Maximum compression | 50 | 40 |
