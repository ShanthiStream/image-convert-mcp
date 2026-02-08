# Image Convert MCP

High-performance image conversion to **WebP** and **AVIF** via Model Context Protocol.

<div class="grid cards" markdown>

-   :material-speedometer:{ .lg .middle } **High Performance**

    ---

    Parallel processing with configurable workers for batch operations

-   :material-image-multiple:{ .lg .middle } **Multiple Formats**

    ---

    Convert to WebP, AVIF, or both simultaneously

-   :material-tune:{ .lg .middle } **8 Built-in Presets**

    ---

    web, thumbnail, social, hd, 4k, archive, lossless, max-compression

-   :material-robot:{ .lg .middle } **AI Agent Ready**

    ---

    Full MCP integration with agent-optimized tool descriptions

</div>

## Quick Start

=== "CLI"

    ```bash
    # Install
    pip install image-convert-mcp

    # Convert an image
    image-convert photo.png --preset web

    # Batch convert with stats
    image-convert ./images/ --batch --stats
    ```

=== "MCP Server"

    ```json
    {
      "mcpServers": {
        "image-convert": {
          "command": "python",
          "args": ["-m", "mcp_server"]
        }
      }
    }
    ```

=== "Python"

    ```python
    from src import convert_one, get_preset

    preset = get_preset("thumbnail")
    result = convert_one(
        image_path=Path("photo.png"),
        output_dir=Path("./output"),
        **preset
    )
    ```

## Features

| Feature | Description |
|---------|-------------|
| WebP conversion | High quality with adjustable compression |
| AVIF conversion | Best-in-class compression ratios |
| Batch processing | Multi-threaded directory conversion |
| Presets | 8 ready-to-use configurations |
| Compression stats | Detailed savings reporting |
| Resize on convert | Maintain aspect ratio |

## Support

If you find this project useful, consider supporting its development:

<a href="https://buymeacoffee.com/shanthistream" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50">
</a>
