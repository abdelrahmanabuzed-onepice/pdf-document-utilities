"""PDF tabular structure detection and CSV extraction engine."""

import argparse
import csv
import os
import re
import sys
from typing import Any, Dict, List, Optional
import pypdf


def _extract_tables_from_text(text: str, min_columns: int = 2) -> List[List[List[str]]]:
    """Parse structured text lines into detected table matrix representations."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    tables: List[List[List[str]]] = []
    current_table: List[List[str]] = []

    for line in lines:
        # Check if line contains pipe or multi-space column separators
        if "|" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
        else:
            parts = [p.strip() for p in re.split(r"\s{2,}|\t+", line) if p.strip()]

        if len(parts) >= min_columns:
            current_table.append(parts)
        else:
            if len(current_table) >= 2:
                tables.append(current_table)
            current_table = []

    if len(current_table) >= 2:
        tables.append(current_table)

    return tables


def execute_pdf_table_extractor(
    input_path: str,
    output_path: Optional[str] = None,
    page_numbers: Optional[List[int]] = None,
    min_columns: int = 2,
) -> Dict[str, Any]:
    """Extract structured tabular data from PDF documents into CSV matrices.

    Args:
        input_path: Path to target PDF.
        output_path: Optional path to write extracted CSV.
        page_numbers: Optional 1-indexed page list to scan.
        min_columns: Minimum column count threshold for table rows.

    Returns:
        Structured dictionary reporting discovered tables and rows.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"PDF document not found: {input_path}")

    reader = pypdf.PdfReader(input_path)
    total_pages = len(reader.pages)

    if page_numbers:
        target_indices = [p - 1 for p in page_numbers if 1 <= p <= total_pages]
    else:
        target_indices = list(range(total_pages))

    all_tables: List[Dict[str, Any]] = []
    flat_rows: List[List[str]] = []

    for idx in target_indices:
        page = reader.pages[idx]
        text = page.extract_text() or ""
        page_tables = _extract_tables_from_text(text, min_columns=min_columns)

        for t_idx, tbl in enumerate(page_tables):
            all_tables.append({
                "page": idx + 1,
                "table_index": t_idx + 1,
                "row_count": len(tbl),
                "column_count": max(len(r) for r in tbl) if tbl else 0,
                "rows": tbl,
            })
            flat_rows.extend(tbl)

    if output_path and flat_rows:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
        max_cols = max(len(r) for r in flat_rows)
        with open(output_path, "w", encoding="utf-8", newline="") as out_f:
            writer = csv.writer(out_f)
            for row in flat_rows:
                padded = row + [""] * (max_cols - len(row))
                writer.writerow(padded)

    return {
        "status": "success",
        "input_path": input_path,
        "output_path": output_path,
        "tables_detected": len(all_tables),
        "total_rows_extracted": len(flat_rows),
        "tables": all_tables,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        description="PDF tabular structure detection and CSV extraction engine."
    )
    parser.add_argument("--input", "-i", required=True, help="Input PDF file path")
    parser.add_argument("--output", "-o", help="Output CSV file path")
    parser.add_argument(
        "--pages",
        "-p",
        type=int,
        nargs="+",
        help="Specific 1-indexed page numbers to scan",
    )
    parser.add_argument(
        "--min-cols",
        "-c",
        type=int,
        default=2,
        help="Minimum columns to qualify as tabular data",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        res = execute_pdf_table_extractor(
            input_path=args.input,
            output_path=args.output,
            page_numbers=args.pages,
            min_columns=args.min_cols,
        )
        print(f"Extracted {res['tables_detected']} tables ({res['total_rows_extracted']} rows) from {res['input_path']}")
        return 0
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
