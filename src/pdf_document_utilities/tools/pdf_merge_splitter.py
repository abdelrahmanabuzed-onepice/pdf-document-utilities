"""PDF merging and page range splitting utility utilizing offline stream processing."""

import argparse
import os
import sys
from typing import Any, Dict, List, Optional
import pypdf


def _parse_page_ranges(range_str: str, max_pages: int) -> List[int]:
    """Parse comma-separated page ranges (e.g. '1-3,5,7-9') into zero-indexed integer list."""
    pages = []
    for part in range_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = max(1, int(start_s.strip()))
            end = min(max_pages, int(end_s.strip()))
            pages.extend(range(start - 1, end))
        else:
            p = int(part)
            if 1 <= p <= max_pages:
                pages.append(p - 1)
    return pages


def execute_pdf_merge_splitter(
    mode: str,
    input_files: List[str],
    output_path: str,
    page_ranges: Optional[str] = None,
    rotation: int = 0,
) -> Dict[str, Any]:
    """Merge multiple PDFs or split a PDF across designated page ranges.

    Args:
        mode: Operation mode ('merge' or 'split').
        input_files: List of input PDF file paths.
        output_path: Target path for output PDF file.
        page_ranges: 1-indexed page ranges for splitting (e.g. '1-3,5').
        rotation: Optional rotation angle (0, 90, 180, 270) to apply.

    Returns:
        Structured dictionary reporting operations and final page count.
    """
    for f in input_files:
        if not os.path.isfile(f):
            raise FileNotFoundError(f"Input PDF not found: {f}")

    writer = pypdf.PdfWriter()

    if mode == "merge":
        total_source_pages = 0
        for f in input_files:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                if rotation in (90, 180, 270):
                    page.rotate(rotation)
                writer.add_page(page)
                total_source_pages += 1

    elif mode == "split":
        source_file = input_files[0]
        reader = pypdf.PdfReader(source_file)
        total_source_pages = len(reader.pages)

        if page_ranges:
            selected_indices = _parse_page_ranges(page_ranges, total_source_pages)
        else:
            selected_indices = list(range(total_source_pages))

        for idx in selected_indices:
            page = reader.pages[idx]
            if rotation in (90, 180, 270):
                page.rotate(rotation)
            writer.add_page(page)
    else:
        raise ValueError(f"Unknown mode: {mode}. Choose 'merge' or 'split'.")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    with open(output_path, "wb") as out_f:
        writer.write(out_f)

    return {
        "status": "success",
        "mode": mode,
        "input_files": input_files,
        "output_path": output_path,
        "pages_written": len(writer.pages),
        "rotation_applied": rotation,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        description="PDF merging and page range splitting utility."
    )
    parser.add_argument(
        "--mode",
        "-m",
        choices=["merge", "split"],
        required=True,
        help="Operation mode: 'merge' or 'split'",
    )
    parser.add_argument(
        "--inputs",
        "-i",
        nargs="+",
        required=True,
        help="Input PDF file path(s)",
    )
    parser.add_argument("--output", "-o", required=True, help="Output destination PDF path")
    parser.add_argument(
        "--pages",
        "-p",
        help="Page range expression for split mode (e.g. '1-4,7,9-12')",
    )
    parser.add_argument(
        "--rotate",
        "-r",
        type=int,
        choices=[0, 90, 180, 270],
        default=0,
        help="Clockwise rotation degrees",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        res = execute_pdf_merge_splitter(
            mode=args.mode,
            input_files=args.inputs,
            output_path=args.output,
            page_ranges=args.pages,
            rotation=args.rotate,
        )
        print(f"Success: {res['mode'].capitalize()} written {res['pages_written']} pages to {res['output_path']}")
        return 0
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
