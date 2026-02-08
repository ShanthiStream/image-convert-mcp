"""
Image Convert MCP Server

A Model Context Protocol server for converting images to WebP and AVIF formats
with support for both single file and batch directory processing.
"""

import asyncio
import logging
import argparse
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route
import uvicorn

# Import from src package
from src import (
    convert_one,
    convert_batch_parallel,
    validate_path,
    validate_params,
    ValidationError,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("image-convert-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="convert_image_single",
            description="""Convert a single image to WebP and/or AVIF format.

USE WHEN: Optimizing images for web, reducing file sizes, or converting 
legacy formats (PNG/JPG/TIFF/BMP) to modern next-gen formats.

COMMON PATTERNS:
• Web optimization: format='webp', webp_quality=80
• Maximum compression: format='avif', avif_quality=50
• Thumbnails: max_width=300, max_height=300
• Lossless archival: format='webp', lossless=True

SUPPORTED INPUT: PNG, JPG, JPEG, TIFF, BMP, WebP""",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Path to the input image file"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory for output files (default: same as input)"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["webp", "avif", "both"],
                        "description": "Output format (default: both)"
                    },
                    "webp_quality": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "description": "WebP quality 1-100 (default: 80)"
                    },
                    "avif_quality": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "description": "AVIF quality 1-100 (default: 50)"
                    },
                    "lossless": {
                        "type": "boolean",
                        "description": "Enable lossless compression for WebP (default: false)"
                    },
                    "max_width": {
                        "type": "integer",
                        "description": "Maximum output width (maintains aspect ratio)"
                    },
                    "max_height": {
                        "type": "integer",
                        "description": "Maximum output height (maintains aspect ratio)"
                    }
                },
                "required": ["input_path"]
            }
        ),
        Tool(
            name="convert_image_batch",
            description="""Convert multiple images in a directory to WebP and/or AVIF format.

USE WHEN: Processing all images in a folder, bulk optimization, or 
converting entire image libraries at once.

PERFORMANCE TIP: Uses parallel processing. Set workers=4-8 for optimal 
performance on most systems. Default uses all CPU cores.

COMMON PATTERNS:
• Batch web optimization: format='webp', webp_quality=80, workers=4
• Create thumbnail directory: max_width=300, max_height=300
• Full archive conversion: format='both', workers=8

SUPPORTED INPUT: PNG, JPG, JPEG, TIFF, BMP, WebP files in directory""",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Path to directory containing images"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory for output files (default: same as input)"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["webp", "avif", "both"],
                        "description": "Output format (default: both)"
                    },
                    "webp_quality": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "description": "WebP quality 1-100 (default: 80)"
                    },
                    "avif_quality": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "description": "AVIF quality 1-100 (default: 50)"
                    },
                    "lossless": {
                        "type": "boolean",
                        "description": "Enable lossless compression for WebP (default: false)"
                    },
                    "max_width": {
                        "type": "integer",
                        "description": "Maximum output width (maintains aspect ratio)"
                    },
                    "max_height": {
                        "type": "integer",
                        "description": "Maximum output height (maintains aspect ratio)"
                    },
                    "workers": {
                        "type": "integer",
                        "description": "Number of parallel workers (default: CPU count)"
                    }
                },
                "required": ["input_path"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle MCP tool calls."""
    try:
        # Validate parameters
        validate_params(arguments)
        
        # Validate and resolve paths
        input_path = validate_path(Path(arguments["input_path"]), must_exist=True)
        output_dir = Path(arguments.get("output_dir", input_path.parent))
        output_dir = validate_path(output_dir, must_exist=False)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Common conversion arguments
        common_args = {
            "output_dir": output_dir,
            "format": arguments.get("format", "both"),
            "webp_quality": arguments.get("webp_quality", 80),
            "avif_quality": arguments.get("avif_quality", 50),
            "lossless": arguments.get("lossless", False),
            "max_width": arguments.get("max_width"),
            "max_height": arguments.get("max_height"),
        }

        if name == "convert_image_batch":
            if not input_path.is_dir():
                raise ValidationError("Batch mode requires a directory path")
            
            result = await asyncio.to_thread(
                convert_batch_parallel,
                input_dir=input_path,
                workers=arguments.get("workers"),
                **common_args
            )
            return [TextContent(
                type="text",
                text=f"✅ Batch conversion complete: {len(result)} images processed\n{result}"
            )]
            
        elif name == "convert_image_single":
            if not input_path.is_file():
                raise ValidationError("Single mode requires a file path")
            
            result = await asyncio.to_thread(
                convert_one,
                image_path=input_path,
                **common_args
            )
            return [TextContent(
                type="text",
                text=f"✅ Image conversion successful:\n{result}"
            )]
            
        raise ValueError(f"Unknown tool: {name}")
        
    except (ValidationError, ValueError) as e:
        logger.error(f"Tool error: {e}")
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Unexpected error: {str(e)}")]


async def run_stdio():
    """Run MCP server with stdio transport."""
    async with stdio_server() as (r, w):
        await app.run(r, w, app.create_initialization_options())


def main():
    """Main entry point for MCP server."""
    parser = argparse.ArgumentParser(
        description="Image Convert MCP Server"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport mode (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to for SSE transport (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to for SSE transport (default: 8000)"
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        logger.info("Starting MCP server with stdio transport")
        asyncio.run(run_stdio())
    else:
        logger.info(f"Starting MCP server with SSE transport on {args.host}:{args.port}")
        
        # Use SseServerTransport with custom endpoint /mcp
        sse = SseServerTransport(endpoint="/mcp")

        async def handle_mcp(request):
            """Handle SSE connection at /mcp endpoint."""
            async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send
            ) as (r, w):
                await app.run(r, w, app.create_initialization_options())

        async def handle_messages(request):
            """Handle POST messages at /messages endpoint."""
            await sse.handle_post_message(
                request.scope,
                request.receive,
                request._send
            )

        starlette_app = Starlette(
            routes=[
                Route("/mcp", endpoint=handle_mcp, methods=["GET"]),
                Route("/messages", endpoint=handle_messages, methods=["POST"]),
            ]
        )
        
        uvicorn.run(starlette_app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
