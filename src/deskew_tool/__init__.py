"""PDF Deskew Tool - A tool for deskewing scanned PDF documents."""

import argparse
import logging
import sys
from pathlib import Path

from .config import DeskewConfig
from .deskew_pdf import deskew_pdf

__version__ = "0.1.8"
__author__ = "driezy"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Command-line entry point for PDF deskewing."""
    parser = argparse.ArgumentParser(
        description="Deskew scanned PDF documents", prog="pdf-deskew-cli"
    )
    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument(
        "-o",
        "--output",
        help="Output PDF file path (default: input_deskewed.pdf)",
        default=None,
    )
    parser.add_argument(
        "-d", "--dpi", type=int, default=300, help="DPI for rendering (default: 300)"
    )
    parser.add_argument(
        "--bg-color",
        type=str,
        default="white",
        choices=["white", "black"],
        help="Background color (default: white)",
    )

    # Enhancement group
    enhance_group = parser.add_argument_group("Image Enhancement")
    enhance_group.add_argument(
        "--enhance", action="store_true", help="Enable image enhancement"
    )
    enhance_group.add_argument(
        "--contrast-level",
        type=int,
        default=2,
        choices=[1, 2, 3],
        help="Contrast level (1-3)",
    )
    enhance_group.add_argument(
        "--denoising",
        choices=["Gaussian", "Median"],
        default="Gaussian",
        help="Denoising method",
    )
    enhance_group.add_argument(
        "--sharpen", action="store_true", help="Enable sharpening"
    )

    # Watermark group
    watermark_group = parser.add_argument_group("Watermark Removal")
    watermark_group.add_argument(
        "--remove-watermark", action="store_true", help="Enable watermark removal"
    )
    watermark_group.add_argument(
        "--watermark-threshold",
        type=int,
        default=127,
        help="Watermark mask threshold (0-255)",
    )

    # Grayscale group
    grayscale_group = parser.add_argument_group("Grayscale Conversion")
    grayscale_group.add_argument(
        "--grayscale", action="store_true", help="Convert to grayscale"
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file does not exist: {args.input}")
        sys.exit(1)
    if not input_path.suffix.lower() == ".pdf":
        logger.error(f"Input file must be a PDF: {args.input}")
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = str(input_path.parent / f"{input_path.stem}_deskewed.pdf")

    # Parse background color
    bg_color_map = {"white": (255, 255, 255), "black": (0, 0, 0)}
    bg_color = bg_color_map.get(args.bg_color.lower(), (255, 255, 255))

    # Create config
    config = DeskewConfig(
        dpi=args.dpi,
        background_color=bg_color,
        remove_watermark=args.remove_watermark,
        watermark_threshold=args.watermark_threshold,
        enhance_image=args.enhance,
        contrast_enhancement=args.enhance,  # Linked to enhance for now in CLI
        contrast_level=args.contrast_level,
        denoising_method=args.denoising,
        sharpening=args.sharpen,
        convert_grayscale=args.grayscale,
    )

    try:
        logger.info(f"Starting deskewing: {input_path}")
        logger.info(f"Output will be saved to: {output_path}")
        logger.info(f"Config: {config}")

        deskew_pdf(
            input_path,
            output_path,
            config=config,
        )

        logger.info("Deskewing completed successfully!")
        print(f"✓ PDF deskewed successfully: {output_path}")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Error during deskewing: {e}", exc_info=True)
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
