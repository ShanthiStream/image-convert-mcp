"""
Image Convert MCP - Core functionality.

This package provides image conversion capabilities for WebP and AVIF formats.
"""

from .core import (
    load_image,
    resize_if_needed,
    convert_one,
    convert_batch_parallel,
    SUPPORTED_EXTS,
)

from .validation import (
    validate_path,
    validate_file_size,
    validate_image_dimensions,
    validate_params,
    ValidationError,
    ImageConversionError,
    MAX_FILE_SIZE_MB,
    MAX_DIMENSION,
)

__all__ = [
    # Core functions
    "load_image",
    "resize_if_needed",
    "convert_one",
    "convert_batch_parallel",
    "SUPPORTED_EXTS",
    # Validation functions
    "validate_path",
    "validate_file_size",
    "validate_image_dimensions",
    "validate_params",
    # Exceptions
    "ValidationError",
    "ImageConversionError",
    # Constants
    "MAX_FILE_SIZE_MB",
    "MAX_DIMENSION",
]
