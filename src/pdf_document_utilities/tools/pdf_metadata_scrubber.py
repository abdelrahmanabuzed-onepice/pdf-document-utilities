"""PDF metadata inspector and sanitizer purging author tags and software footprints."""

import argparse
import os
import sys
from typing import Any, Dict, List, Optional
import pypdf


def execute_pdf_metadata_scrubber(
    input_path: str,
    output_path: Optional[str] = None,
    inspect_only: bool = False,
) -> Dict[str, Any]:
    """Inspect or purge metadata fields from a PDF file.

    Args:
        input_path: Path to target PDF.
        output_path: Path to save sanitized PDF (required if not inspect_only).
        inspect_only: Only read and report metadata without writing.

    Returns:
        Structured dictionary listing metadata before and after scrubbing.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"PDF file not found: {input_path}")

    reader = pypdf.PdfReader(input_path)
    raw_metadata = reader.metadata or {}

    metadata_dict: Dict[str, str] = {}
    for k, v in raw_metadata.items():
        key_str = str(k).lstrip("/")
        metadata_dict[key_str] = str(v)

    if inspect_only or not output_path:
        return {
            "status": "success",
            "mode": "inspect",
            "input_path": input_path,
            "metadata_fields": metadata_dict,
            "field_count": len(metadata_dict),
        }

    writer = pypdf.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    # Purge metadata by setting empty metadata dictionary
    writer.add_metadata({})

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    with open(output_path, "wb") as out_f:
        writer.write(out_f)

    return {
        "status": "success",
        "mode": "scrub",
        "input_path": input_path,
        "output_path": output_path,
        "purged_fields": list(metadata_dict.keys()),
        "purged_count": len(metadata_dict),
    }


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        description="PDF metadata inspector and sanitizer purging author tags and footprints."
    )
    parser.add_argument("--input", "-i", required=True, help="Input PDF file path")
    parser.add_argument("--output", "-o", help="Output sanitized PDF path")
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="Inspect metadata only without modifying or writing output",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        res = execute_pdf_metadata_scrubber(
            input_path=args.input,
            output_path=args.output,
            inspect_only=args.inspect,
        )
        if res["mode"] == "inspect":
            print(f"Found {res['field_count']} metadata attributes in {res['input_path']}:")
            for k, v in res["metadata_fields"].items():
                print(f"  {k}: {v}")
        else:
            print(f"Purged {res['purged_count']} metadata attributes -> {res['output_path']}")
        return 0
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
