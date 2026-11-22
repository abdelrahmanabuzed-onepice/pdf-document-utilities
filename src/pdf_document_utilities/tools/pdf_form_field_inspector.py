"""Interactive PDF form field, AcroForm value, and digital signature inspector."""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional
import pypdf


def execute_pdf_form_field_inspector(
    input_path: str,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Inspect and extract AcroForm fields, values, and signatures from a PDF.

    Args:
        input_path: Path to target PDF document.
        output_path: Optional destination to write JSON report.

    Returns:
        Structured dictionary listing form fields, types, and values.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"PDF document not found: {input_path}")

    reader = pypdf.PdfReader(input_path)
    fields = reader.get_fields() or {}

    inspected_fields: List[Dict[str, Any]] = []
    for field_name, field_data in fields.items():
        if isinstance(field_data, dict):
            field_type = str(field_data.get("/FT", "Unknown"))
            value = str(field_data.get("/V", ""))
            default_val = str(field_data.get("/DV", ""))
            read_only = bool(int(field_data.get("/Ff", 0)) & 1)
        else:
            field_type = "Object"
            value = str(field_data)
            default_val = ""
            read_only = False

        inspected_fields.append({
            "name": field_name,
            "type": field_type,
            "value": value,
            "default_value": default_val,
            "read_only": read_only,
        })

    result = {
        "status": "success",
        "input_path": input_path,
        "output_path": output_path,
        "total_fields": len(inspected_fields),
        "fields": inspected_fields,
        "has_form_fields": len(inspected_fields) > 0,
    }

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as out_f:
            json.dump(result, out_f, indent=2)

    return result


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Interactive PDF form field, AcroForm value, and signature inspector."
    )
    parser.add_argument("--input", "-i", required=True, help="Input PDF file path")
    parser.add_argument("--output", "-o", help="Output path for JSON report")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        res = execute_pdf_form_field_inspector(
            input_path=args.input,
            output_path=args.output,
        )
        print(f"Found {res['total_fields']} form fields in {res['input_path']}")
        return 0
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
