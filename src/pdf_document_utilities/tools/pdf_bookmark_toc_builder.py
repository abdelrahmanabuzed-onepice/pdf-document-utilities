"""PDF hierarchical bookmark outline and Table of Contents injection builder."""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional
import pypdf


def execute_pdf_bookmark_toc_builder(
    input_path: str,
    output_path: str,
    bookmarks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Inject hierarchical outline bookmarks into a PDF document.

    Args:
        input_path: Path to target PDF document.
        output_path: Output path for PDF with outline bookmarks.
        bookmarks: List of bookmark objects, each having 'title', 'page' (1-indexed),
                   and optional nested 'children' list.

    Returns:
        Structured dictionary summarizing injected bookmarks.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"PDF document not found: {input_path}")

    reader = pypdf.PdfReader(input_path)
    total_pages = len(reader.pages)

    writer = pypdf.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    injected_count = 0

    def add_outline_recursive(items: List[Dict[str, Any]], parent_outline=None):
        nonlocal injected_count
        for item in items:
            title = str(item.get("title", "Untitled"))
            page_num = int(item.get("page", 1)) - 1
            if not (0 <= page_num < total_pages):
                page_num = 0

            outline_item = writer.add_outline_item(
                title=title,
                page_number=page_num,
                parent=parent_outline,
            )
            injected_count += 1

            children = item.get("children", [])
            if children and isinstance(children, list):
                add_outline_recursive(children, parent_outline=outline_item)

    add_outline_recursive(bookmarks)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    with open(output_path, "wb") as out_f:
        writer.write(out_f)

    return {
        "status": "success",
        "input_path": input_path,
        "output_path": output_path,
        "bookmarks_injected": injected_count,
        "total_pages": total_pages,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        description="PDF hierarchical bookmark outline and Table of Contents injection builder."
    )
    parser.add_argument("--input", "-i", required=True, help="Input PDF file path")
    parser.add_argument("--output", "-o", required=True, help="Output PDF destination path")
    parser.add_argument(
        "--bookmarks-json",
        "-b",
        required=True,
        help="Path to JSON file containing bookmark definitions or JSON string",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if os.path.isfile(args.bookmarks_json):
            with open(args.bookmarks_json, "r", encoding="utf-8") as f:
                b_data = json.load(f)
        else:
            b_data = json.loads(args.bookmarks_json)

        res = execute_pdf_bookmark_toc_builder(
            input_path=args.input,
            output_path=args.output,
            bookmarks=b_data if isinstance(b_data, list) else [b_data],
        )
        print(f"Injected {res['bookmarks_injected']} bookmarks into {res['output_path']}")
        return 0
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
