"""PDF embedded image extraction and page rasterization utility."""

import argparse
import os
import sys
from typing import Any, Dict, List, Optional
import pypdf


def execute_pdf_image_rasterizer(
    input_path: str,
    output_dir: str,
    page_numbers: Optional[List[int]] = None,
    image_format: str = "png",
) -> Dict[str, Any]:
    """Extract embedded raster images from PDF pages.

    Args:
        input_path: Path to target PDF.
        output_dir: Directory where extracted images will be saved.
        page_numbers: Optional 1-indexed list of pages to scan.
        image_format: Target format extension ('png', 'jpg').

    Returns:
        Structured dictionary reporting extracted images and file paths.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"PDF document not found: {input_path}")

    reader = pypdf.PdfReader(input_path)
    total_pages = len(reader.pages)

    if page_numbers:
        target_indices = [p - 1 for p in page_numbers if 1 <= p <= total_pages]
    else:
        target_indices = list(range(total_pages))

    os.makedirs(output_dir, exist_ok=True)
    extracted_images: List[Dict[str, Any]] = []

    for idx in target_indices:
        page = reader.pages[idx]
        for img_idx, img in enumerate(page.images):
            ext = image_format.lower().lstrip(".")
            file_name = f"page_{idx + 1}_img_{img_idx + 1}.{ext}"
            file_path = os.path.join(output_dir, file_name)

            with open(file_path, "wb") as f:
                f.write(img.data)

            extracted_images.append({
                "page": idx + 1,
                "image_index": img_idx + 1,
                "file_path": file_path,
                "size_bytes": len(img.data),
                "original_name": img.name,
            })

    return {
        "status": "success",
        "input_path": input_path,
        "output_directory": output_dir,
        "images_extracted": len(extracted_images),
        "pages_scanned": len(target_indices),
        "files": extracted_images,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        description="PDF embedded image extraction and page rasterization utility."
    )
    parser.add_argument("--input", "-i", required=True, help="Input PDF file path")
    parser.add_argument("--output-dir", "-o", required=True, help="Output directory for extracted images")
    parser.add_argument(
        "--pages",
        "-p",
        type=int,
        nargs="+",
        help="Specific 1-indexed page numbers to scan",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["png", "jpg"],
        default="png",
        help="Image file extension",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        res = execute_pdf_image_rasterizer(
            input_path=args.input,
            output_dir=args.output_dir,
            page_numbers=args.pages,
            image_format=args.format,
        )
        print(f"Extracted {res['images_extracted']} images to {res['output_directory']}")
        return 0
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
