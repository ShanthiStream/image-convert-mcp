"""
Image Convert API for Vercel

A REST API wrapper for image conversion tools, optimized for Vercel's serverless platform.
"""

import logging
from pathlib import Path
from typing import Any, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image
import pillow_avif  # noqa: F401

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Configuration
SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}
MAX_FILE_SIZE_MB = 100
MAX_DIMENSION = 10000

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


# --- REST API Endpoints ---

async def list_tools_endpoint(request: Request):
    """List available conversion tools."""
    tools = [
        {
            "name": "convert_image_single",
            "description": "Convert a single image to WebP and/or AVIF format",
            "endpoint": "/api/convert/single",
            "method": "POST",
            "parameters": {
                "input_path": "string (required)",
                "output_dir": "string (optional)",
                "format": "webp|avif|both (optional, default: both)",
                "webp_quality": "integer 1-100 (optional, default: 80)",
                "avif_quality": "integer 1-100 (optional, default: 50)",
                "lossless": "boolean (optional, default: false)",
                "max_width": "integer (optional)",
                "max_height": "integer (optional)"
            }
        },
        {
            "name": "convert_image_batch",
            "description": "Convert multiple images in a directory",
            "endpoint": "/api/convert/batch",
            "method": "POST",
            "parameters": {
                "input_path": "string (required, directory path)",
                "output_dir": "string (optional)",
                "format": "webp|avif|both (optional, default: both)",
                "workers": "integer (optional)"
            }
        }
    ]
    return JSONResponse({"tools": tools, "status": "success"})


async def convert_single_endpoint(request: Request):
    """Convert a single image."""
    try:
        data = await request.json()
        validate_params(data)
        
        input_path = validate_path(Path(data["input_path"]), must_exist=True)
        output_dir = Path(data.get("output_dir", input_path.parent))
        output_dir = validate_path(output_dir, must_exist=False)
        output_dir.mkdir(parents=True, exist_ok=True)

        if not input_path.is_file():
            raise ValidationError("Single mode requires a file path")

        result = convert_one(
            image_path=input_path,
            output_dir=output_dir,
            format=data.get("format", "both"),
            webp_quality=int(data.get("webp_quality", 80)),
            avif_quality=int(data.get("avif_quality", 50)),
            lossless=bool(data.get("lossless", False)),
            max_width=data.get("max_width"),
            max_height=data.get("max_height"),
        )
        
        return JSONResponse({"result": result, "status": "success"})
    except (ValidationError, ImageConversionError) as e:
        return JSONResponse({"error": str(e), "status": "error"}, status_code=400)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JSONResponse({"error": "Internal server error", "status": "error"}, status_code=500)


async def convert_batch_endpoint(request: Request):
    """Convert multiple images in a directory."""
    try:
        data = await request.json()
        validate_params(data)
        
        input_path = validate_path(Path(data["input_path"]), must_exist=True)
        output_dir = Path(data.get("output_dir", input_path))
        output_dir = validate_path(output_dir, must_exist=False)
        output_dir.mkdir(parents=True, exist_ok=True)

        if not input_path.is_dir():
            raise ValidationError("Batch mode requires a directory path")

        results = convert_batch_parallel(
            input_dir=input_path,
            workers=data.get("workers"),
            output_dir=output_dir,
            format=data.get("format", "both"),
            webp_quality=int(data.get("webp_quality", 80)),
            avif_quality=int(data.get("avif_quality", 50)),
            lossless=bool(data.get("lossless", False)),
            max_width=data.get("max_width"),
            max_height=data.get("max_height"),
        )
        
        return JSONResponse({"results": results, "status": "success"})
    except (ValidationError, ImageConversionError) as e:
        return JSONResponse({"error": str(e), "status": "error"}, status_code=400)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JSONResponse({"error": "Internal server error", "status": "error"}, status_code=500)


async def homepage(request: Request):
    """API homepage with documentation."""
    return JSONResponse({
        "name": "Image Convert API",
        "version": "1.0.0",
        "description": "REST API for converting images to WebP and AVIF formats",
        "endpoints": {
            "GET /": "This documentation",
            "GET /api/tools": "List available tools",
            "POST /api/convert/single": "Convert a single image",
            "POST /api/convert/batch": "Convert multiple images"
        },
        "documentation": "https://github.com/ShanthiStream/image-convert-mcp"
    })


# Create Starlette app with CORS
middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
]

app = Starlette(
    routes=[
        Route("/", endpoint=homepage, methods=["GET"]),
        Route("/api/tools", endpoint=list_tools_endpoint, methods=["GET"]),
        Route("/api/convert/single", endpoint=convert_single_endpoint, methods=["POST"]),
        Route("/api/convert/batch", endpoint=convert_batch_endpoint, methods=["POST"]),
    ],
    middleware=middleware
)

# Vercel handler
handler = app
