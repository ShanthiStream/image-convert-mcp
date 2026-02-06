"""
Image Convert MCP Server

A Model Context Protocol server for converting images to WebP and AVIF formats
with support for both single file and batch directory processing.
"""

import asyncio
import logging
import argparse
from pathlib import Path
from typing import Any, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image
import pillow_avif  # noqa: F401

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route
import uvicorn

# Configuration
SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}
MAX_FILE_SIZE_MB = 100  # Maximum file size in MB
MAX_DIMENSION = 10000  # Maximum width or height

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class ImageConversionError(Exception):
    """Custom exception for image conversion errors"""
    pass


class ValidationError(Exception):
    """Custom exception for input validation errors"""
    pass


def validate_path(path: Path, must_exist: bool = True) -> Path:
    """Validate and sanitize file paths."""
    try:
        abs_path = path.resolve()
        if must_exist and not abs_path.exists():
            raise ValidationError(f"Path does not exist: {path}")
        return abs_path
    except Exception as e:
        raise ValidationError(f"Invalid path: {path} - {str(e)}")


def validate_file_size(path: Path, max_size_mb: int = MAX_FILE_SIZE_MB) -> None:
    """Validate file size."""
    if not path.exists():
        return
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        raise ValidationError(
            f"File too large: {file_size_mb:.2f}MB (max: {max_size_mb}MB)"
        )


def validate_image_dimensions(img: Image.Image) -> None:
    """Validate image dimensions."""
    width, height = img.size
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValidationError(
            f"Image dimensions too large: {width}x{height} (max: {MAX_DIMENSION})"
        )


def validate_params(arguments: dict[str, Any]) -> None:
    """Validate tool parameters."""
    if "input_path" not in arguments:
        raise ValidationError("Missing required parameter: input_path")
        
    format_type = arguments.get("format", "both")
    if format_type not in ("webp", "avif", "both"):
        raise ValidationError(f"Invalid format: {format_type}")
        
    try:
        webp_quality = int(arguments.get("webp_quality", 80))
        avif_quality = int(arguments.get("avif_quality", 50))
    except (ValueError, TypeError):
        raise ValidationError("Quality must be an integer")
    
    if not 1 <= webp_quality <= 100:
        raise ValidationError(f"webp_quality must be 1-100, got {webp_quality}")
    if not 1 <= avif_quality <= 100:
        raise ValidationError(f"avif_quality must be 1-100, got {avif_quality}")
    
    # Mode validation
    mode = arguments.get("mode")
    if mode and mode not in ("single", "batch"):
        raise ValidationError(f"Invalid mode: {mode}")


def load_image(path: Path) -> Image.Image:
    """Load and validate image."""
    try:
        logger.info(f"Loading image: {path}")
        validate_file_size(path)
        img = Image.open(path).convert("RGBA")
        validate_image_dimensions(img)
        return img
    except ValidationError:
        raise
    except Exception as e:
        raise ImageConversionError(f"Failed to load image {path}: {str(e)}")


def resize_if_needed(
    img: Image.Image,
    max_width: Optional[int],
    max_height: Optional[int]
) -> Image.Image:
    """Resize image."""
    if max_width or max_height:
        original_size = img.size
        img.thumbnail(
            (max_width or img.width, max_height or img.height),
            Image.LANCZOS,
        )
        new_size = img.size
        if original_size != new_size:
            logger.info(f"Resized image from {original_size} to {new_size}")
    return img


def convert_one(
    image_path: Path,
    output_dir: Path,
    format: str,
    webp_quality: int,
    avif_quality: int,
    lossless: bool,
    max_width: Optional[int],
    max_height: Optional[int],
) -> dict[str, str]:
    """Convert one image."""
    try:
        img = load_image(image_path)
        img = resize_if_needed(img, max_width, max_height)
        results: dict[str, str] = {"input": str(image_path)}
        name = image_path.stem

        if format in ("webp", "both"):
            webp_path = output_dir / f"{name}.webp"
            img.save(webp_path, "WEBP", quality=webp_quality, lossless=lossless, method=6)
            results["webp"] = str(webp_path)

        if format in ("avif", "both"):
            avif_path = output_dir / f"{name}.avif"
            img.save(avif_path, "AVIF", quality=avif_quality, speed=4)
            results["avif"] = str(avif_path)

        return results
    except Exception as e:
        raise ImageConversionError(f"Conversion failed for {image_path}: {str(e)}")


