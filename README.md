# Image Convert MCP Server

A Model Context Protocol (MCP) server for high-performance image format conversion supporting WebP and AVIF formats with parallel processing capabilities.

## 🚀 Features

- **Multiple Format Support**: Convert images to WebP, AVIF, or both formats simultaneously
- **Batch Processing**: Process entire directories with configurable parallel workers
- **Image Resizing**: Optional width/height constraints with aspect ratio preservation
- **Quality Control**: Configurable quality settings for both WebP and AVIF
- **High Performance**: Multi-process parallel execution for batch operations
- **Flexible Input**: Supports PNG, JPG, JPEG, TIFF, BMP, and WebP as input formats

## 📋 Requirements

- Python 3.11+
- MCP Python SDK (`mcp>=1.0.0`)
- Pillow (PIL)
- pillow-avif-plugin
- libavif-dev (system dependency)

## 🔧 Installation

### Using pip

```bash
cd /path/to/image-convert-mcp
pip install -e .
```

Or install requirements directly:

```bash
pip install -r requirements.txt
```

### Using Docker

```bash
docker build -t image-convert-mcp .
```

## 📖 Usage

The MCP server implements the Model Context Protocol with support for both Stdio and Unified HTTP transports.

## 🚌 Transport Modes

The server supports two transport mechanisms:

### 1. Stdio (Default)
Standard communication via stdin/stdout. Ideal for local use with MCP clients like Claude Desktop.

```bash
python mcp_server.py --transport stdio
```

### 2. HTTP (Unified)
Web-based communication via HTTP. This is the modern, recommended transport for remote MCP access.

```bash
python mcp_server.py --transport http --host 0.0.0.0 --port 8000
```

When running in HTTP mode, the server provides a unified MCP endpoint at the root path (e.g., `http://localhost:8000/`).

### MCP Tools

#### `convert_image_single`
Convert a single image to WebP and/or AVIF format.

**Parameters:**
- `input_path` (required): Path to the input image file
- `output_dir` (optional): Directory for output files (default: same as input)
- `format` (optional): Output format - "webp", "avif", or "both" (default: "both")
- `webp_quality` (optional): WebP quality 1-100 (default: 80)
- `avif_quality` (optional): AVIF quality 1-100 (default: 50)
- `lossless` (optional): Enable lossless WebP compression (default: false)
- `max_width` (optional): Maximum output width
- `max_height` (optional): Maximum output height

#### `convert_image_batch`
Convert multiple images in a directory to WebP and/or AVIF format.

**Parameters:**
- `input_path` (required): Path to directory containing images
- `output_dir` (optional): Directory for output files (default: same as input)
- `format` (optional): Output format - "webp", "avif", or "both" (default: "both")
- `webp_quality` (optional): WebP quality 1-100 (default: 80)
- `avif_quality` (optional): AVIF quality 1-100 (default: 50)
- `lossless` (optional): Enable lossless WebP compression (default: false)
- `max_width` (optional): Maximum output width
- `max_height` (optional): Maximum output height
- `workers` (optional): Number of parallel workers (default: CPU count)

## 🔑 Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | string | `"single"` | Processing mode: `"single"` or `"batch"` |
| `input_path` | string | **required** | Path to image file (single mode) or directory (batch mode) |
| `output_dir` | string | parent of input | Directory for output files |
| `format` | string | `"both"` | Output format: `"webp"`, `"avif"`, or `"both"` |
| `webp_quality` | int | `80` | WebP quality (1-100) |
| `avif_quality` | int | `50` | AVIF quality (1-100) |
| `lossless` | bool | `false` | Enable lossless compression for WebP |
| `max_width` | int | `null` | Maximum output width (maintains aspect ratio) |
| `max_height` | int | `null` | Maximum output height (maintains aspect ratio) |
| `workers` | int | CPU count | Number of parallel workers (batch mode only) |

## 🐳 Docker Usage

```bash
# Build the image
docker build -t image-convert-mcp .

# Run conversion
echo '{"params":{"input_path":"/app/input.png","format":"webp"}}' | \
  docker run -i -v /path/to/images:/app image-convert-mcp
```

## 🔌 MCP Configuration

Add to your MCP settings file (e.g., `opencode.json`):

```json
{
  "mcpServers": {
    "image-convert": {
      "command": "python",
      "args": ["/path/to/image-convert-mcp/mcp_server.py"],
      "disabled": false
    }
  }
}
```

Or using Docker:

```json
{
  "mcpServers": {
    "image-convert": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        "${workspaceFolder}:/workspace",
        "image-convert-mcp"
      ],
      "disabled": false
    }
  }
}
```

## 📊 Output Format

### Single Mode
```json
{
  "result": {
    "input": "/path/to/input.png",
    "webp": "/path/to/output/input.webp",
    "avif": "/path/to/output/input.avif"
  }
}
```

### Batch Mode
```json
{
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

## 🎯 Supported Input Formats

- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- TIFF (`.tiff`)
- BMP (`.bmp`)
- WebP (`.webp`)

## 🛠️ Development

### Project Structure
```
image-convert-mcp/
├── mcp_server.py      # Main MCP server implementation
├── requirements.txt   # Python dependencies
└── Dockerfile         # Docker container definition
```

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 🔮 Roadmap

- [ ] Support for JPEG XL format
- [ ] Metadata preservation options
- [ ] Progress reporting for long operations
- [ ] Comprehensive test suite
- [ ] Input validation and security enhancements
- [ ] Caching for frequently converted images
