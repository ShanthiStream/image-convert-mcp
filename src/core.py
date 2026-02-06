"""
Core image conversion functionality.

This module provides the core image conversion logic for converting images
to WebP and AVIF formats with support for resizing and quality control.
"""

import logging
from pathlib import Path
from typing import Any, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image
import pillow_avif  # noqa: F401

from .validation import (
    validate_file_size,
    validate_image_dimensions,
    ImageConversionError,
)

# Configuration
SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}

# Setup logging
logger = logging.getLogger(__name__)


def load_image(path: Path) -> Image.Image:
    """
    Load and validate an image file.
    
    Args:
        path: Path to the image file
        
    Returns:
        PIL Image object in RGBA mode
        
    Raises:
        ImageConversionError: If image cannot be loaded or is invalid
    """
    try:
        logger.info(f"Loading image: {path}")
        validate_file_size(path)
        img = Image.open(path).convert("RGBA")
        validate_image_dimensions(img)
        return img
    except ImageConversionError:
        raise
    except Exception as e:
        raise ImageConversionError(f"Failed to load image {path}: {str(e)}")


def resize_if_needed(
    img: Image.Image,
    max_width: Optional[int],
    max_height: Optional[int]
) -> Image.Image:
    """
    Resize image if it exceeds maximum dimensions.
    
    Args:
        img: PIL Image object
        max_width: Maximum width (None for no limit)
        max_height: Maximum height (None for no limit)
        
    Returns:
        Resized PIL Image object (or original if no resize needed)
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
        webp_quality: WebP quality (1-100)
        avif_quality: AVIF quality (1-100)
        lossless: Enable lossless compression for WebP
        max_width: Maximum output width
        max_height: Maximum output height
        
    Returns:
        Dictionary with conversion results
        
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
            img.save(webp_path, "WEBP", quality=webp_quality, lossless=lossless, method=6)
            results["webp"] = str(webp_path)
            logger.info(f"Created WebP: {webp_path}")

        if format in ("avif", "both"):
            avif_path = output_dir / f"{name}.avif"
            img.save(avif_path, "AVIF", quality=avif_quality, speed=4)
            results["avif"] = str(avif_path)
            logger.info(f"Created AVIF: {avif_path}")

        return results
    except Exception as e:
        raise ImageConversionError(f"Conversion failed for {image_path}: {str(e)}")


def convert_batch_parallel(
    input_dir: Path,
    workers: Optional[int],
    **kwargs: Any
) -> list[dict[str, str]]:
    """
    Convert multiple images in parallel.
    
    Args:
        input_dir: Directory containing input images
        workers: Number of parallel workers (None for CPU count)
        **kwargs: Additional arguments passed to convert_one()
        
    Returns:
        List of conversion results for each image
    """
    import os
    
    images = [
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    ]
    
    if not images:
        logger.warning(f"No supported images found in {input_dir}")
        return []
    
    results: list[dict[str, str]] = []
    max_workers = workers or os.cpu_count() or 1
    
    logger.info(f"Processing {len(images)} images with {max_workers} workers")
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(convert_one, img, **kwargs): img
            for img in images
        }
        
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                img_path = futures[future]
                logger.error(f"Failed to convert {img_path}: {e}")
                results.append({"input": str(img_path), "error": str(e)})
    
    return results
