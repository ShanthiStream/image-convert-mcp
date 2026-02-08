# Statistics API Reference

The `src.stats` module provides compression statistics utilities.

## Functions

### get_conversion_stats

Get comprehensive statistics for a conversion.

```python
from pathlib import Path
from src.stats import get_conversion_stats

stats = get_conversion_stats(
    input_path=Path("photo.png"),
    webp_path=Path("photo.webp"),
    avif_path=Path("photo.avif"),
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `input_path` | `Path` | Original input file |
| `webp_path` | `Path \| None` | Output WebP file |
| `avif_path` | `Path \| None` | Output AVIF file |

**Returns:** Dictionary with:

```python
{
    "input": "/path/to/photo.png",
    "input_size": "2.50 MB",
    "input_size_bytes": 2621440,
    "webp": {
        "path": "/path/to/photo.webp",
        "original_size": "2.50 MB",
        "new_size": "450 KB",
        "saved_bytes": "2.05 MB",
        "savings_percent": "82.0%",
        "compression_ratio": "5.8:1",
        "increased": False
    },
    "avif": {...},
    "best_format": "avif"
}
```

---

### format_stats_summary

Format statistics as a human-readable summary.

```python
from src.stats import format_stats_summary

summary = format_stats_summary(stats)
print(summary)
```

**Output:**

```
📊 Compression Statistics
   Input: 2.50 MB
   📉 WebP: 450 KB (82.0% saved)
   📉 AVIF: 280 KB (89.3% saved)
   🏆 Best: AVIF
```

---

### calculate_savings

Calculate compression savings between two sizes.

```python
from src.stats import calculate_savings

result = calculate_savings(original_size=1000000, new_size=250000)
# {'original_size': '976.6 KB', 'new_size': '244.1 KB', 'savings_percent': '75.0%', ...}
```

---

### format_size

Format byte size to human-readable string.

```python
from src.stats import format_size

format_size(1024)        # "1.0 KB"
format_size(1048576)     # "1.00 MB"
format_size(500)         # "500 B"
```

---

## CLI Integration

Use with CLI's `--stats` flag:

```bash
image-convert photo.png -f webp --stats
```

Output:

```
✅ Converted: photo.png
   → WebP: photo.webp

📊 Compression Statistics
   Input: 2.50 MB
   📉 WebP: 450 KB (82.0% saved)
```
