"""PDF Deskew Tool - A tool for deskewing scanned PDF documents."""

import argparse
import logging
import sys
from pathlib import Path

from .deskew_pdf import deskew_pdf

__version__ = "0.1.7"
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
    parser.add_argument(
        "--enhance", action="store_true", help="Enable image enhancement"
    )
    parser.add_argument(
        "--remove-watermark", action="store_true", help="Enable watermark removal"
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

    # Prepare features
    selected_features = {
        "enhance_image": args.enhance,
        "remove_watermark": args.remove_watermark,
        "contrast_enhancement": args.enhance,
        "convert_grayscale": False,
        "contrast_level": 2,
        "denoising_method": "Gaussian",
        "denoising_kernel": 3,
        "sharpening": False,
        "sharpening_strength": 3,
        "watermark_removal_method": "Inpainting",
        "inpainting_algorithm": "Telea",
        "watermark_mask_threshold": 127,
        "grayscale_quant_levels": 64,
        "grayscale_scale_factor": 1,
        "grayscale_smoothing_method": "Gaussian",
        "grayscale_smoothing_kernel": 3,
    }

    try:
        logger.info(f"Starting deskewing: {input_path}")
        logger.info(f"Output will be saved to: {output_path}")
        logger.info(f"DPI: {args.dpi}")
        logger.info(f"Background color: {args.bg_color}")

        deskew_pdf(
            input_path,
            output_path,
            dpi=args.dpi,
            background_color=bg_color,
            selected_features=selected_features,
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
