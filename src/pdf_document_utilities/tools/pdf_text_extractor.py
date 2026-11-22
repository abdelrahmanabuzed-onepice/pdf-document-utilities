"""PDF text extraction utility preserving page-by-page structure and layout."""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional
import pypdf


def execute_pdf_text_extractor(
    input_path: str,
    output_path: Optional[str] = None,
    output_format: str = "text",
    page_numbers: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """Extract textual content from PDF pages with structural layout awareness.

    Args:
        input_path: Path to target PDF document.
        output_path: Optional destination file for extracted text.
        output_format: Output format ('text' or 'json').
        page_numbers: Optional 1-indexed list of specific pages to extract.

    Returns:
        Structured dictionary containing extracted text and character metrics.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"PDF document not found: {input_path}")

    reader = pypdf.PdfReader(input_path)
    total_pages = len(reader.pages)

    if page_numbers:
        target_indices = [p - 1 for p in page_numbers if 1 <= p <= total_pages]
    else:
        target_indices = list(range(total_pages))

    pages_text: List[Dict[str, Any]] = []
    full_text_chunks: List[str] = []

    for idx in target_indices:
        page = reader.pages[idx]
        extracted = page.extract_text() or ""
        pages_text.append({
            "page_number": idx + 1,
            "text": extracted,
            "character_count": len(extracted),
            "word_count": len(extracted.split()),
        })
        full_text_chunks.append(f"--- Page {idx + 1} ---\n{extracted}\n")

    combined_text = "\n".join(full_text_chunks)

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as out_f:
            if output_format.lower() == "json":
                json.dump(pages_text, out_f, indent=2)
            else:
                out_f.write(combined_text)

    total_characters = sum(p["character_count"] for p in pages_text)
    total_words = sum(p["word_count"] for p in pages_text)

    return {
        "status": "success",
        "input_path": input_path,
        "output_path": output_path,
        "pages_extracted": len(pages_text),
        "total_pages": total_pages,
        "total_characters": total_characters,
        "total_words": total_words,
        "pages": pages_text,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        description="PDF text extraction utility preserving page layout and word statistics."
    )
    parser.add_argument("--input", "-i", required=True, help="Path to input PDF file")
    parser.add_argument("--output", "-o", help="Path to write extracted text output")
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="Format for output file (plain text or structured JSON)",
    )
    parser.add_argument(
        "--pages",
        "-p",
        type=int,
        nargs="+",
        help="Specific 1-indexed page numbers to extract",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        res = execute_pdf_text_extractor(
            input_path=args.input,
            output_path=args.output,
            output_format=args.format,
            page_numbers=args.pages,
        )
        print(f"Extracted {res['pages_extracted']} pages ({res['total_words']} words, {res['total_characters']} characters)")
        return 0
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
