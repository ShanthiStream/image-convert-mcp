"""
Image Convert MCP Server

A Model Context Protocol server for converting images to WebP and AVIF formats
with support for both single file and batch directory processing.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image
import pillow_avif  # noqa: F401

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

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
    """
    Validate and sanitize file paths to prevent directory traversal attacks.
    
    Args:
        path: Path to validate
        must_exist: Whether the path must already exist
        
    Returns:
        Validated absolute path
        
    Raises:
        ValidationError: If path is invalid or doesn't exist when required
    """
    try:
        abs_path = path.resolve()
        
        # Prevent directory traversal
        if must_exist and not abs_path.exists():
            raise ValidationError(f"Path does not exist: {path}")
            
        return abs_path
    except Exception as e:
        raise ValidationError(f"Invalid path: {path} - {str(e)}")


def validate_file_size(path: Path, max_size_mb: int = MAX_FILE_SIZE_MB) -> None:
    """
    Validate file size is within acceptable limits.
    
    Args:
        path: File path to check
        max_size_mb: Maximum allowed file size in MB
        
    Raises:
        ValidationError: If file is too large
    """
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        raise ValidationError(
            f"File too large: {file_size_mb:.2f}MB (max: {max_size_mb}MB)"
        )


def validate_image_dimensions(img: Image.Image) -> None:
    """
    Validate image dimensions are within acceptable limits.
    
    Args:
        img: PIL Image object
        
    Raises:
        ValidationError: If dimensions exceed maximum
    """
    width, height = img.size
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValidationError(
            f"Image dimensions too large: {width}x{height} (max: {MAX_DIMENSION})"
        )


def load_image(path: Path) -> Image.Image:
    """
    Load and validate an image file.
    
    Args:
        path: Path to image file
        
    Returns:
        PIL Image object in RGBA mode
        
    Raises:
        ImageConversionError: If image cannot be loaded
        ValidationError: If image fails validation
    """
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
    """
    Resize image if dimensions exceed specified maximums.
    
    Args:
        img: PIL Image object
        max_width: Maximum width (None for no limit)
        max_height: Maximum height (None for no limit)
        
    Returns:
        Resized image (or original if no resize needed)
    """
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
    """
    Convert a single image to WebP and/or AVIF format.
    
    Args:
        image_path: Path to input image
        output_dir: Directory for output files
        format: Output format ('webp', 'avif', or 'both')
        webp_quality: WebP quality setting (1-100)
        avif_quality: AVIF quality setting (1-100)
        lossless: Enable lossless compression for WebP
        max_width: Maximum output width
        max_height: Maximum output height
        
    Returns:
        Dictionary with input path and output path(s)
        
    Raises:
        ImageConversionError: If conversion fails
    """
    try:
        img = load_image(image_path)
        img = resize_if_needed(img, max_width, max_height)

        results: dict[str, str] = {"input": str(image_path)}
        name = image_path.stem

        if format in ("webp", "both"):
            webp_path = output_dir / f"{name}.webp"
            logger.info(f"Converting to WebP: {webp_path}")
            img.save(
                webp_path,
                "WEBP",
                quality=webp_quality,
                lossless=lossless,
                method=6,
            )
            results["webp"] = str(webp_path)
            logger.info(f"WebP conversion complete: {webp_path}")

        if format in ("avif", "both"):
            avif_path = output_dir / f"{name}.avif"
            logger.info(f"Converting to AVIF: {avif_path}")
            img.save(
                avif_path,
                "AVIF",
                quality=avif_quality,
                speed=4,
            )
            results["avif"] = str(avif_path)
            logger.info(f"AVIF conversion complete: {avif_path}")

        return results
    except (ValidationError, ImageConversionError):
        raise
    except Exception as e:
        raise ImageConversionError(f"Conversion failed for {image_path}: {str(e)}")


def convert_batch_parallel(
    input_dir: Path,
    workers: Optional[int],
    **kwargs: Any,
) -> list[dict[str, str]]:
    """
    Convert multiple images in parallel from a directory.
    
    Args:
        input_dir: Directory containing input images
        workers: Number of parallel workers (None for auto)
        **kwargs: Arguments passed to convert_one()
        
    Returns:
        List of result dictionaries (one per image)
    """
    import os
    
    images = [
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    ]

    logger.info(f"Found {len(images)} images to convert")
    
    if not images:
        logger.warning(f"No supported images found in {input_dir}")
        return []

    results: list[dict[str, str]] = []
    max_workers = workers or os.cpu_count() or 1
    
    logger.info(f"Starting batch conversion with {max_workers} workers")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(convert_one, img, **kwargs): img
            for img in images
        }

        completed = 0
        total = len(futures)
        
        for future in as_completed(futures):
            completed += 1
            try:
                result = future.result()
                results.append(result)
                logger.info(f"Progress: {completed}/{total} images processed")
            except Exception as e:
                img_path = futures[future]
                error_msg = str(e)
                logger.error(f"Failed to convert {img_path}: {error_msg}")
                results.append({
                    "input": str(img_path),
                    "error": error_msg,
                })

    logger.info(f"Batch conversion complete: {completed} images processed")
    return results


# Initialize MCP server
app = Server("image-convert-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available image conversion tools."""
    return [
        Tool(
            name="convert_image_single",
            description="Convert a single image to WebP and/or AVIF format",
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
                        "default": "both",
                        "description": "Output format"
                    },
                    "webp_quality": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 80,
                        "description": "WebP quality (1-100)"
                    },
                    "avif_quality": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 50,
                        "description": "AVIF quality (1-100)"
                    },
                    "lossless": {
                        "type": "boolean",
                        "default": False,
                        "description": "Enable lossless compression for WebP"
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
            description="Convert multiple images in a directory to WebP and/or AVIF format",
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
                        "default": "both",
                        "description": "Output format"
                    },
                    "webp_quality": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 80,
                        "description": "WebP quality (1-100)"
                    },
                    "avif_quality": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 50,
                        "description": "AVIF quality (1-100)"
                    },
                    "lossless": {
                        "type": "boolean",
                        "default": False,
                        "description": "Enable lossless compression for WebP"
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
    """Handle tool calls for image conversion."""
    try:
        # Extract and validate parameters
        input_path = validate_path(Path(arguments["input_path"]), must_exist=True)
        output_dir = Path(arguments.get("output_dir", input_path.parent))
        output_dir = validate_path(output_dir, must_exist=False)
        output_dir.mkdir(parents=True, exist_ok=True)

        format_type = arguments.get("format", "both")
        webp_quality = arguments.get("webp_quality", 80)
        avif_quality = arguments.get("avif_quality", 50)
        lossless = arguments.get("lossless", False)
        max_width = arguments.get("max_width")
        max_height = arguments.get("max_height")

        # Validate quality settings
        if not 1 <= webp_quality <= 100:
            raise ValidationError(f"webp_quality must be 1-100, got {webp_quality}")
        if not 1 <= avif_quality <= 100:
            raise ValidationError(f"avif_quality must be 1-100, got {avif_quality}")

        common_args = {
            "output_dir": output_dir,
            "format": format_type,
            "webp_quality": webp_quality,
            "avif_quality": avif_quality,
            "lossless": lossless,
            "max_width": max_width,
            "max_height": max_height,
        }

        # Route to appropriate handler
        if name == "convert_image_batch":
            if not input_path.is_dir():
                raise ValidationError("Batch mode requires a directory as input_path")
            
            workers = arguments.get("workers")
            result = await asyncio.to_thread(
                convert_batch_parallel,
                input_dir=input_path,
                workers=workers,
                **common_args,
            )
            
            # Format batch results
            success_count = sum(1 for r in result if "error" not in r)
            error_count = len(result) - success_count
            
            response = f"Batch conversion complete!\n"
            response += f"✅ Successfully converted: {success_count} images\n"
            if error_count > 0:
                response += f"❌ Failed: {error_count} images\n"
            response += f"\nResults:\n{result}"
            
        elif name == "convert_image_single":
            if not input_path.is_file():
                raise ValidationError("Single mode requires a file as input_path")
            
            result = await asyncio.to_thread(
                convert_one,
                image_path=input_path,
                **common_args,
            )
            
            response = f"✅ Image conversion successful!\n\n"
            response += f"Input: {result['input']}\n"
            if "webp" in result:
                response += f"WebP: {result['webp']}\n"
            if "avif" in result:
                response += f"AVIF: {result['avif']}\n"
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=response)]

    except ValidationError as e:
        error_msg = f"❌ Validation Error: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]
    
    except ImageConversionError as e:
        error_msg = f"❌ Conversion Error: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]
    
    except Exception as e:
        error_msg = f"❌ Unexpected Error: {str(e)}"
        logger.exception("Unexpected error in tool call")
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
