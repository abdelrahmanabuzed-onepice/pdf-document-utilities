"""PDF page reordering, rearrangement, and rotation tool."""

import argparse
import os
import sys
from typing import Any, Dict, List, Optional
import pypdf


def execute_pdf_page_reorder_rotator(
    input_path: str,
    output_path: str,
    page_order: Optional[List[int]] = None,
    rotations: Optional[Dict[int, int]] = None,
    global_rotation: int = 0,
) -> Dict[str, Any]:
    """Reorder and rotate pages of a PDF document.

    Args:
        input_path: Path to target PDF document.
        output_path: Output path for modified PDF.
        page_order: 1-indexed list of page order (e.g. [3, 1, 2]). Defaults to sequential.
        rotations: Dictionary mapping 1-indexed page numbers to rotation angles (90, 180, 270).
        global_rotation: Rotation angle applied to all pages not explicitly mapped.

    Returns:
        Structured dictionary summarizing executed reordering and rotations.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"PDF document not found: {input_path}")

    reader = pypdf.PdfReader(input_path)
    total_pages = len(reader.pages)

    if not page_order:
        page_order = list(range(1, total_pages + 1))

    rotations = rotations or {}
    writer = pypdf.PdfWriter()
    applied_rotations: Dict[int, int] = {}

    for target_p in page_order:
        if not (1 <= target_p <= total_pages):
            continue
        page = reader.pages[target_p - 1]
        rot = rotations.get(target_p, global_rotation)
        if rot in (90, 180, 270):
            page.rotate(rot)
            applied_rotations[target_p] = rot
        writer.add_page(page)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    with open(output_path, "wb") as out_f:
        writer.write(out_f)

    return {
        "status": "success",
        "input_path": input_path,
        "output_path": output_path,
        "original_page_count": total_pages,
        "output_page_count": len(writer.pages),
        "page_order": page_order,
        "rotations_applied": applied_rotations,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        description="PDF page reordering, rearrangement, and rotation tool."
    )
    parser.add_argument("--input", "-i", required=True, help="Input PDF file path")
    parser.add_argument("--output", "-o", required=True, help="Output destination PDF path")
    parser.add_argument(
        "--order",
        "-p",
        type=int,
        nargs="+",
        help="1-indexed sequence of page numbers (e.g. 3 1 2)",
    )
    parser.add_argument(
        "--rotate",
        "-r",
        type=int,
        choices=[0, 90, 180, 270],
        default=0,
        help="Uniform rotation angle in degrees clockwise",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        res = execute_pdf_page_reorder_rotator(
            input_path=args.input,
            output_path=args.output,
            page_order=args.order,
            global_rotation=args.rotate,
        )
        print(f"Reordered PDF written to {res['output_path']} ({res['output_page_count']} pages)")
        return 0
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
