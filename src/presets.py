"""
Presets for common image conversion scenarios.

This module provides predefined conversion settings for common use cases,
making it easy to apply optimal settings without manual configuration.
"""

from typing import TypedDict, Optional


class PresetConfig(TypedDict, total=False):
    """Type definition for preset configuration."""
    format: str
    webp_quality: int
    avif_quality: int
    lossless: bool
    max_width: Optional[int]
    max_height: Optional[int]


# Predefined conversion presets
PRESETS: dict[str, PresetConfig] = {
    "web": {
        "format": "webp",
        "webp_quality": 80,
        "avif_quality": 50,
        "lossless": False,
        "max_width": 1920,
        "max_height": None,
    },
    "thumbnail": {
        "format": "webp",
        "webp_quality": 70,
        "avif_quality": 50,
        "lossless": False,
        "max_width": 300,
        "max_height": 300,
    },
    "social": {
        "format": "webp",
        "webp_quality": 85,
        "avif_quality": 50,
        "lossless": False,
        "max_width": 1200,
        "max_height": 630,
    },
    "hd": {
        "format": "webp",
        "webp_quality": 90,
        "avif_quality": 80,
        "lossless": False,
        "max_width": 1920,
        "max_height": 1080,
    },
    "4k": {
        "format": "webp",
        "webp_quality": 90,
        "avif_quality": 80,
        "lossless": False,
        "max_width": 3840,
        "max_height": 2160,
    },
    "archive": {
        "format": "both",
        "webp_quality": 95,
        "avif_quality": 90,
        "lossless": False,
        "max_width": None,
        "max_height": None,
    },
    "lossless": {
        "format": "webp",
        "webp_quality": 100,
        "avif_quality": 100,
        "lossless": True,
        "max_width": None,
        "max_height": None,
    },
    "max-compression": {
        "format": "avif",
        "webp_quality": 50,
        "avif_quality": 40,
        "lossless": False,
        "max_width": None,
        "max_height": None,
    },
}


def get_preset(name: str) -> PresetConfig:
    """
    Get a preset configuration by name.
    
    Args:
        name: Preset name (web, thumbnail, social, hd, 4k, archive, lossless, max-compression)
        
    Returns:
        PresetConfig dictionary with conversion settings
        
    Raises:
        ValueError: If preset name is not found
    """
    if name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{name}'. Available presets: {available}")
    return PRESETS[name].copy()


def list_presets() -> dict[str, str]:
    """
    List all available presets with descriptions.
    
    Returns:
        Dictionary mapping preset names to descriptions
    """
    descriptions = {
        "web": "Optimized for web pages (WebP, quality 80, max 1920px wide)",
        "thumbnail": "Small thumbnails (WebP, quality 70, max 300x300)",
        "social": "Social media images (WebP, quality 85, 1200x630)",
        "hd": "HD resolution (WebP, quality 90, 1920x1080)",
        "4k": "4K resolution (WebP, quality 90, 3840x2160)",
        "archive": "High quality archival (Both formats, quality 95/90)",
        "lossless": "Lossless WebP compression (no quality loss)",
        "max-compression": "Maximum file size reduction (AVIF, quality 40)",
    }
    return descriptions
