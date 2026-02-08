# Presets API Reference

The `src.presets` module provides predefined conversion configurations.

## Functions

### get_preset

Get a preset configuration by name.

```python
from src.presets import get_preset

preset = get_preset("thumbnail")
# {'format': 'webp', 'webp_quality': 70, 'max_width': 300, 'max_height': 300, ...}
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Preset name |

**Returns:** `PresetConfig` dictionary.

**Raises:** `ValueError` if preset not found.

---

### list_presets

List all available presets with descriptions.

```python
from src.presets import list_presets

for name, desc in list_presets().items():
    print(f"{name}: {desc}")
```

**Returns:** `dict[str, str]` mapping names to descriptions.

---

## Available Presets

### PRESETS

Dictionary of all preset configurations:

| Preset | Format | Quality | Dimensions | Use Case |
|--------|--------|---------|------------|----------|
| `web` | webp | 80 | 1920px wide | General web images |
| `thumbnail` | webp | 70 | 300x300 | Thumbnails, avatars |
| `social` | webp | 85 | 1200x630 | Social media cards |
| `hd` | webp | 90 | 1920x1080 | HD displays |
| `4k` | webp | 90 | 3840x2160 | 4K displays |
| `archive` | both | 95/90 | Original | High quality archival |
| `lossless` | webp | 100 | Original | No quality loss |
| `max-compression` | avif | 40 | Original | Smallest file size |

---

## Types

### PresetConfig

TypedDict for preset configuration:

```python
class PresetConfig(TypedDict, total=False):
    format: str
    webp_quality: int
    avif_quality: int
    lossless: bool
    max_width: Optional[int]
    max_height: Optional[int]
```

---

## Usage with convert_one

```python
from pathlib import Path
from src.core import convert_one
from src.presets import get_preset

preset = get_preset("social")
result = convert_one(
    image_path=Path("photo.png"),
    output_dir=Path("./output"),
    **preset  # Unpack preset settings
)
```
