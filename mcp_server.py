"""
Image Convert MCP Server

A Model Context Protocol server for converting images to WebP and AVIF formats
with support for both single file and batch directory processing.
"""

import sys
import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image
import pillow_avif  # noqa: F401

# Configuration
SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}
MAX_FILE_SIZE_MB = 100  # Maximum file size in MB
MAX_DIMENSION = 10000  # Maximum width or height

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
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
) -> Dict[str, str]:
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

        results: Dict[str, str] = {"input": str(image_path)}
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
) -> List[Dict[str, str]]:
    """
    Convert multiple images in parallel from a directory.
    
    Args:
        input_dir: Directory containing input images
        workers: Number of parallel workers (None for auto)
        **kwargs: Arguments passed to convert_one()
        
    Returns:
        List of result dictionaries (one per image)
    """
    images = [
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    ]

    logger.info(f"Found {len(images)} images to convert")
    
    if not images:
        logger.warning(f"No supported images found in {input_dir}")
        return []

    results: List[Dict[str, str]] = []
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


def validate_params(params: Dict[str, Any]) -> None:
    """
    Validate input parameters.
    
    Args:
        params: Parameter dictionary
        
    Raises:
        ValidationError: If parameters are invalid
    """
    if "input_path" not in params:
        raise ValidationError("Missing required parameter: input_path")
    
    mode = params.get("mode", "single")
    if mode not in ("single", "batch"):
        raise ValidationError(f"Invalid mode: {mode} (must be 'single' or 'batch')")
    
    format_type = params.get("format", "both")
    if format_type not in ("webp", "avif", "both"):
        raise ValidationError(
            f"Invalid format: {format_type} (must be 'webp', 'avif', or 'both')"
        )
    
    # Validate quality settings
    webp_quality = params.get("webp_quality", 80)
    if not 1 <= webp_quality <= 100:
        raise ValidationError(f"webp_quality must be 1-100, got {webp_quality}")
    
    avif_quality = params.get("avif_quality", 50)
    if not 1 <= avif_quality <= 100:
        raise ValidationError(f"avif_quality must be 1-100, got {avif_quality}")


def main() -> None:
    """Main entry point for MCP server."""
    try:
        request = json.loads(sys.stdin.read())
        params = request.get("params", {})
        
        logger.info("Received conversion request")
        
        # Validate parameters
        validate_params(params)

        mode = params.get("mode", "single")
        format_type = params.get("format", "both")

        # Validate and resolve paths
        input_path = validate_path(Path(params["input_path"]), must_exist=True)
        output_dir = Path(params.get("output_dir", input_path.parent))
        output_dir = validate_path(output_dir, must_exist=False)
        output_dir.mkdir(parents=True, exist_ok=True)

        common_args = dict(
            output_dir=output_dir,
            format=format_type,
            webp_quality=params.get("webp_quality", 80),
            avif_quality=params.get("avif_quality", 50),
            lossless=params.get("lossless", False),
            max_width=params.get("max_width"),
            max_height=params.get("max_height"),
        )

        if mode == "batch":
            if not input_path.is_dir():
                raise ValidationError("Batch mode requires a directory as input_path")

            result = convert_batch_parallel(
                input_dir=input_path,
                workers=params.get("workers"),
                **common_args,
            )
        else:
            if not input_path.is_file():
                raise ValidationError("Single mode requires a file as input_path")

            result = convert_one(
                image_path=input_path,
                **common_args,
            )

        # Return success response
        response = {"status": "success", "result": result}
        print(json.dumps(response))
        logger.info("Conversion completed successfully")
        
    except ValidationError as e:
        error_response = {
            "status": "error",
            "error_type": "validation_error",
            "error": str(e)
        }
        print(json.dumps(error_response))
        logger.error(f"Validation error: {e}")
        sys.exit(1)
        
    except ImageConversionError as e:
        error_response = {
            "status": "error",
            "error_type": "conversion_error",
            "error": str(e)
        }
        print(json.dumps(error_response))
        logger.error(f"Conversion error: {e}")
        sys.exit(1)
        
    except Exception as e:
        error_response = {
            "status": "error",
            "error_type": "unexpected_error",
            "error": str(e)
        }
        print(json.dumps(error_response))
        logger.exception("Unexpected error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()
