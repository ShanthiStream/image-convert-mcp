# Core API Reference

The `src.core` module provides the core image conversion functionality.

## Functions

### convert_one

Convert a single image to WebP and/or AVIF format.

```python
from pathlib import Path
from src.core import convert_one

result = convert_one(
    image_path=Path("photo.png"),
    output_dir=Path("./output"),
    format="webp",
    webp_quality=80,
    avif_quality=50,
    lossless=False,
    max_width=1920,
    max_height=None,
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `image_path` | `Path` | Path to input image |
| `output_dir` | `Path` | Output directory |
| `format` | `str` | `"webp"`, `"avif"`, or `"both"` |
| `webp_quality` | `int` | WebP quality (1-100) |
| `avif_quality` | `int` | AVIF quality (1-100) |
| `lossless` | `bool` | Enable lossless WebP |
| `max_width` | `int \| None` | Maximum width |
| `max_height` | `int \| None` | Maximum height |

**Returns:** `dict[str, str]` with input path and output paths.

---

### convert_batch_parallel

Convert multiple images in parallel.

```python
from pathlib import Path
from src.core import convert_batch_parallel

results = convert_batch_parallel(
    input_dir=Path("./images"),
    output_dir=Path("./output"),
    format="webp",
    webp_quality=80,
    avif_quality=50,
    lossless=False,
    max_width=1920,
    max_height=None,
    workers=4,
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `input_dir` | `Path` | Directory containing images |
| `workers` | `int \| None` | Number of parallel workers |
| `**kwargs` | | Arguments passed to `convert_one()` |

**Returns:** `list[dict[str, str]]` with results for each image.

---

### load_image

Load and validate an image file.

```python
from src.core import load_image

img = load_image(Path("photo.png"))
```

**Returns:** `PIL.Image.Image` in RGBA mode.

**Raises:** `ImageConversionError` if loading fails.

---

### resize_if_needed

Resize image if it exceeds maximum dimensions.

```python
from src.core import resize_if_needed

img = resize_if_needed(img, max_width=1920, max_height=1080)
```

**Returns:** Resized `PIL.Image.Image` (or original if no resize needed).

---

## Constants

### SUPPORTED_EXTS

Set of supported input file extensions:

```python
SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}
```
