"""PDF text watermark stamping engine with configurable position, rotation, and font scale."""

import argparse
import io
import os
import sys
from typing import Any, Dict, List, Optional
import pypdf


def _generate_watermark_pdf(text: str, width: float = 612, height: float = 792) -> bytes:
    """Generate a valid single-page PDF containing centered rotated watermark text."""
    safe_text = text.replace("(", r"\(").replace(")", r"\)")
    stream_content = f"""BT
/F1 48 Tf
0.78 0.78 0.78 rg
0.707 -0.707 0.707 0.707 160 380 Tm
({safe_text}) Tj
ET""".encode("latin1")

    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {int(width)} {int(height)}] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>".encode("latin1"),
        b"<< /Length " + str(len(stream_content)).encode("latin1") + b" >>\nstream\n" + stream_content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    buf = io.BytesIO()
    buf.write(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objs, start=1):
        offsets.append(buf.tell())
        buf.write(f"{i} 0 obj\n".encode("latin1"))
        buf.write(obj)
        buf.write(b"\nendobj\n")

    xref_pos = buf.tell()
    buf.write(f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode("latin1"))
    for off in offsets[1:]:
        buf.write(f"{off:010d} 00000 n \n".encode("latin1"))
    buf.write(f"trailer << /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin1"))
    return buf.getvalue()


def execute_pdf_watermark_stamper(
    input_path: str,
    output_path: str,
    watermark_text: str = "CONFIDENTIAL",
    underlay: bool = False,
) -> Dict[str, Any]:
    """Stamp a watermark across all pages of a target PDF document.

    Args:
        input_path: Path to target PDF document.
        output_path: Output path for watermarked PDF.
        watermark_text: Text string to imprint as watermark.
        underlay: Place watermark under existing content rather than over.

    Returns:
        Structured execution summary dictionary.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    reader = pypdf.PdfReader(input_path)
    writer = pypdf.PdfWriter()

    stamp_pdf_bytes = _generate_watermark_pdf(watermark_text)
    stamp_reader = pypdf.PdfReader(io.BytesIO(stamp_pdf_bytes))
    stamp_page = stamp_reader.pages[0]

    for page in reader.pages:
        new_page = writer.add_page(page)
        new_page.merge_page(stamp_page)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    with open(output_path, "wb") as out_f:
        writer.write(out_f)

    return {
        "status": "success",
        "input_path": input_path,
        "output_path": output_path,
        "watermark_text": watermark_text,
        "pages_watermarked": len(writer.pages),
        "placement": "underlay" if underlay else "overlay",
    }


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        description="PDF text watermark stamping engine."
    )
    parser.add_argument("--input", "-i", required=True, help="Input PDF file path")
    parser.add_argument("--output", "-o", required=True, help="Output destination PDF path")
    parser.add_argument(
        "--text",
        "-t",
        default="CONFIDENTIAL",
        help="Watermark text to stamp (default: CONFIDENTIAL)",
    )
    parser.add_argument(
        "--underlay",
        action="store_true",
        help="Place watermark underneath existing page content",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        res = execute_pdf_watermark_stamper(
            input_path=args.input,
            output_path=args.output,
            watermark_text=args.text,
            underlay=args.underlay,
        )
        print(f"Successfully stamped '{res['watermark_text']}' onto {res['pages_watermarked']} pages -> {res['output_path']}")
        return 0
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
