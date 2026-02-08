# Installation

## Requirements

- Python 3.11+
- libavif-dev (system dependency for AVIF support)

## Install via pip

```bash
pip install image-convert-mcp
```

## Install from source

```bash
git clone https://github.com/ShanthiStream/image-convert-mcp.git
cd image-convert-mcp
pip install -e .
```

## Install development dependencies

```bash
pip install -e ".[dev]"
```

## System Dependencies

### macOS

```bash
brew install libavif
```

### Ubuntu/Debian

```bash
sudo apt-get install libavif-dev
```

### Docker

Use the included Dockerfile for a complete environment:

```bash
docker build -t image-convert-mcp .
```

## Verify Installation

```bash
# Check CLI is available
image-convert --version

# List available presets
image-convert --list-presets
```

If you see the version number and preset list, you're ready to go!
