"""
Input validation and security checks.

This module provides validation functions for file paths, sizes, dimensions,
and parameters to ensure safe and correct operation.
"""

from pathlib import Path
from typing import Any
from PIL import Image

# Security limits
MAX_FILE_SIZE_MB = 100
MAX_DIMENSION = 10000


class ImageConversionError(Exception):
    """Custom exception for image conversion errors."""
    pass


class ValidationError(Exception):
    """Custom exception for input validation errors."""
    pass


def validate_path(path: Path, must_exist: bool = True) -> Path:
    """
    Validate and sanitize file paths.
    
    Args:
        path: Path to validate
        must_exist: Whether the path must exist
        
    Returns:
        Resolved absolute path
        
    Raises:
        ValidationError: If path is invalid or doesn't exist when required
    """
    try:
        abs_path = path.resolve()
        if must_exist and not abs_path.exists():
            raise ValidationError(f"Path does not exist: {path}")
        return abs_path
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Invalid path: {path} - {str(e)}")


def validate_file_size(path: Path, max_size_mb: int = MAX_FILE_SIZE_MB) -> None:
    """
    Validate file size against maximum limit.
    
    Args:
        path: Path to file
        max_size_mb: Maximum allowed size in MB
        
    Raises:
        ValidationError: If file exceeds size limit
    """
    if not path.exists():
        return
        
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        raise ValidationError(
            f"File too large: {file_size_mb:.2f}MB (max: {max_size_mb}MB)"
        )


def validate_image_dimensions(img: Image.Image) -> None:
    """
    Validate image dimensions against maximum limits.
    
    Args:
        img: PIL Image object
        
    Raises:
        ValidationError: If image dimensions exceed limits
    """
    width, height = img.size
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValidationError(
            f"Image dimensions too large: {width}x{height} (max: {MAX_DIMENSION})"
        )


def validate_params(arguments: dict[str, Any]) -> None:
    """
    Validate tool parameters.
    
    Args:
        arguments: Dictionary of parameters to validate
        
    Raises:
        ValidationError: If parameters are invalid
    """
    if "input_path" not in arguments:
        raise ValidationError("Missing required parameter: input_path")
        
    format_type = arguments.get("format", "both")
    if format_type not in ("webp", "avif", "both"):
        raise ValidationError(f"Invalid format: {format_type}")
        
    webp_quality = arguments.get("webp_quality", 80)
    avif_quality = arguments.get("avif_quality", 50)
    
    if not 1 <= webp_quality <= 100:
        raise ValidationError(f"webp_quality must be 1-100, got {webp_quality}")
    if not 1 <= avif_quality <= 100:
        raise ValidationError(f"avif_quality must be 1-100, got {avif_quality}")
    
    mode = arguments.get("mode")
    if mode and mode not in ("single", "batch"):
        raise ValidationError(f"Invalid mode: {mode}")
