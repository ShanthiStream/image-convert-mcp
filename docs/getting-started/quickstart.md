# Quick Start

Get started converting images in under a minute.

## CLI Quick Start

### Convert a single image

```bash
image-convert photo.png
```

This creates both `photo.webp` and `photo.avif` in the same directory.

### Use a preset

```bash
image-convert photo.png --preset thumbnail
```

Creates a 300x300 WebP thumbnail.

### Batch convert a directory

```bash
image-convert ./images/ --batch -f webp
```

Converts all images in the directory to WebP using parallel processing.

### View compression savings

```bash
image-convert photo.png --stats
```

Output:
```
✅ Converted: photo.png
   → WebP: /path/to/photo.webp
   → AVIF: /path/to/photo.avif

📊 Compression Statistics
   Input: 2.50 MB
   📉 WebP: 450 KB (82.0% saved)
   📉 AVIF: 280 KB (88.8% saved)
   🏆 Best: AVIF
```

## MCP Server Quick Start

### 1. Configure your MCP client

Add to your MCP settings (e.g., `settings.json`):

```json
{
  "mcpServers": {
    "image-convert": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/image-convert-mcp"
    }
  }
}
```

### 2. Use with your AI agent

Ask your agent to:

> "Convert all PNG files in /images to WebP with 80% quality"

The agent will use the `convert_image_batch` tool automatically.

## Available Presets

| Preset | Format | Quality | Max Size | Use Case |
|--------|--------|---------|----------|----------|
| `web` | WebP | 80 | 1920px | General web images |
| `thumbnail` | WebP | 70 | 300x300 | Thumbnails, avatars |
| `social` | WebP | 85 | 1200x630 | Social media cards |
| `hd` | WebP | 90 | 1920x1080 | HD displays |
| `4k` | WebP | 90 | 3840x2160 | 4K displays |
| `archive` | Both | 95/90 | Original | Archival quality |
| `lossless` | WebP | 100 | Original | No quality loss |
| `max-compression` | AVIF | 40 | Original | Smallest file size |

## Next Steps

- [CLI Reference](../cli.md) - Full command-line options
- [MCP Tools](../mcp/tools.md) - Detailed tool documentation
- [Examples](../examples.md) - Real-world usage patterns
