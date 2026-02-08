"""
Compression statistics for image conversion.

This module provides utilities for calculating and formatting
file size savings from image conversion.
"""

import os
from pathlib import Path
from typing import Optional


def get_file_size(path: Path) -> int:
    """Get file size in bytes."""
    return os.path.getsize(path)


def format_size(size_bytes: int) -> str:
    """
    Format byte size to human readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human readable size string (e.g., "1.5 MB", "256 KB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def calculate_savings(original_size: int, new_size: int) -> dict[str, str]:
    """
    Calculate compression savings.
    
    Args:
        original_size: Original file size in bytes
        new_size: New file size in bytes
        
    Returns:
        Dictionary with:
        - original_size: Formatted original size
        - new_size: Formatted new size
        - saved_bytes: Formatted bytes saved
        - savings_percent: Percentage saved (e.g., "75%")
        - compression_ratio: Compression ratio (e.g., "4:1")
    """
    saved = original_size - new_size
    
    if original_size > 0:
        percent = (saved / original_size) * 100
        ratio = original_size / new_size if new_size > 0 else float('inf')
    else:
        percent = 0
        ratio = 1
    
    return {
        "original_size": format_size(original_size),
        "new_size": format_size(new_size),
        "saved_bytes": format_size(abs(saved)),
        "savings_percent": f"{percent:.1f}%",
        "compression_ratio": f"{ratio:.1f}:1" if ratio != float('inf') else "∞:1",
        "increased": saved < 0,  # True if file got larger
    }


def get_conversion_stats(
    input_path: Path,
    webp_path: Optional[Path] = None,
    avif_path: Optional[Path] = None,
) -> dict[str, any]:
    """
    Get comprehensive statistics for a conversion.
    
    Args:
        input_path: Original input file path
        webp_path: Output WebP file path (if created)
        avif_path: Output AVIF file path (if created)
        
    Returns:
        Dictionary with input size and stats for each output format
    """
    try:
        original_size = get_file_size(input_path)
    except (OSError, IOError):
        return {"error": f"Could not read input file: {input_path}"}
    
    stats = {
        "input": str(input_path),
        "input_size": format_size(original_size),
        "input_size_bytes": original_size,
    }
    
    if webp_path and webp_path.exists():
        webp_size = get_file_size(webp_path)
        stats["webp"] = {
            "path": str(webp_path),
            **calculate_savings(original_size, webp_size),
        }
    
    if avif_path and avif_path.exists():
        avif_size = get_file_size(avif_path)
        stats["avif"] = {
            "path": str(avif_path),
            **calculate_savings(original_size, avif_size),
        }
    
    # Determine best format
    if "webp" in stats and "avif" in stats:
        webp_size = get_file_size(webp_path)
        avif_size = get_file_size(avif_path)
        stats["best_format"] = "avif" if avif_size < webp_size else "webp"
    elif "webp" in stats:
        stats["best_format"] = "webp"
    elif "avif" in stats:
        stats["best_format"] = "avif"
    
    return stats


def format_stats_summary(stats: dict) -> str:
    """
    Format conversion stats as a human-readable summary.
    
    Args:
        stats: Stats dictionary from get_conversion_stats
        
    Returns:
        Formatted multi-line string summary
    """
    if "error" in stats:
        return f"❌ {stats['error']}"
    
    lines = [
        "📊 Compression Statistics",
        f"   Input: {stats['input_size']}",
    ]
    
    if "webp" in stats:
        webp = stats["webp"]
        emoji = "📈" if webp["increased"] else "📉"
        lines.append(f"   {emoji} WebP: {webp['new_size']} ({webp['savings_percent']} saved)")
    
    if "avif" in stats:
        avif = stats["avif"]
        emoji = "📈" if avif["increased"] else "📉"
        lines.append(f"   {emoji} AVIF: {avif['new_size']} ({avif['savings_percent']} saved)")
    
    if "best_format" in stats:
        lines.append(f"   🏆 Best: {stats['best_format'].upper()}")
    
    return "\n".join(lines)
