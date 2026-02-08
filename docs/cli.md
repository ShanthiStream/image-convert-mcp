# CLI Reference

Complete reference for the `image-convert` command-line interface.

## Synopsis

```bash
image-convert [OPTIONS] INPUT
```

## Arguments

| Argument | Description |
|----------|-------------|
| `INPUT` | Input image file or directory (for batch mode) |

## Options

### Output Options

| Option | Default | Description |
|--------|---------|-------------|
| `-o, --output DIR` | Same as input | Output directory |
| `-f, --format {webp,avif,both}` | `both` | Output format |

### Quality Options

| Option | Default | Description |
|--------|---------|-------------|
| `-q, --quality N` | - | Quality for both formats (1-100) |
| `--webp-quality N` | 80 | WebP quality (1-100) |
| `--avif-quality N` | 50 | AVIF quality (1-100) |
| `-l, --lossless` | false | Enable lossless WebP compression |

### Size Options

| Option | Description |
|--------|-------------|
| `-W, --max-width PX` | Maximum output width (maintains aspect ratio) |
| `-H, --max-height PX` | Maximum output height (maintains aspect ratio) |

### Batch Options

| Option | Description |
|--------|-------------|
| `--batch` | Process all images in a directory |
| `-w, --workers N` | Number of parallel workers (default: CPU count) |

### Preset Options

| Option | Description |
|--------|-------------|
| `-p, --preset NAME` | Use a named preset (overrides quality/size options) |
| `--list-presets` | List available presets and exit |

### Other Options

| Option | Description |
|--------|-------------|
| `-s, --stats` | Show compression statistics |
| `-v, --verbose` | Enable verbose output |
| `-V, --version` | Show version and exit |
| `-h, --help` | Show help and exit |

## Examples

### Basic conversion

```bash
# Convert to both formats
image-convert photo.png

# Convert to WebP only with custom quality
image-convert photo.png -f webp -q 85

# Convert to AVIF with lossless WebP backup
image-convert photo.png -f both --avif-quality 60 --lossless
```

### Using presets

```bash
# Create thumbnail
image-convert photo.png --preset thumbnail

# Optimize for social media
image-convert photo.png --preset social

# Maximum compression
image-convert photo.png --preset max-compression
```

### Batch processing

```bash
# Convert all images in directory
image-convert ./photos/ --batch

# Batch with specific preset
image-convert ./photos/ --batch --preset web -w 8

# Batch with custom output directory
image-convert ./photos/ --batch -o ./optimized/ -f webp
```

### With statistics

```bash
# Show compression stats for single file
image-convert photo.png --stats

# Verbose batch with stats
image-convert ./photos/ --batch --stats -v
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (validation, conversion, or IO failure) |

## Environment Variables

None required. All configuration is via command-line arguments.
