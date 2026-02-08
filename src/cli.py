"""
Command-line interface for image-convert-mcp.

Provides direct image conversion without running as an MCP server.

Usage:
    image-convert input.png -f webp -q 80
    image-convert ./images/ --batch -f both --preset web
    image-convert input.png --preset thumbnail
"""

import argparse
import sys
import logging
from pathlib import Path

from .core import convert_one, convert_batch_parallel, SUPPORTED_EXTS
from .validation import validate_path, validate_params, ValidationError
from .presets import get_preset, list_presets, PRESETS
from .stats import get_conversion_stats, format_stats_summary


def setup_logging(verbose: bool) -> None:
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="image-convert",
        description="Convert images to WebP and AVIF formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  image-convert photo.png                    # Convert to both WebP and AVIF
  image-convert photo.png -f webp            # Convert to WebP only
  image-convert photo.png --preset thumbnail # Use thumbnail preset
  image-convert ./images/ --batch            # Batch convert directory
  image-convert --list-presets               # Show available presets
        """,
    )
    
    parser.add_argument(
        "input",
        nargs="?",
        help="Input image file or directory (for batch mode)",
    )
    
    parser.add_argument(
        "-o", "--output",
        dest="output_dir",
        help="Output directory (default: same as input)",
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["webp", "avif", "both"],
        default="both",
        help="Output format (default: both)",
    )
    
    parser.add_argument(
        "-q", "--quality",
        type=int,
        metavar="N",
        help="Quality for both formats (1-100, default: 80 for WebP, 50 for AVIF)",
    )
    
    parser.add_argument(
        "--webp-quality",
        type=int,
        default=80,
        metavar="N",
        help="WebP quality 1-100 (default: 80)",
    )
    
    parser.add_argument(
        "--avif-quality",
        type=int,
        default=50,
        metavar="N",
        help="AVIF quality 1-100 (default: 50)",
    )
    
    parser.add_argument(
        "-l", "--lossless",
        action="store_true",
        help="Enable lossless WebP compression",
    )
    
    parser.add_argument(
        "-W", "--max-width",
        type=int,
        metavar="PX",
        help="Maximum output width (maintains aspect ratio)",
    )
    
    parser.add_argument(
        "-H", "--max-height",
        type=int,
        metavar="PX",
        help="Maximum output height (maintains aspect ratio)",
    )
    
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch process a directory",
    )
    
    parser.add_argument(
        "-w", "--workers",
        type=int,
        help="Number of parallel workers for batch mode (default: CPU count)",
    )
    
    parser.add_argument(
        "-p", "--preset",
        choices=list(PRESETS.keys()),
        help="Use a named preset (overrides other quality/size options)",
    )
    
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List available presets and exit",
    )
    
    parser.add_argument(
        "-s", "--stats",
        action="store_true",
        help="Show compression statistics",
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    
    parser.add_argument(
        "-V", "--version",
        action="version",
        version="%(prog)s 0.2.0",
    )
    
    return parser


def print_presets() -> None:
    """Print available presets."""
    print("Available presets:\n")
    for name, desc in list_presets().items():
        print(f"  {name:15} {desc}")
    print("\nUsage: image-convert input.png --preset <preset-name>")


def convert_single(args: argparse.Namespace) -> int:
    """Handle single file conversion."""
    input_path = validate_path(Path(args.input), must_exist=True)
    output_dir = Path(args.output_dir) if args.output_dir else input_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build conversion args
    kwargs = {
        "output_dir": output_dir,
        "format": args.format,
        "webp_quality": args.webp_quality,
        "avif_quality": args.avif_quality,
        "lossless": args.lossless,
        "max_width": args.max_width,
        "max_height": args.max_height,
    }
    
    # Apply preset if specified
    if args.preset:
        preset = get_preset(args.preset)
        kwargs.update(preset)
    
    # Override with explicit quality if specified
    if args.quality:
        kwargs["webp_quality"] = args.quality
        kwargs["avif_quality"] = args.quality
    
    result = convert_one(image_path=input_path, **kwargs)
    
    print(f"✅ Converted: {input_path.name}")
    
    if "webp" in result:
        print(f"   → WebP: {result['webp']}")
    if "avif" in result:
        print(f"   → AVIF: {result['avif']}")
    
    # Show stats if requested
    if args.stats:
        webp_path = Path(result["webp"]) if "webp" in result else None
        avif_path = Path(result["avif"]) if "avif" in result else None
        stats = get_conversion_stats(input_path, webp_path, avif_path)
        print()
        print(format_stats_summary(stats))
    
    return 0


def convert_batch(args: argparse.Namespace) -> int:
    """Handle batch directory conversion."""
    input_dir = validate_path(Path(args.input), must_exist=True)
    
    if not input_dir.is_dir():
        print(f"❌ Error: {input_dir} is not a directory", file=sys.stderr)
        return 1
    
    output_dir = Path(args.output_dir) if args.output_dir else input_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build conversion args
    kwargs = {
        "output_dir": output_dir,
        "format": args.format,
        "webp_quality": args.webp_quality,
        "avif_quality": args.avif_quality,
        "lossless": args.lossless,
        "max_width": args.max_width,
        "max_height": args.max_height,
    }
    
    # Apply preset if specified
    if args.preset:
        preset = get_preset(args.preset)
        kwargs.update(preset)
    
    # Override with explicit quality if specified
    if args.quality:
        kwargs["webp_quality"] = args.quality
        kwargs["avif_quality"] = args.quality
    
    results = convert_batch_parallel(
        input_dir=input_dir,
        workers=args.workers,
        **kwargs,
    )
    
    success_count = sum(1 for r in results if "error" not in r)
    error_count = len(results) - success_count
    
    print(f"✅ Batch conversion complete: {success_count} succeeded, {error_count} failed")
    
    if error_count > 0:
        print("\nFailed conversions:")
        for r in results:
            if "error" in r:
                print(f"   ❌ {r['input']}: {r['error']}")
    
    return 0 if error_count == 0 else 1


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle list presets
    if args.list_presets:
        print_presets()
        return 0
    
    # Require input for conversion
    if not args.input:
        parser.print_help()
        return 1
    
    setup_logging(args.verbose)
    
    try:
        if args.batch:
            return convert_batch(args)
        else:
            return convert_single(args)
    except ValidationError as e:
        print(f"❌ Validation error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
