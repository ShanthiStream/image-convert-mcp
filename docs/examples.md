# Examples

Real-world usage examples for image-convert-mcp.

## CLI Examples

### Website Optimization

Optimize all images in a website's assets folder:

```bash
image-convert ./public/images/ --batch --preset web -o ./public/optimized/
```

### Create Responsive Images

Generate multiple sizes for responsive images:

```bash
# Full size
image-convert hero.png --preset hd -o ./images/

# Medium
image-convert hero.png -W 1024 -f webp -o ./images/ 

# Thumbnail
image-convert hero.png --preset thumbnail -o ./images/
```

### Social Media Optimization

Optimize images for social sharing:

```bash
image-convert og-image.png --preset social
```

### Maximum Compression

Reduce file sizes as much as possible:

```bash
image-convert ./large-images/ --batch --preset max-compression
```

---

## Python Examples

### Basic Conversion

```python
from pathlib import Path
from src import convert_one

result = convert_one(
    image_path=Path("photo.png"),
    output_dir=Path("./output"),
    format="webp",
    webp_quality=80,
    lossless=False,
    max_width=None,
    max_height=None,
)

print(f"Created: {result['webp']}")
```

### Using Presets

```python
from pathlib import Path
from src import convert_one, get_preset

# Get thumbnail preset
preset = get_preset("thumbnail")

# Apply preset
result = convert_one(
    image_path=Path("photo.png"),
    output_dir=Path("./thumbs"),
    **preset
)
```

### Batch with Statistics

```python
from pathlib import Path
from src import convert_batch_parallel, get_conversion_stats, format_stats_summary

# Batch convert
results = convert_batch_parallel(
    input_dir=Path("./images"),
    output_dir=Path("./optimized"),
    format="webp",
    webp_quality=80,
    workers=4,
)

# Show stats for each
for result in results:
    if "webp" in result:
        stats = get_conversion_stats(
            Path(result["input"]),
            webp_path=Path(result["webp"])
        )
        print(format_stats_summary(stats))
```

---

## MCP Agent Examples

### Prompt: Optimize Website Images

> "Convert all PNG images in /var/www/images to WebP with 80% quality"

The agent uses `convert_image_batch`:

```json
{
  "input_path": "/var/www/images",
  "format": "webp",
  "webp_quality": 80
}
```

### Prompt: Create Thumbnails

> "Create 300x300 thumbnails for all images in /photos"

The agent uses:

```json
{
  "input_path": "/photos",
  "format": "webp",
  "webp_quality": 70,
  "max_width": 300,
  "max_height": 300
}
```

### Prompt: Maximum Compression

> "I need to reduce the size of banner.png as much as possible"

The agent uses `convert_image_single`:

```json
{
  "input_path": "/images/banner.png",
  "format": "avif",
  "avif_quality": 40
}
```

---

## Docker Examples

### Basic Usage

```bash
docker run --rm -v /path/to/images:/images image-convert-mcp \
    image-convert /images/photo.png -f webp
```

### Batch Processing

```bash
docker run --rm -v /path/to/images:/images image-convert-mcp \
    image-convert /images/ --batch --preset web
```

### As MCP Server

```bash
docker run -i --rm -v /images:/images image-convert-mcp \
    python -m mcp_server
```
