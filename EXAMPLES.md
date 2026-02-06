# Example Usage Scripts

## Single Image Conversion Examples

### Convert to WebP only
```bash
echo '{
  "params": {
    "mode": "single",
    "input_path": "/path/to/image.png",
    "format": "webp",
    "webp_quality": 85
  }
}' | python mcp_server.py
```

### Convert to AVIF only
```bash
echo '{
  "params": {
    "mode": "single",
    "input_path": "/path/to/image.jpg",
    "format": "avif",
    "avif_quality": 60
  }
}' | python mcp_server.py
```

### Convert to both WebP and AVIF
```bash
echo '{
  "params": {
    "mode": "single",
    "input_path": "/path/to/image.png",
    "format": "both",
    "webp_quality": 80,
    "avif_quality": 50
  }
}' | python mcp_server.py
```

### Convert with resizing
```bash
echo '{
  "params": {
    "mode": "single",
    "input_path": "/path/to/large-image.png",
    "format": "webp",
    "webp_quality": 85,
    "max_width": 1920,
    "max_height": 1080
  }
}' | python mcp_server.py
```

### Lossless WebP conversion
```bash
echo '{
  "params": {
    "mode": "single",
    "input_path": "/path/to/image.png",
    "format": "webp",
    "lossless": true
  }
}' | python mcp_server.py
```

## Batch Conversion Examples

### Convert entire directory to WebP
```bash
echo '{
  "params": {
    "mode": "batch",
    "input_path": "/path/to/images/",
    "output_dir": "/path/to/output/",
    "format": "webp",
    "webp_quality": 85,
    "workers": 4
  }
}' | python mcp_server.py
```

### Batch convert with auto-detected CPU cores
```bash
echo '{
  "params": {
    "mode": "batch",
    "input_path": "/path/to/images/",
    "format": "both",
    "webp_quality": 80,
    "avif_quality": 50
  }
}' | python mcp_server.py
```

### Batch convert with resizing
```bash
echo '{
  "params": {
    "mode": "batch",
    "input_path": "/path/to/images/",
    "output_dir": "/path/to/thumbnails/",
    "format": "webp",
    "webp_quality": 90,
    "max_width": 800,
    "max_height": 600
  }
}' | python mcp_server.py
```

## Using with Docker

### Build the image
```bash
docker build -t image-convert-mcp .
```

### Single conversion
```bash
echo '{
  "params": {
    "input_path": "/workspace/image.png",
    "format": "webp"
  }
}' | docker run -i --rm -v $(pwd):/workspace image-convert-mcp
```

### Batch conversion
```bash
echo '{
  "params": {
    "mode": "batch",
    "input_path": "/workspace/images",
    "output_dir": "/workspace/output",
    "format": "both"
  }
}' | docker run -i --rm -v $(pwd):/workspace image-convert-mcp
```

## Expected Output

### Success Response
```json
{
  "status": "success",
  "result": {
    "input": "/path/to/image.png",
    "webp": "/path/to/output/image.webp",
    "avif": "/path/to/output/image.avif"
  }
}
```

### Error Response
```json
{
  "status": "error",
  "error_type": "validation_error",
  "error": "Invalid mode: xyz (must be 'single' or 'batch')"
}
```

### Batch Success Response
```json
{
  "status": "success",
  "result": [
    {
      "input": "/path/to/image1.png",
      "webp": "/path/to/output/image1.webp"
    },
    {
      "input": "/path/to/image2.jpg",
      "webp": "/path/to/output/image2.webp"
    }
  ]
}
```

## Logging Output (stderr)

The server outputs detailed logs to stderr for debugging:

```
2026-02-06 16:00:00 - INFO - Received conversion request
2026-02-06 16:00:00 - INFO - Loading image: /path/to/image.png
2026-02-06 16:00:00 - INFO - Converting to WebP: /path/to/output/image.webp
2026-02-06 16:00:01 - INFO - WebP conversion complete: /path/to/output/image.webp
2026-02-06 16:00:01 - INFO - Converting to AVIF: /path/to/output/image.avif
2026-02-06 16:00:02 - INFO - AVIF conversion complete: /path/to/output/image.avif
2026-02-06 16:00:02 - INFO - Conversion completed successfully
```
