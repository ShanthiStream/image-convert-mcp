# Image Convert API - REST Endpoints

## Base URL
- **Local**: `http://localhost:8999`
- **Vercel**: `https://your-app.vercel.app`

## Endpoints

### GET /
Returns API documentation and available endpoints.

**Response:**
```json
{
  "name": "Image Convert API",
  "version": "1.0.0",
  "description": "REST API for converting images to WebP and AVIF formats",
  "endpoints": {
    "GET /": "This documentation",
    "GET /api/tools": "List available tools",
    "POST /api/convert/single": "Convert a single image",
    "POST /api/convert/batch": "Convert multiple images"
  }
}
```

### GET /api/tools
Lists all available conversion tools with their parameters.

**Response:**
```json
{
  "tools": [
    {
      "name": "convert_image_single",
      "description": "Convert a single image to WebP and/or AVIF format",
      "endpoint": "/api/convert/single",
      "method": "POST",
      "parameters": {...}
    }
  ],
  "status": "success"
}
```

### POST /api/convert/single
Convert a single image file.

**Request Body:**
```json
{
  "input_path": "/path/to/image.png",
  "output_dir": "/path/to/output",
  "format": "both",
  "webp_quality": 80,
  "avif_quality": 50,
  "lossless": false,
  "max_width": 1920,
  "max_height": 1080
}
```

**Response:**
```json
{
  "result": {
    "input": "/path/to/image.png",
    "webp": "/path/to/output/image.webp",
    "avif": "/path/to/output/image.avif"
  },
  "status": "success"
}
```

### POST /api/convert/batch
Convert multiple images in a directory.

**Request Body:**
```json
{
  "input_path": "/path/to/images",
  "output_dir": "/path/to/output",
  "format": "both",
  "workers": 4
}
```

**Response:**
```json
{
  "results": [
    {
      "input": "/path/to/images/img1.png",
      "webp": "/path/to/output/img1.webp",
      "avif": "/path/to/output/img1.avif"
    }
  ],
  "status": "success"
}
```

## Error Responses

All endpoints return errors in this format:
```json
{
  "error": "Error message",
  "status": "error"
}
```

HTTP Status Codes:
- `400`: Bad Request (validation error)
- `500`: Internal Server Error