def convert_batch_parallel(input_dir: Path, workers: Optional[int], **kwargs: Any) -> list[dict[str, str]]:
    """Batch conversion."""
    import os
    images = [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]
    if not images: return []
    results: list[dict[str, str]] = []
    max_workers = workers or os.cpu_count() or 1
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(convert_one, img, **kwargs): img for img in images}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                results.append({"input": str(futures[future]), "error": str(e)})
    return results


# Initialize MCP server
mcp_app = Server("image-convert-mcp")


@mcp_app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="convert_image_single",
            description="Convert a single image to WebP and/or AVIF format",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {"type": "string"},
                    "output_dir": {"type": "string"},
                    "format": {"type": "string", "enum": ["webp", "avif", "both"]},
                    "webp_quality": {"type": "integer", "minimum": 1, "maximum": 100},
                    "avif_quality": {"type": "integer", "minimum": 1, "maximum": 100},
                    "lossless": {"type": "boolean"},
                    "max_width": {"type": "integer"},
                    "max_height": {"type": "integer"}
                },
                "required": ["input_path"]
            }
        ),
        Tool(
            name="convert_image_batch",
            description="Convert multiple images in a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {"type": "string"},
                    "output_dir": {"type": "string"},
                    "format": {"type": "string", "enum": ["webp", "avif", "both"]},
                    "workers": {"type": "integer"}
                },
                "required": ["input_path"]
            }
        )
    ]


@mcp_app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    try:
        validate_params(arguments)
        input_path = validate_path(Path(arguments["input_path"]), must_exist=True)
        output_dir = Path(arguments.get("output_dir", input_path.parent))
        output_dir = validate_path(output_dir, must_exist=False)
        output_dir.mkdir(parents=True, exist_ok=True)

        common_args = {
            "output_dir": output_dir,
            "format": arguments.get("format", "both"),
            "webp_quality": int(arguments.get("webp_quality", 80)),
            "avif_quality": int(arguments.get("avif_quality", 50)),
            "lossless": bool(arguments.get("lossless", False)),
            "max_width": arguments.get("max_width"),
            "max_height": arguments.get("max_height"),
        }

        if name == "convert_image_batch":
            if not input_path.is_dir(): raise ValidationError("Batch mode requires directory")
            result = await asyncio.to_thread(convert_batch_parallel, input_dir=input_path, workers=arguments.get("workers"), **common_args)
            return [TextContent(type="text", text=f"Batch conversion complete: {result}")]
        elif name == "convert_image_single":
            if not input_path.is_file(): raise ValidationError("Single mode requires file")
            result = await asyncio.to_thread(convert_one, image_path=input_path, **common_args)
            return [TextContent(type="text", text=f"Image conversion successful: {result}")]
        raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


# --- Web Server Setup (for SSE/Vercel) ---

sse = SseServerTransport(endpoint="/mcp")

async def handle_mcp(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (r, w):
        await mcp_app.run(r, w, mcp_app.create_initialization_options())

async def handle_messages(request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

# Global app for Vercel/Starlette
app = Starlette(
    routes=[
        Route("/mcp", endpoint=handle_mcp, methods=["GET"]),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
    ]
)

# Alias for compatibility if needed
handler = app

async def run_stdio():
    async with stdio_server() as (r, w):
        await mcp_app.run(r, w, mcp_app.create_initialization_options())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.transport == "stdio":
        asyncio.run(run_stdio())
    else:
        logger.info(f"Starting SSE server on {args.host}:{args.port}...")
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
